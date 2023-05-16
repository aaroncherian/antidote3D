
import cv2
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QCheckBox, QPushButton, QGroupBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from pathlib import Path

from utils.mediapipe_joints import joint_groups

import numpy as np

from typing import Union


class CheckBoxList(QWidget):
    def __init__(self, items):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.checkboxes = []  # Add this line to initialize a list to store the checkboxes

        self.checkboxes = {}
        for group in joint_groups:
            group_box = QGroupBox(group["name"])
            group_layout = QVBoxLayout()
            group_box.setLayout(group_layout)
            self.layout.addWidget(group_box)
            for joint_name in group["joints"]:
                checkbox = QCheckBox(joint_name)
                checkbox.setChecked(True)
                group_layout.addWidget(checkbox)
                self.checkboxes[joint_name] = checkbox

    def get_checked_items(self):
        checked_items = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            checkbox = self.list_widget.itemWidget(item)
            if checkbox.isChecked():
                checked_items.append(checkbox.text())
        return checked_items