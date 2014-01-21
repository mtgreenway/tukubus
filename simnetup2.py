#!/usr/bin/env python

#  Copyright 2014 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
''' simnetup status listener '''


import argparse
import socket
import sqlalchemy
import time

from multiprocessing import Process

def compact(db_string, sleep, wiggle):
    '''process that compacts the database down to a few entries per hour
    every hour '''
    while True:
        time.sleep(sleep)
        timestamp = time.time()
        stmnt = 'DELETE from usage where timestamp < %s and timestamp > %s' % (
                timestamp - wiggle, (timestamp - sleep) + wiggle)
        engine = sqlalchemy.create_engine(db_string)
        with engine.begin() as connection:
            connection.execute(stmnt)


def listen(host, port, db_string):
    ''' Listen for UDP packets with vm usage info then insert those into the
    database'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        data, addr = sock.recvfrom(9000)
        remote_host = addr[0]

        timestamp = time.time()
        statement = '''
        INSERT INTO usage (host, timestamp, data) values ('%s', '%s', '%s')
        ''' % (remote_host, timestamp, data)

        engine = sqlalchemy.create_engine(db_string)
        with engine.begin() as connection:
            connection.execute(statement)


def main():
    '''handle args and calls listen() '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="10.103.114.1")
    parser.add_argument("--port", default=7777)
    parser.add_argument("--db", default='sqlite:///test.db')
    args = parser.parse_args()

    compact_procs = []
    # keep every minute for the last hour
    compact_procs.append(Process(target=compact, args=(args.db, 60, 2)))
    # keep every hour for the last ever
    compact_procs.append(Process(target=compact, args=(args.db, 3600, 60)))
    for proc in compact_procs:
        proc.start()

    listen(args.host, args.port, args.db)

    for proc in compact_procs:
        proc.join()

if __name__ == "__main__":
    main()
