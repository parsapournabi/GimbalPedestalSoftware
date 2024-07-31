import socket
import pickle

def start_server():
    host = '192.168.0.1'  # Localhost
    port = 12345  # Arbitrary non-privileged port

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    print('trying to connect...')
    print(socket.gethostname())
    server_socket.bind((host, port))
    print('connected')
    # Listen for incoming connections
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        # Wait for a connection
        client_socket, address = server_socket.accept()
        print(f"Connection from {address} established")

        # Receive data from the client
        data = client_socket.recv(1024)
        print(f"Received data: {data.hex()}")

        # Send response back to the client
        response = "Hello, client!"
        client_socket.send(response.encode())

        # Close the client socket
        client_socket.close()


if __name__ == "__main__":
    start_server()
