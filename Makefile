
.PHONY: install clean uninstall build upload test release-version commit-version git-status-clean push-release release-checkout

GIT_COMMIT = $(shell git log -1 "--pretty=format:%H")
GIT_BRANCH = $(shell git describe --contains --all HEAD)
GIT_STATUS = $(shell git status -sb --untracked=no | wc -l | awk '{ if($$1 == 1){ print "clean" } else { print "pending" } }')

VERSION_PATTERN = "^[0-9]+\.[0-9]+\.[0-9]+$$"

DRYRUN ?= false

ifeq ($(DRYRUN),false)
	DRYRUN_ARG=
else
	DRYRUN_ARG=--dry-run
endif

install: test commit-version
	sudo python setup.py check install

remove uninstall:
	sudo pip uninstall universal-analytics-python

clean:
	@rm -rvf dist build universal_analytics_python.egg-info/
	@rm -vf RELEASE_VERSION 

build: test 
	python setup.py check build sdist bdist 

upload: git-status-clean test commit-version build
	test -s commit-version
	python setup.py ${DRYRUN_ARG} sdist bdist upload


push-release: release upload


git-status-clean:
	test "${GIT_STATUS}" == "clean" || (echo "GIT STATUS NOT CLEAN"; exit 1) >&2


release: release-version
	echo "## Tagging release " `cat release-version`
	git tag `cat release-version`

release-checkout:
	git checkout release


release-version: git-status-clean release-checkout test
	(echo "0.0.0"; git tag --list) | egrep "${VERSION_PATTERN}" | \
		sort -n | tail -n 1 | \
		awk -F '.' '{ printf("%d.%d.%d\n", ($$1), ($$2), ($$3) + 1 ) }' > $@


commit-version: git-status-clean
	git tag --list --points-at=${GIT_COMMIT} | egrep "${VERSION_PATTERN}" | \
		sort -n | tail -n 1 > $@


test:
	python -m unittest discover -f -s test/ -p 'test_*.py'
