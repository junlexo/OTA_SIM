for i in "$@"
do
case $i in
    -ICCID=*)
    ICCID="${i#*=}"
    shift
    ;;
esac
done

echo "Request device certificate with ICCID=${ICCID}"

RESPONSE=$(curl -H 'Content-Type: application/json' -H 'GATEWAY_TOKEN: 2hj745jdZ$lK^6ltr23YTs' -X POST -d "{\"ICCID\": \"${ICCID}\", \"api_key\": \"asGk4SlfdsEKt53@w\"}" http://18.136.9.47:8080/api/gateway/dev-singtel-jitr-registrar)
CERTIFICATE_URL=$(echo $RESPONSE | jq '.crt' -r)
PRIVATE_KEY_URL=$(echo $RESPONSE | jq '.key' -r)
MQTT_ENDPOINT=$(echo $RESPONSE | jq '.endpoint' -r)
MQTT_TOPIC=$(echo $RESPONSE | jq '.topic' -r)
MQTT_PORT=$(echo $RESPONSE | jq '.port' -r)

echo "$(curl $CERTIFICATE_URL)" > device.crt
echo "$(curl $PRIVATE_KEY_URL)" > device.key

echo "Certificate URL      : $CERTIFICATE_URL"
echo "Private key URL      : $PRIVATE_KEY_URL"
echo "Device certificate   : saved to file device.crt"
echo "Device private key   : saved to file device.key"
echo "MQTT Endpoint        : $MQTT_ENDPOINT"
echo "MQTT Port            : $MQTT_PORT"
echo "MQTT Topic           : $MQTT_TOPIC"

cat device.crt CACertificate.pem > deviceAndCACert.crt
echo "Combining device and CA certificate into file: deviceAndCACert.crt"
