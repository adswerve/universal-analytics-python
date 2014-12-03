
.PHONY: install clean remove build upload test release-tag commit-tag git-status-clean push-release release-checkout

GIT_COMMIT = $(shell git log -1 "--pretty=format:%H")
GIT_BRANCH = $(shell git describe --contains --all HEAD)
GIT_STATUS = $(shell git status -sb --untracked=no | wc -l | awk '{ if($$1 == 1){ print "clean" } else { print "pending" } }')

VERSION_PATTERN = "^[0-9]+\.[0-9]+\.[0-9]+$$"


install:
	python setup.py install

clean:
	@rm -rf dist build universal_analytics_python.egg-info/
	@rm RELEASE_VERSION 

build: test 
	python setup.py build 

upload: git-status-clean test commit-tag
	python setup.py sdist upload


push-release: release upload


git-status-clean:
	test "${GIT_STATUS}" == "clean" || (echo "GIT STATUS NOT CLEAN"; exit 1) >&2


release: release-tag
	echo "## Tagging release " `cat release-tag`
	git tag `cat release-tag`

release-checkout:
	git checkout release


release-tag: git-status-clean release-checkout test
	(echo "0.0.0"; git tag --list) | egrep "${VERSION_PATTERN}" | \
		sort -n | tail -n 1 | \
		awk -F '.' '{ printf("%d.%d.%d\n", ($$1), ($$2), ($$3) + 1 ) }' > $@


commit-tag: git-status-clean
	git tag --list --points-at=${GIT_COMMIT} | egrep "${VERSION_PATTERN}" | \
		sort -n | tail -n 1 > $@


test:
	python -m unittest discover -f -s test/ -p 'test_*.py'
