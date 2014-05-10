import os
from pyimgur import Imgur

from screenshot.upload import Upload

class ImgurUpload(Upload):

    upload_method = 'imgur'

    def __init__(self, clipboard, client_id, client_secret):
        Upload.__init__(self, clipboard)
        im = Imgur(client_id, client_secret)
        self.im = im
        self.__dict__.update(locals())

    def upload(self, filename, shortname):
        basename = os.path.basename(filename)
        result = self.im.upload_image(filename, title=shortname)
        self.set_url('http://imgur.com/v/'+result.id)
        return True
        
