PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE usage(
host text,
timestamp int,
data text,
primary key(host, timestamp)
);
COMMIT;
