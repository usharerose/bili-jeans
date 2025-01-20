.PHONY: clean-pyc

build: clean-pyc
	docker-compose build bili-jeans-build

run: build clean-container
	docker-compose up -d bili-jeans-run

ssh:
	docker-compose exec bili-jeans-run /bin/sh

clean-pyc:
	# clean all pyc files
	find . -name '__pycache__' | xargs rm -rf | cat
	find . -name '*.pyc' | xargs rm -f | cat

clean-container:
	# stop and remove useless containers
	docker-compose down --remove-orphans
