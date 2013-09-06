#!/usr/bin/python

from UniversalAnalytics import Tracker
from UniversalAnalytics import HTTPLog

HTTPLog.consume() # Overtakes standard output to show cleaner reports from urllib2's debugging
Tracker.HTTPPost.debug() # Enables debugging in urllib2

tracker = Tracker.create('UA-8705807-11', name = 'mytracker')

tracker.set('campaignName', 'testing')
tracker.set('campaignMedium', 'testing')
tracker.send('pageview', '/test')
tracker.send('event', 'mycat', 'myact', 'mylbl', { 'noninteraction': 1, 'page': '/1' })
tracker.send('social', 'facebook', 'test', '/test#social')

# A few more hits for good measure (testing real-time support for time offset)
tracker.send('pageview', '/test', { 'campaignName': 'testing2' }, hitage = 60 * 5) # 5 minutes ago
tracker.send('pageview', '/test', { 'campaignName': 'testing3' }, hitage = 60 * 20) # 20 minutes ago


tracker.send('item', {
    'transactionId': '12345abc',
    'itemName': 'pizza',
    'itemCode': 'abc',
    'itemCategory': 'hawaiian',
    
    'itemQuantity': 1
}, hitage = 7200)

tracker.send('transaction', {
    'transactionId': '12345abc',
    'transactionAffiliation': 'phone order',
    'transactionRevenue': 28.00,
    'transactionTax': 3.00,
    'transactionShipping': 0.45,
    'transactionCurrency': 'USD'
}, hitage = 7200)



# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
