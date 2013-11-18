import os
import json

def usage(host, stats):
    usage_val = float(stats["cpu_usage"]) / float(stats["cpu_size"])
    return [usage_val for _ in range(int(stats["cpu_size"]))]


def generate_matrices(hosts, cores):
    usages, tenancies = [], []
    for entry in os.listdir("."):
        if entry in hosts:
            with open(entry) as node:
               json_data = json.loads(node.read())
            tenancy = 0
            node_tenancies = []
            node_usage = []
            for stats in json_data:
                tenancy += 1
                my_usage = usage(entry, stats)
                node_usage += my_usage                
                node_tenancies += [tenancy for i in range(len(my_usage))]
            left_over = cores-len(node_usage)
            node_usage += [0.0 for i in range(left_over)]
            node_tenancies += [0 for i in range(left_over)]
            usages.append(node_usage)
            tenancies.append(node_tenancies)
    return tenancies, usages


def rack_usages(rack_start, rack_end, cores, index):
    ten_use = generate_matrices(["10.103.114.%s" % i for i in range(rack_start, rack_end)], cores)
    return "\n".join([",".join([str(ent) for ent in line]) for line in ten_use[index]])

#print rack_usages(40, 61, 32, 0)
#print rack_usages(40, 61, 32, 1)
#rack_usages(4, 39, 8, 0)
#rack_usages(4, 39, 8, 1)

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return rack_usages(40, 61, 32, 1)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001)
