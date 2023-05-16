import cv2
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QCheckBox, QPushButton, QGroupBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from pathlib import Path

import numpy as np

from typing import Union

class JointDataLoader:
    def __init__(self, joint_2d_data):
        self.original_joint_data = joint_2d_data
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


class FileManager:
    def __init__(self, recording_session_folder_path: Union[str,Path]):
        self.recording_session_folder_path = recording_session_folder_path
        
        self.video_folder_path = recording_session_folder_path/'synchronized_videos'
        self.joint_2d_data_path = recording_session_folder_path/ 'output_data' / 'raw_data' / 'mediapipe2dData_numCams_numFrames_numTrackedPoints_pixelXY.npy'

    def get_video_folder_path(self):
        return self.video_folder_path
    
    def get_joint_2d_data(self):
        return np.load(self.joint_2d_data_path)

class MainWindow(QMainWindow):
    def __init__(self, recording_session_folder_path: Union[str,Path]):
        super().__init__()
        self.setWindowTitle('Video Viewer')
        self.tab_widget = QTabWidget()

        self.file_manager = FileManager()

        joint_2d_data = self.file_manager.get_joint_2d_data_path
        video_folder_path = self.file_manager.get_video_folder_path


        self.joint_data_loader = JointDataLoader(joint_2d_data)

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