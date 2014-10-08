PYTHON=python3

all:
	$(PYTHON) setup.py

install:
	$(PYTHON) setup.py install

localinstall:
	$(PYTHON) setup.py install --user

tests:
	$(PYTHON) run_tests.py

.PHONY: all install localinstall tests
