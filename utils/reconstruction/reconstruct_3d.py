import numpy as np
from utils.reconstruction.anipose_object_loader import load_anipose_calibration_toml_from_path
import multiprocessing


def process_2d_data_to_3d(mediapipe_2d_data: np.ndarray, calibration_toml_path: str, mediapipe_confidence_cutoff_threshold: float, kill_event: multiprocessing.Event = None):
    # Load calibration object
    anipose_calibration_object = load_anipose_calibration_toml_from_path(calibration_toml_path)

    # 3D reconstruction
    spatial_data3d, reprojection_error_data3d = triangulate_3d_data(
        anipose_calibration_object=anipose_calibration_object,
        mediapipe_2d_data=mediapipe_2d_data,
        mediapipe_confidence_cutoff_threshold=mediapipe_confidence_cutoff_threshold,
        kill_event=kill_event,
    )

    # Handle output
    # (You'll need to fill in this part with whatever you want to do with the results)
    return spatial_data3d, reprojection_error_data3d


def triangulate_3d_data(
    anipose_calibration_object,
    mediapipe_2d_data: np.ndarray,
    mediapipe_confidence_cutoff_threshold: float,
    kill_event: multiprocessing.Event = None,
):
    # Validation
    number_of_cameras, number_of_frames, number_of_tracked_points, number_of_spatial_dimensions = mediapipe_2d_data.shape
    if number_of_spatial_dimensions != 2:
        raise ValueError(f"Expected 2D data, got {number_of_spatial_dimensions} dimensions")

    mediapipe_2d_data = threshold_by_confidence(
        mediapipe_2d_data=mediapipe_2d_data,
        mediapipe_confidence_cutoff_threshold=mediapipe_confidence_cutoff_threshold,
    )

    # Reshape data to collapse across 'frames' so it becomes [number_of_cameras, number_of_2d_points(numFrames*numPoints), XY]
    data2d_flat = mediapipe_2d_data.reshape(number_of_cameras, -1, 2)

    # Triangulate
    data3d_flat = anipose_calibration_object.triangulate(data2d_flat, progress=True, kill_event=kill_event)

    # Reshape the flat data back to [numFrames, numPoints, XYZ]
    spatial_data3d_numFrames_numTrackedPoints_XYZ = data3d_flat.reshape(number_of_frames, number_of_tracked_points, 3)

    # Compute reprojection error
    data3d_reprojectionError_flat = anipose_calibration_object.reprojection_error(data3d_flat, data2d_flat, mean=True)
    reprojection_error_data3d_numFrames_numTrackedPoints = data3d_reprojectionError_flat.reshape(number_of_frames, number_of_tracked_points)

    # Filter data with high reprojection error
    spatial_data3d_numFrames_numTrackedPoints_XYZ = remove_3d_data_with_high_reprojection_error(
        data3d_numFrames_numTrackedPoints_XYZ=spatial_data3d_numFrames_numTrackedPoints_XYZ,
        data3d_numFrames_numTrackedPoints_reprojectionError=reprojection_error_data3d_numFrames_numTrackedPoints,
    )

    return spatial_data3d_numFrames_numTrackedPoints_XYZ, reprojection_error_data3d_numFrames_numTrackedPoints


def threshold_by_confidence(
    mediapipe_2d_data: np.ndarray,
    mediapipe_confidence_cutoff_threshold: float = 0.0,
):
    mediapipe_2d_data[mediapipe_2d_data <= mediapipe_confidence_cutoff_threshold] = np.NaN

    number_of_nans = np.sum(np.isnan(mediapipe_2d_data))
    number_of_points = np.prod(mediapipe_2d_data.shape)
    percentage_that_are_nans = (np.sum(np.isnan(mediapipe_2d_data)) / number_of_points) * 100

    return mediapipe_2d_data

def remove_3d_data_with_high_reprojection_error(
    data3d_numFrames_numTrackedPoints_XYZ: np.ndarray,
    data3d_numFrames_numTrackedPoints_reprojectionError: np.ndarray,
):

    return data3d_numFrames_numTrackedPoints_XYZ

