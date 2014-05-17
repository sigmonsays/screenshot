#!/usr/bin/env python
import logging
from optparse import OptionParser

from screenshot import Screenshot
from screenshot import config

def configure_logging(level):
   level = level.upper()
   rootlog = logging.getLogger()
   stderr_handler = logging.StreamHandler()
   logformat = "[%(process)d] %(levelname)s %(name)s.%(funcName)s.%(lineno)d %(message)s"
   formatter = logging.Formatter(logformat)
   stderr_handler.setFormatter(formatter)
   rootlog.addHandler(stderr_handler)
   rootlog.setLevel(getattr(logging, level))

class Application:

    def __init__(self):
       self.log = logging.getLogger(self.__class__.__name__)

    def main(self):

       parser = OptionParser()
       parser.add_option("-c", "--config", dest="config", help="config file", metavar="FILE", default=None)
       parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False)
       parser.add_option("-l", "--log-level", dest="log_level", default='info', help="set logging level [%default]")
       parser.add_option("-s", "--summary", dest="summary", default=None, help="optional summary of picture")
       parser.add_option("-u", "--uploaders", dest="uploaders", default=[], action="append", help="enable specific uploaders")
       parser = parser

       (options, args) = parser.parse_args()

       configure_logging(options.log_level)

       # Mute boto unless we're verbose
       if options.verbose == False:
            logging.getLogger('boto').setLevel(logging.CRITICAL)
            logging.getLogger('requests').setLevel(logging.CRITICAL)


       opts = config.GetScreenshotOptions(options.config)
       for k, v in opts.__dict__.iteritems():
            self.log.debug("%s: %s", k, v)
       app = Screenshot(opts)

       app.configure()

       shortname = None
       if len(args) > 0:
        shortname = args[0]
       summary = options.summary
       opts.summary = options.summary
       opts.uploaders = options.uploaders


       app.take_screenshot(shortname, summary)

def main():
    Application().main()

if __name__ == '__main__':
    main()
