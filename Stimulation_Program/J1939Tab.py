
from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QTreeView,
                             QMessageBox,
                             QFileDialog,
                             QLabel,
                             QSlider,
                             QCheckBox,
                             QLineEdit,
                             QVBoxLayout,
                             QApplication,
                             QPushButton,
                             QTableWidget,
                             QTableView,
                             QTableWidgetItem,
                             QScrollArea,
                             QAbstractScrollArea,
                             QAbstractItemView,
                             QSizePolicy,
                             QGridLayout,
                             QGroupBox,
                             QComboBox,
                             QAction,
                             QDockWidget,
                             QDialog,
                             QFrame,
                             QDialogButtonBox,
                             QInputDialog,
                             QProgressDialog,
                             QTabWidget)
from PyQt5.QtCore import Qt, QTimer, QAbstractTableModel, QCoreApplication, QVariant, QAbstractItemModel, QSortFilterProxyModel
from PyQt5.QtGui import QIcon
import threading
import queue
import time
import calendar
import struct
import base64
import traceback
from collections import OrderedDict
from RP1210.RP1210Functions import *
from TableModel.TableModel import *
#from Graphing.graphing import *

import logging
logger = logging.getLogger(__name__)

class J1939Tab(QWidget):
    def __init__(self, parent, tabs):
        super(J1939Tab,self).__init__()
        self.root = parent
        self.tabs = tabs
        

        self.previous_spn_length = 0
        self.previous_uds_length = 0
        self.reset_data()

        self.spn_needs_updating = True
       
        self.init_pgn()
        self.init_spn()
        
        self.j1939db = self.root.j1939db
        self.time_spns = [959, 960, 961, 963, 962, 964]
        

        self.j1939_request_pgns = [40448, 64891, 64920, 64966, 64981, 65154, 65155, 65164, 65193,
                                   65260, 65200, 65101, 65210, 64888, 64889, 65199, 65214, 65244,
                                   65203, 64896, 64951, 65131, 64898, 64952, 65202, 64950, 64949,
                                   49408, 49664, 65230, 65229, 65231, 65254, 65227, 65212, 65203,
                                   40960, 65208, 65255, 65205, 65211, 65209, 65257, 65236, 40704,
                                   65234, 65259, 65242, 54016, 65206, 65207, 65204, 65248, 64792,
                                   64957, 64969, 65099, 65194, 65201, 65216, 65249, 65250, 65253,
                                   65261]
        self.j1939_request_pgns += [65259 for i in range(6)] #Component ID
        self.j1939_request_pgns += [65260 for i in range(6)] #VIN 
        self.j1939_request_pgns += [65242 for i in range(6)] #Software ID
        
        self.pgns_to_not_decode = []
         # [  59392, #Ack
         #                            0xEA00, #request messages
         #                            0xEB00, # Transport
         #                            0xEC00, # Transport
         #                            0xDA00, #ISO 15765
         #                            65247, # EEC3 at 20 ms
         #                            #65265, # Cruise COntrol Vehicle SPeed
         #                            0xF001,
         #                            0xF002,
         #                            0xF003,
         #                            0xF004,
         #                            57344, #CM1 message
         #                            ]
    def get_pgn_label(self, pgn):

        try:
            return self.j1939db["J1939PGNdb"]["{}".format(pgn)]["Name"]
        except KeyError:
            
            return "Not Provided"

    def reset_data(self):
        self.j1939_count = 0  # successful 1939 messages
        self.ecm_time = {}
        self.battery_potential = {}
        self.speed_record = {}
        self.pgn_rows = []
        self.j1939_unique_ids = OrderedDict()
        self.unique_spns = OrderedDict()
        self.active_trouble_codes = {}
        self.previous_trouble_codes = {}
        self.freeze_frame = {}
        

    def init_pgn(self):
        logger.debug("Setting up J1939 PGN Tab.")
        self.j1939_tab = QWidget()
        self.tabs.addTab(self.j1939_tab,"J1939 PGNs")
        tab_layout = QVBoxLayout()
        j1939_id_box = QGroupBox("J1939 Parameter Group Numbers")
        
        self.add_message_button = QCheckBox("Dynamically Update Table")
        self.add_message_button.setChecked(True)

        clear_button = QPushButton("Clear J1939 PGN Table")
        clear_button.clicked.connect(self.clear_j1939_table)
        
        #Set up the Table Model/View/Proxy
        self.j1939_id_table = QTableView()
        self.pgn_data_model = J1939TableModel()
        self.pgn_table_proxy = Proxy()
        self.pgn_data_model.setDataDict(self.j1939_unique_ids)
        self.j1939_id_table_columns = ["PGN","Acronym","Parameter Group Label","SA","Source","Message Count","Period (ms)","Raw Hexadecimal"]
        self.pgn_resizable_rows = [0,1,2,3,4]
        self.pgn_data_model.setDataHeader(self.j1939_id_table_columns)
        self.pgn_table_proxy.setSourceModel(self.pgn_data_model)
        self.j1939_id_table.setModel(self.pgn_table_proxy)
        self.j1939_id_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.j1939_id_table.setSortingEnabled(True)
        self.j1939_id_table.setWordWrap(False)
        
        #Create a layout for that box using a grid
        j1939_id_box_layout = QGridLayout()
        #Add the widgets into the layout
        j1939_id_box_layout.addWidget(self.j1939_id_table,0,0,1,5)
        j1939_id_box_layout.addWidget(self.add_message_button,1,0,1,1)
        j1939_id_box_layout.addWidget(clear_button,1,2,1,1)
       
        #setup the layout to be displayed in the box
        j1939_id_box.setLayout(j1939_id_box_layout)
        tab_layout.addWidget(j1939_id_box)
        self.j1939_tab.setLayout(tab_layout)
    
    
    def init_spn(self):
        
        self.tabs.currentChanged.connect(self.fill_spn_table)
        
        logger.debug("Setting up J1939 SPN User Interface Tab.")
        self.j1939_spn_tab = QWidget()
        self.tabs.addTab(self.j1939_spn_tab,"J1939 SPNs")
        tab_layout = QVBoxLayout()
        self.spn_table = QTableWidget()
        spn_box = QGroupBox("J1939 Suspect Parameter Numbers and Values")
        
        #Set up the Table Model/View/Proxy for SPNs
        self.spn_table = QTableView()
        self.spn_data_model = J1939TableModel()
        self.spn_table_proxy = Proxy()
        self.spn_data_model.setDataDict(self.unique_spns)
        self.spn_table_columns = ["Acronym","PGN","SA","Source","SPN","Suspect Parameter Number Label","Value","Units","Meaning"]
        self.spn_resizable_rows = [0,1,2,4,5,6,7,8]
        self.spn_data_model.setDataHeader(self.spn_table_columns)
        self.spn_table_proxy.setSourceModel(self.spn_data_model)
        self.spn_table.setModel(self.spn_table_proxy)
        self.spn_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.spn_table.setSortingEnabled(True)
        self.spn_table.setWordWrap(False)

        #Create a layout for that box using the vertical
        spn_box_layout = QGridLayout()
        spn_box_layout.addWidget(self.spn_table,0,0,1,1)
        
        #setup the layout to be displayed in the box
        spn_box.setLayout(spn_box_layout)
        tab_layout.addWidget(spn_box)
        self.j1939_spn_tab.setLayout(tab_layout)
    
    def fill_spn_table(self):
        if self.tabs.currentIndex() == self.tabs.indexOf(self.j1939_spn_tab):
            if len(self.unique_spns) > self.previous_spn_length:
                self.previous_spn_length = len(self.unique_spns)
                self.spn_data_model.aboutToUpdate()
                self.spn_data_model.signalUpdate()
                self.spn_table.resizeRowsToContents()
                for r in self.spn_resizable_rows:
                    self.spn_table.resizeColumnToContents(r)
        #self.spn_table.scrollToBottom()

    def look_up_spns(self, pgn, sa, data_bytes):
        try:
            spn_list = self.j1939db["J1939PGNdb"]["{}".format(pgn)]["SPNs"]
        except KeyError:
            logger.debug("No SPN for PGN {}".format(pgn))
            return False #We don't have meaning for the data
        if pgn in self.pgns_to_not_decode:
            logger.debug("Programmed not to decode PGN {}".format(pgn))
            return False

        for spn in spn_list:
            spn_key = repr((spn, sa))
            if spn_key in self.unique_spns:
                spn_dict = self.unique_spns[spn_key]
            else:
                spn_dict = {}
                spn_dict["Value"] = ""
                spn_dict["Last Value"] = ""
                spn_dict["Units"] = self.j1939db["J1939SPNdb"]["{}".format(spn)]["Units"]
                spn_dict["Meaning"] = ""
                #spn_dict["Value List"] = []
                #spn_dict["Time List"] = []
                #spn_dict["Table Key"] = repr(spn_key)
                spn_dict["Acronym"] = self.j1939db["J1939PGNdb"]["{}".format(pgn)]["Label"]
                spn_dict["PGN"] = "{:6d}".format(pgn)
                spn_dict["SA"] = "{:3d}".format(sa)
                spn_dict["Source"] = self.get_sa_name(sa)
                spn_dict["SPN"] = "{:5d}".format(spn)
                spn_dict["Suspect Parameter Number Label"] = self.j1939db["J1939SPNdb"]["{}".format(spn)]["Name"]
                self.unique_spns[spn_key] = spn_dict
                #self.spn_needs_updating = True
                self.spn_data_model.aboutToUpdate()
                self.spn_data_model.setDataDict(self.unique_spns)
                self.fill_spn_table()


            spn_start = self.j1939db["J1939SPNdb"]["{}".format(spn)]["StartBit"]
            spn_length = self.j1939db["J1939SPNdb"]["{}".format(spn)]["SPNLength"]
            scale = self.j1939db["J1939SPNdb"]["{}".format(spn)]["Resolution"]
            offset = self.j1939db["J1939SPNdb"]["{}".format(spn)]["Offset"]
            high_value = self.j1939db["J1939SPNdb"]["{}".format(spn)]["OperationalHigh"]
            low_value = self.j1939db["J1939SPNdb"]["{}".format(spn)]["OperationalLow"]
            if pgn == 65259: # Component ID
                comp_id_string = get_printable_chars(data_bytes)
                comp_id_list = comp_id_string.split("*")
                if spn == 586: # Make
                    value = comp_id_list[0]
                elif spn == 587: # Model
                    try:
                        value = comp_id_list[1]
                    except IndexError:
                        value = ""
                elif spn == 588: #Serial Number
                    try:
                        value = comp_id_list[2]
                    except IndexError:
                        value = ""
                elif spn == 233: #Unit Number
                    try:
                        value = comp_id_list[3]
                    except IndexError:
                        value = ""
            elif spn_dict["Units"] == 'ASCII':
                value = get_printable_chars(data_bytes)
            
            elif scale > 0 or scale == -3:
                while (spn_start+spn_length) > 64:
                    spn_start -= 64
                    data_bytes = data_bytes[8:]
                if len(data_bytes) < 8:
                    data_bytes = bytes(list(data_bytes) + [0xFF]*(8 - len(data_bytes)))

                if spn_length <= 8:
                        fmt = "B"
                        rev_fmt = "B"
                elif spn_length <= 16:
                    fmt = ">H"
                    rev_fmt = "<H"
                elif spn_length <= 32:
                    fmt = ">L"
                    rev_fmt = "<L"
                elif spn_length <= 64:
                    fmt = ">Q"
                    rev_fmt = "<Q"
                shift = 64 - spn_start - spn_length
                
                #Create a mask one bit at a time
                try:
                    mask = 0
                    for m in range(spn_length):
                        mask += 1 << (63 - m - spn_start) 
                except ValueError:
                    logger.debug("Experienced a ValueError on the Bit Masks with SPN {}".format(spn))
                    logger.debug("mask: {:08X}".format(mask))
                    logger.debug("spn_start: {}".format(spn_start))
                    logger.debug("spn_length: {}".format(spn_length))
                    return
                if scale <= 0:
                    scale = 1
                try:
                    
                    decimal_value = struct.unpack(">Q",data_bytes[0:8])[0] & mask
                except:
                    logger.debug(traceback.format_exc())
                    return
                #the < takes care of reverse byte orders
                shifted_decimal = decimal_value >> shift
                #reverse the byte order
                reversed_decimal = struct.unpack(fmt,struct.pack(rev_fmt, shifted_decimal))[0]
                numerical_value = reversed_decimal * scale + offset
                
                # Check for out of range numbers
                if numerical_value > high_value:
                    spn_dict["Meaning"] = "Out of Range - High"
                elif numerical_value < low_value:
                    spn_dict["Meaning"] = "Out of Range - Low"
                elif spn_dict["Units"] == 'bit':
                    spn_dict["Meaning"] = self.get_j1939_bits_decoded(spn,numerical_value)
                else:
                    spn_dict["Meaning"] = ""
                
                # Display the results
                if scale >= 1 or spn in self.time_spns:
                    try:
                        value = "{:d}".format(int(numerical_value))
                    except ValueError:
                        value = "{}".format(numerical_value)
                else:
                    try:
                        value = "{:0.3f}".format(numerical_value)
                    except ValueError:
                        value = "{}".format(numerical_value)

            else: #Should not be converted to a decimal number
                value = repr(data_bytes)

            spn_dict["Value"] = value
            self.unique_spns[spn_key].update(spn_dict)
            
            if spn_dict["Value"] != self.unique_spns[spn_key]["Last Value"]: #Check to see if the SPN value changed from last time.
                self.spn_rows = list(self.unique_spns.keys())
                row = self.spn_rows.index(spn_key)
                col = self.spn_table_columns.index("Value")
                idx = self.spn_data_model.index(row, col)
                entry = str(spn_dict["Value"])
                self.spn_data_model.setData(idx, entry)
                
                col = self.spn_table_columns.index("Meaning")
                idx = self.spn_data_model.index(row, col)
                entry = str(spn_dict["Meaning"])
                self.spn_data_model.setData(idx, entry)
                self.unique_spns[spn_key]["Last Value"] = spn_dict["Value"]
            
            self.root.data_package["J1939 Suspect Parameter Numbers"].update(self.unique_spns)        
            
            #logger.debug("Updated SPN Dictionary")
            #logger.debug(self.unique_spns[spn_key])
        return True    
    def get_sa_name(self, sa):
        try:
            return self.j1939db["J1939SATabledb"]["{}".format(sa)]
        except KeyError:
            return "Unknown"

    def get_j1939_bits_decoded(self, spn, value):
        try:
            return self.j1939db["J1939BitDecodings"]["{}".format(spn)]["{:d}".format(int(value))].strip().capitalize()
        except KeyError:
            return ""


    def clear_j1939_table(self):

        self.pgn_data_model.beginResetModel()
        self.j1939_unique_ids = OrderedDict()
        self.pgn_data_model.setDataDict(self.j1939_unique_ids)
        self.pgn_data_model.endResetModel()
        
        self.spn_data_model.beginResetModel()
        self.unique_spns = OrderedDict()
        self.spn_data_model.setDataDict(self.unique_spns)
        self.spn_data_model.endResetModel()
        
    def fill_j1939_table(self, j1939_buffer):
        #See The J1939 Message from RP1210_ReadMessage in RP1210
        current_time = j1939_buffer['current_time']
        rx_buffer = j1939_buffer['data']
        try:
            vda_time = struct.unpack(">L", rx_buffer[0:4])[0]
            pgn = rx_buffer[5] + (rx_buffer[6] << 8) + (rx_buffer[7] << 16)
            pri = rx_buffer[8] # how/priority
            sa = rx_buffer[9] #Source Address
            da = rx_buffer[10] #Destination Address
        except (struct.error, IndexError):
            logger.debug(traceback.format_exc())
            return

        pgn_key = repr((pgn,sa))
        source_key = "{} on J1939".format(self.get_sa_name(sa))
        
        if sa not in self.speed_record.keys():
            self.speed_record[sa] = []
            logger.debug("Set speed record for SA {} to an empty list.".format(sa))

        if sa not in self.root.source_addresses:
            self.root.source_addresses.append(sa)    
            logger.info("Added source address {} - {} to the list of known source addresses.".format(sa,self.get_sa_name(sa)))
        
        data_bytes = rx_buffer[11:]
        
        try:
            self.j1939_unique_ids[pgn_key]["Num"] += 1
            previous_data_bytes = base64.b64decode(self.j1939_unique_ids[pgn_key]["Message List"].encode('ascii'))
        except KeyError:
            previous_data_bytes = base64.b64encode(b'').decode()
            self.j1939_unique_ids[pgn_key] = {"Num": 1}
            self.pgn_rows = list(self.j1939_unique_ids.keys())
            self.j1939_unique_ids[pgn_key]["Start Time"] = current_time
            self.j1939_unique_ids[pgn_key]["Message Time"] = current_time
            self.j1939_unique_ids[pgn_key]["Message List"] = base64.b64encode(data_bytes).decode()
            self.j1939_unique_ids[pgn_key]["VDATime List"] = vda_time
            try:
                self.j1939_unique_ids[pgn_key]["Acronym"] = self.j1939db["J1939PGNdb"]["{}".format(pgn)]["Label"]
            except KeyError:
                self.j1939_unique_ids[pgn_key]["Acronym"] = "Unknown"
            try:
                self.j1939_unique_ids[pgn_key]["Parameter Group Label"] = self.j1939db["J1939PGNdb"]["{}".format(pgn)]["Name"]
            except KeyError:
                self.j1939_unique_ids[pgn_key]["Parameter Group Label"] = "Not Provided"
            try:
                self.j1939_unique_ids[pgn_key]["Source"] = self.j1939db["J1939SATabledb"]["{}".format(sa)]
            except KeyError:
                self.j1939_unique_ids[pgn_key]["Source"] = "Reserved"
            self.look_up_spns(pgn, sa, data_bytes)

        self.j1939_unique_ids[pgn_key]["Message Count"] = "{:12d}".format(self.j1939_unique_ids[pgn_key]["Num"])
        self.j1939_unique_ids[pgn_key]["VDATime"] = vda_time
        self.j1939_unique_ids[pgn_key]["PGN"] = "{:6d}".format(pgn)
        self.j1939_unique_ids[pgn_key]["SA"] = "{:3d}".format(sa)
        self.j1939_unique_ids[pgn_key]["Bytes"] = data_bytes
        self.j1939_unique_ids[pgn_key]["Raw Hexadecimal"] = bytes_to_hex_string(data_bytes)
        self.j1939_unique_ids[pgn_key]["Period (ms)"] = "{:10.2f}".format(1000 * (current_time - self.j1939_unique_ids[pgn_key]["Start Time"])/self.j1939_unique_ids[pgn_key]["Num"])
        
        if self.j1939_unique_ids[pgn_key]["Num"] == 1:
            #logger.debug("Adding Row to PGN Table:")
            #logger.debug(self.j1939_unique_ids[pgn_key])
            self.pgn_data_model.aboutToUpdate()
            self.pgn_data_model.setDataDict(self.j1939_unique_ids)
            self.pgn_data_model.signalUpdate()
            self.j1939_id_table.resizeRowsToContents()     
            self.j1939_id_table.scrollToBottom()
            for r in self.pgn_resizable_rows:
                self.j1939_id_table.resizeColumnToContents(r)

            QCoreApplication.processEvents()

        elif self.add_message_button.isChecked():
           
            row = self.pgn_rows.index(pgn_key)
            col = self.j1939_id_table_columns.index("Message Count")
            idx = self.pgn_data_model.index(row, col)
            entry = self.j1939_unique_ids[pgn_key]["Message Count"]
            self.pgn_data_model.setData(idx, entry)
                
            col = self.j1939_id_table_columns.index("Period (ms)")
            idx = self.pgn_data_model.index(row, col)
            entry = self.j1939_unique_ids[pgn_key]["Period (ms)"]
            self.pgn_data_model.setData(idx, entry)
            self.look_up_spns(pgn, sa, data_bytes)

            if not base64.b64encode(data_bytes).decode() == self.j1939_unique_ids[pgn_key]["Message List"]:
                self.j1939_unique_ids[pgn_key]["Message Time"] = current_time
                self.j1939_unique_ids[pgn_key]["Message List"] = base64.b64encode(data_bytes).decode()
                self.j1939_unique_ids[pgn_key]["VDATime List"] = vda_time
                
                col = self.j1939_id_table_columns.index("Raw Hexadecimal")
                idx = self.pgn_data_model.index(row, col)
                entry = self.j1939_unique_ids[pgn_key]["Raw Hexadecimal"]
                self.pgn_data_model.setData(idx, entry)
            
        # # Update if something has changed or if the speed comes in.
        # if  data_bytes != previous_data_bytes or pgn in [65265]:
        #     self.look_up_spns(pgn, sa, data_bytes)
            
        #     if pgn == 65265: #Cruise Control Vehcile Speed
        #         #print(self.unique_spns[repr((84,sa))])
        #         if "Out" not in self.unique_spns[repr((84,sa))]["Meaning"]: 
        #             # The speed data is not out of range
        #             #Save speed from the ECU as a tuple along with PC time.
        #             self.speed_record[sa].append((current_time, float(self.unique_spns[repr((84,sa))]["Value"]) ))
        #             if len(self.speed_record[sa]) > 1000:
        #                 self.speed_record[sa].pop(0)
        #             self.root.speed_graph.add_data(self.speed_record[sa], 
        #                 marker = '.', 
        #                 label = self.j1939_unique_ids[pgn_key]["Source"]+": SPN 84")
                
        #             self.root.speed_graph.plot()
           
        self.root.data_package["J1939 Parameter Group Numbers"].update(self.j1939_unique_ids)
