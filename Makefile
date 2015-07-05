define HELPBODY
Available commands:

	make help       - this thing.
	make init       - install python dependancies
	make test       - run tests and coverage
	make pylint     - code analysis
	make build      - pylint + test

endef

export HELPBODY
help:
	@echo "$$HELPBODY"

init:
	pip install -r requirements.txt

test:
	rm -f .coverage steam/*.pyc tests/*.pyc
	PYTHONHASHSEED=0 nosetests --verbosity 2 --with-coverage --cover-package=steam

pylint:
	pylint -r n -f colorized steam || true

build: pylint test

clean:
	rm -rf dist steam.egg-info steam/*.pyc

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel --universal

register:
	python setup.py register -r pypi

upload: dist register
	twine upload -r pypi dist/*
