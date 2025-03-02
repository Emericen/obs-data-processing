import sys
import socket


BROADCAST_IP = "255.255.255.255"
LISTEN_IP = "0.0.0.0"

BROADCAST_PORT = 8765
BROADCAST_MESSAGE = b"setup from host"
ACK_MESSAGE = b"setup ack from guest"


def host_broadcast_discovery(
    broadcast_port=BROADCAST_PORT,
    broadcast_message=BROADCAST_MESSAGE,
    ack_message=ACK_MESSAGE,
):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind((LISTEN_IP, broadcast_port))

    print("[Host] Sending broadcast...")
    while True:
        s.sendto(broadcast_message, (BROADCAST_IP, broadcast_port))
        data, addr = s.recvfrom(1024)
        if data == ack_message:
            guest_ip = addr[0]
            print(f"[Host] Received ack from guest at IP: {guest_ip}")
            s.close()
            return guest_ip


def guest_listen_and_ack(
    broadcast_port=BROADCAST_PORT,
    broadcast_message=BROADCAST_MESSAGE,
    ack_message=ACK_MESSAGE,
):
    gs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    gs.bind((LISTEN_IP, broadcast_port))

    print("[Guest] Listening for host broadcast...")
    while True:
        data, addr = gs.recvfrom(1024)
        if data == broadcast_message:
            host_ip = addr[0]
            print(f"[Guest] Received setup from host at IP: {host_ip}")

            # Respond directly to the host
            gs.sendto(ack_message, (host_ip, broadcast_port))
            print("[Guest] Sent ack back to host.")
            gs.close()
            return host_ip


if __name__ == "__main__":
    mode = sys.argv[1].lower()
    if mode == "host":
        guest_ip = host_broadcast_discovery()
        print(f"Guest IP is {guest_ip}")
    elif mode == "guest":
        print("[Guest] Booting up...")
        # time.sleep(...) for a startup delay
        host_ip = guest_listen_and_ack()
        print(f"Host IP is {host_ip}")
    else:
        print("Usage: python script.py [host|guest]")
