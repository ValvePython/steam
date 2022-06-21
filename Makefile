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
	pip install -r dev_requirements.txt

init_docs:
	pip install sphinx==1.8.5 sphinx_rtd_theme

COVOPTS = --cov-config .coveragerc --cov=steam

ifeq ($(NOCOV), 1)
	COVOPTS =
endif

test:
	coverage erase
	PYTHONHASHSEED=0 pytest --tb=short $(COVOPTS) tests

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
	mv protobufs/friends_mobile.proto protobufs/steammessages_webui_friends.steamclient.proto
	sed -i 's/CCommunity_ClanAnnouncementInfo/xCCommunity_ClanAnnouncementInfo/' protobufs/steammessages_webui_friends.steamclient.proto
	sed -i 's/CMsgClientSecret/xCMsgClientSecret/' protobufs/steammessages_webui_friends.steamclient.proto
	sed -i '1s/^/option py_generic_services = true\;\n/' protobufs/steammessages_webui_friends.steamclient.proto
	rename -v '.proto' '.proto.notouch' protobufs/{steammessages_physicalgoods,gc,test_messages}.proto
	rename -v '.steamclient' '' protobufs/*.proto
	sed -i '1s/^/syntax = "proto2"\;\n/' protobufs/*.proto
	sed -i 's/cc_generic_services/py_generic_services/' protobufs/*.proto
	sed -i 's/\.steamclient\.proto/.proto/' protobufs/*.proto
	rename -v '.notouch' '' protobufs/*.proto.notouch

pb_compile:
	for filepath in ./protobufs/*.proto; do \
		protoc3 --python_out ./steam/protobufs/ --proto_path=./protobufs "$$filepath"; \
	done;
	sed -i '/^import sys/! s/^import /import steam.protobufs./' steam/protobufs/*_pb2.py

pb_clear:
	rm -f ./protobufs/*.proto ./steam/protobufs/*_pb2.py

pb_services:
	grep -B 99999 MARK_SERVICE_START steam/core/msg/unified.py > steam/core/msg/unified.py.tmp
	grep '^service' protobufs/*.proto | tr '/.:' ' ' | awk '{ printf("    %-35s '\''steam.protobufs.%s_pb2'\'',\n", "'\''" $$5 "'\'':", $$2) }' >> steam/core/msg/unified.py.tmp
	grep -A 99999 MARK_SERVICE_END steam/core/msg/unified.py >> steam/core/msg/unified.py.tmp
	mv steam/core/msg/unified.py.tmp steam/core/msg/unified.py

pb_update: pb_fetch pb_compile pb_services
