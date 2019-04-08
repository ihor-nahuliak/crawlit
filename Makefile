.PHONY: all

DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
SHELL=/bin/bash

LIB := $(DIR)/.env/lib/python3/site-packages
PYTHON := $(DIR)/.env/bin/python
PIP := $(DIR)/.env/bin/pip
FLAKE8 := $(DIR)/.env/bin/flake8 --config=$(DIR)/.flake8
NOSETESTS := $(DIR)/.env/bin/nosetests

STATUS_ERROR := \033[1;31m*\033[0m Error
STATUS_OK := \033[1;32m*\033[0m OK


install-env:
	rm -rf "$(DIR)/.env/" ;\
	virtualenv -p /usr/bin/python3 --clear "$(DIR)/.env/" ;\
	if [ $$? -eq 0 ]; then \
		echo -e "${STATUS_OK}" ;\
	else \
		echo -e "${STATUS_ERROR}" ;\
	fi;

env-activate:
	. $(DIR)/.env/bin/activate

install-python-libs:
	$(PIP) install --upgrade pip ;\
	$(PIP) install --no-cache-dir --upgrade \
	-r "$(DIR)/requirements.txt" ;\
	if [ $$? -eq 0 ]; then \
		echo -e "${STATUS_OK}" ;\
	else \
		echo -e "${STATUS_ERROR}" ;\
	fi;

install: install-env env-activate install-python-libs


test-unittests:
	@mkdir -p ./tests/.reports/ ;\
	$(NOSETESTS) \
	    --with-coverage \
	    --cover-erase \
	    --cover-html --cover-html-dir="$(DIR)/tests/.reports/coverage/" \
	    --cover-package="$(DIR)/crawlit" \
	;\
	if [ $$? -eq 0 ]; then \
		echo -e "unittests: ... ${STATUS_OK}" ;\
	else \
		echo -e "unittests: ... ${STATUS_ERROR}" ;\
	fi;

test-flake8:
	@$(FLAKE8) "$(DIR)/crawlit" \
	           "$(DIR)/tests" \
	;\
	if [ $$? -eq 0 ]; then \
		echo -e "flake8: ........ ${STATUS_OK}" ;\
	else \
		echo -e "flake8: ........ ${STATUS_ERROR}" ;\
	fi;

test: test-unittests test-flake8
