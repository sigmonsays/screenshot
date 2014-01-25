The goal of this program is to store screenshots on s3 (and others) as simple as possible
while still presenting a HTML based browser for all the screenshots. Mostly these are a
collection of scripts organized into a single script. I actually have no idea what all
the options do at this point in time.

Features
- supported on linux and Mac OSX
- capture screenshots
- send screenshot images to s3 or couchdb database
- copy url to clipboard
- integrate with a tinyurl services
- build a static HTML image calendar for archival purposes (s3 only)

The script uses the boto library to upload content to S3 at http://code.google.com/p/boto/

There is also support for storing metadata and image data in CouchDB. This uses httplib
and stores them in a document with a 'image' attachment.

If configured you can also use a tinyurl service, although support for that is very limited
at the moment. It only supports a HTTP POST to a custom script.

--- sample ~/.screenshot/screenshot.ini config file ---
[screenshot]
use_clipboard = yes
egress_fqdn = screenshot.example.net

[s3]
enabled = yes
key = XXXXXXXXXXXXXXXXXXXX
secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bucket = XXXXXXXXXX

---- end configuration sample -------------------------

An image calendar can be build using static HTML when you are storing
objects in S3. This can be done using the --update-full-calendar option.


Software dependancies
---------------------------------
- boto library
- xclip command line 
- image magick for the import command

Setup on ubuntu lucid

sudo apt-get install python-boto xclip imagemagick

