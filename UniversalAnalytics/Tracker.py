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
    valid_hittypes = ('pageview', 'event', 'social', 'screenview', 'transaction', 'item', 'exception', 'timing')
 

    @classmethod
    def alias(cls, typemap, base, *names):
        """ Declare an alternate (humane) name for a measurement protocol parameter """
        cls.parameter_alias[ base ] = (typemap, base)
        for i in names:
            cls.parameter_alias[ i ] = (typemap, base)


    @classmethod
    def getparam(cls, name): 
        """ Clean up parameter names, translate parameter aliases as needed """
        if name and name[0] == '&':
            return name[1:]
        else:
            return cls.parameter_alias.get(name, None)


    @classmethod
    def setparam(cls, params, name, value): 
        """ Store or remove persistent values in tracker state (dictionary) """
        param = cls.getparam(name)
        if param is not None:
            if value is None:
                del params[ param ]
            else:
                params[ param ] = value


    @classmethod
    def payload_map(cls, data):
        for k, v in data.iteritems():
            if k in cls.parameter_alias:
                yield v, cls.parameter_alias[ k ]

    def payload(self, data):
        for v, k in self.payload_map(data):
            yield k[1], k[0](v) 


    option_sequence = {
        'pageview': [ (basestring, 'dp') ],
        'event': [ (basestring, 'ec'), (basestring, 'ea'), (basestring, 'el'), (int, 'ev') ],
        'social': [ (basestring, 'sn'), (basestring, 'sa'), (basestring, 'st') ],
        'timing': [ (basestring, 'utc'), (basestring, 'utv'), (basestring, 'utt'), (basestring, 'utl') ]
    }

    @classmethod
    def consume_options(cls, data, hittype, args):
        """ Interpret sequential arguments related to known hittypes based on declared structures """
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


    def __init__(self, account, name = None, client_id = None, hash_client_id = False, user_id = None, user_agent = None, use_post = True):
    
        if use_post is False:
            self.http = HTTPRequest(user_agent = user_agent)
        else: 
            self.http = HTTPPost(user_agent = user_agent)

        self.params = { 'v': 1, 'tid': account }

        if client_id is None:
            client_id = generate_uuid()

        self.params[ 'cid' ] = client_id

        self.hash_client_id = hash_client_id

        if user_id:
            self.params[ 'uid' ] = user_id


    def set_timestamp(self, data):
        """ Interpret time-related options, apply queue-time parameter as needed """
        if 'hittime' in data: # an absolute timestamp
            data['qt'] = self.hittime(timestamp = data.pop('hittime', None))
        if 'hitage' in data: # a relative age (in seconds)
            data['qt'] = self.hittime(age = data.pop('hitage', None))


    def send(self, hittype, *args, **data):
        """ Transmit HTTP requests to Google Analytics using the measurement protocol """

        if hittype not in self.valid_hittypes:
            raise KeyError('Unsupported Universal Analytics Hit Type: {0}'.format(repr(hittype)))

        self.set_timestamp(data)
        self.consume_options(data, hittype, args)

        for item in args: # process dictionary-object arguments of transcient data
            if isinstance(item, dict):
                for key, val in self.payload(item):
                    data[ key ] = val

        for k in self.params: # update only absent parameters
            if k not in data:
                data[ k ] = self.params[ k ]

   
        data = dict(self.payload(data))

        if self.hash_client_id:
            data[ 'cid' ] = generate_uuid(data[ 'cid' ])

        # Transmit the hit to Google...
        self.http.send(data)




    # Setting persistent attibutes of the session/hit/etc (inc. custom dimensions/metrics)
    def set(self, name, value = None):
        if isinstance(name, dict):
            for key, value in name.iteritems():
                self.setparam(self.params, key, value)
        elif isinstance(name, basestring):
            self.setparam(self.params, name, value)


    def __getitem__(self, name):
        return self.params.get(self.getparam(name), None)

    def __setitem__(self, name, value):
        self.setparam(self.params, name, value)

    def __delitem__(self, name):
        self.setparam(self.params, name, None)




# Declaring name mappings for Measurement Protocol parameters
Tracker.alias(int, 'v', 'protocol-version')
Tracker.alias(str, 'cid', 'client-id', 'clientId', 'clientid')
Tracker.alias(str, 'tid', 'trackingId', 'account')
Tracker.alias(str, 'uid', 'user-id', 'userId', 'userid')
Tracker.alias(str, 'uip', 'user-ip', 'userIp', 'ipaddr')
Tracker.alias(str, 'ua', 'userAgent', 'userAgentOverride', 'user-agent')
Tracker.alias(str, 'dp', 'page', 'path')
Tracker.alias(str, 'dt', 'title', 'pagetitle', 'pageTitle' 'page-title')
Tracker.alias(str, 'dl', 'location')
Tracker.alias(str, 'dh', 'hostname')
Tracker.alias(str, 'sc', 'sessioncontrol', 'session-control', 'sessionControl')
Tracker.alias(str, 'dr', 'referrer', 'referer')
Tracker.alias(int, 'qt', 'queueTime', 'queue-time')
Tracker.alias(str, 't', 'hitType', 'hittype')
Tracker.alias(int, 'aip', 'anonymizeIp', 'anonIp', 'anonymize-ip')


# Campaign attribution
Tracker.alias(str, 'cn', 'campaign', 'campaignName', 'campaign-name')
Tracker.alias(str, 'cs', 'source', 'campaignSource', 'campaign-source')
Tracker.alias(str, 'cm', 'medium', 'campaignMedium', 'campaign-medium')
Tracker.alias(str, 'ck', 'keyword', 'campaignKeyword', 'campaign-keyword')
Tracker.alias(str, 'cc', 'content', 'campaignContent', 'campaign-content')
Tracker.alias(str, 'ci', 'campaignId', 'campaignID', 'campaign-id')

# Technical specs
Tracker.alias(str, 'sr', 'screenResolution', 'screen-resolution', 'resolution')
Tracker.alias(str, 'vp', 'viewport', 'viewportSize', 'viewport-size')
Tracker.alias(str, 'de', 'encoding', 'documentEncoding', 'document-encoding')
Tracker.alias(int, 'sd', 'colors', 'screenColors', 'screen-colors')
Tracker.alias(str, 'ul', 'language', 'user-language', 'userLanguage')

# Mobile app
Tracker.alias(str, 'an', 'appName', 'app-name', 'app')
Tracker.alias(str, 'cd', 'contentDescription', 'screenName', 'screen-name', 'content-description')
Tracker.alias(str, 'av', 'appVersion', 'app-version', 'version')
Tracker.alias(str, 'aid', 'appID', 'appId', 'application-id', 'app-id', 'applicationId')
Tracker.alias(str, 'aiid', 'appInstallerId', 'app-installer-id')

# Ecommerce
Tracker.alias(str, 'ta', 'affiliation', 'transactionAffiliation', 'transaction-affiliation')
Tracker.alias(str, 'ti', 'transaction', 'transactionId', 'transaction-id')
Tracker.alias(float, 'tr', 'revenue', 'transactionRevenue', 'transaction-revenue')
Tracker.alias(float, 'ts', 'shipping', 'transactionShipping', 'transaction-shipping')
Tracker.alias(float, 'tt', 'tax', 'transactionTax', 'transaction-tax')
Tracker.alias(str, 'cu', 'currency', 'transactionCurrency', 'transaction-currency') # Currency code, e.g. USD, EUR
Tracker.alias(str, 'in', 'item-name', 'itemName')
Tracker.alias(float, 'ip', 'item-price', 'itemPrice')
Tracker.alias(float, 'iq', 'item-quantity', 'itemQuantity')
Tracker.alias(str, 'ic', 'item-code', 'sku', 'itemCode')
Tracker.alias(str, 'iv', 'item-variation', 'item-category', 'itemCategory', 'itemVariation')

# Events
Tracker.alias(str, 'ec', 'event-category', 'eventCategory', 'category')
Tracker.alias(str, 'ea', 'event-action', 'eventAction', 'action')
Tracker.alias(str, 'el', 'event-label', 'eventLabel', 'label')
Tracker.alias(int, 'ev', 'event-value', 'eventValue', 'value')
Tracker.alias(int, 'ni', 'noninteractive', 'nonInteractive', 'noninteraction', 'nonInteraction')


# Social
Tracker.alias(str, 'sa', 'social-action', 'socialAction')
Tracker.alias(str, 'sn', 'social-network', 'socialNetwork')
Tracker.alias(str, 'st', 'social-target', 'socialTarget')

# Exceptions
Tracker.alias(str, 'exd', 'exception-description', 'exceptionDescription', 'exDescription')
Tracker.alias(int, 'exf', 'exception-fatal', 'exceptionFatal', 'exFatal')

# User Timing
Tracker.alias(str, 'utc', 'timingCategory', 'timing-category')
Tracker.alias(str, 'utv', 'timingVariable', 'timing-variable')
Tracker.alias(float, 'utt', 'time', 'timingTime', 'timing-time')
Tracker.alias(str, 'utl', 'timingLabel', 'timing-label')
Tracker.alias(float, 'dns', 'timingDNS', 'timing-dns')
Tracker.alias(float, 'pdt', 'timingPageLoad', 'timing-page-load')
Tracker.alias(float, 'rrt', 'timingRedirect', 'timing-redirect')
Tracker.alias(str, 'tcp', 'timingTCPConnect', 'timing-tcp-connect')
Tracker.alias(str, 'srt', 'timingServerResponse', 'timing-server-response')

# Custom dimensions and metrics
for i in range(0,200):
    Tracker.alias(str, 'cd{0}'.format(i), 'dimension{0}'.format(i))
    Tracker.alias(int, 'cm{0}'.format(i), 'metric{0}'.format(i))

# Shortcut for creating trackers
def create(account, *args, **kwargs):
    return Tracker(account, *args, **kwargs)

# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
