from intervaltree import Interval, IntervalTree

class SpnValues:
	def __init__(self):
		self.spnValue=()
		self.stateArray={}
		self.itree={}
		self.valMaps = {}
		self.intervalMaps={}
		self.intervals=[]
	def __repr__(self):
		return ("spnValue: " + str(self.spnValue) + "\nstateArray: " + str(self.stateArray) + "\nitree: " + str(self.itree) + "\nvalMaps: " + str(self.valMaps) + "\nintervalMaps: " + str(self.intervalMaps) + "\nintervals: " + str(self.intervals))


#~ SpnObjects=[]
pCount=0
SpnObjIndexes={}
parameter_state_map={}
state_parameter_map={}


import lib.file_io as fi

def start_up(args):
	global SpnObjIndexes,SpnObjects,parameter_state_map,state_parameter_map,pCount
	parameter_state_map=args['parameter_state_map']
	state_parameter_map=args['state_parameter_map']

	#Constructing Parameter Objects
	for k in parameter_state_map.keys():
		spn = SpnObjIndexes.get(k,SpnValues())
		spn.spnValue=k
		spn.stateArray=parameter_state_map[k][0]
		
		for v in parameter_state_map[k][1].keys():
			lst = list(parameter_state_map[k][1][v])
			if (len(v) < 2):
				spn.valMaps.update({v[0]:lst})
			else:
				spn.intervals.append(Interval(v[0],v[1]))
				spn.intervalMaps.update({Interval(v[0],v[1]):lst})
		if(len(spn.intervals)>0):
			spn.itree=IntervalTree(Interval(*iv) for iv in spn.intervals)
		
		SpnObjIndexes[spn.spnValue] = spn




prevStates = {} #need to store previious values
#Processing Messages
def process(val):
	global SpnObjIndexes,parameter_state_map,prevStates
	
	currStates = {}
	#~ finalStates=prevStates
	for p in val:
		try:
			SpnObject=SpnObjIndexes[p[0]]
		except KeyError:
			return None
			
		try:
			for st in SpnObject.valMaps[p[1]]:
				SpnObject.stateArray[st]=1
		except KeyError:
			pass
			
		#Then cheking the intervals trees
		if(SpnObject.itree != {}):
			#~ print ("Interval: IN")
			res=SpnObject.itree.search(p[1])
			for r in res:
				lst=SpnObject.intervalMaps[r]
				for sw in lst:
					SpnObject.stateArray[sw] = 1
		
		for s in SpnObject.stateArray.keys():
			val_p=state_parameter_map[s][0][p[0]]
			sval=SpnObject.stateArray[s]
			if (sval != val_p):
				state_parameter_map[s][0][p[0]] = sval
				if sval == 0:
					state_parameter_map[s][1] = state_parameter_map[s][1] - 1
				else:
					state_parameter_map[s][1] = state_parameter_map[s][1] + 1
				prevStates[s] = state_parameter_map[s]
				currStates[s] = state_parameter_map[s]	
			# ~ if (sval==1 and val_p==0):
				# ~ state_parameter_map[s][0][p[0]] = 1
				# ~ state_parameter_map[s][1] = state_parameter_map[s][1] + 1
				# ~ tup=(s[0], s[1], str(state_parameter_map[s][0]))
				# ~ prevStates[s] = state_parameter_map[s]
				# ~ currStates[s] = state_parameter_map[s]

			# ~ if(sval==0 and val_p==1):
				# ~ state_parameter_map[s][0][p[0]] = 0
				# ~ state_parameter_map[s][1] = state_parameter_map[s][1] - 1
				# ~ tup=(s[0], s[1], str(state_parameter_map[s][0]))
				# ~ prevStates[s] = state_parameter_map[s]
				# ~ currStates[s] = state_parameter_map[s]

			SpnObject.stateArray[s]=0
	to_ret = prevStates
	prevStates = currStates
	
	if to_ret == {}:
		return None
	#print (to_ret)
	return to_ret


def communicate(in_q,out_q,args): #args is a dictionary of whatever this module needs
	print ("Launched disp..") 
	start_up(args)
	import lib.process as proc
	proc.io(in_q,out_q,process,"indexer")





















