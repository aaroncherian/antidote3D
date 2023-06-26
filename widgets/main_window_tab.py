from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QWidget, QCheckBox, QPushButton, QGroupBox, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class ScatterPlot3DWidget(QWidget):
    def __init__(self, data_holder, parent=None):
        super(ScatterPlot3DWidget, self).__init__(parent)
        self.data_holder = data_holder

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 3D Scatter Plot
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.layout.addWidget(self.canvas)

        # Slider Layout
        self.slider_layout = QHBoxLayout()
        self.layout.addLayout(self.slider_layout)

        # Frame label
        self.frame_label = QLabel("Frame 0")
        self.slider_layout.addWidget(self.frame_label)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)  # Initially set to 0
        self.slider.setEnabled(False)  # Initially disabled
        self.slider.valueChanged.connect(self.update_plot)
        self.slider_layout.addWidget(self.slider)

        # Axis range
        self.ax_range = 900
        self.mean_x = 0
        self.mean_y = 0
        self.mean_z = 0

    def set_reconstructed_data(self, data):
        self.slider.setEnabled(True)
        self.slider.setMaximum(len(data) - 1)
        # Calculate mean for entire reconstructed data
        self.mean_x = np.nanmean(data[:, 0:33, 0])
        self.mean_y = np.nanmean(data[:, 0:33, 1])
        self.mean_z = np.nanmean(data[:, 0:33, 2])

    def update_plot(self, value):
        # Clear the current plot
        self.ax.cla()

        # Update frame label
        self.frame_label.setText(f"Frame {value}")

        # Get the data for the selected frame
        frame_data = self.data_holder.new_3d_data[value, 0:33, :]

        # Update the scatter plot with the new data
        self.ax.scatter(frame_data[:, 0], frame_data[:, 1], frame_data[:, 2])

        # Set equal axes based on mean for entire reconstructed data
        self.ax.set_xlim([self.mean_x - self.ax_range, self.mean_x + self.ax_range])
        self.ax.set_ylim([self.mean_y - self.ax_range, self.mean_y + self.ax_range])
        self.ax.set_zlim([self.mean_z - self.ax_range, self.mean_z + self.ax_range])

        # Redraw the plot
        self.canvas.draw()


class MainTab(QWidget):
    def __init__(self, joint_data_holder, reconstructed_data_holder):
        super().__init__()
        self.joint_data_holder = joint_data_holder
        self.reconstructed_data_holder = reconstructed_data_holder

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scatter_plot_widget = ScatterPlot3DWidget(self.reconstructed_data_holder)
        self.layout.addWidget(self.scatter_plot_widget)

        self.path_label = QLabel("Save Path:")
        self.layout.addWidget(self.path_label)

        self.path_input = QLineEdit()
        self.layout.addWidget(self.path_input)

        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)
        self.layout.addWidget(self.save_button)
        
        # Horizontal layout for start and end frame input
        self.frame_range_layout = QHBoxLayout()
        
        # Input for start frame
        self.start_frame_label = QLabel("Start Frame:")
        self.start_frame_input = QLineEdit()
        self.start_frame_input.setFixedWidth(50)  # Set a fixed width for the input field
        self.frame_range_layout.addWidget(self.start_frame_label)
        self.frame_range_layout.addWidget(self.start_frame_input)
        
        # Input for end frame
        self.end_frame_label = QLabel("End Frame:")
        self.end_frame_input = QLineEdit()
        self.end_frame_input.setFixedWidth(50)  # Set a fixed width for the input field
        self.frame_range_layout.addWidget(self.end_frame_label)
        self.frame_range_layout.addWidget(self.end_frame_input)
        
        # Add horizontal layout to the main layout
        self.layout.addLayout(self.frame_range_layout)

        self.reconstruction_button = QPushButton("Reconstruct")
        self.reconstruction_button.clicked.connect(self.reconstruct_3d_data)
        self.layout.addWidget(self.reconstruction_button)

    def save_data(self):
        path = Path(self.path_input.text())
        np.save(path / 'mediapipe2dData_numCams_numFrames_numTrackedPoints_pixelXY.npy', self.joint_data_holder.joint_data)

    def reconstruct_3d_data(self):
        # Get the start and end frame numbers from the input fields
        start_frame = int(self.start_frame_input.text())
        end_frame = int(self.end_frame_input.text())

        # Call the reconstruction method with the start and end frames as parameters
        self.reconstructed_data_holder.reconstruct_new_3d_data(start_frame=start_frame, end_frame=end_frame)

        self.scatter_plot_widget.set_reconstructed_data(self.reconstructed_data_holder.new_3d_data)

