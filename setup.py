from setuptools import setup
import sys

VERSION=open('commit-version').read().strip()
print >>sys.stderr, "Preparing version {0}\n".format(VERSION or "NOTFOUND")


try:
    long_description=open('DESCRIPTION.rst', 'rt').read()
except Exception:
    long_description="Universal Analytics in Python; an implementation of Google's Universal Analytics Measurement Protocol"



setup(
    name = "universal-analytics-python",
    description = "Universal Analytics Python Module",
    long_description = long_description,

    version = VERSION or 'NOTFOUND',

    author = 'Sam Briesemeister',
    author_email = 'opensource@analyticspros.com',

    url = 'https://github.com/analytics-pros/universal-analytics-python',
    download_url = "https://github.com/analytics-pros/universal-analytics-python/tarball/" + VERSION,

    license = 'BSD',
    packages = ["UniversalAnalytics"],

    install_requires = [],

    zip_safe = True,
)
