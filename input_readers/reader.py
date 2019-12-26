def generateEngineDisableAttack(input_q):
	import csv, time, random
	#Skip some data if needed with a skip time
	skip_start = 270.0
	skip_end = 300.0
	input_file = 'input_readers/input_csv/data.csv'
	print ("Reading from...", input_file)
	with open(input_file) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if float(row['Abs']) > skip_start: 
				data = ""
				for i in range(8,0,-1):
					data = data + row['B' + str(i)].strip().zfill(2)
				time.sleep(float(row['Rel']))	
				if (random.uniform(0.0, 1.0) > .8):
					input_q.put({'ID':'00000011', 'Data':int('000000007D000000',16)}) #0% torque command attack
					input_q.put({'ID':'00F00400', 'Data':int('00000000007D0000',16)}) #0% torque reported by engine
				input_q.put({'ID':row['ID'].zfill(8), 'Data':int(data,16)})
			
			if float(row['Abs']) > skip_end: 
				 break



def parse_csv(input_q):
	import csv, time, math
	#This module expects 9 fields in the CSV, ID and Data bytes B1 through B8
	input_file = 'input_readers/input_csv/data.csv'
	print ("Reading from...", input_file)
	with open(input_file) as csvfile:
		reader = csv.DictReader(csvfile)
		num = 0
		for row in reader:
			data = ""
			for i in range(8,0,-1):
				data = data + row['B' + str(i)].strip().zfill(2)
			time.sleep(float(row['Rel']))	
			print ("@"  +row['Abs'])
			input_q.put({'ID':row['ID'].zfill(8), 'Data':int(data,16)})
			#~ time.sleep(.0003)
			num = num  +1
			
def self_crafted_messages(input_q):
	import csv, time, math
	#This module expects 9 fields in the CSV, ID and Data bytes B1 through B8
	input_file = 'input_readers/input_csv/kenworth.csv'
	print ("Reading from...", input_file)
	set_i  = True
	with open(input_file) as csvfile:
		reader = csv.DictReader(csvfile)
		num = 0
		for row in reader:
			#~ print ("type row: ", type(row['B8']))
			data = ""
			for i in range(8,0,-1):
				if set_i:
					data = data + "FF"
				else:
					data = data + "00"
			print ('ID: 00FEF100', " Data: ", data)
			input_q.put({'ID':'00FEF100', 'Data':int(data,16)})
			time.sleep(.0003)
			num = num  +1
			if set_i:
				set_i = False
			else:
				set_i = True

def get_data(input_q):
	#get data should always return a dictionary as {'ID': 8 hex chars, 'Data': [a list of 8 2-hex chars, B1, B2, B3,...B8. Note the LSB first (left-most) order]}. Eg. {'ID': 18FEF100, 'Data':['01','FF','FF','FF','FF','FF','FF','FF']}
	#Ofcourse, the function itself does not return anything. The internally called module, puts new elements into the queue.
	#~ parse_csv(input_q)
	#~ self_crafted_messages(input_q)
	generateEngineDisableAttack(input_q)
	input_q.put("stop")	
