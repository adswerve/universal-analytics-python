
.PHONY: install clean remove upload test

install:
	python setup.py install

clean:
	@rm -rf dist universal_analytics_python.egg-info/

upload:
	python setup.py sdist upload


test:
	python -m unittest discover -f -s test/ -p 'test_*.py'
