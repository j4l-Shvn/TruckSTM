import multiprocessing as mul, lib.file_io as fi

def io(in_q, out_q,exec_func,caller="default"):
	while True:
		val = in_q.get(block=True)
		if val == "stop":
			print ("Stoppping ", caller)
			if out_q is not None:
				out_q.put("stop",block=True)
			in_q.close()
			break
		output = exec_func(val)
		if output is not None and out_q is not None:
			out_q.put(output, block=True)
