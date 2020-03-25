#!/bin/bash

LAYER_DIR=${1}   # Where the contents of the Layer file reside
PYTHON_VER=${2}  # Which Python Version is being used 3.6/3.7 etc. its whats is in you venv
S3_BUCKET=${3}   # Name of the S3 bucket to cp the Layer file to, bucket must exist
AWS_PROFILE=${4} # Must exist somewhere e.g. ~/.aws/credentials and ~/.aws/config blank for Default

# Define LAYER_ZIP file, it is named after its directory
LAYER_ZIP="${LAYER_DIR}-layer.zip"
if [ ! -z ${LAYER_ZIP} ] ; then
    echo "${0}: Layer file is name defined as: ${LAYER_ZIP}"
else
    exit -1
fi

cd ${LAYER_DIR}
if [ $(basename `pwd`) = ${LAYER_DIR} ] ; then
    echo "${0}: Changed to Directory: ${LAYER_DIR}"
else
    exit -1
fi

# Delete LAYER_ZIP if it exists
if [ -f ${LAYER_ZIP} ] ; then
    rm ${LAYER_ZIP}
fi

# Delete the python directory if it exists
if [ -d python ] ; then
    rm -rf python
fi

mkdir python # This is the directory name that aws layers expects 
if [ -d python ] ; then
    echo "${0}: Created directory: python"
else
    exit -1
fi

# Copy everything that needs to be in the LAYER_FILE to the python directory
cp -r venv/lib/python${PYTHON_VER}/site-packages/* python 2>/dev/null
cp -r venv/lib64/python${PYTHON_VER}/site-packages/* python 2>/dev/null
cp -r venv/*.py python 2>/dev/null
cp -r venv/*.txt python 2>/dev/null

# Zip python directory into LAYER
zip -q -r ${LAYER_ZIP} ./python
if [ -f ${LAYER_ZIP} ] ; then
    echo "${0}: Created Layer File: ${LAYER_ZIP}"
else
    exit -1
fi

# If an AWS_PROFILE was defined - modifier for the aws s3 command
if [ ! -z ${AWS_PROFILE} ] ; then
    CMD_PROFILE=${AWS_PROFILE}
    echo "${0}: Using AWS Profile: ${AWS_PROFILE}"
else
    CMD_PROFILE="default"
    echo "${0}: Using AWS Profile: default"
fi

# Copy LAYER_ZIP to S3_BUCKET using CMD_PROFILE (if defined) 
aws s3 cp ${LAYER_ZIP} s3://${S3_BUCKET} --profile ${CMD_PROFILE} --output text
EXIT_STATUS=$?

if [ ${EXIT_STATUS} -eq 0 ] ; then
    echo "${0}: ${LAYER_ZIP} successfully copied to s3://${S3_BUCKET} using profile: ${CMD_PROFILE}"
else
    echo "${0}: ${LAYER_ZIP} failed to copy to s3://${S3_BUCKET} using profile: ${CMD_PROFILE}"
    echo "${0}: aws s3 cp exit status: ${EXIT_STATUS}"
fi
