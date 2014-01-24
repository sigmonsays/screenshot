import os
import logging
from StringIO import StringIO
from ConfigParser import SafeConfigParser

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


DEFAULT_CONFIG = """
[screenshot]
# Override what FQDN is use (for a reverse proxy if setup)
egress_fqdn = localhost
index_file = %(HOME)s/.screenshots.index
directory = /tmp/screenshots
# How many images per page for HTML generation
page_size = 10

# use xclip to capture the URL
use_clipboard = yes

# screenshot method (autodetected by default) but you can override if you wish
# method can be 
# - imagemagick - use "import" command
# - gnome - use gnome-screenshot -a -f FILE
# - auto - detect automatically based on platform
# - screencapture - for MacOSX
# capture_method = gnome

capture_method = auto

random_filename = no

# use randomized filename
random_filename = no

# download the remote file url (clipboard url) to warm any cache
warm_cache = yes

[couchdb]
enabled = no
#uri = "http://username.couchone.com/screenshot"

[disk]
enabled = yes
save_dir = ~/Pictures/screenshot

[s3]
enabled = no
#key = XXX
#secret = XXX
#bucket = XXX
end_point = s3.amazonaws.com

[imgur]
enabled = no
client_id = 2ff238bd2a1883c
client_secret = 
title = Screenshot

[tinyurl]
enabled = no
#service = custom
#service_url = http://example.org/r

"""

def GetScreenshotOptions(configfile):
   log = logging.getLogger()
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

   couchdb_config = None
   if config.has_section('couchdb') and boolval(config.get('couchdb', 'enabled')):
      couchdb_config = {}
      couchdb_config['uri'] = config.get('couchdb', 'uri')
      log.info("couchdb is disabled")
   else:
      log.info("couchdb is disabled")

   disk_config = None
   if config.has_section('disk') and boolval(config.get('disk', 'enabled')):
      disk_config = {}
      disk_config['save_dir'] = config.get('disk', 'save_dir')
      log.info("disk is enabled")
   else:
      log.info("disk is disabled")

   s3_config = None
   if config.has_section('s3') and boolval(config.get('s3', 'enabled')):
      s3_config = {}
      s3_config['key'] = config.get('s3', 'key')
      s3_config['secret'] = config.get('s3', 'secret')
      s3_config['bucket'] = config.get('s3', 'bucket')
      s3_config['end_point'] = config.get('s3', 'end_point')
      log.info("s3 is enabled")
   else:
      log.info("s3 is disabled")


   imgur_config = None
   if config.has_section('imgur') and boolval(config.get('imgur', 'enabled')):
      imgur_config = {}
      imgur_config['client_id'] = config.get('imgur', 'client_id')
      imgur_config['client_secret'] = config.get('imgur', 'client_secret')
      imgur_config['title'] = config.get('imgur', 'title')
      log.info("imgur is enabled")
   else:
      log.info("imgur is disabled")

   tinyurl_config = None
   if config.has_section('tinyurl') and boolval(config.get('tinyurl', 'enabled')):
      tinyurl_config = {}
      tinyurl_config['service'] = config.get('tinyurl', 'service')
      if tinyurl_config['service'] == 'custom':
         tinyurl_config['service_url'] = config.get('tinyurl', 'service_url')
         log.info("tinyurl is enabled")
      else:
         log.warn("tinyurl is disabled, unknown service")
   else:
      log.info("tinyurl is disabled")

   opts.couchdb_config = couchdb_config
   opts.disk_config = disk_config
   opts.imgur_config = imgur_config
   opts.s3_config = s3_config
   opts.tinyurl_config = tinyurl_config

   opts.capture_method = config.get('screenshot', 'capture_method').lower()
   opts.egress_fqdn = config.get('screenshot', 'egress_fqdn')
   opts.page_size = config.getint('screenshot', 'page_size')
   opts.random_filename = boolval(config.get('screenshot', 'random_filename'))
   opts.screenshot_dir = config.get('screenshot', 'directory')
   opts.screenshot_index = config.get('screenshot', 'index_file')
   opts.use_clipboard = boolval(config.get('screenshot', 'use_clipboard'))
   opts.warm_cache = boolval(config.get('screenshot', 'warm_cache'))
   return opts

class ScreenshotOptions(object):

   def __init__(self, 
      screenshot_dir = '/tmp/screenshots', 
      screenshot_index = 'tmp/screenshots.index',
      disk_config = None,
      s3_config = None,
      imgur_config = None,
      couchdb_config = None,
      tinyurl_config = None,
      use_clipboard = False,
      random_filename=True,
      capture_method=None,
      warm_cache = True,
      egress_fqdn = None,
   ):
      self.__dict__.update(locals())
