import cv2
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QCheckBox, QPushButton, QGroupBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from pathlib import Path

import numpy as np

from typing import Union

from widgets.video_tab import VideoTab
from widgets.main_window_tab import MainTab
from utils.joint_data_loader import JointDataLoader

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

        self.file_manager = FileManager(recording_session_folder_path)

        joint_2d_data = self.file_manager.get_joint_2d_data()
        video_folder_path = self.file_manager.get_video_folder_path()


        self.joint_data_loader = JointDataLoader(joint_2d_data)
        
        save_tab = MainTab(self.joint_data_loader)
        self.tab_widget.addTab(save_tab, "Save")
    
        # Load each video in the video folder into a new tab
        for i, video_path in enumerate(video_folder_path.iterdir()):
            if video_path.suffix in ['.mp4', '.avi']:  # add more video formats if needed
                video_tab = VideoTab(video_path, self.joint_data_loader, i)
                self.tab_widget.addTab(video_tab, video_path.name)

        self.setStyleSheet("background-color: #F6F9F8;")  # Set background color to white

        self.setCentralWidget(self.tab_widget)


def main():
    video_folder = Path(r'D:\2023-05-10_session_aaron_michael_jon_milo\1.0_recordings\calibration_one\sesh_2023-05-10_16_31_56_JSM_')  # replace with your actual folder path

    app = QApplication([])
    window = MainWindow(video_folder)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()