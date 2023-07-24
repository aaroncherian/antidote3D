import numpy as np

class JointDataHolder:
    def __init__(self, joint_2d_data):
        self.original_joint_data = joint_2d_data
        self.joint_data = np.copy(self.original_joint_data)
        self.joint_data = self.apply_confidence_threshold(self.joint_data, 0.7)
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

    def apply_confidence_threshold(self,array, threshold):
            """
            Set X,Y values to zero where the corresponding confidence value is below threshold.

            Parameters:
            - array: 4D numpy array with shape (num_cameras, num_frames, num_markers, 3)
            The last dimension should have the structure (x, y, confidence).
            - threshold: Confidence threshold. All X,Y values with a confidence below this threshold will be set to zero.
            """
            confidences = array[:, :, :, 2]  # Get the confidence values
            mask = confidences < threshold  # Create a boolean mask where the confidence values are below threshold
            array[mask, 0:2] = np.nan  # Set the X,Y values to zero where the mask is True
            return array