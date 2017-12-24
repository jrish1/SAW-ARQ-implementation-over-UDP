#P2MP File transfer Protocol 1.0 - Client application
#Rishabh Jain - rjain11@ncsu.edu

import sys,socket,signal,time,math,os,re,fnctl

def calcchecksum(msg):
	if msg:
		total = 0
		data = [msg[i:i+16] for i in range(64,len(msg),16)]
	        for y in data:
			total += int(y,2)
			if total >= 65535:
				total -= 65535
		checksum = 65535 - total
		check_sum_bits = '{0:016b}'.format(checksum)
		send_msg = msg[0:32] + check_sum_bits + msg[48:]
		return send_msg
	else:
		return '0'

def rdt_send(filetotransfer,seq_no):
	global mss
	data=''
	with open(filetotransfer,'rb') as file_data:
		index=seq_no*mss
		file_data.seek(index,0)
		for i in range(1,mss+1):
			fdata=file_data.read(1)
			if fdata:
				data=data+str(fdata)
	file_data.close()
	head=datagram(seq_no,data)
	data_with_checksum=calcchecksum(head)
	return data_with_checksum

def datagram(seq_no,segment_data):
	seq_no_bits = '{0:032b}'.format(seq_no)
	checksum = '0' * 16
	indicator_bits = '01' * 8
	data = ''
	for i in range(1,len(segment_data)+1):
  		data_character = segment_data[i-1]
       		data_byte = '{0:08b}'.format(ord(data_character))
       		data = data + data_byte
    	segment = seq_no_bits + checksum + indicator_bits + data
    	return segment

def ackrecv(s,serverlist):
	global seq_count
	iplist=list(serverlist)
	try:
		s.settimeout(0.015)
		while 1:
			data,addr=s.recvfrom(65535)
			if data:
				seq_no=validate_recv_msg(data)
				if seq_no!=-1 and seq_no == seq_count[0]:
					for i in iplist:
						if i==addr[0]:
							iplist.remove(addr[0])

	except socket.timeout:
		print "Timeout, Sequence no = %d"%(seq_count[0])
		return iplist

def mark_seqno_ack(seq_no):
	global seq_count
	seq_count.remove(seq_no)
	return

def validate_recv_msg(msg):
	seq_no = int(msg[0:32],2)
	pad = msg[32:48]
	ack_ind = msg[48:]
	if pad == ('0' * 16) and ack_ind == ('10' * 8):
		return seq_no
	return -1

def recv_seq_no():
	global seq_count
	if seq_count:
		seq_no=seq_count[0]
		return seq_no
	else:
		return -1

def create_seq():
	global mss
	global filetotransfer
	global seq_count
	sequence=0
	seq_count.append(sequence)
	with open(filetotransfer,'rb') as file_rj:
		while 1:
			pos=(sequence+1)*mss
			file_rj.seek(pos,0)
			data=file_rj.read(1)
			if not data:
				break
			sequence=sequence+1
			seq_count.append(sequence)
	file_rj.close()

arg_count=len(sys.argv)
serverip=[]
for i in range(1,arg_count-3):
	serverip.append(sys.argv[i])

serverport=int(sys.argv[arg_count-3])
filetotransfer=str(sys.argv[arg_count-2])
mss=int(sys.argv[arg_count-1])
seq_count=[]
print "Mss="+str(mss)
clientname=socket.gethostbyname(socket.gethostname())
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
create_seq()
start_time=time.time()
while True:
	seq_to_send=recv_seq_no()
	if seq_to_send>-1:
		msg2send=rdt_send(filetotransfer,seq_to_send)
		for i in serverip:
			s.sendto(msg2send,(i,serverport))
		ack_pending=ackrecv(s,serverip)
		while ack_pending:
			for i in ack_pending:
				s.sendto(msg2send,(i,serverport))
			ack_pending=ackrecv(s,ack_pending)
		mark_seqno_ack(seq_to_send)

	else:
		print "Process Completed"
		end_time=time.time()
		print "Time Taken="+str(end_time-start_time)
		break

print "Exit"
s.close()