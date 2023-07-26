#!/bin/bash

mydir=$(dirname $(readlink -f $0))

PYTHONPATH=${mydir}/../python python3 -m replace_key $@

