#!/usr/bin/python

from UniversalAnalytics import Tracker
from UniversalAnalytics import HTTPLog
import sys

HTTPLog.consume() # Overtakes standard output to show cleaner reports from urllib2's debugging
Tracker.HTTPPost.debug() # Enables debugging in urllib2

tracker = Tracker.create('UA-8705807-11', name = 'mytracker')

tracker.set('campaignName', 'testing')
tracker.set('campaignMedium', 'testing')
tracker.send('pageview', '/test')
tracker.send('event', 'mycat', 'myact', 'mylbl', { 'noninteraction': 1 })

# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
