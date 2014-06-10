The goal of this program is to store screenshots on s3 (and others) as simple as possible.

Features
--------------------
- supported on linux and Mac OSX
- capture screenshots
- send screenshot images to various backends
- supports uploading images to s3, couchdb, tumblr and imgur
- automatically copies selected url to clipboard
- integrate with a variety of url shortening services, ie tinyurl
- build a static HTML image calendar for archival purposes (s3 only)

Requirements
--------------------
For uploading images
- S3 requires boto
- couchdb has no requirements
- tumblr requires pytumblr
- imgur requires pyimgur

For clipboard support
- xclip command line 
- image magick for the import command


Install on ubuntu lucid
<pre>
sudo apt-get install python-boto xclip imagemagick
</pre>


Configuration
--------------------
sample ~/.screenshot/screenshot.ini config file

<pre>
[screenshot]
use_clipboard = yes
egress_url = http://screenshot.example.net//%%(key)s
clipboard_method = template

[s3]
enabled = yes
key = XXXXXXXXXXXXXXXXXXXX
secret = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
bucket = XXXXXXXXXX
</pre>


