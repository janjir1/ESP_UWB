from typing import Dict, Any
import time, os

from Functions import *
from Classes import Anchor

anchors: Dict[str, Any] = dict()

def calculate(name: str, antenna_calibration_file: str) -> None:

    
    anchors[name].apply_antenna_calibration(antenna_calibration_file)
    anchors[name].calculate_tag_distance()

def decode(recived_data: Any) -> str:

    name = decode_bytes_to_hex(recived_data, 0, 2)
            
    if name not in anchors.keys():
        anchors[name] = Anchor(name)

    anchors[name].decode_data(recived_data, 2)

    return name


def get_anchors(sock: socket, timer: int = 2) -> list:
    anchors_to_track: Dict[str, Any] = dict()

    start_time = time.time()
    end_time = start_time + timer

    while time.time() < end_time:

        recived_data, adrr = sock.recvfrom(120)

        if recived_data:
            name = decode(recived_data)
            anchors_to_track[name] = None

    return list(anchors_to_track.keys())

def live(sock: socket) -> None:
    

    while True:

        recived_data, adrr = sock.recvfrom(1024)

        if recived_data:

            name = decode(recived_data)
            calculate(name, r"C:\Users\Janjiri\Desktop\Soubory\ESP_UWB\Python\DW1000_antenna_delay.csv")

        
            print(f"{name} : {anchors[name].get_distance()[0] * 100:.2f} cm, RXPower: {anchors[name].get_distance()[1]}")

def record(sock: socket) -> None:

    
    path = r"C:\Users\Janjiri\Desktop\Soubory\ESP_UWB\Python"

    meassurment_name = input("Enter meassurment name (folder name): ")

    folder_path = os.path.join(path, meassurment_name)
    os.makedirs(folder_path)
    print(f"Meassurment will be saved in {folder_path}")

    meassurment_number = int(input("Meassurment number: "))

    anchors_list = get_anchors(sock)
    print(anchors_list)

    anchors_finished: Dict[str, bool] = {key: False for key in anchors_list}


    while not all(value for value in anchors_finished.values()):

        recived_data, adrr = sock.recvfrom(120)

        if recived_data:

            name = decode(recived_data)

            file_name = f"data_{meassurment_name}_{name}.csv"
            file_path = os.path.join(folder_path, file_name)

            anchors_finished[name] = anchors[name].export_to_csv(meassurment_number, file_path, True)

    print(f"Done")
            

def main():

    user_input = input("Press Enter to run live or any key to save to excel ")

    sock = start_UDP()

    if user_input == "":
        live(sock)
    else:
        record(sock)

if __name__ == "__main__":
    main()

