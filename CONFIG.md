# Configuration Parameters

| Directive                     | Default Value                             | Description                                                                  |
| ---                           | ---                                       | ---                                                                          |
| `screenshot.egress_url`       | http://example.net/%%s                    | Override what FQDN is use (for a reverse proxy if setup)                     |
| `screenshot.index_file`       | %(HOME)s/.screenshots.index               |                                                                              |
| `screenshot.directory`        | /tmp/screenshots                          |                                                                              |
| `screenshot.page_size`        | 10                                        | How many images per page for HTML generation                                 |
| `screenshot.use_clipboard`    | yes                                       | use xclip to capture the URL                                                 |
| `screenshot.clipboard_method` | last                                      | How to decide what url gets copied to the clipboard (See Notes below)        |
| `screenshot.capture_method`   | auto                                      | screenshot method (autodetected by default) but you can override if you wish |
| `screenshot.random_filename`  | no                                        | use randomized filename                                                      |
| `screenshot.warm_cache`       | yes                                       | download the remote file url (clipboard url) to warm any cache               |
| `couchdb.enabled`             | no                                        | enable uploading to couchdb                                                  |
| `couchdb.uri`                 | "http://username.couchone.com/screenshot" | couchdb database uri                                                         |
| `disk.enabled`                | yes                                       | enable saving to disk                                                        |
| `disk.save_dir`               | ~/Pictures/screenshot                     | path where images are saved to disk                                          |
| `s3.enabled`                  | no                                        | enable uploading to s3                                                       |
| `s3.key`                      | XXX                                       | key                                                                          |
| `s3.secret`                   | XXX                                       | secret                                                                       |
| `s3.bucket`                   | XXX                                       | bucket                                                                       |
| `s3.end_point`                | s3.amazonaws.com                          | s3 api endpoint name                                                         |
| `imgur.enabled`               | no                                        | enable uploading to imgur                                                    |
| `imgur.client_id`             | 2ff238bd2a1883c                           | client id                                                                    |
| `imgur.client_secret`         |                                           | client secret                                                                |
| `imgur.title`                 | Screenshot                                | default title to use for uploads                                             |
| `tinyurl.enabled`             | no                                        | enable uploading to tinyurl                                                  |
| `tinyurl.service`             | custom                                    | tiny url service                                                             |
| `tinyurl.service_url`         | http://example.org/r                      |                                                                              |

Notes

`screenshot.clipboard_method` method can be 
 - [backend] - a storage backend, like s3, couchdb, imgur, etc
 - tinyurl - from a url service, like tinyurl
 - template - from egress_url template
 - last - select the last image

`screenshot.capture_method` can be 
 - imagemagick - use "import" command
 - gnome - use gnome-screenshot -a -f FILE
 - auto - detect automatically based on platform
 - screencapture - for MacOSX


# Default Configuration

<pre>

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
# capture_method = gnome

capture_method = auto

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

</pre>
