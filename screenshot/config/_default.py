
DEFAULT_CONFIG = """

[screenshot]
# Override what FQDN is use (for a reverse proxy if setup)
egress_url = http://example.net/%%s

index_file = %(HOME)s/.screenshots.index
directory = /tmp/screenshots

# How many images per page for HTML generation
page_size = 10

# use xclip to capture the URL
use_clipboard = yes

# How to decide what url gets copied to the clipboard
# clipboard method can be 
# - [backend] - a storage backend, like s3, couchdb, imgur, etc
# - tinyurl - from a url service, like tinyurl
# - template - from egress_url template
# - last - select the last image
clipboard_method = last

# screenshot method (autodetected by default) but you can override if you wish
# method can be 
# - imagemagick - use "import" command
# - gnome - use gnome-screenshot -a -f FILE
# - auto - detect automatically based on platform
# - screencapture - for MacOSX
# - custom - use custom command (see capture_command)
# capture_method = gnome

capture_method = auto

# if capture_method = custom
capture_command = capture-script.sh

random_filename = no

# use randomized filename
random_filename = no

# download the remote file url (clipboard url) to warm any cache
warm_cache = yes

[couchdb]
enabled = no
#uri = "http://username.couchone.com/screenshot"

[disk]
enabled = yes
save_dir = ~/Pictures/screenshot

[s3]
enabled = no
#key = XXX
#secret = XXX
#bucket = XXX
end_point = s3.amazonaws.com

[imgur]
enabled = no
client_id = 2ff238bd2a1883c
client_secret = 
title = Screenshot

[tinyurl]
enabled = no
#service = custom
#service_url = http://example.org/r

[tumblr]
enabled = no
#blog_url = yourname.tumblr.com
#consumer_key = XX
#consumer_secret = XX
#oauth_token = XX
#oauth_secret = XX

"""
