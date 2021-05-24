from tkinter import *
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

PORT = None
BUFSIZ = 1024
HOST = ''


# Handles receiving of messages.
def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(END, msg)
        except OSError:  # IF client has left the chat.
            break


# Handles sending of messages.
def sendMsg(event=None):
    msg = type_msg.get()
    type_msg.set("")
    try:
        client_socket.send(bytes(msg, "utf8"))
    except:
        print("Socket Closed")
    if msg == "{quit}":
        app.destroy()


# This function is called when is window is closed.
def on_closing(event=None):
    type_msg.set("{quit}")
    sendMsg()


# Getting IP:PORT, the user entered.
def getIpPort(event=None):

    entered_ip_port = ip_port.get()

    if ":" not in entered_ip_port:
        ip_port.set("Invalid Address!")
        return

    entered_ip_port = entered_ip_port.split(':')
    HOST = entered_ip_port[0]
    PORT = int(entered_ip_port[1])

    BUFSIZ = 1024
    client_socket_address = (HOST, int(PORT))

    global client_socket
    client_socket = socket(AF_INET, SOCK_STREAM)

    try:
        # Connecting to the Server.
        client_socket.connect(client_socket_address)

        # Changing Status on succesfull connection.
        status.delete('0', 'end')
        status.insert(END, "                                       Connected")

        # Creating a thread for clients to receive messages.
        global RECEIVE_THREAD
        RECEIVE_THREAD = Thread(target=receive)
        RECEIVE_THREAD.daemon = True
        RECEIVE_THREAD.start()

    except:
        ip_port.set("Connection Failed!")


# Creating Tkinter Window
app = Tk()

# Naming Window and Adjusting Size
app.title('CLIENT')
app.geometry('450x500')

# Widgets

# Label and input field for ip_port
ip_port_label = Label(app, text='Enter IP and Port: ',
                      font=('bold', 10))
ip_port_label.grid(row=0, column=0, sticky=W, padx=(10, 1), pady=(20, 0))

ip_port = StringVar()
ip_port.set("      127.0.0.1:3000")
ip_port_entry = Entry(app, textvariable=ip_port, width=30)
ip_port_entry.grid(row=0, column=1, pady=(20, 0))
ip_port_entry.bind("<Return>", getIpPort)

# Status_Area
status = Listbox(app, width=49, height=1)
status.insert(END, "                                   Not Connected")
status.grid(row=1, column=0, columnspan=2, padx=(10, 0))

# Connect_btn
port_button = Button(app, text="Connect",
                     command=getIpPort,  font=('bold', 10), bg='#3487ed', height=3, width=10)
port_button.grid(row=0, column=2, rowspan=2, padx=10, pady=(20, 0))


# Creating a msg_area
msg_list = Listbox(app, height=20, width=67)
msg_list.grid(row=2, column=0, columnspan=3,
              rowspan=6, pady=(10, 2), padx=(10, 0), sticky=W)
scrollbar = Scrollbar(app)
scrollbar.grid(row=3, column=3)

msg_list.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=msg_list.yview)

# Creating a type_msg_area
type_msg = StringVar()
type_msg.set("Enter message here")
type_msg_entry = Entry(app, textvariable=type_msg, width=55)
type_msg_entry.grid(row=8, column=0, columnspan=3,
                    sticky=W, pady=(10, 5), padx=(12, 0))
type_msg_entry.bind("<Return>", sendMsg)

send_button = Button(app, text="Send",
                     command=sendMsg,  font=('bold', 10), bg='#3487ed')
send_button.grid(row=8, column=2, pady=(10, 5), padx=(60, 0))

app.protocol("WM_DELETE_WINDOW", on_closing)

# Running the app
app.mainloop()
