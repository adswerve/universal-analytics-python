# Universal Analytics for Python

This library provides a Python interface to Google Analytics, supporting the Universal Analytics Measurement Protocol, with an interface modeled (loosely) after Google's `analytics.js`.

**NOTE** this project is reasonably feature-complete for most use-cases, covering all relevant features of the Measurement Protocol, however we still consider it _beta_. Please feel free to file issues for feature requests.

# Contact
Email: `opensource@analyticspros.com`

# Installation

The easiest way to install universal-analytics is directly from PyPi using `pip` by running the following command:

    pip install universal-analytics-python

Or use latest code:

    pip install -e git+https://github.com/analytics-pros/universal-analytics-python.git#egg=universal-analytics-python-dev

Otherwise you can download source code and install it directly:

    python setup.py install

# Usage

For the most accurate data in your reports, Analytics Pros recommends establishing a distinct ID for each of your users, and integrating that ID on your front-end web tracking, as well as back-end tracking calls. This provides for a consistent, correct representation of user engagement, without skewing overall visit metrics (and others).

A simple example:

```python
from UniversalAnalytics import Tracker

tracker = Tracker.create('UA-XXXXX-Y', client_id = CUSTOMER_UNIQUE_ID)
tracker.send('event', 'Subscription', 'billing')
```

Please see the [tests/main.py](./tests/main.py) script for additional examples.

This library support the following tracking types, with corresponding (optional) arguments:

* pageview: [ page path ]
* event: category, action, [ label [, value ] ] 
* social: network, action [, target ] 
* timing: category, variable, time [, label ]

Additional tracking types supported with property dictionaries:

* transaction
* item
* screenview 
* exception

Property dictionaries permit the same naming conventions given in the [analytics.js Field Reference](https://developers.google.com/analytics/devguides/collection/analyticsjs/field-reference), with the addition of common spelling variations, abbreviations, and hyphenated names (rather than camel-case).  These are also demonstrated in the [tests/main.py](./tests/main.py) file.

Further, the property dictionaries support names as per the [Measurement Protocol Parameter Reference](https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters), and properties/parameters can be passed as named arguments.

Example:

```python
  # as python named-arguments
  tracker.send('pageview', path = "/test", title = "Test page") 
  
  # as property dictionary 
  tracker.send('pageview', {
    'path': "/test",
    'title': "Test page"
  })
```

# Features not implemented

* Throttling

We're particularly interested in the scope of throttling for back-end tracking for users who have a defined use-case for it. Please [contact us](mailto:opensource@analyticspros.com) if you have such a use-case.


# License

universal-analytics-python is licensed under the [BSD license](./LICENSE)
