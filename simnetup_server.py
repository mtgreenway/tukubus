import os
import json
from flask import Flask
from flask import Response

def usage(host, stats):
    usage_val = float(stats["cpu_usage"]) / float(stats["cpu_size"])
    return [usage_val for _ in range(int(stats["cpu_size"]))]


def generate_matrices(hosts, cores):
    usages, tenancies = [], []
    for entry in os.listdir("."):
        if entry in hosts:
            print entry
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
            node_tenancies = [10 + (90.0 / tenancy) * (i) for i in node_tenancies]
            node_tenancies += [0 for i in range(left_over)]
            usages.append(node_usage)
            tenancies.append(node_tenancies)
    return tenancies, usages


def rack_usages(rack_start, rack_end, cores, index):
    ten_use = generate_matrices(["10.103.114.%s" % i for i in range(rack_start, rack_end)], cores)
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
    return Response(rack_usages(rack_start, rack_end, cores, 1), mimetype='application/json')

@app.route('/usage/<int:rack_start>/<int:rack_end>/<int:cores>')
def occupancy(rack_start, rack_end, cores):
    return Response(rack_usages(rack_start, rack_end, cores, 0), mimetype='application/json')

@app.route('/nodes/<int:rack_start>/<int:rack_end>')
def nodes(rack_start, rack_end):
    hosts = ["10.103.114.%s" % i for i in range(rack_start, rack_end)]
    return Response(json.dumps([entry for entry in os.listdir(".") if entry in hosts]), mimetype='application/json')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001, debug=True)
