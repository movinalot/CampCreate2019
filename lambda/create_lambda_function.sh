#REST_API_NAME=${1}
#REST_API_PATH=${2}
#REST_API_METHOD=${3}

JQ_CMD='.Role.Arn'
LAMBDA_ROLE=$(aws iam get-role --role-name AWSLambdaBasicExecutionRole | jq -r "${JQ_CMD}")
echo ${LAMBDA_ROLE}

#JQ_CMD='.items[] | select(.name == "'${REST_API_NAME}'") | .id'
#REST_API_ID=$(aws apigateway get-rest-apis | jq -r "${JQ_CMD}")
#echo ${REST_API_ID}

#JQ_CMD='.items[] | select(.path == "'${REST_API_PATH}'") | .id'
#REST_API_RESOURCES_ID=$(aws apigateway get-resources --rest-api-id ${REST_API_ID} | jq -r "${JQ_CMD}")
#echo ${REST_API_RESOURCES_ID}

#aws apigateway get-method --rest-api-id ${REST_API_ID} --resource-id ${REST_API_RESOURCES_ID} --http-method ${REST_API_METHOD} | \
#jq -r '.methodIntegration.uri'

aws lambda create-function \
  --function-name "devnet-create" \
  --runtime "python3.7" \
  --handler "devnet_skill.lambda_handler" \
  --timeout 30 \
  --role ${LAMBDA_ROLE} \
  --code S3Bucket="campcreate",S3Key="campcreate-lf.zip" \
  --environment Variables="{UCS_HOST=0.0.0.0, UCS_USER=admin}" \
  --environment Variables="{SSH_HOST=0.0.0.0, SSH_USER=admin}"


#aws lambda update-function-code \
#  --function-name ${1} \
#  --s3-bucket ${2} \
#  --s3-key ${1}.zip \
#  --publish --profile ${3}