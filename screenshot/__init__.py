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

from screenshot.upload.filesystem import FilesystemUpload
from screenshot.tinyurl import MakeTinyUrl

class Screenshot(object):
   def __init__(self, opts):
      self.log = logging.getLogger(self.__class__.__name__)
      self.screenshot_dir = opts.screenshot_dir
      self.screenshot_index = opts.screenshot_index
      self.disk_config = opts.disk_config
      self.s3_config = opts.s3_config
      self.imgur_config = opts.imgur_config
      self.couchdb_config = opts.couchdb_config
      self.use_clipboard = opts.use_clipboard
      self.clipboard_method = opts.clipboard_method
      self.random_filename = opts.random_filename
      self.capture_method = opts.capture_method
      self.warm_cache = opts.warm_cache
      self.egress_url = opts.egress_url
      self.tinyurl_config = opts.tinyurl_config

      self.egress_url = opts.egress_url

      self.platform = platform.system()
      self.tiny = MakeTinyUrl(opts.tinyurl_config)
      self.uploaders = {}

   def configure_filesystem(self):
      if not self.disk_config:
         return
      if not self.disk_config.get('enabled') != True:
         return
      c = self.disk_config
      save_dir = os.path.expanduser(c['save_dir'])
      filesystem = FilesystemUpload(self.clipboard, save_dir)
      self.uploaders['filesystem'] = filesystem

   def configure_s3(self):
      if not self.s3_config or S3Upload == NullUpload:
         return
      if self.s3_config.get('enabled') != True:
         return
      c = self.s3_config
      s3 = S3Upload(self.clipboard, c['key'], c['secret'], c['end_point'], c['bucket'])
      self.uploaders['s3'] = s3

   def configure_couchdb(self):
      if not self.couchdb_config or CouchdbUpload == NullUpload:
         return
      if self.couchdb_config.get('enabled') != True:
         return
      couchdb_uri = self.couchdb_config['uri']
      couchdb = CouchdbUpload(self.clipboard, couchdb_uri)
      self.uploaders['couchdb'] = couchdb

   def configure_imgur(self):
      if not self.imgur_config or ImgurUpload == NullUpload:
         return
      if self.imgur_config.get('enabled') != True:
         return

      imgur = ImgurUpload(self.clipboard, self.imgur_config['client_id'], self.imgur_config['client_secret'])
      self.uploaders['imgur'] = imgur

   def configure(self):

      self.capture = MakeCapture()
      self.clipboard = MakeClipboard()

      self.configure_filesystem()
      self.configure_s3()
      self.configure_couchdb()
      self.configure_imgur()


   def get_shortname(self, shortname=None):
      if shortname == None:
         shortname = "screenshot"
      return shortname

   def get_filename(self):
      """
      return a local filename where we save our screenshot

      This is a temporary location and will be deleted when finished
      """
      ts = time.strftime("%F-%T").replace(":", "-")
      shortname = self.get_shortname()

      if self.random_filename:
         ts  = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(18)])

      basename = "%s-%s.jpg" % ( shortname, ts )
      filename = os.path.join(self.screenshot_dir, basename)
      self.log.debug("return %s", filename)
      return filename

   def take_screenshot(self, shortname=None):
      shortname = self.get_shortname(shortname)
      filename = self.get_filename()
      dir = os.path.dirname(filename)
      if not os.path.exists(dir): os.makedirs(dir)

      result = self.capture.capture(filename)
      if result != True:
        self.log.error("Capturing screenshot failed, result %s", result)
        return

      self.log.info("Uploading %s to %d places", filename, len(self.uploaders))
      for uploader_name, uploader in self.uploaders.iteritems():
        if isinstance(uploader, NullUpload):
            self.log.error("Support for %s is not available", uploader_name)
            continue

        self.log.debug("Uploading %s using %s", filename, uploader.__class__.__name__)
        result = uploader.upload(filename, shortname)
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
      if self.clipboard_method == 'tinurl':
            self.clipboard.copy(short_url)
      elif self.clipboard_method == 'template':
            egress_url = self.egress_url % (shortname)
            self.clipboard.copy(egress_url)
      elif clipboard_url:
            self.clipboard.copy(clipboard_url)

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

