from utils.reconstruction.reconstruct_3d import process_2d_data_to_3d

class ReconstructedDataHolder:
    def __init__(self, calibration_toml_path,joint_data_loader):
        self.calibration_toml_path = calibration_toml_path
        self.joint_data_loader = joint_data_loader
    
    def reconstruct_new_3d_data(self, start_frame=None, end_frame=None):
        new_3d_data, repro_error = process_2d_data_to_3d(mediapipe_2d_data=self.joint_data_loader.joint_data[:,start_frame:end_frame,:,:], calibration_toml_path=self.calibration_toml_path, mediapipe_confidence_cutoff_threshold=.5)
        self.new_3d_data = new_3d_data