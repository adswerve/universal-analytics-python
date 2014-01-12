###############################################################################
# Universal Analytics for Python
# Copyright (c) 2013, Analytics Pros
# 
# This project is free software, distributed under the BSD license. 
# Analytics Pros offers consulting and integration services if your firm needs 
# assistance in strategy, implementation, or auditing existing work.
###############################################################################

from urllib2 import urlopen, build_opener, install_opener
from urllib2 import Request, HTTPSHandler
from urllib2 import URLError, HTTPError
from urllib import urlencode

import random
import datetime
import time
import uuid
import hashlib
import socket

import logging
logging.basicConfig(level=logging.DEBUG)


def generate_uuid(basedata = None):
    """ Provides a _random_ UUID with no input, or a UUID4-format MD5 checksum of any input data provided """
    if basedata is None:
        return str(uuid.uuid4())
    elif isinstance(basedata, basestring):
        checksum = hashlib.md5(basedata).hexdigest()
        return '%8s-%4s-%4s-%4s-%12s' % (checksum[0:8], checksum[8:12], checksum[12:16], checksum[16:20], checksum[20:32])


class Time(datetime.datetime):
    """ Wrappers and convenience methods for processing various time representations """
    
    @classmethod
    def from_unix(cls, seconds, milliseconds = 0):
        """ Produce a full |datetime.datetime| object from a Unix timestamp """
        base = list(time.gmtime(seconds))[0:6]
        base.append(milliseconds * 1000) # microseconds
        return cls(* base)

    @classmethod
    def to_unix(cls, timestamp):
        """ Wrapper over time module to produce Unix epoch time as a float """
        if not isinstance(timestamp, datetime.datetime):
            raise TypeError, 'Time.milliseconds expects a datetime object'
        base = time.mktime(timestamp.timetuple())
        return base

    @classmethod
    def milliseconds_offset(cls, timestamp, now = None):
        """ Offset time (in milliseconds) from a |datetime.datetime| object to now """
        if isinstance(timestamp, (int, float)):
            base = timestamp
        else:
            base = cls.to_unix(timestamp) 
            base = base + (timestamp.microsecond / 1000000)
        if now is None:
            now = time.time()
        return (now - base) * 1000



class HTTPRequest(object):
    """ URL Construction and request handling abstraction.
        This is not intended to be used outside this module.

        Automates mapping of persistent state (i.e. query parameters)
        onto transcient datasets for each query.
    """

    endpoint = 'https://www.google-analytics.com/collect'

    
    @staticmethod
    def debug():
        """ Activate debugging on urllib2 """
        handler = HTTPSHandler(debuglevel = 1)
        opener = build_opener(handler)
        install_opener(opener)

    # Store properties for all requests
    def __init__(self, user_agent = None, *args, **opts):
        self.user_agent = user_agent or 'Analytics Pros - Universal Analytics (Python)'


    @classmethod
    def fixUTF8(cls, data): # Ensure proper encoding for UA's servers...
        """ Convert all strings to UTF-8 """
        for key in data:
            if isinstance(data[ key ], basestring):
                data[ key ] = data[ key ].encode('utf-8')
        return data



    # Apply stored properties to the given dataset & POST to the configured endpoint 
    def send(self, data):     
        request = Request(
                self.endpoint + '?' + urlencode(self.fixUTF8(data)), 
                headers = {
                    'User-Agent': self.user_agent
                }
            )
        self.open(request)

    def open(self, request):
        try:
            return urlopen(request)
        except HTTPError as e:
            return False
        except URLError as e:
            self.cache_request(request)
            return False

    def cache_request(self, request):
        record = (Time.now(), request.get_full_url(), request.get_data(), request.headers)
        pass




class HTTPPost(HTTPRequest):

    # Apply stored properties to the given dataset & POST to the configured endpoint 
    def send(self, data):
        request = Request(
                self.endpoint, 
                data = urlencode(self.fixUTF8(data)), 
                headers = {
                    'User-Agent': self.user_agent
                }
            )
        self.open(request)






class Tracker(object):
    """ Primary tracking interface for Universal Analytics """
    params = None
    parameter_alias = {}
    valid_hittypes = ('pageview', 'event', 'social', 'appview', 'transaction', 'item', 'exception', 'timing')
 

    @classmethod
    def alias(cls, base, *names):
        """ Declare an alternate (humane) name for a measurement protocol parameter """
        cls.parameter_alias[ base ] = base
        for i in names:
            cls.parameter_alias[ i ] = base


    @classmethod
    def getparam(cls, name):
        if name and name[0] == '&':
            return name
        else:
            return cls.parameter_alias.get(name, None)


    @classmethod
    def filter_payload(cls, data):
        for k, v in data.iteritems():
            param = cls.getparam(k) 
            if param is not None:
                yield (param, v) 

    option_sequence = {
        'pageview': [ (basestring, 'dp') ],
        'event': [ (basestring, 'ec'), (basestring, 'ea'), (basestring, 'el'), (int, 'ev') ],
        'social': [ (basestring, 'sn'), (basestring, 'sa'), (basestring, 'st') ],
        'timing': [ (basestring, 'utc'), (basestring, 'utv'), (basestring, 'utt'), (basestring, 'utl') ]
    }

    @classmethod
    def consume_options(cls, data, hittype, args):
        opt_position = 0
        data[ 't' ] = hittype # integrate hit type parameter
        if hittype in cls.option_sequence:
            for expected_type, optname in cls.option_sequence[ hittype ]:
                if opt_position < len(args) and isinstance(args[opt_position], expected_type):
                    data[ optname ] = args[ opt_position ]
                opt_position += 1



    @classmethod
    def hittime(cls, timestamp = None, age = None, milliseconds = None):
        """ Returns an integer represeting the milliseconds offset for a given hit (relative to now) """
        if isinstance(timestamp, (int, float)):
            return int(Time.miliseconds_offset(Time.from_unix(timestamp, milliseconds = milliseconds)))
        if isinstance(timestamp, datetime.datetime):
            return int(Time.milliseconds_offset(timestamp))
        if isinstance(age, (int, float)):
            return int(age * 1000) + (milliseconds or 0)

  

    @property
    def account(self):
        return self.params.get('tid', None)


    def __init__(self, account, name = None, client_id = None, user_id = None, user_agent = None, use_post = True):
    
        if use_post is False:
            self.http = HTTPRequest(user_agent = user_agent)
        else: 
            self.http = HTTPPost(user_agent = user_agent)

        self.params = { 'v': 1, 'tid': account }

        if client_id is None:
            client_id = generate_uuid()

        self.params[ 'cid' ] = client_id

        if user_id:
            self.params[ 'uid' ] = user_id


    # Issue HTTP requests on the measurement protocol
    def send(self, hittype, *args, **data):

        if hittype not in self.valid_hittypes:
            raise KeyError('Unsupported Universal Analytics Hit Type: {0}'.format(repr(hittype)))

        hittime = data.pop('hittime', None)
        hitage = data.pop('hitage', None)


        if hittime is not None: # an absolute timestamp
            data['qt'] = self.hittime(timestamp = hittime)

        if hitage is not None: # a relative age (in seconds)
            data['qt'] = self.hittime(age = hitage)


        self.consume_options(data, hittype, args)


        for item in args: # process dictionary-object arguments of transcient data
            if isinstance(item, dict):
                for key, val in self.filter_payload(item):
                    data[ key ] = val


        for k in self.params: # update only absent parameters
            if k not in data:
                data[ k ] = self.params[ k ]
   

        # Transmit the hit to Google...
        self.http.send(dict(self.filter_payload(data)))




    # Setting persistent attibutes of the session/hit/etc (inc. custom dimensions/metrics)
    def set(self, name, value):
        param = self.getparam(name)
        if param is not None:
            if value is None:
                del self.params[ name ]
            else:
                self.params[ param ] = value



    def __getitem__(self, name):
        return self.params.get(self.getparam(name), None)

    def __setitem__(self, name, value):
        param = self.getparam(name)
        if param is not None:
            self.params[ param ] = value

    def __delitem__(self, name):
        param = self.getparam(name)
        if param in self.params:
            del self.params[ param ]





# Declaring name mappings for Measurement Protocol parameters
Tracker.alias('cid', 'client-id', 'clientId', 'clientid')
Tracker.alias('uid', 'user-id', 'userId', 'userid')
Tracker.alias('dp', 'page', 'path')
Tracker.alias('dt', 'title', 'pagetitle', 'pageTitle' 'page-title')
Tracker.alias('dl', 'location')
Tracker.alias('dh', 'hostname')
Tracker.alias('sc', 'sessioncontrol', 'session-control', 'sessionControl')
Tracker.alias('dr', 'referrer', 'referer')
Tracker.alias('qt', 'queueTime', 'queue-time')
Tracker.alias('t', 'hitType', 'hittype')
Tracker.alias('v', 'protocol-version')
Tracker.alias('tid', 'trackingId', 'account')

# Campaign attribution
Tracker.alias('cn', 'campaign', 'campaignName', 'campaign-name')
Tracker.alias('cs', 'source', 'campaignSource', 'campaign-source')
Tracker.alias('cm', 'medium', 'campaignMedium', 'campaign-medium')
Tracker.alias('ck', 'keyword', 'campaignKeyword', 'campaign-keyword')
Tracker.alias('cc', 'content', 'campaignContent', 'campaign-content')
Tracker.alias('ci', 'campaignId', 'campaignID', 'campaign-id')

# Technical specs
Tracker.alias('sr', 'screenResolution', 'screen-resolution', 'resolution')
Tracker.alias('vp', 'viewport', 'viewportSize', 'viewport-size')
Tracker.alias('de', 'encoding', 'documentEncoding', 'document-encoding')
Tracker.alias('sd', 'colors', 'screenColors', 'screen-colors')
Tracker.alias('ul', 'language', 'user-language', 'userLanguage')

# Mobile app
Tracker.alias('an', 'appName', 'app-name', 'app')
Tracker.alias('cd', 'contentDescription', 'screenName', 'screen-name', 'content-description')
Tracker.alias('av', 'appVersion', 'app-version', 'version')

# Ecommerce
Tracker.alias('ta', 'affiliation', 'transactionAffiliation', 'transaction-affiliation')
Tracker.alias('ti', 'transaction', 'transactionId', 'transaction-id')
Tracker.alias('tr', 'revenue', 'transactionRevenue', 'transaction-revenue')
Tracker.alias('ts', 'shipping', 'transactionShipping', 'transaction-shipping')
Tracker.alias('tt', 'tax', 'transactionTax', 'transaction-tax')
Tracker.alias('cu', 'currency', 'transactionCurrency', 'transaction-currency') # Currency code, e.g. USD, EUR
Tracker.alias('in', 'item-name', 'itemName')
Tracker.alias('ip', 'item-price', 'itemPrice')
Tracker.alias('iq', 'item-quantity', 'itemQuantity')
Tracker.alias('ic', 'item-code', 'sku', 'itemCode')
Tracker.alias('iv', 'item-variation', 'item-category', 'itemCategory', 'itemVariation')

# Events
Tracker.alias('ec', 'event-category', 'eventCategory', 'category')
Tracker.alias('ea', 'event-action', 'eventAction', 'action')
Tracker.alias('el', 'event-label', 'eventLabel', 'label')
Tracker.alias('ev', 'event-value', 'eventValue', 'value')
Tracker.alias('ni', 'noninteractive', 'nonInteractive', 'noninteraction', 'nonInteraction')


# Social
Tracker.alias('sa', 'social-action', 'socialAction')
Tracker.alias('sn', 'social-network', 'socialNetwork')
Tracker.alias('st', 'social-target', 'socialTarget')

# Exceptions
Tracker.alias('exd', 'exception-description', 'exceptionDescription')
Tracker.alias('exf', 'exception-fatal', 'exceptionFatal')

# User Timing
Tracker.alias('utc', 'timingCategory', 'timing-category')
Tracker.alias('utv', 'timingVariable', 'timing-variable')
Tracker.alias('utt', 'time', 'timingTime', 'timing-time')
Tracker.alias('utl', 'timingLabel', 'timing-label')
Tracker.alias('dns', 'timingDNS', 'timing-dns')
Tracker.alias('pdt', 'timingPageLoad', 'timing-page-load')
Tracker.alias('rrt', 'timingRedirect', 'timing-redirect')
Tracker.alias('tcp', 'timingTCPConnect', 'timing-tcp-connect')
Tracker.alias('srt', 'timingServerResponse', 'timing-server-response')

# Custom dimensions and metrics
for i in range(0,200):
    Tracker.alias('cd{0}'.format(i), 'dimension{0}'.format(i))
    Tracker.alias('cm{0}'.format(i), 'metric{0}'.format(i))

# Shortcut for creating trackers
def create(account, *args, **kwargs):
    return Tracker(account, *args, **kwargs)

# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
