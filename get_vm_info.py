#!/usr/bin/env python

import subprocess
import socket
import json
import time
import argparse

def get_vm_info(host, port):
    pgrep = subprocess.Popen("pgrep -f /usr/bin/kvm", shell=True, stdout=subprocess.PIPE)
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
    
    top = subprocess.Popen("top -p %s -b -n 1" % ",".join(procs), shell=True, stdout=subprocess.PIPE)
    top_output = top.stdout.readlines()
    if len(top_output) < 5:
        exit(1)
    
    cpu_per = {}
    mem_per = {}
    for i in procs:
        cpu_per[i] = 0.0
        mem_per[i] = 0.0
    for line in top_output[6:-1]:
        info = line.split()
        if info[0] in procs:
            cpu_per[info[0]] += float(info[8])
            mem_per[info[0]] += float(info[9])
    
    new_vm_info = []
    for d in vm_info:
        d["cpu_usage"] = cpu_per[d["pid"]]
        d["mem_usage"] = mem_per[d["pid"]]
        new_vm_info.append(d)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(new_vm_info), (host, port))


def main():
    while True:
        get_vm_info("10.103.114.1", 7777)
        time.sleep(2)
   
    
if __name__ == "__main__":
    main()
