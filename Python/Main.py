from typing import Dict, Any
import time, os

from Functions import *
from Anchor import Anchor
from ParticleSpace import space

calib_file_path = r"C:\Users\Janjiri\Desktop\Soubory\ESP_UWB\Python\DW1000_antenna_delay.csv"

anchors: Dict[str, Any] = dict()

def calculate(name: str, antenna_calibration_file: str) -> None:

    anchors[name].apply_antenna_calibration(antenna_calibration_file)
    anchors[name].calculate_tag_distance()

def decode(recived_data: Any) -> str:

    name = decode_bytes_to_hex(recived_data, 0, 2)
            
    if name not in anchors.keys():
        anchors[name] = Anchor(name, calib_file_path)

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

    anchors_list = get_anchors(sock)
    print(anchors_list)
    data_list = []

    #initial space dimension
    init_space_dimension = [6, 4, 2]
    particleSpace = space(7500, init_space_dimension)

    #location of anchors, if location is not provided filter ignores that anchor
    particleSpace.update_anchor("11a1", [0.0, 0.0, 0.51])
    particleSpace.update_anchor("12a2", [4.6, 0.1, 0.23])
    particleSpace.update_anchor("13a3", [5.14, 3.3, 0.5])
    #particleSpace.update_anchor("14a4", [0.7, 3.34, 0.2])
    #particleSpace.update_anchor("15a5", [2.83, 2.47, 1.39])

    sock.setblocking(0)

    while True:

        while True:

            #reads last couple of messages
            try:
                sock_data, addr = sock.recvfrom(1024)

                data_list.append([sock_data, time.perf_counter()])
                if len(data_list) > len(anchors_list):
                    data_list = data_list[-len(anchors_list):]

            except BlockingIOError:
                break

        start_time = time.perf_counter()
        delta_time = 0

        if len(data_list) > 0:
            for packet in data_list:

                recived_data = packet[0]
                recive_time = packet[1] + delta_time

                #anchor.py decodimg and calculation
                name = decode(recived_data)
                calculate(name, r"C:\Users\Janjiri\Desktop\Soubory\ESP_UWB\Python\DW1000_antenna_delay.csv")

                #calculated_time = time.perf_counter()

                print(f"{name} : {anchors[name].get_distance()[0] * 100:.2f} cm, RXPower: {anchors[name].get_distance()[1]}")
                distance = anchors[name].get_distance()[0]

                if bs_filter(distance):
                    time_start = time.perf_counter()

                    #particle space iteration
                    if particleSpace.update_space(name, anchors[name].get_distance()[0], recive_time):
                        #print(f"average fit = {particleSpace.average_fit():.2f}")
                        print(f"update space {time.perf_counter() - time_start}")

                        time_start = time.perf_counter()
                        particleSpace.evolve_space()
                        print(f"evolve space {time.perf_counter() - time_start}")

                        particleSpace.calculate_tag()

                        time_start = time.perf_counter()
                        particleSpace.visualize()
                        print(f"visualize {time.perf_counter() - time_start}")

                        #print(f"decode and calulation time {calculated_time-recive_time}, particle time {time.perf_counter() - calculated_time}, total {time.perf_counter()-recive_time}")

                delta_time = time.perf_counter() - start_time
        data_list = []


def record(sock: socket) -> None:
    #used for antenna delay calibration
    
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
