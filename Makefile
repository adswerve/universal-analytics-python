
.PHONY: install clean remove build upload test RELEASE_VERSION release-tag

GIT_COMMIT = $(shell git log -1 "--pretty=format:%H")
GIT_BRANCH = $(shell git describe --contains --all HEAD)
GIT_STATUS = $(shell git status -sb --untracked=no | wc -l | awk '{ if($$1 == 1){ print "clean" } else { print "pending" } }')

install:
	python setup.py install

clean:
	@rm -rf dist build universal_analytics_python.egg-info/
	@rm RELEASE_VERSION 

build: test 
	python setup.py build 

upload: build test RELEASE_VERSION
	python setup.py sdist upload

release-tag: RELEASE_VERSION
	test "${GIT_STATUS}" == "clean" || echo "GIT STATUS NOT CLEAN" >&2
	git tag `tail -n 1 RELEASE_VERSION` 


RELEASE_VERSION:
	(echo "0.0.0"; git tag --list) | sort -n | egrep "^[0-9]+\.[0-9]+\.[0-9]+$$" | awk -F '.' '{ printf("%d.%d.%d\n", ($$1), ($$2), ($$3) + 1 ) }' > $@


test:
	python -m unittest discover -f -s test/ -p 'test_*.py'
