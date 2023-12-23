CODE_FOLDERS := hw_15
TEST_FOLDERS := tests

.PHONY: update test lint

install:
	poetry install --no-root

update:
	poetry lock
	poetry install --no-root

test:
	pytest $(TEST_FOLDER) --cov=$(CODE_FOLDERS)

format:
	poetry run black .

lint:
	poetry run black --check .
	poetry run flake8 $(CODE_FOLDERS) $(TEST_FOLDERS)
	poetry run pylint $(CODE_FOLDERS)
	poetry run mypy $(CODE_FOLDERS)