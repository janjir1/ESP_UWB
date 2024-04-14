from typing import Dict, Any

from Functions import *
from Classes import Anchor

anchors: Dict[str, Any] = dict()

def decode_and_calculate(recived_data: Any, antenna_calibration_file: str) -> str:

    name = decode_bytes_to_hex(recived_data, 0, 2)
            
    if name not in anchors.keys():
        anchors[name] = Anchor(name)

    anchors[name].decode_data(recived_data, 2)
    anchors[name].apply_antenna_calibration(antenna_calibration_file)
    anchors[name].calculate_tag_distance()

    return name

def live() -> None:
    sock = start_UDP()

    while True:

        recived_data, adrr = sock.recvfrom(1024)

        if recived_data:
            name = decode_and_calculate(recived_data, r"D:\Files\Projects\ESP_UWB\Python\DW1000_antenna_delay.csv")
           
            if name == "11a1":
                print(f"{name} : {anchors[name].get_distance() * 100:.2f} cm")

def record() -> None:
    sock = start_UDP()

    anchors_finished: Dict[str, bool] = dict()

    while (not len(anchors_finished) == 0) ^ all(value for value in anchors_finished.values()):

        recived_data, adrr = sock.recvfrom(1024)

        if recived_data:
            name = decode_and_calculate(recived_data, r"D:\Files\Projects\ESP_UWB\Python\DW1000_antenna_delay.csv")

            anchors_finished[name] = anchors[name].export_to_csv(1000, f"data_{name}.csv", True)

    print(f"Done")
            

def main():

    

    user_input = input("Press Enter to run live or any key to save to excel ")
    if user_input == "":
        live()
    else:
        record()


if __name__ == "__main__":
    main()

