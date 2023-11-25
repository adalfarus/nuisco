# {{project_name}} (ppt) Guide
[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)
[![Build Status](https://github.com/[github_name]/{{project_name}}/actions/workflows/python-publish.yml/badge.svg)](https://github.com/[github_name]/{{project_name}}/actions)
[![License: GPL-3.0](https://img.shields.io/github/license/[github_name]/{{project_name}})](https://github.com/[github_name]/{{project_name}}/blob/main/LICENSE)

Welcome to {{project_name}}, this is the dev version of ppt. The content is ordered by sections in markdown.

{{welcome_message}}

## Compiler
We'll be using [NUISCO](https://github.com/adalfarus/nuisco) as our compiler. The specific command for now is `nuisco build --extra-args=select-dll urllib3-module hmac-module email-module`

## Packer
[ISS](https://jrsoftware.org/isinfo.php) will be used as our packer in windows. Please just download and install it and run the pre-configured .iss file from the repo.

## Database
The database interactions will be handeled by aplustools's sqlite3 DBManager class.

## Gui
We'll use PySide6 together with QSS for a clean interface.
