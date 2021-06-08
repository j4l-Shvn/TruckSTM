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
                             QTabWidget,
                             QSizePolicy
                             )
from PyQt5.QtCore import Qt, QTimer, QAbstractTableModel, QCoreApplication, QVariant, QAbstractItemModel, \
    QSortFilterProxyModel
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
from Graphing.graphing import *

import logging

logger = logging.getLogger(__name__)


class SimulationTab(QWidget):
    def __init__(self, parent, tabs):
        super(SimulationTab, self).__init__()
        self.root = parent
        self.tabs = tabs
        self.setup_ui()

    def setup_ui(self):
        self.simulation_tab = QWidget()
        self.tabs.addTab(self.simulation_tab, "Simulation")
        tab_layout = QVBoxLayout()
        speed_box = QGroupBox("Wheel-based Vehicle Speed")
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(65000)
        self.speed_slider.setSingleStep(1)
        self.speed_slider.setFocusPolicy(Qt.StrongFocus)
        # self.speed_slider.setTickPosition(QSlider.TicksBothSides)
        self.speed_slider.valueChanged.connect(self.change_slider_value)

        self.speed_display = QLabel("XX km/h")

        self.brake_button = QPushButton("Press Brake")
        self.brake_button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        # changing color of button 
        # self.brake_button.setStyleSheet("background-color : Green")
        # self.brake_button
        self.brake_button.setStyleSheet("QPushButton"
                                        "{"
                                        "background-color : lightgreen;"
                                        "}"
                                        "QPushButton::pressed"
                                        "{"
                                        "background-color : red;"
                                        "}"
                                        )
        # Turn Signals
        self.left_turn = QPushButton("Left")
        self.left_turn.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        self.left_turn.setStyleSheet("QPushButton"
                                     "{"
                                     "background-color : yellow;"
                                     "}"
                                     "QPushButton::pressed"
                                     "{"
                                     "background-color : red;"
                                     "}"
                                     )
        self.left_turn.setCheckable(True)
        self.right_turn = QPushButton("Right")
        self.right_turn.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        self.right_turn.setStyleSheet("QPushButton"
                                      "{"
                                      "background-color : yellow;"
                                      "}"
                                      "QPushButton::pressed"
                                      "{"
                                      "background-color : red;"
                                      "}"
                                      )
        self.right_turn.setCheckable(True)

        # Create a layout for that box using a grid
        simulation_layout = QGridLayout()
        # Add the widgets into the layout
        simulation_layout.addWidget(self.speed_slider, 0, 0, 1, 1)
        simulation_layout.addWidget(self.speed_display, 0, 1, 1, 1)
        simulation_layout.addWidget(self.brake_button, 1, 0, 1, 2)
        simulation_layout.addWidget(self.left_turn, 2, 0, 1, 1)
        simulation_layout.addWidget(self.right_turn, 2, 1, 1, 1)

        # setup the layout to be displayed in the box
        speed_box.setLayout(simulation_layout)
        tab_layout.addWidget(speed_box)
        self.simulation_tab.setLayout(tab_layout)

    def change_slider_value(self, value):
        self.speed_display.setText("{:0.2f} km/h".format(value / 256))
