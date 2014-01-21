import argparse
import json
import os
import sqlalchemy

from flask import Flask
from flask import Response


DB_STRING = 'sqlite:///test.db'

def host_sorted(host_list):
    return sorted(host_list, key=lambda x: int(x.split(".")[-1]))

def usage(host, stats, utype="cpu"):
    usage_val = int(float(stats["%s_usage" % utype]) / float(
            stats["%s_size" % utype]))
    return [usage_val for _ in range(int(stats["%s_size" % utype]))]

def current_node_info(hosts):
    ''' Query the database for the current info on nodes listed in hosts'''

    statement = "".join(["select host, data from usage where host in (",
            ",".join(["'%s'" % host for host in hosts]),
            ") group by host order by timestamp;"])

    engine = sqlalchemy.create_engine(DB_STRING)
    with engine.begin() as connection:
        results = connection.execute(statement)
        return [(host, json.loads(info)) for host, info in results]


def generate_df(disk, hosts):
    dfs = []
    for _, json_data in current_node_info(hosts):
        if "%s_df" % disk not in json_data:
            dfs.append([])
            continue
        dfs.append([json_data["%s_df" % disk]])
    return dfs


def generate_utilizations(hosts, cores, utype):
    usages = []
    for entry, json_data in current_node_info(hosts):
        node_usage = []
        if "vminfo" not in json_data:
            usages.append([])
            continue
        for stats in json_data["vminfo"]:
            my_usage = usage(entry, stats, utype=utype)
            node_usage += my_usage
        left_over = cores-len(node_usage)
        node_usage += [0.0 for _ in range(left_over)]
        usages.append(node_usage)
    return usages


def generate_matrices(hosts, cores):
    tenancies = []
    for entry, json_data in current_node_info(hosts):
        tenancy = 0
        node_tenancies = []
        node_usage = []
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


def get_usages(prefix, rack_start, rack_end, cores, utype):
    hosts = ["%s.%s" % (prefix, i) for i in range(rack_start, rack_end+1)]
    ten_use = generate_utilizations(hosts, cores, utype)
    return json.dumps(ten_use)


def rack_usages(prefix, rack_start, rack_end, cores, index):
    ten_use = generate_matrices(["%s.%s" % (prefix, i)
            for i in range(rack_start, rack_end+1)], cores)
    return json.dumps(ten_use[index])


app = Flask(__name__,static_folder="html", static_url_path="")


def resp(data):
    ''' Wrap data in flask Response and set mimetype to json'''
    return Response(data, mimetype='application/json')


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/cpu/<prefix>/<int:rack_start>/<int:rack_end>/<int:cores>')
def cpu(prefix, rack_start, rack_end, cores):
    return resp(get_usages(prefix, rack_start, rack_end, cores, "cpu"))


@app.route('/mem/<prefix>/<int:rack_start>/<int:rack_end>/<int:cores>')
def mem(prefix, rack_start, rack_end, cores):
    return resp(get_usages(prefix, rack_start, rack_end, cores, "mem"))


@app.route('/usage/<prefix>/<int:rack_start>/<int:rack_end>/<int:cores>')
def occupancy(prefix, rack_start, rack_end, cores):
    return resp(rack_usages(prefix, rack_start, rack_end, cores, 0))


@app.route('/df/<disk>/<prefix>/<int:rack_start>/<int:rack_end>')
def df(disk, prefix, rack_start, rack_end):
    return resp(json.dumps(generate_df(disk, ["%s.%s" % (prefix, i)
            for i in range(rack_start, rack_end+1)])))


@app.route('/nodes/<prefix>/<int:rack_start>/<int:rack_end>')
def nodes(prefix, rack_start, rack_end):
    hosts = ["%s.%s" % (prefix, i) for i in range(rack_start, rack_end+1)]
    return resp(json.dumps(host_sorted([entry for entry in os.listdir(".")
            if entry in hosts])))


def main():
    '''handle args and calls listen() '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=9001)
    parser.add_argument("--db", default='sqlite:///test.db')
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    global DB_STRING
    DB_STRING = args.db

    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
