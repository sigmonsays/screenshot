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
        couchdb_config = None
        if config.has_section('couchdb') and boolval(config.get('couchdb', 'enabled')):
           cfg = dict(config.items('couchdb'))
           couchdb_config = {}
           couchdb_config['enabled'] = True
           couchdb_config['uri'] = cfg.get('uri')
           self.log.info("couchdb is enabled")
        else:
           self.log.info("couchdb is disabled")

        disk_config = None
        if config.has_section('disk') and boolval(config.get('disk', 'enabled')):
           cfg = dict(config.items('disk'))
           disk_config = {}
           disk_config['enabled'] = True
           disk_config['save_dir'] = cfg.get('save_dir')
           self.log.info("disk is enabled")
        else:
           self.log.info("disk is disabled")

        s3_config = None
        if config.has_section('s3') and boolval(config.get('s3', 'enabled')):
           cfg = dict(config.items('s3'))
           s3_config = {}
           s3_config['enabled'] = True
           s3_config['key'] = cfg.get('key')
           s3_config['secret'] = cfg.get('secret')
           s3_config['bucket'] = cfg.get('bucket')
           s3_config['end_point'] = cfg.get('end_point')
           self.log.info("s3 is enabled")
        else:
           self.log.info("s3 is disabled")


        imgur_config = None
        if config.has_section('imgur') and boolval(config.get('imgur', 'enabled')):
           cfg = dict(config.items('imgur'))
           imgur_config = {}
           imgur_config['enabled'] = True
           imgur_config['client_id'] = cfg.get('client_id')
           imgur_config['client_secret'] = cfg.get('client_secret')
           imgur_config['title'] = cfg.get('title')
           self.log.info("imgur is enabled")
        else:
           self.log.info("imgur is disabled")

        tinyurl_config = None
        if config.has_section('tinyurl') and boolval(config.get('tinyurl', 'enabled')):
           cfg = dict(config.items('tinyurl'))
           tinyurl_config = {}
           tinyurl_config['enabled'] = True
           tinyurl_config['service'] = cfg.get('service')
           tinyurl_config['service_url'] = cfg.get('service_url')
           self.log.info("tinyurl is enabled")
        else:
           self.log.info("tinyurl is disabled")



        self.couchdb_config = couchdb_config
        self.disk_config = disk_config
        self.imgur_config = imgur_config
        self.s3_config = s3_config
        self.tinyurl_config = tinyurl_config
        self.tumblr_config = self.get_uploader_options(config, 'tumblr',    blog_url=str, consumer_key=str, consumer_secret=str, oauth_token=str, oauth_secret=str)

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

