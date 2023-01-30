#!/bin/bash
env


REF=$1
FILE=$2
echo REF=${REF}
echo FILE=${FILE}
python3 /yml2image.py $REF $FILE | tee -a ${GITHUB_OUTPUT:-/dev/null}
