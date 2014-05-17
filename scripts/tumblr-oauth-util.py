#!/usr/bin/env python
"""
http://stackoverflow.com/questions/7569018/oauth-client-initialization-in-python-for-tumblr-api-using-python-oauth2
"""

import sys
import logging
from optparse import OptionParser
from screenshot.s3util import S3Util
from screenshot import config
from screenshot import cli
import urlparse
import oauth2

REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
AUTHORIZATION_URL = 'http://www.tumblr.com/oauth/authorize'

def main():

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config", help="config file", metavar="FILE", default=None)
    parser.add_option("", "--step1", dest="step_one", help="step 1 - request access token", action="store_true", default=False)
    parser.add_option("", "--step2", dest="step_two", help="step 2 - sign access token", action="store_true", default=False)
    (options, args) = parser.parse_args()

    opts = config.GetScreenshotOptions(options.config)

    c = opts.tumblr_config
    consumer_key = c['consumer_key']
    consumer_secret = c['consumer_secret']

    print
    print "consumer_key:", repr(consumer_key)
    print "consumer_secret:", repr(consumer_secret)
    print

    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    client = oauth2.Client(consumer)

    # Step 1: get temporary authentication tokens
    print 
    print "Getting a request token"
    resp, content = client.request(REQUEST_TOKEN_URL, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s" % (resp))

    # Step 2: authorize in web browser
    request_token = dict(urlparse.parse_qsl(content))
    print "Request Token:"
    print "    - oauth_token        = %s" % request_token['oauth_token']
    print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    print
    print "Go to the following link in your browser:"
    print "%s?oauth_token=%s" % (AUTHORIZATION_URL, request_token['oauth_token'])

    print 
    print "Press enter after authorizing..."
    sys.stdin.readline()

    print "Enter the oauth_verifier: ",
    oauth_verifier = raw_input("Enter the oauth_verifier: ")
    print "oauth_verifier:", repr(oauth_verifier)

    # Step 3: request access 
    token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URL, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print

if __name__ == '__main__':
    main()
