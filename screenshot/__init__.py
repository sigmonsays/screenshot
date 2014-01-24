import calendar
import httplib
import json
import logging
import os
import platform
import random
import shutil
import string
import sys
import time
import traceback
import urllib
import urlparse

from boto.s3.connection import S3Connection
from boto.s3.key import Key
try:
    from pyimgur import Imgur
except ImportError:
    Imgur = None

from screenshot.url import TinyUrl

class Screenshot(object):
   def __init__(self, opts):
      self.log = logging.getLogger(self.__class__.__name__)
      self.screenshot_dir = opts.screenshot_dir
      self.screenshot_index = opts.screenshot_index
      self.conn = None
      self.bucket = None
      self.disk_config = opts.disk_config
      self.s3_config = opts.s3_config
      self.imgur_config = opts.imgur_config
      self.couchdb_config = opts.couchdb_config
      self.use_clipboard = opts.use_clipboard
      self.random_filename = opts.random_filename
      self.capture_method = opts.capture_method
      self.warm_cache = opts.warm_cache
      self.egress_fqdn = opts.egress_fqdn
      self.tinyurl_config = opts.tinyurl_config

      if self.tinyurl_config == None:
         self.tiny_class = None
      elif self.tinyurl_config['service'] == 'custom':
         self.tiny_class = TinyUrl
      else:
         self.log.warn("Disabling tinyurl, unknown service %s" % (self.tinyurl_config['service']))
         self.tinyurl_config = None

      self.platform = platform.system()

   def configure_disk(self):
      if not self.disk_config:
         return
      c = self.disk_config
      self.save_dir = os.path.expanduser(c['save_dir'])

   def configure_s3(self):
      if not self.s3_config:
         return
      c = self.s3_config
      self.conn = S3Connection(c['key'], c['secret'], host=c['end_point'])
      self.bucket = self.conn.get_bucket(c['bucket'])

   def configure_couchdb(self):
      if not self.couchdb_config:
         return
      self.couchdb_uri = self.couchdb_config['uri']

   def tiny_url(self, url):
      service = self.tinyurl_config['service']
      service_url = self.tinyurl_config['service_url']
      tinysvc = self.tiny_class(service_url)
      short_url = tinysvc(service, url)
      return short_url

   def detect_capture_methods(self):
      if self.platform == 'Linux':
         return ['imagemagick', 'gnome']
      elif self.platform == 'Darwin':
         return ['screencapture']
      self.log.warn("Unsupported platform %s", self.platform)
      return []

   def take_screenshot(self):
      ts = time.strftime("%F-%T").replace(":", "-")
      if len(sys.argv) > 1:
         shortname = sys.argv[1]
      else:
         shortname = "screenshot"

      if self.random_filename:
         ts  = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(18)])

      basename = "%s-%s.jpg" % ( shortname, ts )
      filename = os.path.join(self.screenshot_dir, basename)

      dir = os.path.dirname(filename)
      if not os.path.exists(dir): os.makedirs(dir)

      if self.capture_method == None or self.capture_method == 'auto':
         methods = self.detect_capture_methods()
         method = methods[0]
      else:
         method = self.capture_method

      self.log.info("capture screenshot method %s", method)
      if method == 'imagemagick':
         os.system("import %s" % (filename))
      elif method == 'gnome':
         os.system("gnome-screenshot -a -f %s" % (filename))
      elif method == 'screencapture':
         os.system("screencapture -s %s" % (filename))
      else:
         raise Exception("Unsupported capture method platform %s, method %s" % (self.platform, method))
      
      URLS = []

      if self.disk_config:
         for n in xrange(1000):
             saved_name = os.path.join(self.save_dir, basename)
             if os.path.exists(saved_name) == False:
                break

         self.log.info("Saving to disk at %s", saved_name)
         if not os.path.exists(dir): os.makedirs(os.path.dirname(saved_name))
         shutil.copyfile(filename, saved_name)

      if self.s3_config:
         s3_key = os.path.join(ts.replace(":", "/").replace("-", "/"), shortname) + ".jpg"
         s3_url = "http://%s.%s/%s" % (self.s3_config['bucket'], self.s3_config['end_point'], s3_key )
         self.log.info("s3 url %s" %(s3_url))
         egress_url = s3_url
         egress_url = "http://%s/%s" %(self.egress_fqdn, s3_key)
         self.clipboard_copy(egress_url)
         k = Key(self.bucket)
         k.key = s3_key
         k.set_contents_from_filename(filename, policy = 'public-read')
         URLS.append(egress_url)
      else:
         s3_key = None
         s3_url = None

      if self.imgur_config:
         im = Imgur(self.imgur_config['client_id'], self.imgur_config['client_secret'])
         uploaded_image = im.upload_image(filename, title=self.imgur_config['title'])
         self.clipboard_copy(uploaded_image.link)
         URLS.append(uploaded_image.link)

      # add metadata record and image to couchdb if configured
      if self.couchdb_config:
         url = self.save_couchdb(ts, filename, shortname, s3_url, s3_key)
         if url:
            self.clipboard_copy(url)
            URLS.append(url)

      # get clipboard URL
      clipboard_url = None
      if len(URLS) > 0:
         clipboard_url = URLS[0]
         self.log.info("Clipboard URL %s" %(clipboard_url))

      # Perform any tiny url translations, just the first url
      short_url = None
      if self.tinyurl_config:
         short_url = self.tiny_url(clipboard_url)
         if short_url:
            self.log.info("Clipboard URL shortened to %s" % (short_url))
            clipboard_url = short_url

      self.clipboard_copy(clipboard_url)

      if self.warm_cache == True:
            self.warm_cache_url(clipboard_url)
      
      # trash original
      os.unlink(filename)

      # write index file
      # XXX: I forget what this was actually used for...
      if self.use_local_index:
         index = "%s %s %s\n" % ( s3_key, filename, egress_url )
         fh = open(self.screenshot_index, "a+")
         fh.write(index)
         fh.close()

         # How many lines are in the index?
         count = 0
         for line in file(self.screenshot_index):
            count = count + 1

         if count > self.page_size:
            items = []
            for line in file(self.screenshot_index):
               s3_key, filename, uri = line.split()
               item = {}
               item['key'] = s3_key
               item['filename'] = filename
               item['uri'] = uri
               items.append(item)

            # Save it in S3 and update latest.json
            latest_obj = self.bucket.get_key('latest.json')
            if latest_obj == None:
               latest = {}
               latest['page_count'] = 1
            else:
               latest = json.loads(latest_obj.get_contents_as_string())
               latest['page_count'] = latest['page_count'] + 1

            self.log.info("Updating latest.json")
            k = Key(self.bucket)
            k.key = "latest.json"
            k.set_contents_from_string(json.dumps(latest), policy = 'public-read')

            s3_key = "screenshot-%d.json" % ( latest['page_count'] )
            self.log.info("Updating %s" % ( s3_key ))
            k = Key(self.bucket)
            k.key = s3_key
            k.set_contents_from_string(json.dumps(items), policy = 'public-read')

            # truncate the index file
            open(self.screenshot_index, "w+").close()

   def clipboard_copy(self, url):
      # Use xclip to copy that shit to the clipboard
      if not self.use_clipboard:
         self.log.info("clipboard disabled")
         return

      if url and self.platform == 'Linux':
         r = os.popen('xclip -i', 'w')
         r.write(url + "\n")
         r.flush()
         r.close()
         self.log.info("xclip url %s" %(url))

      elif url and self.platform == 'Darwin':
         r = os.popen('pbcopy', 'w')
         r.write(url + "\n")
         r.flush()
         r.close()
         self.log.info("pbcopy url %s" %(url))

      else:
         self.log.warn("clipboard not supported or no short url")

   def warm_cache_url(self, url):
      f = None
      self.log.info("warm cache url %s", url)
      try:
         f = urllib.urlopen(url)
      except Exception, e:
         self.log.error("%s", e)
         return

      content = f.read()
      return

   def sync_static(self):
      for dirpath, dirnames, filenames in os.walk("static/"):
         for filename in filenames:
            if filename.startswith('.'): continue
            path = os.path.join(dirpath, filename)
            s3_key = "static/" + filename
            self.log.info("SYNC %s" % (s3_key))
            k = Key(self.bucket)
            k.key = s3_key
            k.set_contents_from_filename(path, policy = 'public-read')

      # save the index file
      path = "static/index.html"
      s3_key = "screenshots.html"
      self.log.info("SYNC %s" %(s3_key))
      k = Key(self.bucket)
      k.key = s3_key
      k.set_contents_from_filename(path, policy = 'public-read')



   def rebuild_index(self):
      latest_obj = self.bucket.get_key('latest.json')
      if latest_obj:
         latest = json.loads(latest_obj.get_contents_as_string())
         self.bucket.delete_key('latest.json')

         for n in xrange(latest['page_count']):
            k = "screenshot-%d.json" % ( n )
            self.bucket.delete_key(k)
      else:
         latest = None

      

      # Iterate all s3 keys and build indexes for each
      latest = {}
      latest['page_count'] = 0

      queue = []
      for obj in self.bucket:

         if obj.name.endswith('.jpg'):
            item = {}
            item['uri'] = obj.name
            queue.append(item)

         if len(queue) > self.page_size:
            latest['page_count'] = latest['page_count'] + 1
            s3_key = "screenshot-%d.json" % ( latest['page_count'] )
            self.log.info("Updating %s" % ( s3_key ))
            k = Key(self.bucket)
            k.key = s3_key
            k.set_contents_from_string(json.dumps(queue), policy = 'public-read')
            queue = []

      # Update latest
      self.log.info("Updating latest.json")
      k = Key(self.bucket)
      k.key = "latest.json"
      k.set_contents_from_string(json.dumps(latest), policy = 'public-read')

   def _iter_s3_images(self):
      queue = []
      for obj in self.bucket:
         if obj.name.endswith('.jpg'):
            yield obj

   def update_calendar(self):
      #organize by year, month tuple
      cal = {}
      IMAGES = {}
      prefix = time.strftime('%Y/%m')
      for obj in self.bucket.get_all_keys( prefix = prefix ):
         tmp = obj.name.split("/", 6)
         tmp.pop()
         tmp = map(int, tmp)
         y, m, d, h, i, s = tmp
         k = (y, m) 
         if not k in cal:
            cal[ k ] = []
         #print (y, m, d, h, i, s, obj.name)
         cal[k].append(obj.name)
         IMAGES[obj.name] = obj
         #break

      #pp.pprint(IMAGES)

   def update_full_calendar(self):
      #organize by year, month tuple
      cal = {}
      IMAGES = {}
      for obj in self._iter_s3_images():
         tmp = obj.name.split("/", 6)
         tmp.pop()
         tmp = map(int, tmp)
         y, m, d, h, i, s = tmp
         k = (y, m) 
         if not k in cal:
            cal[ k ] = []
         #print (y, m, d, h, i, s, obj.name)
         cal[k].append(obj.name)
         IMAGES[obj.name] = obj
         #break

      #pp.pprint(IMAGES)

      datadir = os.path.join(self.screenshot_dir, 'generated')
      self.log.info("Generating static content at %s" % (datadir))
      if not os.path.exists(datadir):
         os.makedirs(datadir)

      # write an index for each y, month
      out = open(os.path.join(datadir, 'calendar.html'), 'w+')
      out.write("<h1>Image Calendar</h1>\n")
      cur_year = None
      for y, m in sorted(cal):
         cnt = len(cal[y,m])
         title = time.strftime("%B %Y", time.localtime(time.mktime((y, m, 1, 0, 0, 0, 0, 0, 0))))
         if cur_year != y:
            out.write("<h2>%s</h2>" % (y))
            cur_year = y
         out.write("<li><a href='cal%04d%02d.html'>%s</a> - %d images</li>" % (y, m, title, cnt))
      out.close()

      # Go through each year, month and write each year and month in seperate files
      for ym, images in cal.iteritems():
         y, m = ym
         filename = os.path.join(datadir, 'cal%04d%02d.html' % (y, m))
         out = open(filename, 'w+')

         title = time.strftime("%B %Y", time.localtime(time.mktime((y, m, 1, 0, 0, 0, 0, 0, 0))))

         self.log.info("Write %s" %(filename))
         self.log.info("%d images" % (len(images)))
         out.write("<h1>%s</h1>" % (title))
         out.write("<a href='calendar.html'>Months</a><br>")
         out.write("<table width='100%' border=1>\n")

         # Organize images by day
         day_images = {}
         for obj_name in images:
            _, _, d, _ = obj_name.split("/", 3)
            d = int(d)
            if not d in day_images:
               day_images[d] = []
            day_images[d].append(obj_name)

         weeks = calendar.monthcalendar(y, m)
         for week in weeks:
            out.write("<tr>")
            for day in week:
               if day == 0:
                  out.write("<td>&nbsp</td>")
                  continue

               out.write("<td valign=top><b>%s</b> &nbsp; " % (day))
               cnt = len(day_images.get(day, []))
               if cnt > 0:
                  out.write("%d images" % (cnt))
               out.write("<br>")

               for img in day_images.get(day, []):
                  url = "http://%s/%s" % (self.egress_fqdn, img)
                  title, ext = os.path.splitext(os.path.basename(img))
                  out.write("<a href='%s'>%s</a><br>" % (url, title))

               out.write("</td>")

            out.write("</tr>\n")
         out.write("</table>\n")
         out.close()
      

      # pp.pprint(calendar)

      # Send all the generated content to S3
      extra_filenames = [ os.path.join(datadir, 'calendar.html') ]

      for y, m in sorted(cal):
         basename = 'cal%04d%02d.html' % (y, m)
         filename = os.path.join(datadir, basename)
         k = Key(self.bucket)
         k.key = basename
         self.log.info( "Loading %s at %s" %(filename,  k.key))
         k.set_contents_from_file(file(filename), policy = 'public-read')

      for filename in extra_filenames:
         k = Key(self.bucket)
         k.key = os.path.basename(filename)
         self.log.info( "Loading %s at %s" %(filename,  k.key))
         k.set_contents_from_file(file(filename), policy = 'public-read')

      calendar_url = "http://%s/%s" %(self.egress_fqdn, 'calendar.html')
      self.log.info("calendar URL is %s" % (calendar_url))

   def save_couchdb(self, ts, filename, shortname, s3_url = None, s3_key = None):
      scheme, netloc, path, query, fragment = urlparse.urlsplit(self.couchdb_uri)
      couch_key = os.path.join(ts.replace(":", "-").replace("-", "-"), shortname) + ".jpg"
      self.log.info("Saving record in couchdb at %s" % (couch_key))

      # save meta data
      rec = {
         "year" : int(time.strftime("%Y")),
         "month" : int(time.strftime("%m")),
         "day" : int(time.strftime("%d")),
         "doctype" : "metadata",
         "s3_url" : s3_url,
         "s3_key" : s3_key,
      }
      headers = {
         "Content-Type" : "application/json",
      }
      ss = httplib.HTTPConnection(netloc)
      ss.request("PUT", os.path.join(path, couch_key), json.dumps(rec), headers)
      res = None
      try:
         res = ss.getresponse()
      except httplib.BadStatusLine, e:
         self.log.error("ERROR: httplib.BadStatusLine: %s" %(e))

      if res:
         try:
            ret = json.loads(res.read())
         except:
            traceback.print_exc()
            ret = None

      if ret:
         self.log.info("Couchdb server said %s, %s, %s" % (res.status, res.reason, ret))

         # Upload the image as an attachment 
         aurl = os.path.join(path, ret['id'], "image")
         aurl_params = "?rev=" + ret['rev']
         ss.request("PUT", aurl + aurl_params, file(filename).read(), { "Content-Type" : "image/jpg" })
         res = ss.getresponse()
         self.log.info("Couchdb server said %s, %s %s" % (res.status, res.reason, res.read()))
         attach_url = scheme + "://" + netloc + os.path.join(path , ret['id'], "image")
         self.log.info("couchdb url %s" %(attach_url))
      else:
         self.log.error("problem with couchdb")
         attach_url = None
      return attach_url

