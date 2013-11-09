from setuptools import setup

try:
    long_description=open('README.md', 'rt').read()
except Exception:
    long_description=""

setup(
    name = "universal-analytics-python",
    description = "Universal Analytics Python Module",
    long_description = long_description,

    version = "0.1",
    author = 'Sam Briesemeister',
    license = 'BSD',
    packages = ["UniversalAnalytics"],

    zip_safe = True,
)
