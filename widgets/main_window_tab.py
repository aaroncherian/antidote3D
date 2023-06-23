from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QCheckBox, QPushButton, QGroupBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from pathlib import Path

from utils.reconstruction.reconstruct_3d import process_2d_data_to_3d
import numpy as np
class MainTab(QWidget):
    def __init__(self, joint_data_loader):
        super().__init__()
        self.joint_data_loader = joint_data_loader

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.path_label = QLabel("Save Path:")
        self.layout.addWidget(self.path_label)

        self.path_input = QLineEdit()
        self.layout.addWidget(self.path_input)

        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)
        self.layout.addWidget(self.save_button)

        self.reconstruction_button = QPushButton("Reconstruct")
        self.reconstruction_button.clicked.connect(self.reconstruct_3d_data)
        self.layout.addWidget(self.reconstruction_button)

    def save_data(self):
        path = Path(self.path_input.text())
        np.save(path / 'mediapipe2dData_numCams_numFrames_numTrackedPoints_pixelXY.npy', self.joint_data_loader.joint_data)

    def reconstruct_3d_data(self):
        process_2d_data_to_3d(self.joint_data_loader.joint_data,)
