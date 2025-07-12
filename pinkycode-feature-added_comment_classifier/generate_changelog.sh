#!/bin/bash

# Генерация CHANGELOG с помощью git-cliff
git cliff --config cliff.toml --output CHANGELOG.md

# Добавление CHANGELOG.md в коммит
git add CHANGELOG.md
git commit -m "chore: update CHANGELOG.md [skip ci]"