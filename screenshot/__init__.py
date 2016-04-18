"""Screen shot program"""
import logging
import os
import platform
import random
import string
import time
import urllib

from screenshot.capture import MakeCapture
from screenshot.clipboard import MakeClipboard

# We use this wildcard import to autoload plugins.  FIXME: find a better way
from screenshot.upload import * # pylint: disable=wildcard-import
from screenshot.tinyurl import MakeTinyUrl

class ShotMetadata(object):
   """I have no idea what this is"""
   def __init__(self):
      self.screenshot_dir = None
      self.shortname = "screenshot"
      self.summary = None
      self.now = time.localtime()
      self.timestamp = time.strftime("%F-%T").replace(":", "-")
      self.url = None

   def __str__(self):
      ret = "<%s " % (self.__class__.__name__)
      ret += " ".join(["%s=%s" % (k, v) for k, v in self.to_dict().iteritems()])
      ret += ">"
      return ret

   def to_dict(self):
      return self.__dict__

   def get_filename(self):
      basename = "%s-%s.jpg" % (self.shortname, self.timestamp)
      return os.path.join(self.screenshot_dir, basename)

   def get_url(self):
      return self.url

class Screenshot(object):
   """Does sweet stuff"""
   def __init__(self, opts):
      self.log = logging.getLogger(self.__class__.__name__)
      self.opts = opts
      self.log.debug("screenshot plugins %s", UPLOAD_PLUGINS)

      capture_opts = {}
      if self.opts.capture_method != None:
          capture_opts['capture_method'] = self.opts.capture_method
          if self.opts.capture_method == 'custom':
            capture_opts['capture_command'] = self.opts.capture_command

      self.platform = platform.system()
      self.tiny = MakeTinyUrl(opts.tinyurl_config)
      self.capture = MakeCapture(**capture_opts)
      self.clipboard = MakeClipboard()
      self.configure_uploaders()

   def configure_uploaders(self):
      self.uploaders = {}
      for name, cls in UPLOAD_PLUGINS:
         self.log.debug("Checking available plugin %s", name)
         uopts = self.opts.get_uploader_options(name)
         # We wont get options if its either disabled or doesn't exist
         if uopts:
            self.log.info("Loading configured plugin %s", name)
            self.uploaders[name] = cls(
               uopts,
               self.opts,
               self.clipboard,
            )

   def get_shot(self, shortname, summary):
      """
      return a local filename where we save our screenshot

      This is a temporary location and will be deleted when finished
      """

      meta = ShotMetadata()
      meta.screenshot_dir = self.opts.screenshot_dir
      meta.summary = summary
      if self.opts.random_filename:
         meta.timestamp = ''.join([
            random.choice(string.ascii_letters + string.digits) for _ in xrange(18)
         ])
      if shortname == None:
         meta.shortname = 'screenshot'
      else:
         meta.shortname = shortname
      self.log.debug("return %s", meta)
      return meta

  
   def download_url(self, url, filename):
      f = None
      self.log.info("download url %s", url)
      try:
         f = urllib.urlopen(url)
      except Exception, e: # pylint: disable=broad-except
         self.log.error("%s", e)
         return

      out = open(filename, 'w+')
      while True:
          content = f.read(4096)
          if content == '':
              break
          out.write(content)
      out.close()

   def take_screenshot(self, shortname=None, summary=None):
      meta = self.get_shot(shortname, summary)

      filename = meta.get_filename()
      dirpath = os.path.dirname(filename)
      if not os.path.exists(dirpath):
         os.makedirs(dirpath)

      tmpl = {
         'basename'  : os.path.basename(filename),
         'filename'  : filename,
         'key'       : os.path.join(
            meta.timestamp.replace(":", "/").replace("-", "/"),
            meta.shortname
         ) + ".jpg",
      }
      tmpl.update(meta.to_dict())
      egress_url = self.opts.egress_url % tmpl
      meta.url = egress_url

      if self.opts.filename == None:
          # No filename given to use as the screenshot so we capture one ourselves
          result = self.capture.capture(filename)
          if result != True:
             self.log.error("Capturing screenshot failed, result %s", result)
             return

      else:
          # filename given, dont capture anything
          self.log.debug("using provided file %s as screenshot", self.opts.filename)

          # support downloading http urls
          if self.opts.filename.startswith('http'):
              self.download_url(self.opts.filename, filename)
          else:
              filename = self.opts.filename

      self.log.info("Uploading %s to %d places", filename, len(self.uploaders))
      for uploader_name, uploader in self.uploaders.iteritems():
         ucfg = self.opts.uploaders[uploader_name]
         if 'active' in ucfg and ucfg['active'] == False:
            self.log.debug("Skipping %s due to active=False", uploader_name)
            continue

         self.log.debug("%s Uploading %s", uploader.__class__.__name__, filename)
         result = uploader.upload(meta, filename, meta.shortname)
         if result != True:
            self.log.warn("Uploading to %s failed: result %s", uploader.__class__.__name__, result)
            continue

         # Decide if we should clipboard the url or not
         if self.opts.clipboard_method == uploader_name:
            if uploader.url:
               self.log.debug("added uploader url to the clipboard url list")
               self.clipboard.add_url(uploader.url)
            else:
               self.log.warn(
                  "clipboard method set to %s but no url returned",
                  self.opts.clipboard_method
               )

      clipboard_url = self.clipboard.get_url()
      self.log.info("clipboard url %s", clipboard_url)

      short_url = self.tiny.make_url(clipboard_url)
      if short_url:
         self.clipboard.add_url(short_url)

      self.log.debug("use clipboard %s: clipboard method %s", self.opts.use_clipboard, self.opts.clipboard_method)

      if self.opts.use_clipboard == False:
         clipboard_url = None
      elif self.opts.clipboard_method == 'tinurl':
         self.clipboard.copy(short_url)
      elif self.opts.clipboard_method == 'template':
         self.clipboard.copy(egress_url)
         clipboard_url = egress_url
      elif clipboard_url:
         self.clipboard.copy(clipboard_url)
      elif self.opts.clipboard_method == 'last':
         clipboard_url = self.clipboard.get_url()
         self.clipboard.copy(clipboard_url)
      else:
         self.log.error("Invalid clipboard method %s", self.opts.clipboard_method)
         clipboard_url = self.clipboard.get_url()

      if clipboard_url and self.opts.warm_cache == True:
         self.warm_cache_url(clipboard_url)

      # trash original
      os.unlink(filename)

   def warm_cache_url(self, url):
      """Warm up a configured cache by fetching the url"""
      f = None
      self.log.info("warm cache url %s", url)
      try:
         f = urllib.urlopen(url)
      except Exception, e: # pylint: disable=broad-except
         self.log.error("%s", e)
         return

      content = f.read()
      self.log.info("read %d bytes from %s", len(content), url)
      return

