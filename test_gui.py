import cv2
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QCheckBox, QPushButton, QGroupBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from pathlib import Path

import numpy as np
mediapipe_indices = ['nose',
    'left_eye_inner',
    'left_eye',
    'left_eye_outer',
    'right_eye_inner',
    'right_eye',
    'right_eye_outer',
    'left_ear',
    'right_ear',
    'mouth_left',
    'mouth_right',
    'left_shoulder',
    'right_shoulder',
    'left_elbow',
    'right_elbow',
    'left_wrist',
    'right_wrist',
    'left_pinky',
    'right_pinky',
    'left_index',
    'right_index',
    'left_thumb',
    'right_thumb',
    'left_hip',
    'right_hip',
    'left_knee',
    'right_knee',
    'left_ankle',
    'right_ankle',
    'left_heel',
    'right_heel',
    'left_foot_index',
    'right_foot_index']

joint_groups = [
    {"name": "Face", "joints": ["nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner", "right_eye", 
    "right_eye_outer", "left_ear", "right_ear", "mouth_left", "mouth_right"]},
    {"name": "Right Arm", "joints": ["right_shoulder", "right_elbow", "right_wrist", "right_pinky", "right_index", "right_thumb"]},
    {"name": "Left Arm", "joints": ["left_shoulder", "left_elbow", "left_wrist", "left_pinky", "left_index", "left_thumb"]},
    {"name": "Right Leg", "joints": ["right_hip", "right_knee", "right_ankle", "right_heel", "right_foot_index"]},
    {"name": "Left Leg", "joints": ["left_hip", "left_knee", "left_ankle", "left_heel", "left_foot_index"]},
]


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


class JointDataLoader:
    def __init__(self, joint_data_path):
        self.original_joint_data = np.load(joint_data_path)
        self.joint_data = np.copy(self.original_joint_data)
        self.plotting_joint_data = self.joint_data[:, :, :33, :]

    def get_joints(self, camera_num, frame_num):
        return self.plotting_joint_data[camera_num, frame_num]

    def remove_joint(self, camera_num, joint_num):
        # Make sure the joint number and camera number are within bounds
        if joint_num < 0 or joint_num >= self.joint_data.shape[2]:
            raise ValueError("Invalid joint number")
        if camera_num < 0 or camera_num >= self.joint_data.shape[0]:
            raise ValueError("Invalid camera number")

        # Set the joint data for the specified joint to NaN for the specified camera across all frames
        self.plotting_joint_data[camera_num, :, joint_num,:] = np.nan
        self.joint_data[camera_num, :, joint_num,:] = np.nan

    def reinstate_joint(self, camera_num, joint_num):
        # Make sure the joint number and camera number are within bounds
        if joint_num < 0 or joint_num >= self.joint_data.shape[2]:
            raise ValueError("Invalid joint number")
        if camera_num < 0 or camera_num >= self.joint_data.shape[0]:
            raise ValueError("Invalid camera number")

        # Set the joint data for the specified joint to the original value for the specified camera across all frames
        self.plotting_joint_data[camera_num, :, joint_num,:] = self.original_joint_data[camera_num, :, joint_num]
        self.joint_data[camera_num, :, joint_num,:] = self.original_joint_data[camera_num, :, joint_num]





class CheckBoxList(QWidget):
    def __init__(self, items):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # self.list_widget = QListWidget()
        # self.layout.addWidget(self.list_widget)

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
        self.canvas.draw()

    def update_joints(self):
        for joint_name, checkbox in self.joint_list.checkboxes.items():
            joint_num = mediapipe_indices.index(joint_name)
            if checkbox.isChecked():
                self.joint_data_loader.reinstate_joint(self.camera_num, joint_num)
            else:
                self.joint_data_loader.remove_joint(self.camera_num, joint_num)
        
        self.update_frame(self.slider.value())


class MainWindow(QMainWindow):
    def __init__(self, recording_session_folder):
        super().__init__()
        self.setWindowTitle('Video Viewer')
        self.tab_widget = QTabWidget()

        video_folder = recording_session_folder / 'synchronized_videos'
        joint_data_path = recording_session_folder / 'output_data' / 'raw_data' / 'mediapipe2dData_numCams_numFrames_numTrackedPoints_pixelXY.npy'
        self.joint_data_loader = JointDataLoader(joint_data_path)

        # Load each video in the video folder into a new tab
        for i, video_path in enumerate(video_folder.iterdir()):
            if video_path.suffix in ['.mp4', '.avi']:  # add more video formats if needed
                video_tab = VideoTab(video_path, self.joint_data_loader, i)
                self.tab_widget.addTab(video_tab, video_path.name)

        save_tab = SaveTab(self.joint_data_loader)
        self.tab_widget.addTab(save_tab, "Save")

        self.setCentralWidget(self.tab_widget)


def main():
    video_folder = Path(r'D:\footropter_pilot_04_19_23\1.0_recordings\recordings_calib_3\sesh_2023-04-19_16_40_09_MDN_antidote')  # replace with your actual folder path

    app = QApplication([])
    window = MainWindow(video_folder)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
