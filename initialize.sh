#!/bin/bash

DEFAULT_ENVFILE="$(dirname $0)/defaults.env"
ENVFILE=${ENVFILE:-"$DEFAULT_ENVFILE"}

source $ENVFILE

if [ ! "$(docker ps -q -f name=bbf-gui-apis)" ]
then
    docker-compose up -d --build
else
    docker-compose up -d 
fi


if [ -d "$WORKING_DIR/blockchain-benchmarking-framework" ] 
then
    echo "Directory $WORKING_DIR/blockchain-benchmarking-framework exists."
	echo "Requesting any updates..."
    if [ -z "$(ls -A $WORKING_DIR/blockchain-benchmarking-framework )" ]; then
        git clone "https://github.com/UNIC-IFF/blockchain-benchmarking-framework.git" 
        git -C $WORKING_DIR/blockchain-benchmarking-framework submodule update --init --recursive
        pip install -r  $WORKING_DIR/blockchain-benchmarking-framework/networks/xrpl/xrpl-unl-manager/requirements.txt
        npm --prefix   $WORKING_DIR/blockchain-benchmarking-framework/networks/xrpl/xrpl_traffic_generator install

    else
        git -C $WORKING_DIR/blockchain-benchmarking-framework submodule update
    fi
	
else
    echo "Error: Directory $WORKING_DIR/blockchain-benchmarking-framework does not exists."
        git clone "https://github.com/UNIC-IFF/blockchain-benchmarking-framework.git"
        git -C $WORKING_DIR/blockchain-benchmarking-framework submodule update --init --recursive
fi

echo "Creating pipe if not exist"
pipe=bbf-commands

if [[ ! -p "$WORKING_DIR/blockchain-benchmarking-framework/$pipe" ]]; then
    mkfifo $WORKING_DIR/blockchain-benchmarking-framework/$pipe
	echo "Pipe created"
else
    echo "Pipe already exists"
fi


echo "Wait until npm install is finished and gulp runs the web application"
while true; do 
    eval "$(cat $WORKING_DIR/blockchain-benchmarking-framework/$pipe) &> $WORKING_DIR/output.txt" 
    
     
done &






