from urllib2 import urlopen, HTTPSHandler, build_opener, install_opener
from urllib import urlencode

import sys

def debug(): 
    handler = HTTPSHandler(debuglevel = 1)
    opener = build_opener(handler)
    install_opener(opener)

class HTTPPost(object):

    endpoint = 'https://www.google-analytics.com/collect'
    attribs = {}
    base_attribs = {}

    # Store properties for all requests
    def __init__(self, *args, **opts):
        self.debug = debug
        self.attribs = {}
        self.base_attribs = opts
        self.attribs.update(opts)

    # Clear transcient properties; restore only the props given at instantiation (__init__)
    def reset(self):
        self.attribs = {}
        self.attribs.update(self.base_attribs)

    # Store transcient properties for subsequent requests
    def update(self, **opts):
        self.attribs.update(opts)

    # Apply stored properties to the given dataset & POST to the configured endpoint 
    def send(self, **data):
        data.update(self.base_attribs)
        data.update(self.attribs)

        print >>sys.stderr, '{0} << {1}\n'.format(self.endpoint, repr(data))

        urlopen(self.endpoint, urlencode(data))

        
# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
