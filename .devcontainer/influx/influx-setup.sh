#!/bin/sh
set -e

echo "Running initial setup"

influx write -b main -o zatan -f /example-data.csv -t ',' \
    --header '#constant measurement,ExposedTemp' \
    --header '#datatype ignore,ignore,time,ignore,ignore,field,ignore'
