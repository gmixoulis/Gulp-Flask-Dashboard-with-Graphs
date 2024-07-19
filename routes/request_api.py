"""The Endpoints to manage the Geth Actions"""
import os
import json
from routes.docker_api import  remove_network, get_running_networks
from flask import  abort, Blueprint, jsonify
from  difflib import get_close_matches as gcm
from readerwriterlock import rwlock
import time
import fnmatch

NUM_OF_NODES=5
PATH="blockchain-benchmarking-framework/control.sh "
GETH_API = Blueprint('traffic_api', __name__)
BLOCKCHAINS= ['geth', 'xrpl', 'besu-poa', 'stellar-docker-testnet']
INIT_PATH="blockchain-benchmarking-framework/"
OUTPUT_FILE="../output.txt"
Time2W=1


def control_command(PATH,network, command, OUTPUT_FILE, Time2W): #
    # send command to hostpipe
    fi= os.open("../blockchain-benchmarking-framework/bbf-commands", os.O_WRONLY)
    
    lock= rwlock.RWLockFairD()
    lock_w=lock.gen_wlock()
    if lock_w.acquire():
        try:
            os.write(fi,f'{PATH} {network} {command}'.encode())
            #os.write(fi," && ls".encode())
            os.close(fi)
        finally:
            lock_w.release()
    while True:
        if os.path.exists(OUTPUT_FILE):
        
                file1 = os.stat(OUTPUT_FILE) # initial file size
                file1_size = file1.st_size
                time.sleep(Time2W)
                file2 = os.stat(OUTPUT_FILE) # updated file size
                file2_size = file2.st_size
                comp = file2_size - file1_size # compares sizes
                if comp == 0:
                    with open(OUTPUT_FILE, 'r') as file:
                        out=file.read().splitlines()
                       
                    break

                else:
                    time.sleep(Time2W)
        else:
            time.sleep(2)
    return out



def get_blueprint():
    """Return the blueprint for the main app module"""
    return GETH_API

def compile_network_name(network):
    """Returns the correct folder name for the benchmarking framework"""
    return gcm(network, BLOCKCHAINS)[0]


@GETH_API.route('/request/<string:network>/path', methods=['GET'])
def path_exists(network):
    dir_path = f'../blockchain-benchmarking-framework/networks/{network}/configfiles/'
    count=5

    if not os.path.exists(f'../blockchain-benchmarking-framework/networks/{network}/docker-compose-testnet.yaml'):
        return json.dumps("NOT CONFIGURED")        
    else:
        dictData = json.loads(get_running_networks())
        print(dictData)
        print(s for s in dictData)
        if any(s for s in dictData):
            if network == "xrpl":
                count = len(fnmatch.filter(os.listdir(dir_path), f'{network}*')) - 1
            print("Started", count)
            return json.dumps(f"Started, {count}")
        else:
            if network == "xrpl":
                count = len(fnmatch.filter(os.listdir(dir_path), f'{network}*'))-1        
            print(os.system("docker stats $(docker ps -q"))
            return json.dumps(f"Configured, {count}")


@GETH_API.route('/request/<string:network>/status', methods=['GET'])
def get_status(network):
    """Return all book requests
    @return: 200: an array of all Nodes and ports as\
    flask/response object with application/json mimetype.
    """
    
    network=compile_network_name(network)
    if network not in BLOCKCHAINS:
         abort(404)
    st=control_command(PATH,network,'status', OUTPUT_FILE, Time2W)
    s=[]
    for i in range(3, len(st)-1):
        s.append(st[i])
    return json.dumps(s)

@GETH_API.route('/request/<string:network>/start/<int:NUM_OF_NODES>', methods=['GET'])
def post_start(network, NUM_OF_NODES):
    """Return all book requests
    @return: 200: an array of all Start logs as a \
    flask/response object with application/json mimetype.
    """
    Time2W=5
    NUM_OF_NODES= abs(NUM_OF_NODES)
    network=compile_network_name(network)
    if network not in BLOCKCHAINS:
         abort(404)
    print(f'Start {NUM_OF_NODES} Nodes') #later we will let the user from the interface to choose this number 
    return jsonify(control_command(PATH,network,f'start -n {NUM_OF_NODES}',OUTPUT_FILE,Time2W))


@GETH_API.route('/request/<string:network>/clean', methods=['GET'])
def clean(network):
    """Return all book requests
    @return: 200: an array of all Start logs as a \
    flask/response object with application/json mimetype.
    """
    network=compile_network_name(network)
    if network not in BLOCKCHAINS:
         abort(404)
    print('CLEAN') #later we will let the user from the interface to choose this number 
    return jsonify(control_command(PATH,network,'clean',OUTPUT_FILE,Time2W))

@GETH_API.route('/request/<string:network>/configure/<int:NUM_OF_NODES>', methods=['POST'])
def put_configure(network, NUM_OF_NODES):
    """Return all book requests
    @return: 200: an array of all Configure logs as a \
    flask/response object with application/json mimetype.
    """
    Time2W=3
    NUM_OF_NODES= abs(NUM_OF_NODES)
    network=compile_network_name(network)
    if network not in BLOCKCHAINS:
         abort(404)
    if network == "besu-poa":
            NUM_OF_NODES_BN= 1
            return jsonify(control_command(PATH,network,f'configure -bn {NUM_OF_NODES_BN} -vn {NUM_OF_NODES}',OUTPUT_FILE,Time2W)) 
    return jsonify(control_command(PATH,network,f'configure -n {NUM_OF_NODES}', OUTPUT_FILE,Time2W))


@GETH_API.route('/request/<string:network>/configure/<int:NUM_OF_NODES_BN>/<int:NUM_OF_NODES_VN>', methods=['POST'])
def put_configure_besu(network, NUM_OF_NODES_BN, NUM_OF_NODES_VN):
    """Return all book requests
    @return: 200: an array of all Configure logs as a \
    flask/response object with application/json mimetype.
    """
    NUM_OF_NODES_BN= abs(NUM_OF_NODES_BN)
    NUM_OF_NODES_VN=abs(NUM_OF_NODES_VN)
    network=compile_network_name(network)
    if network not in BLOCKCHAINS:
         abort(404)
    return jsonify(control_command(PATH,network,f'configure -bn {NUM_OF_NODES_BN} -vn {NUM_OF_NODES_VN}',OUTPUT_FILE,Time2W))

@GETH_API.route('/request/<string:network>/stop', methods=['GET'])
def stop(network):
    """ Stop the Nodes and network    """
    
    network=compile_network_name(network)
    if network not in BLOCKCHAINS:
         abort(404)
    print('stop nodes', network) #later we will let the user from the interface to choose this number with configure
    remove_network(str(network))
    return json.dumps(control_command(PATH,network,'stop',OUTPUT_FILE,Time2W))


@GETH_API.route('/request/list', methods=['GET'])
#begin with this action for the framework
def show_list(): 
    INIT_PATH="blockchain-benchmarking-framework/control.sh -list "
    return json.dumps(control_command(INIT_PATH,"",'',OUTPUT_FILE,Time2W))