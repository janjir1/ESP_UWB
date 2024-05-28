from typing import Dict, Any
from Functions import *
import csv, os

class Anchor:

    instances: Dict[str, Any] = dict()
    max_meassurments: int = 5
    tag_name = "tag"
    delay_dict: Dict[str, int] = dict()
    timestep_res_ps = 15.650040064103
    light_speed = 299702547 #atm
    defalut_antenna_delay = 514

    def __init__(self, our_name: str, delay_file_path: str = "defalut") -> None:
        self.our_name = our_name 
        self.to_tag: list = [ToTagRange() for _ in range(5)]
        self.to_anchor: Dict[str, list] = dict()
        self._read_calibration(delay_file_path)
        Anchor.instances[our_name] = self

    def get_name(self) -> str:
        return self.our_name
    
    def decode_data(self, recived_data: bytes, starting_position: int):

        byte_position = starting_position
        message_num = decode_bytes_to_dec(recived_data, byte_position, 2)
        byte_position += 2

        # Decode tag data
        self._decode_tag_data(recived_data, byte_position, message_num)
        byte_position = byte_position + (len(self._get_tag_decode_key_top()) * get_decode_key_len(self._get_tag_decode_key()))

        # Decode anchor data if present
        if len(recived_data) > byte_position:
            anchor_ranges = decode_bytes_to_dec(recived_data, byte_position, 1)
            byte_position += 1

            for _ in range(anchor_ranges):
                # Extract anchor name
                name = decode_bytes_to_hex(recived_data, byte_position, 2)
                byte_position += 2

                # Ensure anchor exists in 'to_anchor' dictionary
                if name not in self.to_anchor.keys():
                    self.to_anchor[name] = list()

                # Decode anchor data
                self._decode_anchor_data(recived_data, byte_position, name)
                byte_position = byte_position + (get_decode_key_len(self._get_anchor_decode_key()))

    def _decode_tag_data(self, recived_data: bytes, starting_position: int, message_num: int) -> None:

        decode_key_top = self._get_tag_decode_key_top()
        
        decode_position: int = 0
        byte_position = starting_position
        data: Dict[str, Dict[Any, Any]] = dict()
        
        # Iterate through each meassurment in the decoding keys
        for _ in range(len(decode_key_top)):
            decode_sub_position = 0

            content = decode_key_top[decode_position]["content"]
            
            data[content] = dict()

            # Iterate through each sub-meassurment under the current top
            for i in range(len(self._get_tag_decode_key())):

                sub_content = decode_key_top[decode_position]["sub"][decode_sub_position]["content"]
                length = decode_key_top[decode_position]["sub"][decode_sub_position]["bytes"]
                data[content][sub_content] = decode_bytes_to_dec(recived_data, byte_position, length)

                if "Power" in sub_content:
                    data[content][sub_content] = self._decode_power(data[content][sub_content])


                byte_position = byte_position + length

                decode_sub_position +=1  

            decode_position +=1

        # Add the decoded tag data to the system
        self._add_decoded_tag_data(data["POLL"], data["POLL_ACK"], data["RANGE"], message_num)

    def _decode_anchor_data(self, recived_data: bytes, starting_position: int, anchor_name: str) -> None:

        decode_key = self._get_anchor_decode_key()
        
        decode_position: int = 0
        byte_position = starting_position
        data: Dict[str, Any] = dict()

        for _ in range(len(decode_key)):
            
            content = decode_key[decode_position]["content"]
            length = decode_key[decode_position]["bytes"]
            data[content] = decode_bytes_to_dec(recived_data, byte_position, length)

            if "Power" in content:
                    data[content] = self._decode_power(data[content])

            byte_position = byte_position + length

            decode_position +=1

        self._add_decoded_anchor_data(anchor_name, data["recived"], data["RXPower"], data["FPPower"])

    def _decode_power(self, power: int) -> float:
        return -(power/100)

    def _add_decoded_tag_data(self, POLL: dict, POLL_ACK: dict, RANGE: dict, message_num: int) -> None:
        
        # Check if the current message number is sequential to the previous one
        is_sequential = False
        if self.to_tag[0].get_message_num() == message_num-1 :
            is_sequential = True

        # Insert the decoded data into the list of tag data
        self.to_tag.insert(0, ToTagRange(message_num, POLL, POLL_ACK, RANGE, is_sequential))
    
        # Remove the oldest measurement
        if len(self.to_tag) > Anchor.max_meassurments:
            del self.to_tag[-1]

    def _add_decoded_anchor_data(self, anchor_name: str, rPOLL_ACK: int, RXPower: int, FPPower: int) -> None:

       # Extract sPOLL and rPOLL from the most recent tag data
        sPOLL, rPOLL = self.to_tag[0].get_anchor_range_data()

        # Insert the decoded anchor data into the list associated with the anchor name
        self.to_anchor[anchor_name].insert(0, ToAnchorRange(anchor_name, rPOLL, sPOLL, rPOLL_ACK, RXPower, FPPower))

        # Remove the oldest measurement
        if len(self.to_anchor[anchor_name]) > Anchor.max_meassurments:
            del self.to_anchor[anchor_name][-1]

    def _get_tag_decode_key(self) -> Dict[int, Dict[str, Any]]:
        return {0: {"bytes" : 5, "content" : "send"},
                1: {"bytes" : 5, "content" : "recived"},
                2: {"bytes" : 2, "content" : "RXPower"},
                3: {"bytes" : 2, "content" : "FPPower"}}
    
    def _get_tag_decode_key_top(self) -> Dict[int, Dict[str, Any]]:
        decode_key = self._get_tag_decode_key()
        return {0: {"content" : "POLL", "sub" : decode_key},
                1: {"content" : "POLL_ACK", "sub" : decode_key},
                2: {"content" : "RANGE", "sub" : decode_key}}
    
    def _get_anchor_decode_key(self) -> Dict[int, Dict[str, Any]]:
        return {0: {"bytes" : 5, "content" : "recived"},
                1: {"bytes" : 2, "content" : "RXPower"},
                2: {"bytes" : 2, "content" : "FPPower"}}   

    def apply_antenna_calibration(self, delay_file_path: str, position: int = 0) -> None:

        self.to_tag[position].set_antenna_delay(self.calib_data)

    def _read_calibration(self, delay_file_path: str) -> None:

        if os.path.exists(delay_file_path):
            with open(delay_file_path, 'r', encoding='utf-8-sig') as file:
                csv_reader = csv.reader(file, delimiter=';', )

                for row in csv_reader:
                    if row[0] == self.our_name:
                        self.calib_data: list = [float(row[1]), float(row[2])]
        else:
            print("Using only default delay calibration")
            self.calib_data: list = [0, self.defalut_antenna_delay]

    def calculate_tag_distance(self, position: int = 0) -> None:
        self.to_tag[position].calculate_distance(self.timestep_res_ps * 10**(-12), self.light_speed)

    def get_distance(self, position: int = 0) -> tuple:
        return self.to_tag[position].distance, self.to_tag[position].RANGE["RXPower"]
    
    def _add_latest_data_csv(self) -> None:

        raw_data = self.to_tag[0].get_raw_recived()
        message_num = self.to_tag[0].get_message_num()

        self.csv_data.extend([{"Message num": message_num, "Action" : "POLL", **raw_data["POLL"]},
                          {"Message num": message_num, "Action" : "POLL_ACK", **raw_data["POLL_ACK"]},
                          {"Message num": message_num, "Action" : "RANGE", **raw_data["RANGE"]}])

    def export_to_csv(self, num_messages: int, file_path: str, print_flag = False) -> bool:

        if not hasattr(self, 'csv_data'):
           self.csv_data = list()
           self.csv_counter: int = 0
           self.csv_finished = False

        if not self.csv_finished:
            if self.csv_counter < num_messages:
                self._add_latest_data_csv()
                if print_flag:
                    print(f"Saving {self.csv_counter} message from device {self.our_name}")
                self.csv_counter += 1
                return False
            
            with open(file_path, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.csv_data[0].keys())

                writer.writeheader()
    
                writer.writerows(self.csv_data)
                if print_flag:
                    print(f"exported .csv from device {self.our_name}")
                self.csv_finished = True
                return True

        


class ToTagRange:
       
    max_time = 1099511627775

    def __init__(self, message_num: int = 0, POLL: Dict = {}, POLL_ACK: Dict= {}, RANGE: Dict= {}, is_sequential: bool = False):
        self.message_num = message_num
        self.POLL = POLL
        self.POLL_ACK = POLL_ACK
        self.RANGE = RANGE
        self.is_sequential = is_sequential
        self.antenna_calibrated = False

    def get_message_num(self) -> int:
        return self.message_num
    
    def get_anchor_range_data(self) -> tuple:
        return self.POLL["send"], self.POLL["recived"]
    
    def print_times(self) -> None:
        print(f"message_num: {self.message_num}, POLL: {self.POLL}, POLL_ACK: {self.POLL_ACK}, RANGE: {self.RANGE}, is_sequential: {self.is_sequential}")

    def set_antenna_delay(self, antenna_delay: list) -> None:
        self.antenna_calibrated = True
        self.antenna_delay = antenna_delay

    def apply_antenna_delay(self) -> None:

        RXPower = (self.POLL["RXPower"] + self.POLL_ACK["RXPower"] + self.RANGE["RXPower"])/3
        delay = (self.antenna_delay[0]*RXPower + self.antenna_delay[1])*10**-9
        self.TOF = self.TOF - delay

    def _calculate_clk_TOF(self) -> None:

        round1 = wrap(self.POLL_ACK["recived"] - self.POLL["send"], self.max_time)
        reply1 = wrap(self.POLL_ACK["send"] - self.POLL["recived"], self.max_time)
        round2 = wrap(self.RANGE["recived"] - self.POLL_ACK["send"], self.max_time)
        reply2 = wrap(self.RANGE["send"] - self.POLL_ACK["recived"], self.max_time)

        self.clk_TOF = (round1 * round2 - reply1 * reply2)/(round1 + reply1 + round2 + reply2)

    def calculate_TOF(self, timestep: int) -> None:
        self.TOF = self.clk_TOF * timestep

    def to_metres(self, speed_light: int) -> None:
        self.distance = self.TOF * speed_light

    def calculate_distance(self, timestep: int, speed_light: int) -> None:
        self._calculate_clk_TOF()
        self.calculate_TOF(timestep)

        if self.antenna_calibrated:
            self.apply_antenna_delay()

        self.to_metres(speed_light)

    def get_raw_recived(self) -> Dict:
        return {"POLL" : self.POLL, "POLL_ACK" : self.POLL_ACK, "RANGE" : self.RANGE}


class ToAnchorRange:

    def __init__(self, anchor_name: str, rPOLL: float, sPOLL: float, rPOLL_ACK: float, RXPower: float, FPPower: float):
        self.anchor_name = anchor_name
        self.rPOLL = rPOLL
        self.sPOLL = sPOLL
        self.rPOLL_ACK = rPOLL_ACK
        self.RXPower = RXPower
        self.FPPower = FPPower
        self.antenna_calibrated = False

    def get_anchor_name(self):
        return self.anchor_name
    
    def apply_antenna_delay(self, our_delay: int, anchor_delay: int) -> None:
        
        if not self.antenna_calibrated:
            self.sPOLL = self.sPOLL + anchor_delay
            self.rPOLL = self.rPOLL - our_delay

            self.rPOLL_ACK = self.rPOLL_ACK - our_delay

            self.antenna_calibrated = True
