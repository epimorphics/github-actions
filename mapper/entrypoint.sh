#!/bin/bash
# env | sort
python3 /yml2image.py $GITHUB_REF $INPUT_MAPFILE | tee -a ${GITHUB_OUTPUT:-/dev/null}
