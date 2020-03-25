cd ${1}

zip -u ${1}.zip *.py

aws s3 cp ${1}.zip s3://${2} --profile ${3}

aws lambda update-function-code \
  --function-name ${1} \
  --s3-bucket ${2} \
  --s3-key ${1}.zip \
  --publish --profile ${3}
