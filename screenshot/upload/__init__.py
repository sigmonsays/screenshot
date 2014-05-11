import logging

class Upload:
   upload_method = None

   def __init__(self, clipboard, url = None):
      self.log = logging.getLogger(self.__class__.__name__)
      self.__dict__.update(locals())

   def upload(self, localfile, shortname):
      self.log.info("Upload %s shortname %s", localfile, shortname)
      raise Exception(NotImplemented)

   def set_url(self, url):
      self.log.debug("%s", url)
      self.url = url
      
class NullUpload(Upload):
   def __init__(self, clipboard, *args, **kwargs):
      Upload.__init__(self, clipboard)

   def upload(self, localfile, shortname):
      self.log.debug("%s shortname %s", localfile, shortname)
      return True
