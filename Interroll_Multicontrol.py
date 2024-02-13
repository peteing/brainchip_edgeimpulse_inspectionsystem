import socket

def construct_profinet_packet(record_identifier):
    device_ip_address = '192.168.0.1'  # Replace with the actual IP address
    profinet_port = 34962   

    profinet_packet = b'\x00\x01\x02\x03\x04\x05' + b'\x06\x07\x08\x09\x0A\x0B' + \
                      b'\x81\x00' + b'\x02\x00\x00\x00' + b'\x00\x00\x00\x00' + \
                      b'\x00' + b'\x08' + b'\x00\x00' + b'\x00\x00\x00\x00' + \
                      b'\x64\x00' + b'\x00\x00' + b'\x02' + b'\x01' + b'\x00' + \
                      b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
                      b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    profinet_packet = profinet_packet[:52] + record_identifier.to_bytes(2, byteorder='big') + profinet_packet[54:]

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((device_ip_address, profinet_port))
            s.sendall(profinet_packet)
            response = s.recv(1024)
            print(f"Response from Profinet device: {response}")
    except Exception as e:
        print(f"Error connecting to Profinet device: {e}")

# Replace 0x4101 with the appropriate record or parameter identifier
record_identifier_to_read = 0x4101

# Call the function to construct and send the Profinet packet
construct_profinet_packet(record_identifier_to_read)
