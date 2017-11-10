"""
Dropbox image uploader. 

See https://pypi.python.org/pypi/dropbox
and https://www.dropbox.com/developers/apps

"""

from screenshot.upload import UploadPlugin
try:
   dropbox = __import__("dropbox")
except:
   dropbox = None

class Dropbox(UploadPlugin):

   def _create_client(self):
      if 'token' in self.config:
         self.log.debug("create client using token %s", self.config['token'])
         client = dropbox.client.DropboxClient(self.config['token'])
         return client

      session = dropbox.session.DropboxSession(self.config['key'], self.config['secret'])
      client = dropbox.client.DropboxClient(session)
      return client


   def upload(self, meta, localfile, shortname, md):
      self.log.info("%s shortname %s", localfile, shortname)
      self.log.debug("config %s", self.config)

      client = self._create_client()
      if client == None:
         return False

      dest = '/screenshot/'+shortname + '.png'
      f = file(localfile)

      response = client.put_file(dest, f, overwrite=True)
      bytes = response.get('bytes')

      self.log.info("response %s", response)

      return True
