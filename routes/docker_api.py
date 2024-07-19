import json
import re
import docker
from flask import   Blueprint, jsonify
import datetime
import pandas as pd


GETH_API = Blueprint('docker_api', __name__)
BLOCKCHAINS= ['geth', 'xrpl', 'besu-poa', 'stellar-docker-testnet']

Active_Networks=set()
def remove_network(network):
    get_running_networks()
    try:
        Active_Networks.remove(network)
    except:
        return True


def normalize(dictionary): # transforms docker output to dict
    for key, value in dictionary.items():
        if isinstance(value, dict):
            normalize(value)

        item_dict = dict()
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "op" in item:
                    item_dict.update({item.pop("op"): item})
        if item_dict:
            dictionary[key] = item_dict

    return dictionary


def get_blueprint():
    """Return the blueprint for the main app module"""
    return GETH_API



@GETH_API.route("/docker/management/running_networks", methods=['GET'])
def get_running_networks():
    """Return the available networks"""
    import os 
    #print(os.system("docker stats $(docker ps -q)"))
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    c=client.containers.list(all=True)
    a=[container.name for container in c]  
    if ([i for i in a if i.startswith('xrpl-v')]):
        Active_Networks.add("xrpl") 
    if ([i for i in a if i.startswith('geth')]):
        Active_Networks.add("geth") 
    if ([i for i in a if i.startswith('besu')]):
        Active_Networks.add("besu-poa") 
    if ([i for i in a if i.startswith('stellar')]):
        Active_Networks.add("stellar")
    return json.dumps(list(Active_Networks))


@GETH_API.route("/docker/management/is_monitoring_configured", methods=['GET'])
def is_monitoring_configured():
    """Return the available networks"""
    #print(os.system("docker stats $(docker ps -q)"))
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    c=client.containers.list(all=True)
    a=[container.name for container in c]
    if "containers_logs_ui" in a and "prometheus" in a and "alertmanager" in a and "dc_stats_exp" in a and "statsdgraphite" in a and \
     "pushgateway" in a and "grafana" in a:
        print(a)
        return json.dumps("True")      
    print(a)
    return json.dumps("False")


@GETH_API.route('/docker/management/stats', methods=['GET'])
#begin with this action for the framework
def docker_stats():
   container_Stats=[]
   client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
   c=client.containers.list()
   #for container in c:
   # container_Stats.append(container.stats(decode=False,stream=False))
   c2=[]
   for j in c:
        for i in BLOCKCHAINS:
            if j.name.startswith(i):
                c2.append(j)
   stats= {str(c1.name): c1.stats(decode=False, stream=False) for c1 in c2}
   stats = normalize(stats)
   print(stats)
   for i in stats.values():
     if "manager" not in i['name']:
      # --------------------------- CPU STATS ----------------------------
      UsageDelta = i['cpu_stats']['cpu_usage']['total_usage'] - i['precpu_stats']['cpu_usage']['total_usage']
      SystemDelta= i['cpu_stats']['system_cpu_usage'] - i['precpu_stats']['system_cpu_usage']
      try:
        len_cpu = len(i['cpu_stats']['cpu_usage']['percpu_usage'])
      except:
        len_cpu=2
      percent = round((UsageDelta / SystemDelta) * len_cpu * 100,3)

      # --------------------------- Memory STATS -------------------------

      try:
        memory_usage = i["memory_stats"]["usage"] - i["memory_stats"]["stats"]["cache"]
      except:
        memory_usage = i["memory_stats"]["usage"]
      limit = i["memory_stats"]["limit"]
      memory_utilization = round(memory_usage/limit * 100, 3)
     #--------------------------- UpTime ----------------------------------
      date= (pd.to_datetime(datetime.datetime.now(datetime.timezone.utc))-pd.to_datetime(i['read']))
      container_Stats.append({"Container_name":i['name'][1:], "Network_Stats":i['networks'], "memory_usage_percentage":memory_utilization, "CPU_ucsage_percent":percent, "Uptime":str(date)})
     else:
            continue

   return jsonify(sorted(container_Stats, key=lambda d: d['Container_name']))



@GETH_API.route('/docker/management/list', methods=['GET'])
#returns the container list information
def docker_list():
   client = docker.from_env()
   container_dict=[]
   for container in client.containers.list():
        container_dict.append({"Container_name": container.name[1:],"Container_ID":container.short_id,"Container_status": container.status,"Container_image":re.search(r"\'(.*?)\'",str(container.image)).group(1) })
   return jsonify(container_dict)


@GETH_API.route('/docker/management/graph/<string:network>', methods=['GET'])
#returns the container list information
def graph(network):
   client = docker.from_env()
   container_dict=[]
   c=client.containers.list()
   net=BLOCKCHAINS.index(network)
   a=[container.name for container in c]
   for i in a:
        if i.startswith(BLOCKCHAINS[net]):
            container_dict.append( i)
   return json.dumps(container_dict)


def docker_logs():
   client = docker.from_env()
   container_logs={}
   for container in client.containers.list():
    a =pd.DataFrame(container.logs(timestamps=False,tail=40).decode("utf8").splitlines(), index=None, columns=None)
    container_logs[container.name[1:]]= a.to_html(header=False,index=False, table_id="table-logs", classes="table-striped table-dark table-responsive w-100 d-block d-md-table")
   return  container_logs


