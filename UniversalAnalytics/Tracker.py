from urllib2 import urlopen, build_opener, install_opener
from urllib2 import Request, HTTPSHandler
from urllib import urlencode


class HTTPPost(object):

    endpoint = 'https://www.google-analytics.com/collect'
    attribs = {}
    base_attribs = {}
    
    @staticmethod
    def debug(): 
        handler = HTTPSHandler(debuglevel = 1)
        opener = build_opener(handler)
        install_opener(opener)

    # Store properties for all requests
    def __init__(self, *args, **opts):
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
    def fixUTF8(cls, data):
        for key in data:
            if isinstance(data[ key ], basestring):
                data[ key ] = data[ key ].encode('utf-8')

    # Apply stored properties to the given dataset & POST to the configured endpoint 
    def send(self, **data):
        data.update(self.base_attribs)
        data.update(self.attribs)
        self.fixUTF8(data)
        request = Request(
                self.endpoint, 
                data = urlencode(data), 
                headers = {
                    'User-Agent': 'Analytics Pros - Universal Analytics (Python)'
                }
            )
        urlopen(request)




class Tracker(object):
    trackers = {}
    state = {}
    data_mapping = {  }
    valid_hittypes = ('pageview', 'event', 'social', 'appview', 'transaction', 'item', 'exception', 'timing')


    @classmethod
    def params(cls, base, *names):
        for i in names:
            cls.data_mapping[ i ] = base



    def __init__(self, account, name = None, client_id = None):
        self.account = account
        self.state = {}
        if name:
            Tracker.trackers[ name ] = self

        self.http = HTTPPost(v = 1, tid = account, cid = client_id)

    # Issue HTTP requests on the measurement protocol
    def send(self, hittype, *args, **opts):
        data = {}
        data.update(self.state)

        if hittype not in self.valid_hittypes:
            raise KeyError('Unsupported Universal Analytics Hit Type')

        if hittype == 'pageview' and isinstance(args[0], basestring):
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


        for item in args: # process dictionary arguments
            if isinstance(item, dict):
                for key, val in item.items():
                    if key in self.data_mapping:
                        data[ self.data_mapping[ key ] ] = val
                    else:
                        data[ key ] = val

        for key, val in opts: # process attributes given as named arguments
            if key in self.data_mapping:
                data[ self.data_mapping[ key ] ] = val


        self.http.send(t = hittype, **data)



    # Setting attibutes of the session/hit/etc (inc. custom dimensions/metrics)
    def set(self, name, value):
        if name in self.data_mapping:
            self.state[ self.data_mapping[ name ] ] = value
        else:
            pass

# Declaring name mappings for Measurement Protocol parameters
Tracker.params('cid', 'client-id', 'clientId', 'clientid')
Tracker.params('dp', 'page', 'path')
Tracker.params('dt', 'title', 'pagetitle', 'pageTitle' 'page-title')
Tracker.params('dl', 'location')
Tracker.params('dh', 'hostname')
Tracker.params('ni', 'noninteractive', 'noninteraction', 'nonInteraction')
Tracker.params('sc', 'sessioncontrol', 'session-control', 'sessionControl')
Tracker.params('dr', 'referrer', 'referer')

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


def create(account, name = None):
    return Tracker(account, name)
# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
