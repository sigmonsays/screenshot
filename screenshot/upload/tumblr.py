
import pytumblr

from screenshot.upload import Upload

class TumblrUpload(Upload):

    verbose = True
    upload_method = 'tumblr'

    def __init__(self, clipboard, blog_url, consumer_key, consumer_secret, oauth_token, oauth_secret):
        Upload.__init__(self, clipboard)
        cl = pytumblr.TumblrRestClient(
            consumer_key,
            consumer_secret,
            oauth_token,
            oauth_secret,
        )
        self.__dict__.update(locals())

    def upload(self, meta, filename, shortname):
        tags = ["screenshot"]

        if self.verbose:
            inf = self.cl.info()
            self.log.debug("info %s", inf)

        img_url = meta.get_url()
        if meta.summary == None:
            description = shortname
        else:
            description = meta.summary

        x = self.cl.create_photo(self.blog_url,
            state="published", 
            tags=tags, 
            slug=description, 
            caption=description, 
            link=img_url, 
            data=[filename],
        )

        self.log.info("source=%s create_photo returned %s", img_url, x)

        return True
        
