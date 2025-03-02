import sys
import time
import socket

BROADCAST_PORT = 1337
BROADCAST_MESSAGE = b"setup from host"
ACK_MESSAGE = b"setup ack from guest"


def host_broadcast_discovery(
    broadcast_port=BROADCAST_PORT,
    broadcast_message=BROADCAST_MESSAGE,
    ack_message=ACK_MESSAGE,
    timeout_sec=10,
):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(("", broadcast_port))
    s.settimeout(timeout_sec)

    s.sendto(broadcast_message, ("<broadcast>", broadcast_port))
    
    while True:
        try:
            data, addr = s.recvfrom(1024)
            if data == ack_message:
                guest_ip = addr[0]
                print(f"[Host] Received ack from guest at IP: {guest_ip}")
                s.close()
                return guest_ip
        except socket.timeout:
            print(f"[Host] No response after {timeout_sec} seconds.")

            s.close()
            return None


def guest_listen_and_ack(
    broadcast_port=BROADCAST_PORT,
    broadcast_message=BROADCAST_MESSAGE,
    ack_message=ACK_MESSAGE,
):
    """
    Listen once for the host's broadcast, then reply to it with an ack.
    Returns the detected host's IP, or None if something unexpected happens.
    """
    gs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    gs.bind(("", broadcast_port))

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
        host_ip = guest_listen_and_ack()
        print(f"Host IP is {host_ip}")
    else:
        print("Usage: python script.py [host|guest]")
