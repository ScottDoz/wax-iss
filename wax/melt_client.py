import socket
import sys


def send_command(command):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 65433))
        client_socket.sendall(command.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(response)
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 client.py <command>")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    send_command(command)
