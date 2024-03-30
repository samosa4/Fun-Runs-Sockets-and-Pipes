    #!/usr/bin/env python
    # Python Network Programming Cookbook,Second Edition -- Chapter - 1

import socket
import json
from Levenshtein import distance

HOST = "localhost"  # Change to server IP if needed
PORT = 65432  # Make sure this matches the server port

def send_data(data):
    """Sends data to the server."""
    client_socket.sendall(data.encode())

def receive_data():
    """Receives data from the server."""
    return client_socket.recv(1024).decode()

def get_user_input_with_correction(choices, prompt="Enter your desired value: "):
    """Prompts user for input and suggests corrections."""
    while True:
        user_input = input(prompt)
        min_distance = float('inf')
        corrected_text = user_input
        for choice in choices:
            dist = distance(user_input.lower(), choice.lower())
            if dist < min_distance:
                min_distance = dist
                corrected_text = choice
        if min_distance <= 2:  # Adjust threshold for correction suggestion
            if corrected_text.lower() != user_input.lower():
                print(f"There might be a typo in the input. Did you mean '{corrected_text}' instead?")
                confirmation = input("Enter 'y' to accept correction, 'n' to use your input, or 'cancel' to quit: ")
                if confirmation.lower() == 'y':
                    return corrected_text
                elif confirmation.lower() == 'n':
                    continue
                elif confirmation.lower() == 'cancel':
                    exit()
                else:
                    print("Invalid input. Please enter 'y', 'n', or 'cancel'.")
            else:
                return user_input
        else:
            return user_input  # No close match for correction

def recommend_runs(area=None, min_length=0, max_length=10, time=None):
    """Sends a recommendation request to the server and displays results."""
    send_data(f"recommend {area} {min_length} {max_length} {time}")
    data = receive_data()
    try:
        recommendations = json.loads(data)
        if recommendations:
            for run in recommendations:
                pound_symbol = chr(163)  # Encodes the pound symbol in UTF-8
                print(end='\n')
                print(f"Run ID: {run['id']}, Fun Run: {run['name']}, Distance: {run['length']}KM, Time: {run['time']}, Fee: {pound_symbol}{run['fee']}")
        else:
            print("No runs match the criteria.")
    except json.JSONDecodeError:
        print("Error: Invalid response from the server.")

def register_runners(secretary, *run_data):
    """Sends a registration request to the server and displays the total cost."""
    data = f"register {secretary} " + " ".join(f"{run_id} {quantity}" for run_id, quantity in run_data)
    send_data(data)
    response = receive_data()
    print(response)

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # List of valid areas and times
    valid_areas = ["NorthEast", "York", "WestMidlands", "SouthYorkshire", "PeakDistrict", "London", "NorthWales", "any"]
    valid_times = ["Fast", "Slow", "Medium", "Very_Fast", "Very_Slow", "any"]

    while True:
        print("\nMenu:")
        print("1. Recommend Fun Runs")
        print("2. Register Runners")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            area = get_user_input_with_correction(valid_areas, prompt="Enter your desired Area (or 'any'): ")
            min_length = float(input("Enter minimum length (km): "))
            max_length = float(input("Enter maximum length (km): "))
            time = get_user_input_with_correction(valid_times, prompt="Enter desired time (or 'any'): ")
            recommend_runs(area, min_length, max_length, time)
        elif choice == "2":
            secretary = input("Enter your name: ")
            num_requests = int(input("Enter the number of registrations: "))
            requests = []
            for i in range(num_requests):
                run_id = input(f"Enter Run ID for registration {i+1}: ")
                quantity = int(input(f"Enter number of runners for {run_id}: "))
                requests.append((run_id, quantity))
            register_runners(secretary, *requests)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

    client_socket.close()
