.PHONY: clean-pyc

build: clean-pyc
	docker-compose build bili-jeans-build

run: build clean-container
	docker-compose up -d bili-jeans-run

ssh:
	docker-compose exec bili-jeans-run /bin/sh

lint:
	python -m flake8 bili_jeans/ tests/

lintd: build clean-container
	docker-compose up --exit-code-from bili-jeans-lint bili-jeans-lint

type-hint:
	python -m mypy bili_jeans/

type-hintd: build clean-container
	docker-compose up --exit-code-from bili-jeans-type-hint bili-jeans-type-hint

test:
	python -m pytest -sv --disable-warnings -p no:cacheprovider tests

testd: build clean-container
	docker-compose up --exit-code-from bili-jeans-test bili-jeans-test

clean-pyc:
	# clean all pyc files
	find . -name '__pycache__' | xargs rm -rf | cat
	find . -name '*.pyc' | xargs rm -f | cat

clean-container:
	# stop and remove useless containers
	docker-compose down --remove-orphans
