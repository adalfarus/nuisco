#!/bin/bash

function setup() {
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

function test() {
    pytest
}

function lint() {
    flake8 src tests
}

# Call functions based on passed argument
$@
