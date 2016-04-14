The goal of this program is to store screenshots on s3 (and others) as simple as possible.


[![Build Status](https://travis-ci.org/sigmonsays/screenshot.svg?branch=master)](https://travis-ci.org/sigmonsays/screenshot)

Features
--------------------
- supported on linux and Mac OSX
- capture screenshots using various utilities or custom command
- send screenshot images to various backends
- supports uploading images to s3, couchdb, tumblr and more
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
- dropbox requires dropbox

For clipboard support
- xclip command line 

screenshot commands on linux

- import - part of imagemagick
- gnome-screenshot - gnome screenshot command
- emprint - https://git.enlightenment.org/apps/emprint.git
- scrot - http://freshmeat.net/projects/scrot


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





Development
--------------------
For development see DEV.md

