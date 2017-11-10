"""imgur screenshot saver"""
try:
   from pyimgur import Imgur
except:
   Imgur = None

from screenshot.upload import UploadPlugin

class Imgur(UploadPlugin):

   upload_method = 'imgur'

   def upload(self, meta, filename, shortname, md):
      imgur = Imgur(
         self.config['client_id'],
         self.config['client_secret']
      )
      result = imgur.upload_image(filename, title=shortname)
      self.set_url('http://imgur.com/v/'+result.id)
      return True
