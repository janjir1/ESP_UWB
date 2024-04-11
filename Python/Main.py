from typing import Dict, Any
import socket
import time

from Functions import *
from Classes import *

sock = start_UDP()

anchors: Dict[str, Any] = dict()

while True:
    # Receive data and address from the socket
    recived_data, adrr = sock.recvfrom(1024)  # 1024 is the buffer size

    

    if recived_data:
        
        name = decode_bytes_to_hex(recived_data, 0, 2)
        print(f"Name: {name}")

        if name not in anchors.keys():
            anchors[name] = Anchor(name)

        
        anchors[name].decode_data(recived_data, 2)
        anchors[name].apply_antenna_calibration("D:\Files\Projects\ESP_UWB\Python\DW1000_antenna_delay.csv")