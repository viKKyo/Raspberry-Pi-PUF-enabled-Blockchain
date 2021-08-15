#! /bin/bash

curl --location --request POST '192.168.100.101:5000/nodes/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "nodes": ["192.168.100.101"]
}'

sleep 1

curl --location --request POST '192.168.100.101:5000/nodes/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "nodes": ["192.168.100.102"]
}'

sleep 1

curl --location --request POST '192.168.100.101:5000/nodes/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "nodes": ["192.168.100.103"]
}'

sleep 1

curl --location --request POST '192.168.100.101:5000/nodes/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "nodes": ["192.168.100.104"]
}'

