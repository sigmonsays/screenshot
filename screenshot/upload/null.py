"""Null image uploader.  makes it just log"""
from screenshot.upload import UploadPlugin

class Null(UploadPlugin):
   def upload(self, meta, localfile, shortname):
      self.log.info("%s shortname %s", localfile, shortname)
      return True
