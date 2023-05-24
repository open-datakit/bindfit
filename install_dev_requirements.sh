#!/usr/bin/env bash
# Workaround for pip not supporting dependency-only installs from pyproject.toml
# See https://github.com/pypa/pip/issues/8049#issuecomment-788784066
rq -t <pyproject.toml | jq -r '.["project"]["optional-dependencies"]["development"][]' | xargs -d '\n' pip install
