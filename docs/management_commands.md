# Management commands

In this section, we will introduce Pixel's management commands. All commands are
supposed to be run from the repository's root path with an appropriate user
(_i.e._ with permissions to run Django management commands).

## Running management commands

### Development

While in local development, you can run a management command thanks to the
`bin/manage` script:

```bash
# Usage
$ bin/manage [COMMAND]

# An example with the migrate command
$ bin/manage migrate data
```

### Staging / Production

In staging or production, you should execute commands in the `web` container via
`docker-compose exec`.

```bash
# Staging
$ docker-compose -p pixel-staging exec web pipenv run python ./manage.py [COMMAND]
# An example with the migrate command
$ docker-compose -p pixel-staging exec web pipenv run python ./manage.py migrate data

# Production
$ docker-compose -p pixel-production exec web pipenv run python ./manage.py [COMMAND]
# An example with the migrate command
$ docker-compose -p pixel-production exec web pipenv run python ./manage.py migrate data
```

## Initial data

In order to submit new datasets to Pixel, you will need to import initial data
first via:

* development: the `make bootstrap` command will do the hard work for you, but
  you still can import initial data via:

```bash
$ bin/manage loaddata apps/data/fixtures/initial_data.json
$ bin/manage loaddata apps/core/fixtures/initial_data.json
```

* staging:

```bash
$ docker-compose -p pixel-staging exec web pipenv run python ./manage.py loaddata apps/data/fixtures/initial_data.json
$ docker-compose -p pixel-staging exec web pipenv run python ./manage.py loaddata apps/core/fixtures/initial_data.json
```

* production:

```bash
$ docker-compose -p pixel-production exec web pipenv run python ./manage.py loaddata apps/data/fixtures/initial_data.json
$ docker-compose -p pixel-production exec web pipenv run python ./manage.py loaddata apps/core/fixtures/initial_data.json
```

## `load_entries`

The `data` Django application adds the `load_entries` management command. This
command is meant to be used as a loader for repository entries. This command
takes a file as required argument and the `--database` option must also be
specified (to determine how to read the given file):

* `--database CGD`: load chromosome features from a
  [CGD](http://www.candidagenome.org) tab file (see [this example
  file](http://www.candidagenome.org/download/chromosomal_feature_files/C_glabrata_CBS138/C_glabrata_CBS138_current_chromosomal_feature.tab))
* `--database SGD`: load chromosome features from a
  [SGD](https://www.yeastgenome.org/) tab file (see [this example
  file](https://downloads.yeastgenome.org/curation/chromosomal_feature/SGD_features.tab))

### Example

In the following example, we will run the `load_entries` management command
while logged in the `web` container to avoid using Docker `volumes` or `copy` to
download and import a tab file from the internet.

```bash
# We are logged in Pixel's staging server
$ cd pixel/staging

# Run a bash in the web container
$ docker-compose -p pixel-staging exec web bash

# /!\ we are now logged in the container
# Download chromosome features file
app@container:~/pixel$ wget http://www.candidagenome.org/download/chromosomal_feature_files/C_glabrata_CBS138/C_glabrata_CBS138_current_chromosomal_feature.tab -O /tmp/cgd_features.tab
# Load entries from downloaded file
app@container:~/pixel$ pipenv run python ./manage.py load_entries --database CGD /tmp/cgd_features.tab
```
