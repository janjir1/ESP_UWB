from typing import Dict, Any

from Functions import *
from Classes import *

def main() -> None:
    sock = start_UDP()

    anchors: Dict[str, Any] = dict()

    while True:
        # Receive data and address from the socket
        recived_data, adrr = sock.recvfrom(1024)  # 1024 is the buffer size

        

        if recived_data:
            
            name = decode_bytes_to_hex(recived_data, 0, 2)
            

            if name not in anchors.keys():
                anchors[name] = Anchor(name)

            
            anchors[name].decode_data(recived_data, 2)
            anchors[name].apply_antenna_calibration("D:\Files\Projects\ESP_UWB\Python\DW1000_antenna_delay.csv")
            anchors[name].calculate_tag_distance()
            if name == "11a1":
                print(f"{name} : {anchors[name].get_distance() * 100:.2f} cm")

if __name__ == "__main__":
    main()
