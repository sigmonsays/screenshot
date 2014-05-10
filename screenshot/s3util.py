import os
import time
import calendar
import logging

from boto.s3.connection import S3Connection
from boto.s3.key import Key

class S3Util:

   def __init__(self, screenshot_dir, key, secret, end_point, bucket, egress_fqdn):
      self.log = logging.getLogger(self.__class__.__name__)
      self.log.debug("end_point %s bucket %s", end_point, bucket)
      conn = S3Connection(aws_access_key_id=key, aws_secret_access_key=secret, host=end_point)
      bucket = conn.get_bucket(bucket)
      self.__dict__.update(locals())


   def _iter_s3_images(self):
      self.queue = []
      for obj in self.bucket:
         if obj.name.endswith('.jpg'):
            yield obj

   def update_full_calendar(self):
      #organize by year, month tuple
      cal = {}
      IMAGES = {}
      for obj in self._iter_s3_images():
         tmp = obj.name.split("/", 6)
         tmp.pop()
         try:
             tmp = map(int, tmp)
         except Exception, e:
             self.log.exception(e)
             continue
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

