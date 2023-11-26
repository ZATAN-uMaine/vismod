#!/bin/sh
set -e

echo "Running ZATAN initial setup script"

influx write -b main -f /example-data.csv
