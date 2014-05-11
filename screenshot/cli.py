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

def main():

   parser = OptionParser()
   parser.add_option("-c", "--config", dest="config", help="config file", metavar="FILE", default=None)
   parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False)
   parser.add_option("-l", "--log-level", dest="log_level", default='info', help="set logging level [%default]")
   parser = parser

   (options, args) = parser.parse_args()

   configure_logging(options.log_level)

   # Mute boto unless we're verbose
   if options.verbose == False:
        logging.getLogger('boto').setLevel(logging.CRITICAL)
        logging.getLogger('requests').setLevel(logging.CRITICAL)


   opts = config.GetScreenshotOptions(options.config)

   app = Screenshot(opts)

   app.configure()



   shortname = None
   if len(args) > 0:
    shortname = args[0]

   app.take_screenshot(shortname)

if __name__ == '__main__':
   main()