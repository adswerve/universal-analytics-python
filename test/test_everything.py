#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
# Test and example kit for Universal Analytics for Python
# Copyright (c) 2013, Analytics Pros
# 
# This project is free software, distributed under the BSD license. 
# Analytics Pros offers consulting and integration services if your firm needs 
# assistance in strategy, implementation, or auditing existing work.
###############################################################################

import unittest
import urllib

from UniversalAnalytics import Tracker
from UniversalAnalytics import HTTPLog


class UAMPythonTestCase(unittest.TestCase):
    
    def setUp(self):
        self._buffer = HTTPLog.StringIO()
        HTTPLog.consume(self._buffer) # Capture HTTP output in readible fashion
        Tracker.HTTPPost.debug() # Enabled debugging from urllib2
        
        # Create the tracker
        self.tracker = Tracker.create('UA-XXXXX-Y', use_post = True)

    def tearDown(self):
        self._buffer.truncate()
        del self.tracker
        del self._buffer

    @classmethod
    def url_quote(cls, value, safe_chars = ''):
        return urllib.quote(value, safe_chars)


    @property
    def buffer(self):
        return self._buffer.getvalue()

    def reset(self):
        self._buffer.truncate()


    def testTrackerOptionsBasic(self):
        self.assertEqual('UA-XXXXX-Y', self.tracker.params['tid'])  

    def testPersistentCampaignSettings(self):
        
        # Apply campaign settings
        self.tracker.set('campaignName', 'testing-campaign')
        self.tracker.set('campaignMedium', 'testing-medium')
        self.tracker['campaignSource'] = 'test-source'
    
        self.assertEqual(self.tracker.params['cn'], 'testing-campaign') 
        self.assertEqual(self.tracker.params['cm'], 'testing-medium')
        self.assertEqual(self.tracker.params['cs'], 'test-source')

    def testSendPageview(self):
        # Send a pageview
        self.tracker.send('pageview', '/test')
        
        self.assertIn('t=pageview', self.buffer)
        self.assertIn('dp={0}'.format(self.url_quote('/test')), self.buffer)
        self.reset()


    def testSendInteractiveEvent(self):
        # Send an event
        self.tracker.send('event', 'mycat', 'myact', 'mylbl', { 'noninteraction': 1, 'page': '/1' })
        self.assertIn('t=event', self.buffer)
        self.assertIn('ec=mycat', self.buffer)
        self.assertIn('ea=myact', self.buffer)
        self.assertIn('el=mylbl', self.buffer)
        self.assertIn('ni=1', self.buffer)
        self.assertIn('dp={0}'.format(self.url_quote('/1')), self.buffer)

        self.reset()

    def testSendUnicodeEvent(self):

        # Send unicode data:
        # As unicode
        self.tracker.send('event', u'câtēgøry', u'åctîõn', u'låbęl', u'válüē')
        # As str
        self.tracker.send('event', 'câtēgøry', 'åctîõn', 'låbęl', 'válüē')
        
        # TODO  write assertions for these...
        # The output buffer should show both representations in UTF-8 for compatibility


    def testSocialHit(self):
        # Send a social hit
        self.tracker.send('social', 'facebook', 'share', '/test#social')
        self.assertIn('t=social', self.buffer)
        self.assertIn('sn=facebook', self.buffer)
        self.assertIn('sa=share', self.buffer)
        self.assertIn('st={0}'.format(self.url_quote('/test#social')), self.buffer)
        self.reset()

    def testTransaction(self):

        # Dispatch the item hit first (though this is somewhat unusual)
        self.tracker.send('item', {
            'transactionId': '12345abc',
            'itemName': 'pizza',
            'itemCode': 'abc',
            'itemCategory': 'hawaiian',
            'itemQuantity': 1
        }, hitage = 7200)

        # Then the transaction hit...
        self.tracker.send('transaction', {
            'transactionId': '12345abc',
            'transactionAffiliation': 'phone order',
            'transactionRevenue': 28.00,
            'transactionTax': 3.00,
            'transactionShipping': 0.45,
            'transactionCurrency': 'USD'
        }, hitage = 7200)

    def testTimingAdjustedHits(self):

        # A few more hits for good measure, testing real-time support for time offset
        self.tracker.send('pageview', '/test', { 'campaignName': 'testing2' }, hitage = 60 * 5) # 5 minutes ago
        self.tracker.send('pageview', '/test', { 'campaignName': 'testing3' }, hitage = 60 * 20) # 20 minutes ago

# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
