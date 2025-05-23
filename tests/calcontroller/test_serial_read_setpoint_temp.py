# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 16:20:18 2025

@author: scott
"""
def compute_crc(mess):

    # Compute the CRC over the first 6 bytes
    crc = 0xFFFF
    for i in range(6):  # Iterate over the first 6 bytes
        thisbyte = mess[i]
        crc ^= thisbyte
        for _ in range(8):  # Process each bit
            lastbit = crc & 0x0001
            crc = (crc >> 1) & 0x7FFF
            if lastbit == 0x0001:
                crc ^= 0xA001

    # Store CRC low and high bytes
    mess[6] = crc & 0xff       # Low byte
    mess[7] = (crc >> 8) & 0xff  # High byte


    return mess


def build_message_to_read_setpoint():
    mess = [0] * 8  # Initialize message array with 8 bytes
    mess[0] = 0x01  # Slave address
    mess[1] = 0x03  # Read function
    mess[2] = 0x00  # Address hi byte
    mess[3] = 0x7F  # Address lo byte
    mess[4] = 0x00  # Number of data points hi byte
    mess[5] = 0x01  # Number of data points lo byte

    # Compute the CRC over the first 6 bytes
    crc = 0xFFFF
    for i in range(6):  # Iterate over the first 6 bytes
        thisbyte = mess[i]
        crc ^= thisbyte
        for _ in range(8):  # Process each bit
            lastbit = crc & 0x0001
            crc = (crc >> 1) & 0x7FFF
            if lastbit == 0x0001:
                crc ^= 0xA001

    # Store CRC low and high bytes
    mess[6] = crc & 0xff       # Low byte
    mess[7] = (crc >> 8) & 0xff  # High byte


    return mess

def build_message_to_read_temperature():
    mess = [0] * 8  # Initialize message array with 8 bytes
    mess[0] = 0x01  # Slave address
    mess[1] = 0x03  # Read function
    mess[2] = 0x00  # Address hi byte
    mess[3] = 0x1C  # Address lo byte
    mess[4] = 0x00  # Number of data points hi byte
    mess[5] = 0x01  # Number of data points lo byte

    # Compute the CRC over the first 6 bytes
    crc = 0xFFFF
    for i in range(6):  # Iterate over the first 6 bytes
        thisbyte = mess[i]
        crc ^= thisbyte
        for _ in range(8):  # Process each bit
            lastbit = crc & 0x0001
            crc = (crc >> 1) & 0x7FFF
            if lastbit == 0x0001:
                crc ^= 0xA001

    # Store CRC low and high bytes
    mess[6] = crc & 0xff       # Low byte
    mess[7] = (crc >> 8) & 0xff  # High byte


    return mess

# Example usage
setpoint_read_message = build_message_to_read_setpoint()
print("Generated setpoint read message:", [f"0x{byte:02X}" for byte in setpoint_read_message])

temp_read_message = build_message_to_read_temperature()
print("Generated temperature read message:", [f"0x{byte:02X}" for byte in temp_read_message])

# reply = [0x01, 0x03, 0x02, 0x07, 0xD0]
# setpoint = ((reply[3] << 8) + reply[4]) / 10 ;
# print("Generated message:", [f"0x{byte:02X}" for byte in reply])
