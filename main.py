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
from utils.joint_data_holder import JointDataHolder
from utils.reconstructed_data_holder import ReconstructedDataHolder
import os

class FileManager:
    def __init__(self, recording_session_folder_path: Union[str,Path]):
        self.recording_session_folder_path = recording_session_folder_path
        
        self.video_folder_path = recording_session_folder_path/'synchronized_videos'
        self.joint_2d_data_path = recording_session_folder_path/ 'output_data' / 'raw_data' / 'dlc_leg_2d.npy'
        f = 2

    def get_video_folder_path(self):
        return self.video_folder_path
    
    def get_joint_2d_data(self):

        joint_2d_data_all = np.load(self.joint_2d_data_path)
        joint_2d_data_xy = joint_2d_data_all[:,:,:,:]
        return joint_2d_data_xy
    
class MainWindow(QMainWindow):
    def __init__(self, recording_session_folder_path: Union[str,Path], calibration_toml_path: Union[str,Path]):
        super().__init__()
        self.setWindowTitle('Video Viewer')
        self.tab_widget = QTabWidget()

        self.file_manager = FileManager(recording_session_folder_path)

        joint_2d_data = self.file_manager.get_joint_2d_data()
        video_folder_path = self.file_manager.get_video_folder_path()


        self.joint_data_loader = JointDataHolder(joint_2d_data)
        self.reconstructed_data_holder = ReconstructedDataHolder(calibration_toml_path,self.joint_data_loader)

        # self.reconstructed_data_holder.reconstruct_new_3d_data()

        save_tab = MainTab(self.joint_data_loader, self.reconstructed_data_holder)
        self.tab_widget.addTab(save_tab, "Save")
    
        # Load each video in the video folder into a new tab
        for i, video_path in enumerate(video_folder_path.iterdir()):
            if video_path.suffix in ['.mp4', '.avi']:  # add more video formats if needed
                video_tab = VideoTab(video_path, self.joint_data_loader, i)
                self.tab_widget.addTab(video_tab, video_path.name)

        # self.setStyleSheet("background-color: #F6F9F8;")  # Set background color to white

        self.setCentralWidget(self.tab_widget)


def main():
    video_folder = Path(r'D:\2023-06-07_JH\1.0_recordings\treadmill_calib\sesh_2023-06-07_12_06_15_JH_flexion_neutral_trial_1')  # replace with your actual folder path
    calibration_toml_path = Path(r"D:\2023-06-07_JH\1.0_recordings\treadmill_calib\sesh_2023-06-07_11_10_50_treadmill_calibration_01\sesh_2023-06-07_11_10_50_treadmill_calibration_01_camera_calibration.toml")
    app = QApplication([])
    # app.setStyleSheet("QPushButton { background-color: blue; color: black; }")
    window = MainWindow(video_folder, calibration_toml_path)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()