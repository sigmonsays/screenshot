import logging
import os
import platform
import random
import string
import time
import urllib

from screenshot.capture import MakeCapture
from screenshot.clipboard import MakeClipboard
from screenshot.upload import NullUpload
from screenshot.upload.shell import ShellUpload

try:
    from screenshot.upload.s3 import S3Upload
except ImportError:
    S3Upload = NullUpload

try:
    from screenshot.upload.couchdb import CouchdbUpload
except ImportError:
    CouchdbUpload = NullUpload

try:
    from screenshot.upload.imgur import ImgurUpload
except ImportError:
    ImgurUpload = NullUpload

try:
    from screenshot.upload.tumblr import TumblrUpload
except ImportError:
    TumblrUpload = NullUpload

from screenshot.upload.filesystem import FilesystemUpload
from screenshot.tinyurl import MakeTinyUrl

class ShotMetadata:

    def __init__(self):
        self.screenshot_dir = None
        self.shortname = "screenshot"
        self.summary = None
        self.now = time.localtime()
        self.ts = time.strftime("%F-%T").replace(":", "-")
        self.url = None

    def __str__(self):
        ret = "<%s " % (self.__class__.__name__)
        ret += " ".join([ "%s=%s" % (k, v) for k, v in self.to_dict().iteritems() ])
        ret += ">"
        return ret

    def to_dict(self):
        return self.__dict__

    def get_filename(self):
        basename = "%s-%s.jpg" % ( self.shortname, self.ts )
        return os.path.join(self.screenshot_dir, basename)

    def get_url(self):
        return self.url
    
class Screenshot(object):
   def __init__(self, opts):
      self.log = logging.getLogger(self.__class__.__name__)
      self.opts = opts
      self.screenshot_dir = opts.screenshot_dir
      self.screenshot_index = opts.screenshot_index
      self.disk_config = opts.disk_config
      self.s3_config = opts.s3_config
      self.tumblr_config = opts.tumblr_config
      self.imgur_config = opts.imgur_config
      self.shell_config = opts.shell_config
      self.couchdb_config = opts.couchdb_config
      self.use_clipboard = opts.use_clipboard
      self.clipboard_method = opts.clipboard_method
      self.random_filename = opts.random_filename
      self.capture_method = opts.capture_method
      self.warm_cache = opts.warm_cache
      self.egress_url = opts.egress_url
      self.tinyurl_config = opts.tinyurl_config

      self.platform = platform.system()
      self.tiny = MakeTinyUrl(opts.tinyurl_config)
      self.uploaders = {}
      self.uploader_config = {}

   def register_uploader(self, uploader, cfg):
      self.uploaders[uploader.upload_method] = uploader
      self.uploader_config[uploader.upload_method] = cfg
      self.log.debug("Registered %s", uploader)

   def configure_filesystem(self):
      if not self.disk_config:
         return
      if self.disk_config.get('enabled') != True:
         return
      c = self.disk_config
      save_dir = os.path.expanduser(c['save_dir'])
      filesystem = FilesystemUpload(self.clipboard, save_dir)
      self.register_uploader(filesystem, self.disk_config)

   def configure_s3(self):
      if not self.s3_config or S3Upload == NullUpload:
         return
      if self.s3_config.get('enabled') != True:
         return
      c = self.s3_config
      s3 = S3Upload(self.clipboard, c['key'], c['secret'], c['end_point'], c['bucket'])
      self.register_uploader(s3, self.s3_config)

   def configure_couchdb(self):
      if not self.couchdb_config or CouchdbUpload == NullUpload:
         return
      if self.couchdb_config.get('enabled') != True:
         return
      couchdb_uri = self.couchdb_config['uri']
      couchdb = CouchdbUpload(self.clipboard, couchdb_uri)
      self.register_uploader(couchdb, self.couchdb_config)

   def configure_imgur(self):
      if not self.imgur_config or ImgurUpload == NullUpload:
         return
      if self.imgur_config.get('enabled') != True:
         return

      imgur = ImgurUpload(self.clipboard, self.imgur_config['client_id'], self.imgur_config['client_secret'])
      self.register_uploader(imgur, self.imgur_config)

   def configure_shell(self):
      if not self.shell_config or ShellUpload == NullUpload:
         return
      if self.shell_config.get('enabled') != True:
         return

      shell = ShellUpload(self.clipboard, self.shell_config['template'])
      self.register_uploader(shell, self.shell_config)

   def configure_tumblr(self):
      if not self.tumblr_config or TumblrUpload == NullUpload:
         return
      if self.tumblr_config.get('enabled') != True:
         return

      c = self.tumblr_config
      tumblr = TumblrUpload(self.clipboard, c['blog_url'], c['consumer_key'], c['consumer_secret'], c['oauth_token'], c['oauth_secret'])
      self.register_uploader(tumblr, self.tumblr_config)

   def configure(self):

      self.capture = MakeCapture()
      self.clipboard = MakeClipboard()

      self.configure_filesystem()
      self.configure_s3()
      self.configure_couchdb()
      self.configure_imgur()
      self.configure_tumblr()
      self.configure_shell()


   def get_shot(self, shortname, summary):
      """
      return a local filename where we save our screenshot

      This is a temporary location and will be deleted when finished
      """

      meta = ShotMetadata()
      meta.screenshot_dir = self.screenshot_dir
      meta.summary = summary
      if self.random_filename:
         meta.ts  = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(18)])
      if shortname == None:
         meta.shortname = 'screenshot'
      else:
         meta.shortname = shortname
      self.log.debug("return %s", meta)
      return meta

   def take_screenshot(self, shortname=None, summary=None):
      meta = self.get_shot(shortname, summary)

      filename = meta.get_filename()
      dir = os.path.dirname(filename)
      if not os.path.exists(dir): os.makedirs(dir)

      tmpl = {
          'basename'  : os.path.basename(filename),
          'filename'  : filename,
          'key'       : os.path.join(meta.ts.replace(":", "/").replace("-", "/"), meta.shortname) + ".jpg",
      }
      tmpl.update(meta.to_dict())
      egress_url = self.egress_url % tmpl
      meta.url = egress_url

      result = self.capture.capture(filename)
      if result != True:
        self.log.error("Capturing screenshot failed, result %s", result)
        return

      self.log.info("Uploading %s to %d places", filename, len(self.uploaders))
      for uploader_name, uploader in self.uploaders.iteritems():
        print
        if isinstance(uploader, NullUpload):
            self.log.error("Support for %s is not available", uploader_name)
            continue

        uploader_config = self.uploader_config[uploader_name]
        if uploader_config.get('active') == False:
            self.log.debug("Skipping %s due to active=False", uploader_name)
            continue

        self.log.debug("%s Uploading %s", uploader.__class__.__name__, filename)
        result = uploader.upload(meta, filename, meta.shortname)
        if result != True:
            self.log.warn("Uploading to %s failed: result %s", uploader.__class__.__name__, result)
            continue

        # Decide if we should clipboard the url or not
        if self.clipboard_method == uploader.upload_method:
            if uploader.url:
                self.clipboard.add_url(uploader.url)
            else:
                self.log.warn("clipboard method set to %s but no url returned", self.clipboard_method)

      clipboard_url = self.clipboard.get_url()
      self.log.info("clipboard url %s", clipboard_url)

      short_url = self.tiny.make_url(clipboard_url)
      if short_url:
        self.clipboard.add_url(short_url)

      self.log.debug("clipboard method %s", self.clipboard_method)

      if self.clipboard_method == 'tinurl':
            self.clipboard.copy(short_url)
      elif self.clipboard_method == 'template':
            self.clipboard.copy(egress_url)
            clipboard_url = egress_url
      elif clipboard_url:
            self.clipboard.copy(clipboard_url)
      elif self.clipboard_method == 'last':
            clipboard_url = self.clipboard.get_url()
            self.clipboard.copy(clipboard_url)
      else:
            self.log.error("Invalid clipboard method %s", self.clipboard_method)
            clipboard_url = self.clipboard.get_url()

      if self.warm_cache == True:
            self.warm_cache_url(clipboard_url)
      
      # trash original
      os.unlink(filename)


   def warm_cache_url(self, url):
      f = None
      self.log.info("warm cache url %s", url)
      try:
         f = urllib.urlopen(url)
      except Exception, e:
         self.log.error("%s", e)
         return

      content = f.read()
      self.log.info("read %d bytes from %s", len(content), url)
      return

