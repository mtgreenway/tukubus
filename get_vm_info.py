#!/usr/bin/env python

import subprocess
import socket
import json
import time
import argparse

def get_vm_info(host, port):
    pgrep = subprocess.Popen("pgrep -f /usr/bin/kvm", shell=True,
            stdout=subprocess.PIPE)
    procs = [proc.strip("\n") for proc in pgrep.stdout.readlines()]

    vm_info = []

    for proc in procs:

        cmdlf = open("/proc/%s/cmdline" % proc)
        cmdline = cmdlf.read()
        cmdlf.close()

        uuid_pos = cmdline.find("uuid")
        instance_id = cmdline[uuid_pos + 5: uuid_pos + 39]
        args = cmdline.split(',')
        if len(args) < 2:
            continue

        cores = args[1].split("=")[1]
        mem = cmdline[40:].split('-')[0][1:-1]

        vm_info.append({
            "pid": proc,
            "id": instance_id,
            "mem_size": mem,
            "cpu_size": cores
        })

    cpu_per = {}
    mem_per = {}
    for i in procs:
        cpu_per[i] = 0.0
        mem_per[i] = 0.0

    for proc_section in [procs[i: min(i + 19, len(procs))] for i in range(0, len(procs), 20)]:

        top = subprocess.Popen("top -p %s -b -n 1" % ",".join(proc_section),
                shell=True, stdout=subprocess.PIPE)
        top_output = top.stdout.readlines()
        if len(top_output) < 5:
            continue

        for line in top_output[6:-1]:
            info = line.split()
            if info[0] in proc_section:
                cpu_per[info[0]] += float(info[8])
                mem_per[info[0]] += float(info[9])

    new_vm_info = []
    for instance in vm_info:
        instance["cpu_usage"] = cpu_per.get(instance["pid"], 0)
        instance["mem_usage"] = mem_per.get(instance["pid"], 0)
        new_vm_info.append(instance)

    try:
        df_proc = subprocess.Popen("df /", shell=True, stdout=subprocess.PIPE)
        root_df = df_proc.stdout.readlines()[1].split()[4][:-1]
        df_proc = subprocess.Popen("df /exports/gluster", shell=True,
                stdout=subprocess.PIPE)
        gluster_df = df_proc.stdout.readlines()[1].split()[4][:-1]
    except:
        root_df = -1
        gluster_df = -1

    stats = {
        "vminfo": new_vm_info,
        "root_df": root_df,
        "gluster_df": gluster_df
        }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(stats), (host, port))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="10.103.114.1")
    parser.add_argument("--port", default=7777)
    parser.add_argument("--interval", default=2)
    args = parser.parse_args()

    while True:
        get_vm_info(args.host, args.port)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
