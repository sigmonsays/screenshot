"""
image uploader using Limelight Orchestrate Storage (http://www.limelight.com/services/storage.html)
"""
import os
import time
import logging
import hmac
import hashlib
import base64
import requests

from screenshot.upload import UploadPlugin

AgilePrefix = 'x-agile-'

class HmacAuth:
    def __init__(self, access_key, secret_key, expiry=3600):
        self.__dict__.update(locals())
        self.log = logging.getLogger(self.__class__.__name__)

    def signature(self, request_headers):
        ts = int(time.time())
        params = {
                'access_key': self.access_key,
                'expiry': ts + self.expiry,
        }
        param_list = ['access_key', 'expiry']

        for header, value in request_headers.iteritems():
            h = header.lower()
            if h.startswith(AgilePrefix) == False or h == 'x-agile-signature':
                continue
            k = h[len(AgilePrefix):]
            params[k]=value
            param_list.append(k)
        param_list.sort()

        req = '/post/raw?'
        for n, param_name in enumerate(param_list):
            if n > 0:
                req += "&"
            value = params[param_name]
            req += "%s=%s" % (param_name, value)

        self.log.debug("hmac auth request %s", req)

        hm = hmac.new(self.secret_key, req, hashlib.sha256)
        cs = hm.digest()

        sig = base64.encodestring(cs).strip()
        req += '&signature=' + sig

        return req


class LOCS(UploadPlugin):


   def upload(self, meta, localfile, shortname, md):
      self.log.debug("metadata %s", md)
      server = self.config.get('server', 'global.llp.lldns.net')
      url = 'http://%s/post/raw' % (server)

      self.log.debug("post url %s", url) 

      access_key = self.config.get('access_key')
      secret_key = self.config.get('secret_key')

      if access_key == None:
           self.log.error("missing access key")
           return None
      if secret_key == None:
           self.log.error("missing secret key")
           return None

      # begin uploading..
      self.log.info("localfile:%s shortname:%s", localfile, shortname)
      basename = "%s-%s.jpg" % (md.shortname, md.timestamp)

      st = os.stat(localfile)

      auth = HmacAuth(access_key, secret_key)
      request_headers = {
              'Content-Length': str(st.st_size),
              'X-Agile-Recursive': 'true',
              'X-Agile-Directory': '/screenshot',
              'X-Agile-Basename': basename,
      }
      #              'X-Agile-Recursive': 'true',
      request_headers['X-Agile-Signature']=auth.signature(request_headers)
      self.log.debug("request headers %s", request_headers)

      fh = file(localfile)

      r = requests.post(url, fh, headers=request_headers)
      self.log.debug("response headers %s", r.headers)
      self.log.debug("response body %s", r.text)

      http_status = r.status_code
      if http_status != 200:
          self.log.warn("bad http response code: %s", http_status)
          return False

      return True
