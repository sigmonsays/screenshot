"""Tumbler uploader"""
try:
   import pytumblr
except:
   pytumblr = None

from screenshot.upload import UploadPlugin

class Tumblr(UploadPlugin):

   verbose = False
   upload_method = 'tumblr'

   def upload(self, meta, filename, shortname):
      tumblr = pytumblr.TumblrRestClient(
         self.config['consumer_key'],
         self.config['consumer_secret'],
         self.config['oauth_token'],
         self.config['oauth_secret'],
      )
      tags = ["screenshot"]

      if self.verbose:
         inf = tumblr.info()
         self.log.debug("info %s", inf)

      img_url = meta.get_url()
      if meta.summary == None:
         description = shortname
      else:
         description = meta.summary

      result = tumblr.create_photo(
         self.config['blog_url'],
         state="published",
         tags=tags,
         slug=description,
         caption=description,
         link=img_url,
         data=[filename],
      )

      self.log.info("filename %s create_photo %s", filename, result)

      return True
