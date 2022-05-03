.PHONY: lint reset fmt run start-services stop-services run-tests run-component run-server-for-tests

lint:
	pipenv run flake8

fmt:
	pipenv run black . && pipenv run isort .

check-fmt:
	pipenv run black --check . && pipenv run isort --check-only --recursive .
