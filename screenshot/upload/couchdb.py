import os
import time
import urlparse
import json
import httplib

from screenshot.upload import Upload

class CouchdbUpload(Upload):

   upload_method = 'couchdb'

   def __init__(self, couchdb_uri):
      Upload.__init__(self)
      self.__dict__.update(locals())

   def upload(self, meta, filename, shortname):
      # TODO: Generate timestamp from meta.now
      ts = time.strftime("%F-%T").replace(":", "-")
      ret = self.save_couchdb(ts, filename, shortname)
      if ret == None:
        return False
      return True

   def save_couchdb(self, ts, filename, shortname, s3_url = None, s3_key = None):
      scheme, netloc, path, query, fragment = urlparse.urlsplit(self.couchdb_uri)
      couch_key = os.path.join(ts.replace(":", "-").replace("-", "-"), shortname) + ".jpg"
      self.log.info("Saving record in couchdb at %s" % (couch_key))

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
      ss = httplib.HTTPConnection(netloc)
      ss.request("PUT", os.path.join(path, couch_key), json.dumps(rec), headers)
      res = None
      ret = None
      try:
         res = ss.getresponse()
      except httplib.BadStatusLine, e:
         self.log.error("ERROR: httplib.BadStatusLine: %s" %(e))
      except Exception, e:
         self.log.error("ERROR: http exception: %s" %(e))

      if res:
         try:
            ret = json.loads(res.read())
         except Exception, e:
            self.log.warn("json loads: %s", e)
            ret = None

      if ret:
         self.log.info("Couchdb server said %s, %s, %s" % (res.status, res.reason, ret))

         # Upload the image as an attachment 
         aurl = os.path.join(path, ret['id'], "image")
         aurl_params = "?rev=" + ret['rev']
         ss.request("PUT", aurl + aurl_params, file(filename).read(), { "Content-Type" : "image/jpg" })
         res = ss.getresponse()
         self.log.info("Couchdb server said %s, %s %s" % (res.status, res.reason, res.read()))
         attach_url = scheme + "://" + netloc + os.path.join(path , ret['id'], "image")
         self.log.info("couchdb url %s" %(attach_url))
         self.add_url(attach_url)
      else:
         self.log.error("problem with couchdb")
         attach_url = None
      return attach_url

