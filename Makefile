define HELPBODY
Available commands:

	make help       - this thing.

	make init       - install python dependancies
	make test       - run tests and coverage
	make pylint     - code analysis
	make build      - pylint + test
	make docs       - generate html docs using sphinx

	make dist		- build source distribution
	mage register	- register in pypi
	make upload 	- upload to pypi

	make pb_fetch   - fetch protobufs from SteamRE
	make pb_compile - compile with protoc
	make pb_clear   - removes *.proto
	make pb_update  - pb_fetch + pb_compile

endef

export HELPBODY
help:
	@echo "$$HELPBODY"

init:
	pip install -r requirements.txt

test:
	coverage erase
	PYTHONHASHSEED=0 pytest --cov=steam tests

webauth_gen:
	rm -f vcr/webauth*
	python tests/generete_webauth_vcr.py

pylint:
	pylint -r n -f colorized steam || true

build: pylint test docs

.FORCE:
docs: .FORCE
	$(MAKE) -C docs html

clean:
	rm -rf dist steam.egg-info steam/*.pyc

dist: clean
	python setup.py sdist

register:
	python setup.py register -r pypi

upload: dist register
	twine upload -r pypi dist/*

pb_fetch:
	wget -nv --show-progress -N -P ./protobufs/ -i protobuf_list.txt || exit 0
	rename -v '.steamclient' '' protobufs/*.proto
	sed -i '1d' protobufs/{steammessages_physicalgoods,test_messages}.proto
	sed -i '1s/^/package foobar;\n/' protobufs/gc.proto
	sed -i 's/optional \./optional foobar./' protobufs/gc.proto
	sed -i '1s/^/syntax = "proto2"\;\n/' protobufs/*.proto
	sed -i 's/cc_generic_services/py_generic_services/' protobufs/*.proto
	sed -i 's/\.steamclient\.proto/.proto/' protobufs/*.proto

pb_compile:
	for filepath in `ls ./protobufs/*.proto`; do \
		protoc3 --python_out ./steam/protobufs/ --proto_path=./protobufs "$$filepath"; \
	done;
	sed -i '/^import sys/! s/^import /import steam.protobufs./' steam/protobufs/*_pb2.py

pb_clear:
	rm -f ./protobufs/*.proto ./steam/protobufs/*_pb2.py

pb_update: pb_fetch pb_compile
