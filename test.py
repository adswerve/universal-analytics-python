#!/usr/bin/python

from UniversalAnalytics import Tracker


tracker = Tracker.create('UA-8705807-11', name = 'mytracker')

tracker.set('campaignName', 'testing')
tracker.set('campaignMedium', 'testing')
tracker.send('pageview', '/test')
tracker.send('event', 'mycat', 'myact', 'mylbl')

# vim: set nowrap tabstop=4 shiftwidth=4 softtabstop=0 expandtab textwidth=0 filetype=python foldmethod=indent foldcolumn=4
