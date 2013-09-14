#!/usr/bin/python
###############################################################################
# Test and example kit for Universal Analytics for Python
# Copyright (c) 2013, Analytics Pros
# 
# This project is free software, distributed under the BSD license. 
# Analytics Pros offers consulting and integration services if your firm needs 
# assistance in strategy, implementation, or auditing existing work.
###############################################################################

from UniversalAnalytics import Tracker

DEBUG = True

if DEBUG: # these are optional...
    from UniversalAnalytics import HTTPLog
    HTTPLog.consume() # Filters urllib2's standard debugging for readability
    Tracker.HTTPPost.debug() # Enables debugging in urllib2

# Create the tracker
tracker = Tracker.create('UA-XXXXX-Y', name = 'mytracker')

# Apply campaign settings
tracker.set('campaignName', 'testing')
tracker.set('campaignMedium', 'testing')

# Send a pageview
tracker.send('pageview', '/test')

# Send an event
tracker.send('event', 'mycat', 'myact', 'mylbl', { 'noninteraction': 1, 'page': '/1' })

# Send a social hit
tracker.send('social', 'facebook', 'test', '/test#social')

# A few more hits for good measure, testing real-time support for time offset
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
