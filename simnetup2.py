import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("10.103.114.1", 7777))

while True:
    data, addr = sock.recvfrom(9000)
    with open(addr[0], "w") as host:
        host.write(data)
