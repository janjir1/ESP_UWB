from typing import Dict, Any
from Functions import *

class Anchor:
    instances: Dict[str, Any] = dict()
    max_meassurments: int = 5

    def __init__(self, anchor_name: str) -> None:
        self.anchor_name = anchor_name 
        self.to_tag: list = [ToTagRange() for _ in range(5)]
        self.to_anchor: Dict[str, list] = dict()
        Anchor.instances[anchor_name] = self

    def get_name(self) -> str:
        return self.anchor_name
    
    def decode_data(self, recived_data: bytes, starting_position: int):

        byte_position = starting_position
        message_num = decode_bytes_to_dec(recived_data, byte_position, 2)
        byte_position += 2

        self.decode_tag_data(recived_data, byte_position, message_num)
        byte_position = byte_position + (len(self.get_tag_decode_key_top()) * get_decode_key_len(self.get_tag_decode_key()))

        if len(recived_data) > byte_position:
            anchor_ranges = decode_bytes_to_dec(recived_data, byte_position, 1)
            byte_position += 1

            for anchor_range in range(anchor_ranges):
                name = decode_bytes_to_hex(recived_data, byte_position, 2)
                byte_position += 2

                if name not in self.to_anchor.keys():
                    self.to_anchor[name] = list()

                self.decode_anchor_data(recived_data, byte_position, name)
                byte_position = byte_position + (get_decode_key_len(self.get_anchor_decode_key()))

    def decode_tag_data(self, recived_data: bytes, starting_position: int, message_num: int) -> None:

        decode_key_top = self.get_tag_decode_key_top()
        
        decode_position: int = 0
        byte_position = starting_position
        data: Dict[str, Dict[Any, Any]] = dict()
        
        for _ in range(len(decode_key_top)):
            decode_sub_position = 0

            content = decode_key_top[decode_position]["content"]
            
            data[content] = dict()

            for i in range(len(self.get_tag_decode_key())):

                sub_content = decode_key_top[decode_position]["sub"][decode_sub_position]["content"]
                length = decode_key_top[decode_position]["sub"][decode_sub_position]["bytes"]

                data[content][sub_content] = decode_bytes_to_dec(recived_data, byte_position, length)

                byte_position = byte_position + length

                decode_sub_position +=1  

            decode_position +=1

        self.add_decoded_tag_data(data["POLL"], data["POLL_ACK"], data["RANGE"], message_num)

    def decode_anchor_data(self, recived_data: bytes, starting_position: int, anchor_name: str) -> None:
        decode_key = self.get_anchor_decode_key()
        
        decode_position: int = 0
        byte_position = starting_position
        data: Dict[str, Any] = dict()

        for _ in range(len(decode_key)):
            
            content = decode_key[decode_position]["content"]
            length = decode_key[decode_position]["bytes"]
            data[content] = decode_bytes_to_dec(recived_data, byte_position, length)
            byte_position = byte_position + length

            decode_position +=1

        self.add_decoded_anchor_data(anchor_name, data["recived"], data["RXPower"], data["FPPower"])

    def add_decoded_tag_data(self, POLL: dict, POLL_ACK: dict, RANGE: dict, message_num: int) -> None:

        is_sequential = False
        if self.to_tag[0].get_message_num() == message_num-1 :
            is_sequential = True

        self.to_tag.insert(0, ToTagRange(message_num, POLL, POLL_ACK, RANGE, is_sequential))
    

        if len(self.to_tag) > Anchor.max_meassurments:
            del self.to_tag[-1]

    def add_decoded_anchor_data(self, anchor_name: str, rPOLL_ACK: int, RXPower: int, FPPower: int) -> None:

        sPOLL, rPOLL = self.to_tag[0].get_anchor_range_data()
        self.to_anchor[anchor_name].insert(0, ToAnchorRange(anchor_name, rPOLL, sPOLL, rPOLL_ACK, RXPower, FPPower))

        if len(self.to_anchor[anchor_name]) > Anchor.max_meassurments:
            del self.to_anchor[anchor_name][-1]

    def get_tag_decode_key(self) -> Dict[int, Dict[str, Any]]:
        return {0: {"bytes" : 5, "content" : "send"},
                1: {"bytes" : 5, "content" : "recived"},
                2: {"bytes" : 2, "content" : "RXPower"},
                3: {"bytes" : 2, "content" : "FPPower"}}
    
    def get_tag_decode_key_top(self) -> Dict[int, Dict[str, Any]]:
        decode_key = self.get_tag_decode_key()
        return {0: {"content" : "POLL", "sub" : decode_key},
                1: {"content" : "POLL_ACK", "sub" : decode_key},
                2: {"content" : "RANGE", "sub" : decode_key}}
    
    def get_anchor_decode_key(self) -> Dict[int, Dict[str, Any]]:
        return {0: {"bytes" : 5, "content" : "recived"},
                1: {"bytes" : 2, "content" : "RXPower"},
                2: {"bytes" : 2, "content" : "FPPower"}}   


class ToTagRange:
       
    def __init__(self, message_num: int = 0, POLL: Dict = {}, POLL_ACK: Dict= {}, RANGE: Dict= {}, is_sequential: bool = False):
        self.message_num = message_num
        self.POLL = POLL
        self.POLL_ACK = POLL_ACK
        self.RANGE = RANGE
        self.is_sequential = is_sequential

    def get_message_num(self) -> int:
        return self.message_num
    
    def get_anchor_range_data(self) -> tuple:
        return self.POLL["send"], self.POLL["recived"]
    
    def print_times(self) -> None:
        print(f"message_num: {self.message_num}, POLL: {self.POLL}, POLL_ACK: {self.POLL_ACK}, RANGE: {self.RANGE}, is_sequential: {self.is_sequential}")


class ToAnchorRange:

    def __init__(self, anchor_name: str, rPOLL: int, sPOLL: int, rPOLL_ACK: int, RXPower: int, FPPower: int):
        self.anchor_name = anchor_name
        self.rPOLL = rPOLL
        self.sPOLL = sPOLL
        self.rPOLL_ACK = rPOLL_ACK
        self.RXPower = RXPower
        self.FPPower = FPPower

    def get_anchor_name(self):
        return self.anchor_name

