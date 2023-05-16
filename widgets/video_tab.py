
import cv2
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QCheckBox, QPushButton, QGroupBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from pathlib import Path

from utils.mediapipe_joints import mediapipe_indices
from widgets.checkbox_list_widget import CheckBoxList
import numpy as np

class VideoLoader:
    def __init__(self, video_path):
        self.video = cv2.VideoCapture(str(video_path))
        self.num_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_frame(self, frame_num):
        # Seek to the specified frame
        self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

        # Read the current frame
        _, frame = self.video.read()

        # Convert the frame from BGR to RGB
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)



class VideoTab(QWidget):
    def __init__(self, video_path, joint_data_loader, camera_num):
        super().__init__()
        self.video_loader = VideoLoader(video_path)
        self.joint_data_loader = joint_data_loader
        self.camera_num = camera_num

        # Create the main layout
        self.layout = QVBoxLayout()  # Back to a QVBoxLayout
        self.setLayout(self.layout)

        # Create the slider and add it to the main layout
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, self.video_loader.num_frames - 1)
        self.slider.valueChanged.connect(self.update_frame)
        self.layout.addWidget(self.slider)

        # Create a secondary layout for the video and joint list
        self.secondary_layout = QHBoxLayout()
        self.layout.addLayout(self.secondary_layout)

        # Initialize a matplotlib figure and add it to a canvas widget
        self.fig = Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)

        self.secondary_layout.addWidget(self.canvas)

        # Add the joint list to the right side of the video
        self.joint_list = CheckBoxList(mediapipe_indices)
        self.secondary_layout.addWidget(self.joint_list)

        self.update_button = QPushButton("Update Joints")
        self.update_button.clicked.connect(self.update_joints)
        self.layout.addWidget(self.update_button)

        # Display the first frame
        self.update_frame(0)

        self.setStyleSheet("""
            QCheckBox {
                color: #016b65;
            }

            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }

        """)

        

    def update_frame(self, value):
        # Get the specified frame
        frame = self.video_loader.get_frame(value)

        # Get the 2D joint positions for the current frame
        joints = self.joint_data_loader.get_joints(self.camera_num,value)

        # Clear the previous frame
        self.fig.clear()

        # Plot the current frame on the figure
        ax = self.fig.add_subplot(111)
        ax.imshow(frame)

        # Hide the axes labels (numbers and tick marks)
        ax.axis('off')

        height, width, _ = frame.shape
        ax.set_xlim([0, width])
        ax.set_ylim([height, 0])  # the y-axis is inverted in image coordinates


        valid_joints = [joint for joint in joints if not np.isnan(joint).any()]

        # Plot the 2D joints on the figure
        if valid_joints:  # only plot if there are valid joints
            for joint in valid_joints:
                ax.scatter(joint[0],joint[1], color = 'white', s = 4)

        # Refresh the canvas
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        # self.canvas.setFixedSize(width, height)


        self.canvas.draw()

    def update_joints(self):
        for joint_name, checkbox in self.joint_list.checkboxes.items():
            joint_num = mediapipe_indices.index(joint_name)
            if checkbox.isChecked():
                self.joint_data_loader.reinstate_joint(self.camera_num, joint_num)
            else:
                self.joint_data_loader.remove_joint(self.camera_num, joint_num)
        
        self.update_frame(self.slider.value())