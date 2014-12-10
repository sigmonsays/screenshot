"""Store screenshots in couchdb

Handles storing screenshots in couchdb
"""
import os
import time
import urlparse
import json
import httplib

from screenshot.upload import UploadPlugin

class Couchdb(UploadPlugin):
   """Store screenshots in couchdb"""
   upload_method = 'couchdb'

   def upload(self, meta, filename, shortname):
      timestamp = time.strftime("%F-%T", meta.now).replace(":", "-")
      ret = self.save_couchdb(timestamp, filename, shortname)
      if ret == None:
         return False
      return True

   def save_couchdb(self, timestamp, filename, shortname, s3_url=None, s3_key=None):
      """Handle the actual save to a couchdb record"""
      scheme, netloc, path, _, _ = urlparse.urlsplit(self.config['uri'])
      couch_key = os.path.join(timestamp.replace(":", "-").replace("-", "-"), shortname) + ".jpg"
      self.log.info("Saving record in couchdb at %s", couch_key)

      # save meta data
      rec = {
         "year" : int(time.strftime("%Y")),
         "month" : int(time.strftime("%m")),
         "day" : int(time.strftime("%d")),
         "doctype" : "metadata",
         "s3_url" : s3_url,
         "s3_key" : s3_key,
      }
      headers = {
         "Content-Type" : "application/json",
      }
      http = httplib.HTTPConnection(netloc)
      http.request("PUT", os.path.join(path, couch_key), json.dumps(rec), headers)
      res = None
      ret = None
      try:
         res = http.getresponse()
      except httplib.BadStatusLine, e:
         self.log.error("ERROR: httplib.BadStatusLine: %s", e)
      except Exception, e: # pylint: disable=broad-except
         self.log.error("ERROR: http exception: %s", e)

      if res:
         try:
            ret = json.loads(res.read())
         except Exception, e: # pylint: disable=broad-except
            self.log.warn("json loads: %s", e)
            ret = None

      if ret:
         self.log.info("Couchdb server said %s, %s, %s", res.status, res.reason, ret)

         # Upload the image as an attachment
         aurl = os.path.join(path, ret['id'], "image")
         aurl_params = "?rev=" + ret['rev']
         http.request(
            "PUT",
            aurl + aurl_params,
            file(filename).read(),
            {"Content-Type": "image/jpg"}
         )
         res = http.getresponse()
         self.log.info("Couchdb server said %s, %s %s", res.status, res.reason, res.read())
         attach_url = scheme + "://" + netloc + os.path.join(path, ret['id'], "image")
         self.log.info("couchdb url %s", attach_url)
         self.set_url(attach_url)
      else:
         self.log.error("problem with couchdb")
         attach_url = None
      return attach_url

