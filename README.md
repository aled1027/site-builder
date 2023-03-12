# Site Builder

Builds a set of markdown files in a directory into a sqlite database. The common use of the database is serving the posts with [datasette](https://datasette.io).

## Usage

```
poetry install
poetry run python -m site_builder posts/ site.db
```

## Run tests

```
poetry run pytest
```
