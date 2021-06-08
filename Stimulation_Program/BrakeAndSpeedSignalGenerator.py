"""
TU RP1210 is a 32-bit Python 3 program that uses the RP1210 API from the 
American Trucking Association's Technology and Maintenance Council (TMC). This 
framework provides an introduction sample source code with RP1210 capabilities.
To get the full utility from this program, the user should have an RP1210 compliant
device installed. To make use of the device, you should also have access to a vehicle
network with either J1939 or J1708.

The program is release under one of two licenses.  See LICENSE.TXT for details. The 
default license is as follows:

    Copyright (C) 2018  Jeremy Daily, The University of Tulsa
                  2020  Jeremy Daily, Colorado State University

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QMessageBox,
                             QLabel,
                             QSlider,
                             QApplication,
                             QPushButton,
                             QGridLayout,
                             QAction,
                             QScrollArea,
                             QFrame,
                             QSizePolicy,
                             QTabWidget
                             )
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QSize
from PyQt5.QtGui import QIcon

import queue
import humanize
import time
import sys
import struct
import threading
import logging
import logging.config

from RP1210.RP1210 import *
from RP1210.RP1210Functions import *
from RP1210.RP1210Select import *

from J1939Tab import *
from SimulationTab import *

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


# --------- BEGIN
#           Added by DS for capturing and replaying pack
# lfh = open("overrun_moving.log","w")
# def log_message(t,msg):
#    print(t,msg)
#    global lfh 
#    lfh.write(msg+"\n")
#    lfh.flush()
# t0 = 0
# def get_delta():
#  global t0
#  if t0 == 0:
#    t0 = time.time()
#    return 0
#  else:
#    t = time.time()
#    d = t - t0
#    t0 = t
#    return d
# --------- END


class BrakeAndSpeedSignalGenerator(QMainWindow):
    def __init__(self):
        super(BrakeAndSpeedSignalGenerator, self).__init__()

        self.setWindowTitle("Brake and Speed Signal Generator")
        with open("J1939db.json", 'r') as j1939_file:
            self.j1939db = json.load(j1939_file)
        self.rx_queues = {}
        self.tx_queues = {}
        self.read_message_threads = {}
        os.system("TASKKILL /F /IM DGServer2.exe")
        os.system("TASKKILL /F /IM DGServer1.exe")

        self.update_rate = 100  # milliseconds
        self.source_addresses = []
        self.data_package = {}
        self.data_package["J1939 Parameter Group Numbers"] = {}
        self.data_package["J1939 Suspect Parameter Numbers"] = {}

        # self.setGeometry(0,50,1600,850)
        self.RP1210 = None
        self.network_connected = {"J1939": False, }
        self.RP1210_toolbar = None

        self.init_ui()
        logger.debug("Done Setting Up User Interface.")

        self.selectRP1210(automatic=True)
        logger.debug("Done selecting RP1210.")

        connections_timer = QTimer(self)
        connections_timer.timeout.connect(self.check_connections)
        connections_timer.start(1500)  # milliseconds

        read_timer = QTimer(self)
        read_timer.timeout.connect(self.read_rp1210)
        read_timer.start(self.update_rate)  # milliseconds

        send_brake_timer = QTimer(self)
        send_brake_timer.timeout.connect(self.send_brake)
        send_brake_timer.setInterval(100)
        send_brake_timer.start()

        send_turn_timer = QTimer(self)
        send_turn_timer.timeout.connect(self.send_turn)
        send_turn_timer.setInterval(100)
        send_turn_timer.start()
        self.turn_sig_count = 0
        self.turn_left = False
        self.turn_right = False

    def init_ui(self):
        # Builds GUI
        # Start with a status bar
        self.statusBar().showMessage("Welcome!")

        self.grid_layout = QGridLayout()

        # Build common menu options
        menubar = self.menuBar()

        # File Menu Items
        file_menu = menubar.addMenu('&File')

        exit_action = QAction(QIcon(r'icons/icons8_Close_Window_48px.png'), '&Quit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit the program.')
        exit_action.triggered.connect(self.confirm_quit)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # build the entries in the dockable tool bar
        file_toolbar = self.addToolBar("File")
        file_toolbar.addAction(exit_action)

        # RP1210 Menu Items
        self.rp1210_menu = menubar.addMenu('&RP1210')

        help_menu = menubar.addMenu('&Help')
        about = QAction(QIcon(r'icons/icons8_Help_48px.png'), 'A&bout', self)
        about.setShortcut('F1')
        about.setStatusTip('Display a dialog box with information about the program.')
        about.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about)

        help_toolbar = self.addToolBar("Help")
        help_toolbar.addAction(about)

        # Setup the network status windows for logging
        info_box = {}
        info_box_area = {}
        info_layout = {}
        info_box_area_layout = {}
        self.previous_count = {}
        self.status_icon = {}
        self.previous_count = {}
        self.message_count_label = {}
        self.message_rate_label = {}
        self.message_duration_label = {}
        for key in ["J1939"]:
            # Create the container widget
            info_box_area[key] = QScrollArea()
            info_box_area[key].setWidgetResizable(True)
            info_box_area[key].setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            bar_size = QSize(150, 300)
            info_box_area[key].sizeHint()
            info_box[key] = QFrame(info_box_area[key])

            info_box_area[key].setWidget(info_box[key])
            info_box_area[key].setSizePolicy(QSizePolicy.Preferred,
                                             QSizePolicy.Expanding)

            # create a layout strategy for the container 
            info_layout[key] = QVBoxLayout()
            # set the layout so labels are at the top
            info_layout[key].setAlignment(Qt.AlignTop)
            # assign the layout strategy to the container
            info_box[key].setLayout(info_layout[key])

            info_box_area_layout[key] = QVBoxLayout()
            info_box_area[key].setLayout(info_box_area_layout[key])
            info_box_area_layout[key].addWidget(info_box[key])

            # Add some labels and content
            self.status_icon[key] = QLabel(
                "<html><img src='icons/icons8_Unavailable_48px.png'><br>Network<br>Unavailable</html>")
            self.status_icon[key].setAlignment(Qt.AlignCenter)

            self.previous_count[key] = 0
            self.message_count_label[key] = QLabel("Count: 0")
            self.message_count_label[key].setAlignment(Qt.AlignCenter)

            # self.message_duration = 0
            self.message_duration_label[key] = QLabel("Duration: 0 sec.")
            self.message_duration_label[key].setAlignment(Qt.AlignCenter)

            # self.message_rate = 0
            self.message_rate_label[key] = QLabel("Rate: 0 msg/sec")
            self.message_rate_label[key].setAlignment(Qt.AlignCenter)

            csv_save_button = QPushButton("Save as CSV")
            csv_save_button.setToolTip("Save all the {} Network messages to a comma separated values file.".format(key))
            if key == ["J1939"]:
                csv_save_button.clicked.connect(self.save_j1939_csv)
            if key == ["J1708"]:
                csv_save_button.clicked.connect(self.save_j1708_csv)

            info_layout[key].addWidget(QLabel("<html><h3>{} Status</h3></html>".format(key)))
            info_layout[key].addWidget(self.status_icon[key])
            info_layout[key].addWidget(self.message_count_label[key])
            info_layout[key].addWidget(self.message_rate_label[key])
            info_layout[key].addWidget(self.message_duration_label[key])

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setTabShape(QTabWidget.Triangular)
        self.sim = SimulationTab(self, self.tabs)
        self.J1939 = J1939Tab(self, self.tabs)

        # self.speed_graph = GraphDialog(self, title="Tone Ring Base Speed")
        # #self.speed_graph.set_yrange(9, 15)
        # self.speed_graph.set_xlabel("Time")
        # self.speed_graph.set_ylabel("Speed [km/h]")
        # self.speed_graph.set_title("Wheel-based Vehicle Speed from Vehicle Networks")

        self.grid_layout.addWidget(info_box_area["J1939"], 0, 0, 1, 1)
        self.grid_layout.addWidget(self.tabs, 0, 1, 4, 1)

        main_widget = QWidget()
        main_widget.setLayout(self.grid_layout)
        self.setCentralWidget(main_widget)

        self.show()

    def setup_RP1210_menus(self):
        connect_rp1210 = QAction(QIcon(r'icons/icons8_Connected_48px.png'), '&Client Connect', self)
        connect_rp1210.setShortcut('Ctrl+Shift+C')
        connect_rp1210.setStatusTip('Connect Vehicle Diagnostic Adapter')
        connect_rp1210.triggered.connect(self.selectRP1210)
        self.rp1210_menu.addAction(connect_rp1210)

        rp1210_version = QAction(QIcon(r'icons/icons8_Versions_48px.png'), '&Driver Version', self)
        rp1210_version.setShortcut('Ctrl+Shift+V')
        rp1210_version.setStatusTip('Show Vehicle Diagnostic Adapter Driver Version Information')
        rp1210_version.triggered.connect(self.display_version)
        self.rp1210_menu.addAction(rp1210_version)

        rp1210_detailed_version = QAction(QIcon(r'icons/icons8_More_Details_48px.png'), 'De&tailed Version', self)
        rp1210_detailed_version.setShortcut('Ctrl+Shift+T')
        rp1210_detailed_version.setStatusTip('Show Vehicle Diagnostic Adapter Detailed Version Information')
        rp1210_detailed_version.triggered.connect(self.display_detailed_version)
        self.rp1210_menu.addAction(rp1210_detailed_version)

        rp1210_get_hardware_status = QAction(QIcon(r'icons/icons8_Steam_48px.png'), 'Get &Hardware Status', self)
        rp1210_get_hardware_status.setShortcut('Ctrl+Shift+H')
        rp1210_get_hardware_status.setStatusTip(
            'Determine details regarding the hardware interface status and its connections.')
        rp1210_get_hardware_status.triggered.connect(self.get_hardware_status)
        self.rp1210_menu.addAction(rp1210_get_hardware_status)

        rp1210_get_hardware_status_ex = QAction(QIcon(r'icons/icons8_System_Information_48px.png'),
                                                'Get &Extended Hardware Status', self)
        rp1210_get_hardware_status_ex.setShortcut('Ctrl+Shift+E')
        rp1210_get_hardware_status_ex.setStatusTip(
            'Determine the hardware interface status and whether the VDA device is physically connected.')
        rp1210_get_hardware_status_ex.triggered.connect(self.get_hardware_status_ex)
        self.rp1210_menu.addAction(rp1210_get_hardware_status_ex)

        disconnect_rp1210 = QAction(QIcon(r'icons/icons8_Disconnected_48px.png'), 'Client &Disconnect', self)
        disconnect_rp1210.setShortcut('Ctrl+Shift+D')
        disconnect_rp1210.setStatusTip('Disconnect all RP1210 Clients')
        disconnect_rp1210.triggered.connect(self.disconnectRP1210)
        self.rp1210_menu.addAction(disconnect_rp1210)

        self.RP1210_toolbar = self.addToolBar("RP1210")
        self.RP1210_toolbar.addAction(connect_rp1210)
        self.RP1210_toolbar.addAction(rp1210_version)
        self.RP1210_toolbar.addAction(rp1210_detailed_version)
        self.RP1210_toolbar.addAction(rp1210_get_hardware_status)
        self.RP1210_toolbar.addAction(rp1210_get_hardware_status_ex)
        self.RP1210_toolbar.addAction(disconnect_rp1210)

    def confirm_quit(self):
        self.close()

    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm Exit",
                                      "Are you sure you want to quit the program?",
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.Yes)
        if result == QMessageBox.Yes:
            logger.debug("Quitting.")
            event.accept()
        else:
            event.ignore()

    def selectRP1210(self, automatic=False):
        logger.debug("Select RP1210 function called.")
        selection = SelectRP1210()
        logger.debug(selection.dll_name)
        if not automatic:
            selection.show_dialog()
        elif not selection.dll_name:
            selection.show_dialog()

        dll_name = selection.dll_name
        protocol = selection.protocol
        deviceID = selection.deviceID
        speed = selection.speed

        if dll_name is None:  # this is what happens when you hit cancel
            return
        # Close things down
        try:
            self.close_clients()
        except AttributeError:
            pass
        try:
            for thread in self.read_message_threads:
                thread.runSignal = False
        except AttributeError:
            pass

        # Once an RP1210 DLL is selected, we can connect to it using the RP1210 helper file.
        self.RP1210 = RP1210Class(dll_name)

        if self.RP1210_toolbar is None:
            self.setup_RP1210_menus()

        # We want to connect to multiple clients with different protocols.
        self.client_ids = {"J1939": self.RP1210.get_client_id("J1939", deviceID, "{}".format(speed))}

        logger.debug('Client IDs: {}'.format(self.client_ids))

        # If there is a successful connection, save it.
        file_contents = {"dll_name": dll_name,
                         "protocol": protocol,
                         "deviceID": deviceID,
                         "speed": speed
                         }
        with open(selection.connections_file, "w") as rp1210_file:
            json.dump(file_contents, rp1210_file)

        # Set all filters to pass.  This allows messages to be read.
        # Constants are defined in an included file
        i = 0
        for protocol, nClientID in self.client_ids.items():
            QCoreApplication.processEvents()
            if nClientID is not None:
                # By turning on Echo Mode, our logger process can record sent messages as well as received.
                fpchClientCommand = (c_char * RP1210_BUFFER_SIZE)()
                fpchClientCommand[0] = 1  # Echo mode on
                return_value = self.RP1210.SendCommand(c_short(RP1210_Echo_Transmitted_Messages),
                                                       c_short(nClientID),
                                                       byref(fpchClientCommand), 1)
                logger.debug('RP1210_Echo_Transmitted_Messages returns {:d}: {}'.format(return_value,
                                                                                        self.RP1210.get_error_code(
                                                                                            return_value)))

                # Set all filters to pass
                return_value = self.RP1210.SendCommand(c_short(RP1210_Set_All_Filters_States_to_Pass),
                                                       c_short(nClientID),
                                                       None, 0)
                if return_value == 0:
                    logger.debug("RP1210_Set_All_Filters_States_to_Pass for {} is successful.".format(protocol))
                    # setup a Receive queue. This keeps the GUI responsive and enables messages to be received.
                    self.rx_queues[protocol] = queue.Queue(10000)
                    self.tx_queues[protocol] = queue.Queue(10000)
                    self.read_message_threads[protocol] = RP1210ReadMessageThread(self,
                                                                                  self.rx_queues[protocol],
                                                                                  self.tx_queues[protocol],
                                                                                  self.RP1210.ReadMessage,
                                                                                  self.RP1210.SendMessage,
                                                                                  nClientID,
                                                                                  protocol)
                    self.read_message_threads[protocol].setDaemon(
                        True)  # needed to close the thread when the application closes.
                    self.read_message_threads[protocol].start()
                    logger.debug("Started RP1210ReadMessage Thread.")

                    self.statusBar().showMessage("{} connected using {}".format(protocol, dll_name))
                else:
                    debug_str = 'RP1210_Set_All_Filters_States_to_Pass returns {:d}: {}'
                    logger.debug(debug_str.format(return_value, self.RP1210.get_error_code(return_value)))

                if protocol == "J1939":
                    fpchClientCommand[0] = 0x00  # 0 = as fast as possible milliseconds
                    fpchClientCommand[1] = 0x00
                    fpchClientCommand[2] = 0x00
                    fpchClientCommand[3] = 0x00

                    return_value = self.RP1210.SendCommand(c_short(RP1210_Set_J1939_Interpacket_Time),
                                                           c_short(nClientID),
                                                           byref(fpchClientCommand), 4)
                    logger.debug('RP1210_Set_J1939_Interpacket_Time returns {:d}: {}'.format(return_value,
                                                                                             self.RP1210.get_error_code(
                                                                                                 return_value)))


            else:
                logger.debug(
                    "{} Client not connected for All Filters to pass. No Queue will be set up.".format(protocol))

        if self.client_ids["J1939"] is None:
            QMessageBox.information(self, "RP1210 Client Not Connected.",
                                    "The default RP1210 Device was not found or is unplugged. Please reconnect your "
                                    "Vehicle Diagnostic Adapter (VDA) and select the RP1210 device to use.")
        # else:
        #     self.speed_graph.show()

    def check_connections(self):
        '''
        This function checks the VDA hardware status function to see if it has seen network traffic in the last second.
        
        '''
        network_connection = {}

        for key in ["J1939"]:
            network_connection[key] = False
            try:
                current_count = self.read_message_threads[key].message_count
                duration = time.time() - self.read_message_threads[key].start_time
                self.message_duration_label[key].setText(
                    "<html><img src='icons/icons8_Connected_48px.png'><br>Client Connected<br>{:0.0f} "
                    "sec.</html>".format(
                        duration))
                network_connection[key] = True
            except (KeyError, AttributeError) as e:
                current_count = 0
                duration = 0
                self.message_duration_label[key].setText(
                    "<html><img src='icons/icons8_Disconnected_48px.png'><br>Client Disconnected<br>{:0.0f} "
                    "sec.</html>".format(
                        duration))

            count_change = current_count - self.previous_count[key]
            self.previous_count[key] = current_count
            # See if messages come in. Change the 
            if count_change > 0 and not self.network_connected[key]:
                self.status_icon[key].setText("<html><img src='icons/icons8_Ok_48px.png'><br>Network<br>Online</html>")
                self.network_connected[key] = True
            elif count_change == 0 and self.network_connected[key]:
                self.status_icon[key].setText(
                    "<html><img src='icons/icons8_Unavailable_48px.png'><br>Network<br>Unavailable</html>")
                self.network_connected[key] = False

            self.message_count_label[key].setText("Message Count:\n{}".format(humanize.intcomma(current_count)))
            self.message_rate_label[key].setText("Message Rate:\n{} msg/sec".format(count_change))

        # return True if any connection is present.
        for key, val in network_connection.items():
            if val:
                return True
        return False

    def get_hardware_status_ex(self):
        """
        Show a dialog box for valid connections for the extended get hardware status command implemented in the 
        vendor's RP1210 DLL.
        """
        logger.debug("get_hardware_status_ex")
        for protocol, nClientID in self.client_ids.items():
            if nClientID is not None:
                self.RP1210.get_hardware_status_ex(nClientID)
                return
        QMessageBox.warning(self,
                            "Connection Not Present",
                            "There were no Client IDs for an RP1210 device that support the extended hardware status "
                            "command.",
                            QMessageBox.Cancel,
                            QMessageBox.Cancel)

    def get_hardware_status(self):
        """
        Show a dialog box for valid connections for the regular get hardware status command implemented in the 
        vendor's RP1210 DLL.
        """
        logger.debug("get_hardware_status")
        for protocol, nClientID in self.client_ids.items():
            if nClientID is not None:
                self.RP1210.get_hardware_status(nClientID)
                return
        QMessageBox.warning(self,
                            "Connection Not Present",
                            "There were no Client IDs for an RP1210 device that support the hardware status command.",
                            QMessageBox.Cancel,
                            QMessageBox.Cancel)

    def display_detailed_version(self):
        """
        Show a dialog box for valid connections for the detailed version command implemented in the 
        vendor's RP1210 DLL.
        """
        logger.debug("display_detailed_version")
        for protocol, nClientID in self.client_ids.items():
            if nClientID is not None:
                self.RP1210.display_detailed_version(nClientID)
                return
        # otherwise show a dialog that there are no client IDs
        QMessageBox.warning(self,
                            "Connection Not Present",
                            "There were no Client IDs for an RP1210 device.",
                            QMessageBox.Cancel,
                            QMessageBox.Cancel)

    def display_version(self):
        """
        Show a dialog box for valid connections for the extended get hardware status command implemented in the 
        vendor's RP1210 DLL. This does not require connection to a device, just a valid RP1210 DLL.
        """
        logger.debug("display_version")
        self.RP1210.display_version()

    def disconnectRP1210(self):
        """
        Close all the RP1210 read message threads and disconnect the client.
        """
        logger.debug("disconnectRP1210")
        for protocol, nClientID in self.client_ids.items():
            try:
                self.read_message_threads[protocol].runSignal = False
                del self.read_message_threads[protocol]
            except KeyError:
                pass
            self.client_ids[protocol] = None
        for n in range(128):
            try:
                self.RP1210.ClientDisconnect(n)
            except:
                pass
        logger.debug("RP1210.ClientDisconnect() Finished.")

    def send_j1939_message(self, PGN, data_bytes, DA=0xff, SA=0xf9, priority=6, BAM=True):
        # initialize the buffer
        if self.client_ids["J1939"] is not None:
            b0 = PGN & 0xff
            b1 = (PGN & 0xff00) >> 8
            b2 = (PGN & 0xff0000) >> 16
            if BAM and len(data_bytes) > 8:
                priority |= 0x80
            message_bytes = bytes([b0, b1, b2, priority, SA, DA])
            message_bytes += data_bytes
            self.RP1210.send_message(self.client_ids["J1939"], message_bytes)

    def find_j1939_data(self, pgn, sa=0):
        """
        A function that returns bytes data from the data dictionary holding J1939 data.
        This function is used to check the presence of data in the dictionary.
        """
        try:
            return self.J1939.j1939_unique_ids[repr((pgn, sa))]["Bytes"]
        except KeyError:
            return False

    def send_brake(self):
        priority = 0x06
        SA = 0  # Engine
        DA = 255  # Global
        PGN = 0xFEF1  # CCVS, 65265
        b0 = 0xff
        b1 = 0xff
        b2 = 0xff
        b3 = 0xff
        b4 = 0b11110011
        b5 = 0xff
        b6 = 0xff
        b7 = 0xff
        # Update Speed Record
        (b2, b3) = struct.pack("<H", self.sim.speed_slider.value())
        if self.sim.brake_button.isDown():
            b4 |= 1 << 2
        else:
            b4 &= ~(1 << 2)
        message_bytes = bytes([0xF1, 0xFE, 0x00, priority, SA, DA, b0, b1, b2, b3, b4, b5, b6, b7])
        if self.client_ids["J1939"] is not None:
            self.RP1210.send_message(self.client_ids["J1939"], message_bytes)

    def send_turn(self):
        # Check prior state to new state
        right, left = self.sim.right_turn.isChecked(), self.sim.left_turn.isChecked()
        if right == self.turn_right and left == self.turn_left and self.turn_sig_count < 9:
            # no state change, and 1 second has not elapsed
            self.turn_sig_count = self.turn_sig_count + 1
            return
        self.turn_sig_count = 0
        self.turn_left = left
        self.turn_right = right

        priority = 0x06
        SA = 0  # Engine
        DA = 255  # Global
        # Turn Signal work, and keeping it in line with 1-indexed
        b1 = b2 = b3 = b4 = b5 = b6 = b7 = b8 = 0
        if self.sim.left_turn.isChecked() and self.sim.right_turn.isChecked():
            b2 |= 0b11100000
        elif self.sim.left_turn.isChecked():
            b2 |= 0b00010000  # 0b0001
        elif self.sim.right_turn.isChecked():
            b2 |= 0b00100000  # 0b0010
        # SA = 0x37  # 55 - Lighting - Operator Controls
        pgn = 64972  # Operators External Light Controls
        turn_message = bytes([(pgn & 0xff), (pgn >> 8), 0x00, priority, SA, DA, b1, b2, b3, b4, b5, b6, b7, b8])

        if self.client_ids["J1939"] is not None:
            self.RP1210.send_message(self.client_ids["J1939"], turn_message)

    def read_rp1210(self):
        # This function needs to run often to keep the queues from filling
        # try:
        for protocol in self.rx_queues.keys():
            start_time = time.time()
            while self.rx_queues[protocol].qsize():
                # Get a message from the queue. These are raw bytes
                rx_message = self.rx_queues[protocol].get()
                if protocol == "J1939":
                    try:
                        self.J1939.fill_j1939_table(rx_message)
                        # J1939logger.info(rx_message)
                    except:
                        logger.debug(traceback.format_exc())
                if (time.time() - start_time) > self.update_rate:  # give some time to process events
                    logger.debug("Can't keep up with messages.")
                    return

    def show_about_dialog(self):
        logger.debug("show_about_dialog Request")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("About {}".format(self.title))
        msg.setInformativeText("""Icons by Icons8\nhttps://icons8.com/""")
        msg.setWindowTitle("About")
        msg.setDetailedText("There will be some details here.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowModality(Qt.ApplicationModal)
        msg.exec_()

    def close_clients(self):
        logger.debug("close_clients Request")
        for protocol, nClientID in self.client_ids.items():
            logger.debug("Closing {}".format(protocol))
            self.RP1210.disconnectRP1210(nClientID)
            if protocol in self.read_message_threads:
                self.read_message_threads[protocol].runSignal = False
        logger.debug("Exiting.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    execute = BrakeAndSpeedSignalGenerator()
    sys.exit(app.exec_())
