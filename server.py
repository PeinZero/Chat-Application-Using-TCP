from threading import Thread, Event
from socket import AF_INET, socket, SOCK_STREAM
from tkinter import *

SET_SERVER = [False]

# retrive a client from clients(which is dictionary)
def get_client(name):
    for client, client_name in clients.items():
        if client_name == name:
            return client

    return False


# Handles receiving of messages.
def receive():
    while True:
        try:
            msg = client_socket.recv(BUFFER).decode("utf8")
            msg_list.insert(END, msg)
        except OSError:  # If client has left the chat.
            break


# Handles sending of messages.
def sendMsg(event=None):
    msg = type_msg.get()
    type_msg.set("")
    try:
        client_socket.send(bytes(msg, "utf8"))
    except:
        print("Socket Closed.")
    if msg == "{quit}":
        client_socket.close()


# Accept new clients (this function runs on the Thread "CLIENT_THREAD")
def accepting_new_clients():
    while True:
        # Accepting a client and broadcast him a message.
        client, client_address = SERVER.accept()
        client.send(bytes("Welcome To K180187 Server", "utf8"))
        addresses[client] = client_address

        # Create a seprate thread for every new client.
        NEW_CLIENT = Thread(target=handle_single_client, args=(client,))
        NEW_CLIENT.daemon = True
        NEW_CLIENT.start()


# Takes client socket as an argument and handles a single client.
def handle_single_client(client):

    # Get client name from the buffer.
    name = client.recv(BUFFER).decode("utf8")
    if name == 'SERVER' and SET_SERVER[0] == False:
        global THE_SERVER
        THE_SERVER = client
        SET_SERVER[0] = True
    elif name.lower() == 'server' and name.lower() == 'all':
        while name.lower() == 'server' or name.lower() == 'all':
            if name.lower() == 'server':
                msg = "Invalid Name! Name cannot be Server!"
            else:
                msg = "Invalid Name! Name cannot be All!"
            client.send(bytes(msg, "utf8"))

            name = client.recv(BUFFER).decode("utf8")

    # Sending client a welcome message.
    if name != 'SERVER':
        welcome = 'Welcome to the server, %s! Type {quit} anytime to leave.\n' % name
        client.send(bytes(welcome, "utf8"))

        # Telling that a client has connected to the server.
        msg = "%s has joined the chat!" % name
        THE_SERVER.send(bytes(msg, "utf8"))

    else:
        welcome = 'Use the format: \" Client Name @ Server Message\"'
        client.send(bytes(welcome, "utf8"))
        welcome = "to send message to a specific client."
        client.send(bytes(welcome, "utf8"))
        type_msg.set("client name @ Server messgae")

    clients[client] = name

    # Run as long as client is connected.
    while True:
        message = client.recv(BUFFER)
        if message != bytes("{quit}", "utf8"):
            # broadcast(msg, name+": ")
            if name == 'SERVER':

                try:
                    message = str(message).split('@')
                    
                    if message[0][2:].lower().strip() == 'all':
                        message = message[1][:-1].strip()
                        broadcast(bytes(message, "utf8"),name+": " )
                        continue
                    
                    print(message[0][2:].strip())
                    which_client = get_client(message[0][2:].strip())
                    message = message[1][:-1].strip()

                    if which_client != False:
                        THE_SERVER.send(bytes(name+": ", "utf8") +
                                        bytes(message, "utf8"))

                        which_client.send(
                            bytes(name+": ", "utf8")+bytes(message, "utf8"))
                    else:
                        type_msg.set("Client not Found!")
                except:
                    THE_SERVER.send(bytes(name+": ", "utf8") +
                                    bytes("Invalid format of message", "utf8"))
                    continue

            else:
                THE_SERVER.send(bytes(name+": ", "utf8")+message)
                client.send(bytes(name+": ", "utf8")+message)
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            # send message to the server when a client leaves
            THE_SERVER.send(bytes("%s has left the chat." % name, "utf8"))
            break


# Broadcasting messages to all the connected clients.
# Here prefix here is the identity of the client.
def broadcast(message, prefix=""):
    for client in clients:
        client.send(bytes(prefix, "utf8")+message)


# allow server to send and recieve messages
def become_client(event=None):
    client_socket_address = ('192.168.1.109', int(PORT))

    # Server itself connecting to server
    global client_socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(client_socket_address)

    # Creating a thread for clients to receive messages.
    global RECEIVE_THREAD
    RECEIVE_THREAD = Thread(target=receive)
    RECEIVE_THREAD.daemon = True
    RECEIVE_THREAD.start()


def start_server(event=None):
    global clients, addresses
    # To store incoming clients and their address
    clients = {}
    addresses = {}

    # Creating server socket and starting the server.
    global SERVER, BUFFER
    HOST = ''
    BUFFER = 1024
    SERVER = socket(AF_INET, SOCK_STREAM)
    socket_address = (HOST, int(PORT))
    SERVER.bind(socket_address)
    SERVER.listen(5)

    # Making Server both the Server & Client.
    CLIENT_THREAD = Thread(target=become_client)
    CLIENT_THREAD.daemon = True
    CLIENT_THREAD.start()

    # Handling all the incoming clients.
    INCOMING_CLIENT_THREAD = Thread(target=accepting_new_clients)
    INCOMING_CLIENT_THREAD.daemon = True
    INCOMING_CLIENT_THREAD.start()
    INCOMING_CLIENT_THREAD.join()
    SERVER.close()


# This function runs after user has enter the Port Number.
# The server listen on this entered port number.
def getPort(event=None):

    global PORT
    PORT = port_number.get()

    if PORT != 'Enter Port Number':
        port_number.set(f"Listening on port {PORT}")

        # Start the execution of the server.
        global SERVER_THREAD
        SERVER_THREAD = Thread(target=start_server)
        SERVER_THREAD.daemon = True
        SERVER_THREAD.start()
    else:
        port_number.set(f"Enter Port Number")


# This function is called when is window is closed.
def on_closing(event=None):
    app.destroy()


# Creating Tkinter Window
app = Tk()

# Naming Window and Adjusting Size
app.title('SERVER')
app.geometry('450x500')

# Widgets

# Creating top area
port_number_label = Label(app, text='Port Number: ',
                          font=('bold', 10), pady=20)
port_number_label.grid(row=0, column=0, sticky=W, padx=(10, 10))

port_number = StringVar()
port_number.set("Enter Port Number")
port_number_entry = Entry(app, textvariable=port_number, width=30)
port_number_entry.grid(row=0, column=1)
port_number_entry.bind("<Return>", getPort)

port_button = Button(app, text="Start Listening",
                     command=getPort,  font=('bold', 10), bg='#3487ed')
port_button.grid(row=0, column=2, padx=10)

# Creating a msg_area
msg_list = Listbox(app, height=20, width=65)
msg_list.grid(row=1, column=0, columnspan=3,
              rowspan=6, pady=(10, 2), padx=(10, 0))
scrollbar = Scrollbar(app)
scrollbar.grid(row=3, column=3)

msg_list.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=msg_list.yview)

# Creating a type_msg_area
type_msg = StringVar()
type_msg.set("Enter message here")
type_msg_entry = Entry(app, textvariable=type_msg, width=55)
type_msg_entry.grid(row=7, column=0, columnspan=3,
                    sticky=W, pady=(10, 5), padx=(12, 0))
type_msg_entry.bind("<Return>", sendMsg)

send_button = Button(app, text="Send",
                     command=sendMsg,  font=('bold', 10), bg='#3487ed')
send_button.grid(row=7, column=2, pady=(10, 5), padx=(60, 0))

app.protocol("WM_DELETE_WINDOW", on_closing)

# Running the app
app.mainloop()
