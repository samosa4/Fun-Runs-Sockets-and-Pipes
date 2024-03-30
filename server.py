#!/usr/bin/env python 
# Source Python Network Programming Cookbook,Second Edition -- Chapter - 1 
# -*- coding: utf-8 -*-


import socket
import threading
import json
import time

# Define run information (modify with actual run details)
runs = {
    "001": {"area": "NorthEast", "name": "Pier to Pier", "length": 7, "fee": 10, "capacity": 100, "waitlist": [], "time": "Fast"},
    "002": {"area": "York", "name": "York 10KM", "length": 10, "fee": 5, "capacity": 50, "waitlist": [], "time": "Slow"},
    "003": {"area": "WestMidlands", "name": "Combe Abbey", "length": 10, "fee": 20, "capacity": 100, "waitlist": [], "time": "Medium"},
    "004": {"area": "WestMidlands", "name": "Leamington Spa Half Run", "length": 22, "fee": 25, "capacity": 50, "waitlist": [], "time": "Fast"},
    "005": {"area": "SouthYorkshire", "name": "Penistone Fun Run", "length": 5, "fee": 2.50, "capacity": 80, "waitlist": [], "time": "Very_Fast"},
    "006": {"area": "SouthYorkshire", "name": "Rother Valley Sundowner 10K", "length": 10, "fee": 10, "capacity": 40, "waitlist": [], "time": "Medium"},
    "007": {"area": "PeakDistrict", "name": "Exterminator", "length": 8, "fee": 11, "capacity": 130, "waitlist": [], "time": "Very_Slow"},
    "008": {"area": "London", "name": "UKTS Fun Run", "length": 5, "fee": 4, "capacity": 100, "waitlist": [], "time": "Medium"},
    "009": {"area": "London", "name": "Turks Head 10k Fun Run", "length": 10, "fee": 24, "capacity": 70, "waitlist": [], "time": "Fast"},
    "010": {"area": "NorthWales", "name": "Bangor City 10K", "length": 10, "fee": 4, "capacity": 30, "waitlist": [], "time": "Medium"},
    "011": {"area": "NorthWales", "name": "Barry Island 2K Santa Fun Run", "length": 2, "fee": 2, "capacity": 100, "waitlist": [], "time": "Very_Fast"},
}

HOST = "localhost"
PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# Define a global variable to store the current available spaces for each run ID
available_spaces = {run_id: run["capacity"] for run_id, run in runs.items()}

def recommend_runs(data):
    recommendations = []
    try:
        area, min_length, max_length, time = data
        min_length = float(min_length)  # Convert to float
        max_length = float(max_length)  # Convert to float
        for run_id, details in runs.items():
            if (
                (area.lower() in details["area"].lower() or area.lower() == "any") and
                (details["length"] >= min_length and details["length"] <= max_length) and  # Comparison after conversion
                (time.lower() in details["time"].lower() or time.lower() == "any")
            ):
                recommendations.append({"id": run_id, "name": details["name"], "length": details["length"], "time": details['time'], "fee": details["fee"]})
    except (IndexError, ValueError):
        return "Invalid request format. Please provide area, min length, max length, and time."
    return recommendations

# Define a function to periodically update available spaces for all run IDs
def update_available_spaces():
    global available_spaces
    while True:
        # Sleep for some interval
        time.sleep(10)  # Adjust as needed
        # Update available spaces based on current capacity and waitlist length
        for run_id, run in runs.items():
            available_spaces[run_id] = run["capacity"] - len(run["waitlist"])

# Start the thread to periodically update available spaces
update_thread = threading.Thread(target=update_available_spaces)
update_thread.daemon = True
update_thread.start()

def register_runners(data):
    try:
        secretary, *requests = data
        total_cost = 0
        registration_details = []

        for run_id, quantity in zip(*[iter(requests)] * 2):
            quantity = int(quantity)  # Convert to integer
            if run_id not in runs:
                return f"Invalid run ID: {run_id}"

            run = runs[run_id]
            available = run["capacity"] - len(run["waitlist"]) - quantity

            if available < 0:
                return f"Insufficient space for {quantity} runners in Run ID {run_id}. Available spaces: {run['capacity'] - len(run['waitlist'])}"

            run["waitlist"].extend([secretary] * quantity)
            total_cost += run["fee"] * quantity
            registration_details.append((run_id, quantity))

        # Calculate total cost
        if total_cost > 50:
            total_cost *= 0.9

        pound_symbol = chr(163)  # Encodes the pound symbol in UTF-8
        response = f"Total cost for {secretary}: {pound_symbol}{total_cost:.2f}\n"

        # Append available spaces information for each run ID to the response
        for run_id, quantity in registration_details:
            available_spaces = runs[run_id]["capacity"] - len(runs[run_id]["waitlist"])
            response += f"Run ID {run_id}: Available Spaces: {available_spaces}\n"

        return response

    except (IndexError, ValueError):
        return "Invalid request format. Please provide secretary name followed by run ID and quantity."





def handle_client(client_socket, addr):
    print(f"Connected by {addr}")
    print("Waiting to receive a message from the client")
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        print(f"Message received from {addr}: {data}")
        if data.startswith("recommend"):
            response = json.dumps(recommend_runs(data.split()[1:]))
            print(f"Recommendations to be sent to {addr}: {response}")
            print("Waiting to receive a message from the client")
        elif data.startswith("register"):
            response = register_runners(data.split()[1:])
            if response.startswith("Total"):
                secretary, *requests = data.split()[1:]  # Extract secretary name and registration details
                total_cost = 0
                for run_id, quantity in zip(*[iter(requests)] * 2):
                    quantity = int(quantity)
                    total_cost += int(runs[run_id]["fee"]) * quantity  # Calculate total cost using run fee
                pound_symbol = chr(163)  # Encodes the pound symbol in UTF-8
                print(f"Message Received from client for Runner Registration\n"
                      f"The following registration details were sent to {addr}\n"
                      f"Name: {secretary}\n")
                registered_runners = [f"Run ID {run_id}: {q} people" for run_id, q in zip(requests[::2], requests[1::2])]
                output = "Registered Runners:\n" + " \n".join(registered_runners) + "\n"
                print(output)
                print(f"Total Cost: {pound_symbol}{total_cost:.2f}")
                print("\nWaiting to receive a message from the client")
            else:
                print(f"Registration Failed: {response}")  # Print error message if registration fails
        else:
            response = "Invalid command"
        client_socket.sendall(response.encode())
    client_socket.close()
    print(f"Client {addr} disconnected")


print(f"Server listening on {HOST}:{PORT}")
print("Waiting to receive a message from the client")
while True:
    client_socket, addr = server_socket.accept()
    handle_client(client_socket, addr)
