import socket
import threading
import sys
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
import pdb
import os
from libcamera import Transform

#picam2 = Picamera2()
#encoder = H264Encoder(bitrate=1000000)  # Assume encoder is initialized elsewhere
output_file = "Video/output_video.h264"
is_recording = False
is_running = True  # Add this global flag to control the server loop
rotation = False


#server


def server_program(picam,encoder1, output,running,recording,rotate):
    global is_running, picam2, output_file,is_recording, encoder
    encoder = encoder1
    is_running = running
    is_recording = recording
    output_file = output 
    picam2 = picam
    rotation = rotate
    host = "localhost"
    port = 65432

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Camera Controller Server started. Waiting for connections...")

    while is_running:
        try:
            server_socket.settimeout(1.0)  # Allows periodic checks for `is_running`
            try:
                client_socket, address = server_socket.accept()
                print(f"Connection established with {address}")
                client_handler = threading.Thread(target=handle_client_connection, args=(client_socket,))
                client_handler.start()
            except socket.timeout:
                continue  # Check the `is_running` flag after timeout
        except KeyboardInterrupt:
            print("\nServer shutting down (KeyboardInterrupt).")
            is_running = False

    print("Server stopped.")
    server_socket.close()


#client connections
def handle_client_connection(client_socket):
    global is_recording, output_file, is_running

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
            print(f"Received command: {data}")  # Debug

            if not data:
                break

            if data.startswith("start"):
                if len(data.split()) > 1:
                    output_file = data.split(" ", 1)[1]
                start_recording(client_socket,data)

            elif data == "stop":
                stop_recording(client_socket)

            elif data == "exit":
                client_socket.sendall(b"Exiting server.\n")
                is_running = False  # Stop the main server loop
                break
            elif data.startswith("rotate"):
                rotate_camera(client_socket, data)

            else:
                client_socket.sendall(b"Invalid command.\n")

        except Exception as e:
            client_socket.sendall(f"Error: {str(e)}\n".encode('utf-8'))
            break

    client_socket.close()


def send_command(command):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 65432))
        client_socket.sendall(command.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(response)
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")
        
        
        
#commands 

def start_recording(client_socket,data):
    global is_recording, rotation

    if is_recording:
        client_socket.sendall(b"Recording is already in progress.\n")
        return

    try:
        base_folder = "Video"
        os.makedirs(base_folder, exist_ok=True)  # Create the folder if it doesn't exist

        if len(data.split()) > 1:
            file_name = data.split(" ", 1)[1]
            if not file_name.startswith(base_folder):
                output_file = os.path.join(base_folder, os.path.basename(file_name))
            else:
                output_file = file_name
        else:
            output_file = os.path.join(base_folder, "output_video.h264")
        #rotation
        if rotation:
            video_config = picam2.create_video_configuration(transform=Transform(hflip=True, vflip=True))
        else:
            video_config = picam2.create_video_configuration(transform=Transform(hflip=True,vflip=True))
        
        picam2.configure(video_config)


        picam2.start()
        picam2.start_recording(encoder, output_file)
        is_recording = True
        print("Recording started.")
        client_socket.sendall(f"Recording started. Saving to {output_file}\n".encode('utf-8'))
    except Exception as e:
        client_socket.sendall(f"Error starting recording: {str(e)}\n".encode('utf-8'))



def rotate_camera(client_socket, data):
    global rotation
    try:
        rotation = True
        client_socket.sendall(f"Camera rotation set to 180 degrees.\n".encode('utf-8'))
    except Exception as e:
        client_socket.sendall(f"Error rotating camera: {str(e)}\n".encode('utf-8'))


def stop_recording(client_socket):
    global is_recording

    if not is_recording:
        client_socket.sendall(b"No recording in progress to stop.\n")
        return

    try:
        picam2.stop_recording()
        picam2.stop_preview()
        picam2.close()
        is_recording = False
        print("Recording stopped.")
        client_socket.sendall(b"Recording stopped.\n")
    except Exception as e:
        client_socket.sendall(f"Error stopping recording: {str(e)}\n".encode('utf-8'))
        
        

        
  
