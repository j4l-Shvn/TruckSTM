#general imports
import multiprocessing as mul, signal, sys
#import the input reader
import input_readers.reader as reader
	
if __name__ == "__main__":
	import configparser as c
	config = c.ConfigParser()
	config.read('conf.cfg')
	
	#~ startup_file as startup

	#First startup the whole process
	startup_dict = __import__(config.get('Programs','startup').strip()).communicate({'input_filename':"state_defs/" + config.get('General','state_def_filename')})

	#define process out_queues. Note here the visualizer does not need an output queue.
	reader_out_q = mul.Queue()
	J1939_Interpreter_out_q = mul.Queue()
	state_indexer_out_q = mul.Queue()
	visualizer_out_q = None
	
	#create processes
	signal.signal(signal.SIGINT, signal.SIG_IGN) #A ignore interupt is required, otherwise child processes will inherit the interupt.
	inp = mul.Process(target=reader.get_data,args=(reader_out_q,))
	p1 = mul.Process(target=__import__(config.get('Programs','J1939_Interpreter').strip()).communicate,args=(reader_out_q,J1939_Interpreter_out_q,{'startup':startup_dict['to_J1939_Interpreter']},))
	p2 = mul.Process(target=__import__(config.get('Programs','state_indexer').strip()).communicate,args=(J1939_Interpreter_out_q,state_indexer_out_q,startup_dict['to_state_indexer'],))
	p3 = mul.Process(target=__import__(config.get('Programs','visualizer').strip()).communicate,args=(state_indexer_out_q,visualizer_out_q,startup_dict['to_visualizer'],))


	#graceful termination, trap SIGINT
	def signal_term_handler(signal, frame):
		print ('Terminating gracefully....')
		
		reader_out_q.put("stop")
		
		print ('Waiting for processes to stop....')
		p3.join()
		p2.join()
		p1.join()
		print ('Proceseses stopped....')
		print ('Terminating input reader....')
		inp.terminate()
		inp.join()
		print ('Input reader terminated....')
			
		print ('Exiting....')	
		sys.exit(0)
	

	#start processes. Note that the input reader process starts last.
	p3.start()
	p2.start()
	p1.start()
	inp.start()	
	signal.signal(signal.SIGINT, signal_term_handler)
	
