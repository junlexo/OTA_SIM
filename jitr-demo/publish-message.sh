#!/bin/bash

TEMPERATURE=$((10 + (($RANDOM % 400) / 10)))
HUMIDITY=$((($RANDOM % 1000) / 10))
echo "$TEMPERATURE"
echo "$HUMIDITY"
mosquitto_pub --cafile ./root.cert --cert ./deviceAndCACert.crt --key ./device.key -h a1zmup1beu3ree.iot.ap-southeast-1.amazonaws.com -p 8883 -q 1 -t '$aws/things/singtel-starter-kit/shadow/update' -m "{\"ICCID\":\"77777777777777777777\", \"temperature\": ${TEMPERATURE}, \"humidity\": ${HUMIDITY}}" -d
