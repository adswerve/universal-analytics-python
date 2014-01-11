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
    attribs = {}
    base_attribs = {}

    
    @staticmethod
    def debug():
        """ Activate debugging on urllib2 """
        handler = HTTPSHandler(debuglevel = 1)
        opener = build_opener(handler)
        install_opener(opener)

    # Store properties for all requests
    def __init__(self, user_agent = None, *args, **opts):
        self.user_agent = user_agent or 'Analytics Pros - Universal Analytics (Python)'
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

    @classmethod
    def fixUTF8(cls, data): # Ensure proper encoding for UA's servers...
        """ Convert all strings to UTF-8 """
        for key in data:
            if isinstance(data[ key ], basestring):
                data[ key ] = data[ key ].encode('utf-8')
        return data


    def getCurrentParameters(self, transcient_data):
        temp_data = {}
        temp_data.update(self.base_attribs)
        temp_data.update(self.attribs)
        temp_data.update(transcient_data)
        return self.fixUTF8(temp_data)

    # Apply stored properties to the given dataset & POST to the configured endpoint 
    def send(self, **data):     
        request = Request(
                self.endpoint + '?' + urlencode(self.getCurrentParameters(data)), 
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
    def send(self, **data):
        request = Request(
                self.endpoint, 
                data = urlencode(self.getCurrentParameters(data)), 
                headers = {
                    'User-Agent': self.user_agent
                }
            )
        self.open(request)


class Tracker(object):
    """ Primary tracking interface for Universal Analytics """
    trackers = {}
    state = {}
    data_mapping = {  }
    valid_hittypes = ('pageview', 'event', 'social', 'appview', 'transaction', 'item', 'exception', 'timing')


    @classmethod
    def params(cls, base, *names):
        cls.data_mapping[ base ] = base
        for i in names:
            cls.data_mapping[ i ] = base

    @classmethod
    def hittime(cls, timestamp = None, age = None, milliseconds = None):
        """ Returns an integer represeting the milliseconds offset for a given hit (relative to now) """
        if isinstance(timestamp, (int, float)):
            return int(Time.miliseconds_offset(Time.from_unix(timestamp, milliseconds = milliseconds)))
        if isinstance(timestamp, datetime.datetime):
            return int(Time.milliseconds_offset(timestamp))
        if isinstance(age, (int, float)):
            return int(age * 1000) + (milliseconds or 0)

            

    def __init__(self, account, name = None, client_id = None, user_id = None, user_agent = None, use_post = True):
        self.account = account
        self.state = {}
        if name:
            Tracker.trackers[ name ] = self

        if user_id:
            self.state[ 'uid' ] = user_id

        if client_id is None:
            client_id = generate_uuid()

        if use_post is False:
            self.http = HTTPRequest(v = 1, tid = account, cid = client_id)
        else: 
            self.http = HTTPPost(v = 1, tid = account, cid = client_id)

    # Issue HTTP requests on the measurement protocol
    def send(self, hittype, *args, **opts):
        data = {}
        data.update(self.state)

        hittime = opts.get('hittime', None)
        hitage = opts.get('hitage', None)

        if hittime is not None: # an absolute timestamp
            data['qt'] = self.hittime(timestamp = hittime)

        if hitage is not None: # a relative age (in seconds)
            data['qt'] = self.hittime(age = hitage)

        if hittype not in self.valid_hittypes:
            raise KeyError('Unsupported Universal Analytics Hit Type: {0}'.format(repr(hittype)))

        if hittype == 'pageview' and len(args) and isinstance(args[0], basestring):
            data['dp'] = args[0] # page path

        if hittype == 'event' and len(args) > 1:
            data['ec'] = args[0] # event category
            data['ea'] = args[1] # event action
            if len(args) > 2 and isinstance(args[2], basestring):
                data['el'] = args[2] # event label
            if len(args) > 3 and isinstance(args[3], int):
                data['ev'] = args[3] # event value

        if hittype == 'social' and len(args) > 1:
            data['sn'] = args[0] # social network
            data['sa'] = args[1] # social action
            if len(args) > 2 and isinstance(args[2], basestring):
                data['st'] = args[2] # social target

        if hittype == 'timing' and len(args) > 1:
            data['utc'] = args[0] # timing category
            data['utv'] = args[1] # timing variable
            data['utt'] = args[2] # timing time (value)
            if len(args) > 3 and isinstance(args[3], basestring):
                data['utl'] = args[3] # timing label


        for item in args: # process dictionary-object arguments of transcient data
            if isinstance(item, dict):
                for key, val in item.items():
                    if key in self.data_mapping:
                        data[ self.data_mapping[ key ] ] = val
                    else:
                        data[ key ] = val

        for key, val in opts.items(): # process attributes given as named arguments
            if key in self.data_mapping:
                data[ self.data_mapping[ key ] ] = val



        # Transmit the hit to Google...
        self.http.send(t = hittype, **data)




    # Setting persistent attibutes of the session/hit/etc (inc. custom dimensions/metrics)
    def set(self, name, value):
        if name in self.data_mapping:
            self.state[ self.data_mapping[ name ] ] = value
        else:
            pass

# Declaring name mappings for Measurement Protocol parameters
Tracker.params('cid', 'client-id', 'clientId', 'clientid')
Tracker.params('uid', 'user-id', 'userId', 'userid')
Tracker.params('dp', 'page', 'path')
Tracker.params('dt', 'title', 'pagetitle', 'pageTitle' 'page-title')
Tracker.params('dl', 'location')
Tracker.params('dh', 'hostname')
Tracker.params('sc', 'sessioncontrol', 'session-control', 'sessionControl')
Tracker.params('dr', 'referrer', 'referer')
Tracker.params('qt', 'queueTime', 'queue-time')

# Campaign attribution
Tracker.params('cn', 'campaign', 'campaignName', 'campaign-name')
Tracker.params('cs', 'source', 'campaignSource', 'campaign-source')
Tracker.params('cm', 'medium', 'campaignMedium', 'campaign-medium')
Tracker.params('ck', 'keyword', 'campaignKeyword', 'campaign-keyword')
Tracker.params('cc', 'content', 'campaignContent', 'campaign-content')
Tracker.params('ci', 'campaignId', 'campaignID', 'campaign-id')

# Technical specs
Tracker.params('sr', 'screenResolution', 'screen-resolution', 'resolution')
Tracker.params('vp', 'viewport', 'viewportSize', 'viewport-size')
Tracker.params('de', 'encoding', 'documentEncoding', 'document-encoding')
Tracker.params('sd', 'colors', 'screenColors', 'screen-colors')
Tracker.params('ul', 'language', 'user-language', 'userLanguage')

# Mobile app
Tracker.params('an', 'appName', 'app-name', 'app')
Tracker.params('cd', 'contentDescription', 'screenName', 'screen-name', 'content-description')
Tracker.params('av', 'appVersion', 'app-version', 'version')

# Ecommerce
Tracker.params('ta', 'affiliation', 'transactionAffiliation', 'transaction-affiliation')
Tracker.params('ti', 'transaction', 'transactionId', 'transaction-id')
Tracker.params('tr', 'revenue', 'transactionRevenue', 'transaction-revenue')
Tracker.params('ts', 'shipping', 'transactionShipping', 'transaction-shipping')
Tracker.params('tt', 'tax', 'transactionTax', 'transaction-tax')
Tracker.params('cu', 'currency', 'transactionCurrency', 'transaction-currency') # Currency code, e.g. USD, EUR
Tracker.params('in', 'item-name', 'itemName')
Tracker.params('ip', 'item-price', 'itemPrice')
Tracker.params('iq', 'item-quantity', 'itemQuantity')
Tracker.params('ic', 'item-code', 'sku', 'itemCode')
Tracker.params('iv', 'item-variation', 'item-category', 'itemCategory', 'itemVariation')

# Events
Tracker.params('ec', 'event-category', 'eventCategory', 'category')
Tracker.params('ea', 'event-action', 'eventAction', 'action')
Tracker.params('el', 'event-label', 'eventLabel', 'label')
Tracker.params('ev', 'event-value', 'eventValue', 'value')
Tracker.params('ni', 'noninteractive', 'nonInteractive', 'noninteraction', 'nonInteraction')


# Social
Tracker.params('sa', 'social-action', 'socialAction')
Tracker.params('sn', 'social-network', 'socialNetwork')
Tracker.params('st', 'social-target', 'socialTarget')

# Exceptions
Tracker.params('exd', 'exception-description', 'exceptionDescription')
Tracker.params('exf', 'exception-fatal', 'exceptionFatal')

# User Timing
Tracker.params('utc', 'timingCategory', 'timing-category')
Tracker.params('utv', 'timingVariable', 'timing-variable')
Tracker.params('utt', 'time', 'timingTime', 'timing-time')
Tracker.params('utl', 'timingLabel', 'timing-label')
Tracker.params('dns', 'timingDNS', 'timing-dns')
Tracker.params('pdt', 'timingPageLoad', 'timing-page-load')
Tracker.params('rrt', 'timingRedirect', 'timing-redirect')
Tracker.params('tcp', 'timingTCPConnect', 'timing-tcp-connect')
Tracker.params('srt', 'timingServerResponse', 'timing-server-response')

# Custom dimensions and metrics
for i in range(0,200):
    Tracker.params('cd{0}'.format(i), 'dimension{0}'.format(i))
    Tracker.params('cm{0}'.format(i), 'metric{0}'.format(i))

# Shortcut for creating trackers
def create(account, *args, **kwargs):
    return Tracker(account, *args, **kwargs)

# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
