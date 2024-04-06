import socket
import time

# Set the IP address and port to listen on
UDP_IP = "0.0.0.0"  # Use "0.0.0.0" to listen on all available interfaces
UDP_PORT = 3334

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


decode_key_tag = {0: {"bytes" : 5, "content" : "send"},
                  1: {"bytes" : 5, "content" : "recived"},
                  2: {"bytes" : 2, "content" : "RXPower"},
                  3: {"bytes" : 2, "content" : "FPPower"}}

decode_key = {0: {"bytes" : 2, "content" : "name"},
              1: {"bytes" : 2, "content" : "num_message"},
              2: {"content" : "POLL", "sub" : decode_key_tag},
              3: {"content" : "POLL_ACK", "sub" : decode_key_tag},
              4: {"content" : "RANGE", "sub" : decode_key_tag},}




while True:
    try:
        sock.bind((UDP_IP, UDP_PORT))
        break
    except:
        print("Not workin")
        time.sleep(2)

print(f"UDP listener started on {UDP_IP}:{UDP_PORT}")

while True:
    # Receive data and address from the socket
    recived_data, adrr = sock.recvfrom(1024)  # 1024 is the buffer size



    if recived_data:

        data = dict()
        byte_position = 0
        decode_position = 0

        #--------- Decode name -------------
        data[decode_key[decode_position]["content"]] = ""
        for _ in range(decode_key[decode_position]["bytes"]):
            string = str(hex(recived_data[byte_position]))[2:]

            data[decode_key[decode_position]["content"]] = string + data[decode_key[decode_position]["content"]]

            byte_position += 1
        
        
        decode_position +=1

        #--------- Decode message_num -------------

        message_byte = recived_data[byte_position : byte_position + decode_key[decode_position]["bytes"]]
        byte_position = byte_position + decode_key[decode_position]["bytes"]

        message_dec = int.from_bytes(message_byte, byteorder='little')
        data[decode_key[decode_position]["content"]] = message_dec
        
        decode_position +=1

        #--------- Decode Tag -------------
        for _ in range(3):
            decode_sub_position = 0
            data[decode_key[decode_position]["content"]] = dict()

            for i in range(len(decode_key_tag)):
                message_byte = recived_data[byte_position : byte_position + decode_key[decode_position]["sub"][decode_sub_position]["bytes"]]
                byte_position = byte_position + decode_key[decode_position]["sub"][decode_sub_position]["bytes"]

                message_dec = int.from_bytes(message_byte, byteorder='little')
                data[decode_key[decode_position]["content"]][decode_key[decode_position]["sub"][decode_sub_position]["content"]] = message_dec
                decode_sub_position +=1
                
            decode_position +=1



        print(data)

