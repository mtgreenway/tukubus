import os
import json
from flask import Flask
from flask import Response

def host_sorted(host_list):
    return sorted(host_list, key=lambda x: int(x.split(".")[-1]))

def usage(host, stats, utype="cpu"):
    usage_val = int(float(stats["%s_usage" % utype]) / float(stats["%s_size" % utype]))
    return [usage_val for _ in range(int(stats["%s_size" % utype]))]

def generate_df(disk, hosts):
    dfs = []
    for entry in host_sorted([i for i in os.listdir(".") if i in hosts]):
        with open(entry) as node:
           json_data = json.loads(node.read())
        if "%s_df" % disk not in json_data:
            dfs.append([])
            continue
        dfs.append([json_data["%s_df" % disk]])
    return dfs


def generate_utilizations(hosts, cores, utype):
    usages = []
    for entry in host_sorted([i for i in os.listdir(".") if i in hosts]):
        with open(entry) as node:
           json_data = json.loads(node.read())
        node_tenancies = []
        node_usage = []
        if "vminfo" not in json_data:
            usages.append([])
            continue
        for stats in json_data["vminfo"]:
            my_usage = usage(entry, stats, utype=utype)
            node_usage += my_usage                
        left_over = cores-len(node_usage)
        node_usage += [0.0 for i in range(left_over)]
        usages.append(node_usage)
    return usages


def generate_matrices(hosts, cores):
    tenancies = []
    for entry in host_sorted([i for i in os.listdir(".") if i in hosts]):
        with open(entry) as node:
           json_data = json.loads(node.read())
        tenancy = 0
        node_tenancies = []
        node_usage = []
        node_musage = []
        if "vminfo" not in json_data:
            tenancies.append([])
            continue
        for stats in json_data["vminfo"]:
            tenancy += 1
            my_usage = usage(entry, stats)
            node_usage += my_usage                
            node_tenancies += [tenancy for i in range(len(my_usage))]
        left_over = cores-len(node_usage)
        node_tenancies = [10 + (90.0 / tenancy) * (i) for i in node_tenancies]
        node_tenancies += [0 for i in range(left_over)]
        tenancies.append(node_tenancies)
    return [tenancies]


def get_usages(rack_start, rack_end, cores, utype):
    ten_use = generate_utilizations(["10.103.114.%s" % i for i in range(rack_start, rack_end+1)], cores, utype)
    return json.dumps(ten_use)


def rack_usages(rack_start, rack_end, cores, index):
    ten_use = generate_matrices(["10.103.114.%s" % i for i in range(rack_start, rack_end+1)], cores)
    #return "\n".join([",".join([str(ent) for ent in line]) for line in ten_use[index]])
    return json.dumps(ten_use[index])

#print rack_usages(40, 61, 32, 0)
#print rack_usages(40, 61, 32, 1)
#rack_usages(4, 39, 8, 0)
#rack_usages(4, 39, 8, 1)

app = Flask(__name__,static_folder="html", static_url_path="")

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/cpu/<int:rack_start>/<int:rack_end>/<int:cores>')
def cpu(rack_start, rack_end, cores):
    return Response(get_usages(rack_start, rack_end, cores, "cpu"), mimetype='application/json')

@app.route('/mem/<int:rack_start>/<int:rack_end>/<int:cores>')
def mem(rack_start, rack_end, cores):
    return Response(get_usages(rack_start, rack_end, cores, "mem"), mimetype='application/json')

@app.route('/usage/<int:rack_start>/<int:rack_end>/<int:cores>')
def occupancy(rack_start, rack_end, cores):
    return Response(rack_usages(rack_start, rack_end, cores, 0), mimetype='application/json')

@app.route('/df/<disk>/<int:rack_start>/<int:rack_end>')
def df(disk, rack_start, rack_end):
    return Response(json.dumps(generate_df(disk, ["10.103.114.%s" % i for i in range(rack_start, rack_end+1)])), mimetype='application/json')

@app.route('/nodes/<int:rack_start>/<int:rack_end>')
def nodes(rack_start, rack_end):
    hosts = ["10.103.114.%s" % i for i in range(rack_start, rack_end+1)]
    return Response(json.dumps(host_sorted([entry for entry in os.listdir(".") if entry in hosts])), mimetype='application/json')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001, debug=True)
