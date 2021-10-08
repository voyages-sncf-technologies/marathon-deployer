# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [3.0.1] - 2021-10-08
### Added
- `--force-restart` argument for `marathon-deploy --put`
- if `$INITIAL_SLEEP_DURATION` is set, `marathon-check` will sleep this duration instead of the default 20s

## [3.0.0] - 2019-10-20
### Added
- command `marathon-check`
- CLI args: `--user`, `--password`,  `--https-verify`
- Travis CI with `pylint` & this `CHANGELOG.md`

### Changed
- rename command `deploy` io `deploy-marathon`
- rename main package `deploytool` to `marathon_deploy`
