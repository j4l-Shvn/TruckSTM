import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox as msgBx
from threading import Thread
import sys, multiprocessing as mp

#iconlocation = 'C:\\Users\\Jeff\\Documents\\School\\rams_icon_dark_2.ico'
done = False
class visualizer():
	def done_func(self):
		self.winRoot.destroy()
		global done
		done= True
		
	def __init__(self, inputArray):
		self.iarray = inputArray
		self.winRoot = tk.Tk()
		self.winRoot.title("Machine System States")
		
		self.winRoot.protocol("WM_DELETE_WINDOW", self.done_func)
		self.started = True
		#winRoot.iconbitmap(iconlocation)
		#~ mainButton = ttk.Button(winRoot,text = "Start", command=self.processActions({})).grid(column=0, row = 5)
		self.new_state = BuildStateFrame(self.winRoot,"System States", inputArray)
		self.winRoot.update_idletasks()
		self.winRoot.update()
	

	#~ def processActions(self,valsToSend):
		#~ runProcess = True
		#~ if self.started:
			#~ self.createThread(valsToSend)

	#~ def createThread(self, valsToSend):
		#~ runT = Thread(target=self.startProcessing(valsToSend)) ## example threading program
		#~ runT.setDaemon(True)
		#~ runT.start()

		## Read the binary strings here and pass them on
	def startProcessing(self, valsToSend):
		self.new_state.setFrameState(valsToSend)
		self.winRoot.update_idletasks()
		self.winRoot.update()
		#~ if not self.started:
			#~ started = True


class BuildStateFrame(ttk.LabelFrame):
	def __init__(self, parent, systemName, stateDescData):
		ttk.LabelFrame.__init__(self, parent,text = systemName)
		self.grid(column=0, row = 0, sticky='ew')##position of the frame in the window

		#~ self.MAX_STATES = 60 #### needs determining jve

		#state colors
		colorPallet = ["grey","green","red","cyan"]
		self.normalColorPallet = []
		self.normalColorPallet.append(colorPallet[0])#off
		self.normalColorPallet.append(colorPallet[1])#green
		self.normalColorPallet.append(colorPallet[3])#cyan
		self.abnormalColorPallet = []
		self.abnormalColorPallet.append(colorPallet[0])#off
		self.abnormalColorPallet.append(colorPallet[2])#red
		self.abnormalColorPallet.append(colorPallet[3])#cyan

		# Determine the number of columns that will be created to determine
		# the number of rows to set
		numberStates = len(stateDescData)

		#~ if numberStates > self.MAX_STATES:
			#~ print("TOO MANY STATES FOR SYSTEM")
			#~ # ERROR DIALOG
			#~ msg = "System is unable to handle " + str(numberStates) + " states. \nMaximum is " + str(self.MAX_STATES) + "."
			#~ msgBx.showerror("TOO MANY STATES FOR SYSTEM", msg)
			#~ sys.exit(1)

		if numberStates < 11:
			numColsDisp = numberStates
		elif numberStates < 31:
			numColsDisp = numberStates//2
		else:
			numColsDisp = 15

		# track for row and column position used in button defs
		rowNum = 1
		colNum = 0

		# create an array for the buttons
		statePos = 0
		self.stateBtnArray = []*numberStates

		dict = stateDescData
		for key in dict.keys():
			values = dict[key]
			arrayPos = key[1]
			stateLabelName = key[0]
			stateType = values[0]
			stateDesc = "." #not passing in the initial string - will be updated
			activeValue = values[2]

			if stateType.lower() == 'abnormal':
				stateBtn = CircleButton(self,32,32,self.abnormalColorPallet,stateLabelName,stateDesc,activeValue)
			elif stateType.lower() == 'normal':
				stateBtn = CircleButton(self,32,32,self.normalColorPallet,stateLabelName,stateDesc,activeValue)
			else:
				print("BAD SUBSYSTEM TYPE DEFINITION")
				# ERROR DIALOG
				msg = "System definition, " + stateType + ", is an invalid type."
				msgBx.showerror("Invalid state definition", msg)
				sys.exit(1)

			stateBtn.grid(column = colNum, row = rowNum)
			self.stateBtnArray.insert(arrayPos,stateBtn)
			statePos += 1
			#k += 1

			#label
			self.topLabel = ttk.Label(self,text=stateLabelName).grid(column=colNum, row = rowNum-1)
			colNum += 1

			if (colNum == numColsDisp):
				self.spacerLabel = "   \n "
				self.topLeftLabel=ttk.Label(self,text=self.spacerLabel).grid(column=0, row = rowNum+1)
				colNum = 0
				rowNum += 3

		# set a minimum width of all columns for display uniformity
		col_count, row_count = self.grid_size()
		for col in range(col_count):
			self.grid_columnconfigure(col, minsize=85)

############ UPDATING STATES ################################
	def setFrameState(self, newStates):
		self.createDThread(newStates)

	def createDThread(self,newStates):
		runT = Thread(target=self.makeSettings(newStates)) ## example threading program
		runT.setDaemon(True)
		runT.start()

	def makeSettings(self, newStates):
		for key in newStates.keys():
			arrayPos = key[1]            # the position in the button array
			stateLabelName = key[0]      # unneeded - just for checking
			stateDesc = newStates[key][0]           # active value to be sent to the button
			activeValue = newStates[key][1] # new description text for the button

			# perform the update
			state = self.stateBtnArray[arrayPos]
			state.setStateColor(activeValue)
			state.updateDescription(stateDesc)

		#repaint
		self.update_idletasks()

###############################################################################
class CircleButton(tk.Canvas):
	def __init__(self, parent, width, height, colors, stateName, description, activeValue):
		tk.Canvas.__init__(self, parent, borderwidth=1,relief="flat", highlightthickness=0)
		self.colors = colors
		self.stateName = stateName
		self.description = description
		self.lastSetValue = 0
		self.activationValue = activeValue
		self.myColor = 0

		#Create the button and actions
		spacePd = 4
		self.id = self.create_oval((spacePd,spacePd,width+spacePd, height+spacePd), outline=colors[0], fill=colors[0])
		(x0,y0,x1,y1)  = self.bbox("all")
		width = (x1-x0) + spacePd
		height = (y1-y0) + spacePd
		self.configure(width=width, height=height)
		self.bind("<ButtonPress-1>", self._on_press)
		self.bind("<ButtonRelease-1>", self._on_release)
		self.itemconfig(self.id, fill = self.colors[0])

	def updateDescription(self, inString):
		self.description = inString

	# Button actions
	def _on_press(self, event):
		self.configure(relief="sunken")

	def _on_release(self, event):
		self.configure(relief="flat")
		self.lclClick()

	# just an int value is incoming
	def setStateColor(self,inStateValue):
		if(int(inStateValue) != self.activationValue): #!= implies less than, because the max value inStateValue can attend is activatonBValue
			if int(self.lastSetValue) == 1: #was active, goto transition
				self.itemconfig(self.id, fill = self.colors[2])
				self.lastSetValue = 2
			elif int(self.lastSetValue) == 2: #in transition
				self.itemconfig(self.id, fill = self.colors[0])
				self.lastSetValue = 0
		else:
			#if int(self.lastSetValue) == 0 or int(self.lastSetValue) == 2: #refer to the paper state diagram
			self.itemconfig(self.id, fill = self.colors[1])
			self.lastSetValue = 1

############ Data Section ############
	def showData(self):
		self.infoWindow = tk.Toplevel(self)
		#self.infoWindow.wm_iconbitmap(iconlocation)
		self.infoWindow.wm_title("SUBSYSTEM: " +self.stateName)
		self.sytemLabel = ttk.Label(self.infoWindow, text="Description:").grid(column=0, row=0, sticky=tk.W)
		self.systemList = scrolledtext.ScrolledText(self.infoWindow,width=45,height=10,wrap=tk.WORD)
		self.systemList.grid(column=0, row=1)
		self.disMissBtn = ttk.Button(self.infoWindow,text = "Dismiss", command=self.dismissAction)
		self.disMissBtn.grid(column=0, row=2)

		self.textToScrolledText(self.description)
		#repaint
		self.update_idletasks()

	def createThread(self):
		self.runT = mp.Process(target=self.showData())
		#~ runT.setDaemon(True)
		self.runT.start()

	def lclClick(self):
		self.createThread()

	def textToScrolledText(self, inText):
		self.systemList.insert(tk.INSERT, inText)

	def dismissAction(self):
		self.infoWindow.destroy()
		self.runT.terminate()


viz = None        
def process(val):
	if not done:
		viz.startProcessing(val)
		
	return None

def start_up(args):
	global viz
	viz = visualizer(args)

def communicate(in_q,out_q,args): #args is a dictionary of whatever this module needs
	start_up(args)
	import lib.process as proc
	proc.io(in_q,out_q,process,"visualizer")
