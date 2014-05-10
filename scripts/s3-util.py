#!/usr/bin/env python
import sys
import logging
from optparse import OptionParser
from screenshot.s3util import S3Util
from screenshot import config
from screenshot import cli

def main():

   parser = OptionParser()
   parser.add_option("-c", "--config", dest="config", help="config file", metavar="FILE", default=None)
   parser.add_option("", "--update-calendar", dest="update_calendar", action="store_true", default=False)
   (options, args) = parser.parse_args()

   opts = config.GetScreenshotOptions(options.config)

   cli.configure_logging('error')

   c = opts.s3_config
   app = S3Util(opts.screenshot_dir, c['key'], c['secret'], c['end_point'], c['bucket'], opts.egress_fqdn)

   if options.update_calendar:
      print "Updating image calendar.."
      app.update_full_calendar()
      sys.exit(0)

if __name__ == "__main__":
    main()
