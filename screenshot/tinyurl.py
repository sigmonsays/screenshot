import logging
import urllib
import urlparse
import httplib
import contextlib

def MakeTinyUrl(cfg):
  if cfg == None:
     return NoTinyUrl()
  if cfg['service'] == 'custom':
     tiny = CustomTinyUrl(cfg['service_url'])
  if cfg['service'] == 'tinyurl':
     tiny = TinyUrl()
  else:
     tiny = NoTinyUrl()
  return tiny

class UrlShortener:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def make_url(self, url):
        raise Exception(NotImplemented)


class NoTinyUrl(UrlShortener):
    def make_url(self, url):
        self.log.debug("url %s", url)
        return url

class TinyUrl(UrlShortener):
    def make_url(self, url):
        request_url = ('http://tinyurl.com/api-create.php?' + urllib.urlencode({'url':url}))
        resp = None
        with contextlib.closing(urllib.urlopen(request_url)) as response:
            resp = response.read().decode('utf-8')
        self.log.debug("return %s", resp)
        return resp

class CustomTinyUrl(UrlShortener):
   """
   Custom tiny url service that just accepts the url as json

   Example request:

       POST /server HTTP/1.1
       Content-Type: text/json


   Example response:

       HTTP 200 OK
       Content-Type: text/plain

       http://short.net/url

   """
   def __init__(self, short_service):
      UrlShortener.__init__(self)
      self.short_service = short_service
      self.log.info("TinyURL service is at %s" % (short_service))

   def make_url(self, url):
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

