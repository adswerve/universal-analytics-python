from HTTP import HTTPPost
from HTTP import debug as HTTPdebugging

HTTPdebugging()

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
            if len(args) > 2:
                data['el'] = args[2] # event label
            if len(args) > 3:
                data['ev'] = args[3] # event value

        for item in args:
            if isinstance(item, dict):
                data.update(item)

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
