import os
import logging
from StringIO import StringIO
from ConfigParser import SafeConfigParser
from screenshot.config._default import DEFAULT_CONFIG

def boolval(b):
    """
    return a boolean from the given string
    return True for a value of '1', 'true' (any case), 'yes' (any acse)
    return False for a value of '0', 'false' (any case), 'no' (any case)
    """
    b = str(b).lower()
    if b in [ 'true', '1', 'yes']:
        return True
    elif b in [ 'false', '0', 'no']:
        return False
    return False

def GetScreenshotOptions(configfile):
   log = logging.getLogger('')
   opts = ScreenshotOptions()

   # Load config
   config = SafeConfigParser()
   config.add_section('screenshot')
   config.set('screenshot', 'HOME', os.environ['HOME'])

   # Load default config
   config.readfp(StringIO(DEFAULT_CONFIG))

   # if command line given
   cfiles = []
   if configfile:
      cfiles = config.read( [ configfile ] )
      log.info("Loaded configuration %s" % (", ".join(cfiles)))

   if len(cfiles) == 0:
      # load user config from $HOME/.screenshot/screenshot.ini
      conffile = os.path.join(os.environ['HOME'], ".screenshot/screenshot.ini")
      if os.path.exists(conffile):
         cfiles = config.read([conffile])
         log.info("Loaded configuration %s" % (", ".join(cfiles)))
      else:
         log.warn("No configuration loaded, using defaults")

   opts.load_options(config)

   return opts

class ScreenshotOptions(object):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        screenshot_dir = '/tmp/screenshots'
        screenshot_index = 'tmp/screenshots.index'
        disk_config = None
        s3_config = None
        imgur_config = None
        couchdb_config = None
        tinyurl_config = None
        use_clipboard = False
        clipboard_method = 'last'
        random_filename=True
        capture_method=None
        filename_template = None
        warm_cache = True
        egress_url = None
        self.uploaders = {}
        self.__dict__.update(locals())

    def get_uploader_options(self, uploader):
        ucfg = None
        if self.optparse.has_section(uploader) and boolval(self.optparse.get(uploader, 'enabled')):
           ucfg = dict(self.optparse.items(uploader))
           self.log.debug("found options for %s uploader: %s", uploader, ucfg)
           self.uploaders[uploader] = ucfg
        return ucfg

    def load_options(self, config):
        self.cfg = dict(config.items('screenshot'))
        self.optparse = config
        for option in ('random_filename', 'use_clipboard', 'warm_cache'):
            self.cfg[option] = boolval(self.cfg[option])
        for option in ('page_size',):
            self.cfg[option] = int(self.cfg[option])
        self.__dict__.update(self.cfg)
