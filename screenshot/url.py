import logging
import urllib
import urlparse
import httplib

class TinyUrl(object):
   """
   Minimal class to abstract tiny url services
   """
   def __init__(self, short_service):
      self.log = logging.getLogger(self.__class__.__name__)
      self.short_service = short_service
      self.log.info("TinyURL service is at %s" % (short_service))

   def custom(self, url):
      """
      perform HTTP POST to a custom service
      """
      self.log.info("Creating short url for %s" % (url))
      scheme, netloc, path, query, fragment = urlparse.urlsplit(self.short_service)
      ss = httplib.HTTPConnection(netloc)
      params = urllib.urlencode({'data': url})
      headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
      ss.request("POST", path, params, headers)
      res = None
      try:
         res = ss.getresponse()
      except httplib.BadStatusLine, e:
         print "ERROR: httplib.BadStatusLine:", str(e)
      if res:
         short_url = res.read().strip()
      else:
         short_url = None
      return short_url

   def __call__(self, method_name, url):
      if not hasattr(self, method_name):
         return None

      callable = getattr(self, method_name)
      return callable(url)
