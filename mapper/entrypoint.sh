#!/bin/bash
env | sort
python3 /yml2image.py $INPUT_REF $INPUT_MAPFILE | tee -a ${GITHUB_OUTPUT:-/dev/null}
