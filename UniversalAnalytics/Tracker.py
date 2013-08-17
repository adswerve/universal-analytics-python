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

    # Apply stored properties to the given dataset & POST to the configured endpoint 
    def send(self, **data):
        data.update(self.base_attribs)
        data.update(self.attribs)
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
    data_mapping = {
            'page': 'dp',
            'path': 'dp',
            'title': 'dt',
            'location': 'dl',
            'hostname': 'dh',
            'noninteraction': 'ni',
            'noninteractive': 'ni',
            'non-interaction': 'ni',
            'nonInteration': 'ni',
            'client-id': 'cid',
            'clientId': 'cid',
            'clientid': 'cid',
            'sessionControl': 'sc',
            'session-control': 'sc',
            'sessioncontrol': 'sc',
            'referrer': 'dr',
            'referer': 'dr',
            'campaign': 'cn',
            'campaignName': 'cn',
            'campaign-name': 'cn',
            'source': 'cs',
            'campaignSource': 'cs',
            'medium': 'cm',
            'campaignMedium': 'cm',
            'keyword': 'ck',
            'campaignKeyword': 'ck',
            'content': 'cc',
            'campaignContent': 'cc',
            'campaignID': 'ci',
            'campaignId': 'ci',
            'screenResolution': 'sr',
            'resolution': 'sr',
            'screen-resolution': 'sr',
            'viewport': 'vp',
            'viewportSize': 'vp',
            'viewport-size': 'vp',
            'encoding': 'de',
            'documentEncoding': 'de',
            'document-encoding': 'de',
            'screenColors': 'sd',
            'screen-colors': 'sd',
            'colors': 'sd',
            'langauge': 'ul',
            'userLanguage': 'ul',
            'user-language': 'ul',
            'appName': 'an',
            'app': 'an',
            'app-name': 'an',
            'appVersion': 'av',
            'version': 'av',
            'app-version': 'av'
    }

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

        if hittype == 'pageview' and isinstance(args[0], basestring):
            data['dp'] = args[0] # page path
        if hittype == 'event' and len(args) > 2:
            data['ec'] = args[0] # event category
            data['ea'] = args[1] # event action
            if len(args) > 2 and isinstance(args[2], basestring):
                data['el'] = args[2] # event label
            if len(args) > 3 and isinstance(args[3], int):
                data['ev'] = args[3] # event value

        for item in args:
            if isinstance(item, dict):
                for key, val in item.items():
                    if key in self.data_mapping:
                        data[ self.data_mapping[ key ] ] = val
                    else:
                        data[ key ] = val

        for key, val in opts:
            if key in self.data_mapping:
                data[ self.data_mapping[ key ] ] = val


        self.http.send(t = hittype, **data)



    # Setting attibutes of the session/hit/etc (inc. custom dimensions/metrics)
    def set(self, name, value):
        if name in self.data_mapping:
            self.state[ self.data_mapping[ name ] ] = value
        else:
            pass



def create(account, name = None):
    return Tracker(account, name)
# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
