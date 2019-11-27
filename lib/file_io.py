import csv, configparser, getpass
conf_file = 'conf.ini'


def read_csv(filename, delim): #returns is a list of dicts and each dist is (heading:content)
	file_as_list = []
	with open(filename, 'rb') as csvfile:
		read = csv.DictReader(csvfile, delimiter=delim)
		for row in read:
			file_as_list.append(row)
	return file_as_list
	
	
def read_any_file(filename): #return is a list of lines (strings)
	file_as_list = []
	with open(filename) as f:
		file_as_list = f.readlines()
	file_as_list = [x.strip() for x in file_as_list] 
	return file_as_list

log_begin = True	
def error_log(message):
	global log_begin
	if log_begin:
		with open('error_log', 'w') as log:
			log.write(message + '\n')
		log_begin = False
	else:
		with open('error_log', 'a') as log:
			log.write(message + '\n')
	log.close()



write_file_set = []
def write_to_any_file(message,fname):
	global write_file_set
	if fname == None:
		write_file_set = []
	fname = working_directory + fname
	if fname not in write_file_set:
		with open(fname, 'w') as log:
			log.write(message + '\n')
		write_file_set.append(fname)
	else:
		with open(fname, 'a') as log:
			log.write(message + '\n')
	log.close()

def read_config(section):
	Config = configparser.ConfigParser()	
	Config.read(conf_file)
	dict1 = {}
	options = Config.options(section)
	for option in options:
		try:
			dict1[option] = Config.get(section, option)
			if dict1[option] == -1:
				DebugPrint("skip: %s" % option)
		except:
			print("exception on %s!" % option)
			dict1[option] = None
	return dict1

def save_config(args):
	Config = configparser.RawConfigParser()
	Config.read(conf_file)
	for arg in args:
		Config.set(arg[0],arg[1],arg[2])
	with open(conf_file, 'wb') as configfile:
		Config.write(configfile)
		
	
working_directory = ''

	
#print "\n".join(str(x) for x in read_csv("/home/mantin/CAN-J1939/Data/Kenworth-Truck Analysi/61441-0B-Kenworth.csv",","))
