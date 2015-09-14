import socket
from binascii import unhexlify

passw = "petka"

#def bput(frame, char):


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.connect(('95.80.228.249', 8082))

# head
frame = b"\x00AN-D.cz/SDS\x02\x06\x00write\x00"
# data
frame += b"\x00\x00\x00\x0a\x0a\x0a\x0a"
frame += len(passw).to_bytes(4, byteorder='big')

# encode password + padding
# frame += passw.encode('ascii')
for i in range(0,len(passw)):
    frame += (ord(passw[i].encode('ascii')) ^ 0xA5).to_bytes(1, byteorder='big')
frame += bytearray(32 - len(passw))

#number of pairs
frame += (2).to_bytes(4, byteorder='big')
# sys[196] = 2; ovladani SDS-C rele
frame += (196).to_bytes(4, byteorder='big')
frame += (2).to_bytes(4, byteorder='big')
# sys[231] = 255; nastaveni rele 1 ON
frame += (231).to_bytes(4, byteorder='big')
frame += (0).to_bytes(4, byteorder='big')

# rele
#sys[196] = 2
#sys[231] = 255

s.send(frame)
out = s.recv(1024)

print(out)
