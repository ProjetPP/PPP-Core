PYTHON=python3

all: install

install:
	$(PYTHON) setup.py install

localinstall:
	$(PYTHON) setup.py install --user

run:
	gunicorn ppp_core:app

tests:
	$(PYTHON) run_tests.py

.PHONY: all install localinstall tests
