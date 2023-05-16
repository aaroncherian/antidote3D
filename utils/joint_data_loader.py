import numpy as np

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
