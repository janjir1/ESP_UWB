from typing import Dict, Any
import socket
import time
from math import pi as pi
from math import e as euler

def decode_bytes_to_dec(data: bytes, starting_position: int, length: int) -> int:
    message_byte = data[starting_position : starting_position + length]
    return int.from_bytes(message_byte, byteorder='little')

def decode_bytes_to_hex(data: bytes, starting_position: int, length: int) -> str:

        string: str = ""
        byte_position = starting_position

        for _ in range(length):
            hex_byte = str(hex(data[byte_position]))[2:]
            string = hex_byte + string

            byte_position += 1
        
        return string
 
def get_decode_key_len(decode_key: Dict[int, Dict[str, Any]], keyword: str = "bytes") -> int:

    decode_key_len: int  = 0
    for content in decode_key:
        if isinstance(decode_key[content][keyword], int):
            decode_key_len += decode_key[content][keyword]
    
    return decode_key_len

def start_UDP(UDP_IP: str = "0.0.0.0", UDP_PORT: int = 3334) -> socket.socket:

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        try:
            sock.bind((UDP_IP, UDP_PORT))
            print(f"UDP listener started on {UDP_IP}:{UDP_PORT}")
            return sock
        except:
            print("Binding socket ...")
            time.sleep(1)

def wrap(number: float, max_value = int) -> float:
    if number < 0:
        number = number + max_value + 1

    return number
"""
def normal_dist(mean: float, std_deviation: float, number: float) -> float:
    exp = pow(((number-mean)/std_deviation), 2)/2
    return (1/(std_deviation*pow(2*pi, 0.5)))*pow(euler, -exp)
"""
def bs_filter(distance: float) -> bool:
    if distance > 300 or distance < 0: return False
    else: return True
