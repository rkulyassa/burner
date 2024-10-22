#!/bin/bash

if [ -z "$1" ]; then
  echo "No file supplied"
fi

input_file=$1

whisperx \
    --model large-v2 \
    --compute_type int8 \
    --output_format json \
    --suppress_numerals \
    --task transcribe \
    --language en \
    $input_file
