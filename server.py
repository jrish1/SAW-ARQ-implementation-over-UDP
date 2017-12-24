#P2MP File transfer Protocol 1.0 - Server application
#Rishabh Jain - rjain11@ncsu.edu

from socket import *
from decimal import *
import os, random, time,sys


def gen_random_number():
        while 1:
                gen_number = random.uniform(0,1)
                if Decimal(gen_number) != Decimal(0.0):
			break
	return gen_number


def rdt_send(message, seq):
	seq_no = '{0:032b}'.format(seq)
	pad = '0' * 16
	ack_ind = '10' * 8
	return seq_no + pad + ack_ind

def write_file(message,filename):
	file_desc = open(filename,'a')
	msg = str(message[64:])
	iterations = len(msg)/8
	final_data = ''
	for i in range(0,iterations):
		bit_data = str(msg[i*8:(i+1)*8])
		char_data = chr(int(bit_data, 2))
		final_data = final_data + char_data
	file_desc.write(final_data)
	file_desc.close()
	return int(message[0:32],2) + 1


def cal_checksum(msg):
	if msg[48:64] == '01' * 8:
		total = 0
                data = [msg[i:i+16] for i in range(64,len(msg),16)]
                for y in data:
                        total += int(y,2)
                        if total >= 65535:
                                total -= 65535
                if (65535-total) == int(msg[32:48],2):
			return 1
		else:
			return -1
	else:
		return -1


if(len(sys.argv) == 4):
	port = int(sys.argv[1])
	filename = sys.argv[2]
	probability = float(sys.argv[3])
else:
	print "Wrong set of arguments passed"
	exit(0)

if os.path.exists(filename):
	os.remove(filename)

server_socket = socket(AF_INET,SOCK_DGRAM)
server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
server_socket.bind(('',port))
print "Server is ready to receive!!!"
expected_seq = 0
while 1:
	try:
		server_socket.settimeout(10.0)
		message, client_address = server_socket.recvfrom(65535)
		if not message:
			break
	except timeout:
		print "Client is not sending..Exiting!!"
		break

	random_num = gen_random_number()
	if random_num > probability:
		checksum = cal_checksum(message)
		if checksum == 1:
			if int(message[0:32],2) == expected_seq:
				send_msg = rdt_send(message,expected_seq)
				server_socket.sendto(send_msg, client_address)
				expected_seq = write_file(message,filename)
			else:
				if expected_seq!=0:
					print "Ack retransmitted:" + str(expected_seq-1)
					send_msg = rdt_send(message,expected_seq-1)
					server_socket.sendto(send_msg, client_address)
		else:
			print "Packet Discarded, Checksum not matching!!!"
	else:
		checksum = cal_checksum(message)
		if checksum == 1:
			print "Packet Loss, sequence no:" + str(int(message[0:32],2))
		else:
			print "Packet Discarded, Checksum not matching!!!"
print "Closed"
server_socket.close()