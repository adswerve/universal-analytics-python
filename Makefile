
.PHONY: install clean remove upload

install:
	python setup.py install

clean:
	@rm -rf dist universal_analytics_python.egg-info/

upload:
	python setup.py sdist upload


