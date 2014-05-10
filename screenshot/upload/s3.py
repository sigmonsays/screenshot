import os
import time
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from screenshot.upload import Upload

class S3Upload(Upload):
   upload_method = 's3'

   def __init__(self, clipboard, key, secret, end_point, bucket):
      Upload.__init__(self, clipboard)
      self.log.debug("end_point %s bucket %s", end_point, bucket)
      conn = S3Connection(aws_access_key_id=key, aws_secret_access_key=secret, host=end_point)
      bucket = conn.get_bucket(bucket)
      self.__dict__.update(locals())

   def upload(self, localfile, shortname):
      ts = time.strftime("%F-%T").replace(":", "-")

      s3_key = os.path.join(ts.replace(":", "/").replace("-", "/"), shortname) + ".jpg"
      s3_url = "http://%s.%s/%s" % (self.bucket, self.end_point, s3_key )
      self.log.info("s3 url %s" %(s3_url))
      self.set_url(s3_url)
      k = Key(self.bucket)
      k.key = s3_key
      k.set_contents_from_filename(localfile, policy = 'public-read')
      return True

