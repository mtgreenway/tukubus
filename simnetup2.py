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
    listen(args.host, args.port, args.db)


if __name__ == "__main__":
    main()
