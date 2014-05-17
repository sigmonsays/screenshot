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
   # If command line given
   if configfile:
      cfiles = config.read( [ configfile ] )
   # load user config from $HOME/.screenshot/screenshot.conf
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
        warm_cache = True
        egress_url = None
        self.__dict__.update(locals())


    def get_uploader_options(self, config, section, **params):
        uploader_config = None
        if config.has_section(section) and boolval(config.get(section, 'enabled')):
           cfg = dict(config.items(section))
           uploader_config = {}
           uploader_config['enabled'] = True
           for k, v in params.iteritems():
                uploader_config[k] = cfg.get(k)
           self.log.info("%s is enabled", section)
        else:
           self.log.info("%s is disabled", section)
        return uploader_config

    def load_options(self, config):

        self.couchdb_config = self.get_uploader_options(config, 'couchdb',  uri=str)
        self.disk_config    = self.get_uploader_options(config, 'disk',     save_dir=str)
        self.imgur_config   = self.get_uploader_options(config  'imgur'     client_id=str, client_secret=str, title=str)
        self.s3_config      = self.get_uploader_options(config  's3',       key=str, secret=str, bucket=str, end_point, str)
        self.tinyurl_config = self.get_uploader_options(config, 'tinyurl',  service=str, service_url=str)
        self.tumblr_config  = self.get_uploader_options(config, 'tumblr',   blog_url=str, consumer_key=str, consumer_secret=str, oauth_token=str, oauth_secret=str)

        cfg = dict(config.items('screenshot'))
        self.capture_method = cfg.get('capture_method').lower()
        self.egress_url = cfg.get('egress_url')
        self.page_size = int(cfg.get('page_size'))
        self.random_filename = boolval(cfg.get('random_filename'))
        self.screenshot_dir = cfg.get('directory')
        self.screenshot_index = cfg.get('index_file')
        self.use_clipboard = boolval(cfg.get('use_clipboard'))
        self.clipboard_method = cfg.get('clipboard_method')
        self.warm_cache = boolval(cfg.get('warm_cache'))

