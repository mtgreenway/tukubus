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


import argparse
import sqlalchemy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default='sqlite:///test.db')
    args = parser.parse_args()

    #PRAGMA foreign_keys=OFF;
    #BEGIN TRANSACTION;
    statement = '''
    CREATE TABLE usage(
    host text,
    timestamp int,
    data text,
    primary key(host, timestamp)
    );
    '''
    #COMMIT;

    engine = sqlalchemy.create_engine(args.db)
    with engine.begin() as connection:
        connection.execute(statement)

if __name__ == "__main__":
    main()
