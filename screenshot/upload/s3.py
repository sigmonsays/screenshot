"""upload screenshots to s3"""
import os
import time
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from screenshot.upload import UploadPlugin

class S3(UploadPlugin):
   def upload(self, meta, localfile, shortname):
      conn = S3Connection(
         aws_access_key_id=self.config['key'],
         aws_secret_access_key=self.config['secret'],
         host=self.config['end_point']
      )
      bucket = conn.get_bucket(self.config['bucket'])

      timestamp = time.strftime("%F-%T", meta.now).replace(":", "-")

      s3_key = os.path.join(timestamp.replace(":", "/").replace("-", "/"), shortname) + ".jpg"
      s3_url = "http://%s.%s/%s" % (
         self.config['bucket'],
         self.config['end_point'],
         s3_key
      )
      self.log.info("s3 url %s", s3_url)
      self.set_url(s3_url)
      k = Key(bucket)
      k.key = s3_key
      k.set_contents_from_filename(localfile, policy='public-read')
      return True

