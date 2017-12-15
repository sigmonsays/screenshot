"""imgur screenshot saver"""
try:
   from pyimgur import Imgur as PyImgur
except Exception, e:
   PyImgur = None
from screenshot.upload import UploadPlugin

class Imgur(UploadPlugin):
   upload_method = 'imgur'
   def upload(self, meta, filename, shortname, md):
      client_id = self.config['client_id']
      client_secret = self.config['client_secret']
      up = PyImgur(client_id, client_secret)
      result = up.upload_image(filename, title=shortname)
      self.set_url('http://imgur.com/v/'+result.id)
      return True
