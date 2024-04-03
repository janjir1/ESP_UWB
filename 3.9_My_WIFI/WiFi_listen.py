import socket

# Set the IP address and port to listen on
UDP_IP = "0.0.0.0"  # Use "0.0.0.0" to listen on all available interfaces
UDP_PORT = 3333

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"UDP listener started on {UDP_IP}:{UDP_PORT}")

while True:
    # Receive data and address from the socket
    data, addr = sock.recvfrom(1024)  # 1024 is the buffer size

    if data:
        print(f"Received message from {addr}: {data.decode('utf-8')}")
    else:
        print("Received empty message")