#!/bin/bash
set -eux
set -o pipefail

pip install -UI .
pip uninstall requests==2.10 -y
pip install -Iv requests==2.9.1

