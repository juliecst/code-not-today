import csv
import os
import datetime
from pythonosc import dispatcher, osc_server
import threading

# Define the list of ports to listen on
ports = [6570, 6571, 6572, 6575, 6577, 6574, 6578]  # Add or remove ports as needed

# OSC server setup
serverIP =  '192.168.8.101'#'172.20.10.3'  # Replace with the desired IP address
serverAddrs = [(serverIP, port) for port in ports]

count = 1
while os.path.exists(f"saveMe_{count}.csv"):
    count += 1

# This creates a new CSV file; every time I run the code it happens anew
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
filenames = [f"saveMe_{timestamp}_{port}.csv" for port in ports]
filepaths = [os.path.join("/Users/juliecst/Desktop/websocket", filename) for filename in filenames]

def handle_OSC_message(address, squeeze, port):
    try:
        # Find the corresponding file path based on the port
        filepath = filepaths[ports.index(port)]
    except ValueError:
        print(f"Received OSC message with an unknown port: {port}")
        return

    with open(filepath, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), squeeze])

    print(f"Received OSC message on port {port}: {address} {squeeze}")

try:
    # Create a separate OSC server instance for each port
    servers = []
    for i, serverAddr in enumerate(serverAddrs):
        dispatcher_instance = dispatcher.Dispatcher()
        dispatcher_instance.map("/sensorValue", lambda addr, squeeze, port=ports[i]: handle_OSC_message(addr, squeeze, port))

        server = osc_server.ThreadingOSCUDPServer(serverAddr, dispatcher_instance)
        servers.append(server)

        print(f"OSC server listening on {serverIP}:{ports[i]}")

        # Start each server in a separate thread
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

    # Keep the main thread running until interrupted
    while True:
        pass

except KeyboardInterrupt:
    # Clean up and close the servers
    for server in servers:
        server.shutdown()
        server.server_close()
