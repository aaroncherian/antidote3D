import numpy as np
from utils.reconstruction.anipose_object_loader import load_anipose_calibration_toml_from_path
from utils.reconstruction.reprojection_filtering import filter_by_reprojection_error

import multiprocessing
from typing import Union
from pathlib import Path

def process_2d_data_to_3d(mediapipe_2d_data: np.ndarray, calibration_toml_path: str, mediapipe_confidence_cutoff_threshold: float, kill_event: multiprocessing.Event = None):
    # Load calibration object
    anipose_calibration_object = load_anipose_calibration_toml_from_path(calibration_toml_path)

    # 3D reconstruction
    spatial_data3d, reprojection_error_data3d = triangulate_3d_data(
        anipose_calibration_object=anipose_calibration_object,
        mediapipe_2d_data=mediapipe_2d_data,
        output_data_folder_path=None,
        kill_event=kill_event,
    )

    filtered_spatial_data3d, filtered_reprojection_error_data3d = filter_by_reprojection_error(
        reprojection_error_frame_marker= reprojection_error_data3d[:,:33],
        reprojection_error_threshold=17,
        mediapipe_2d_data=mediapipe_2d_data[:,:,:33,:],
        raw_skel3d_frame_marker_xyz=spatial_data3d[:,:33,:],
        anipose_calibration_object=anipose_calibration_object,
        output_data_folder_path=None,
        use_triangulate_ransac=False,

    )

    # Handle output
    # (You'll need to fill in this part with whatever you want to do with the results)
    return filtered_spatial_data3d, filtered_reprojection_error_data3d




def triangulate_3d_data(
    anipose_calibration_object,
    mediapipe_2d_data: np.ndarray,
    output_data_folder_path: Union[str, Path],
    use_triangulate_ransac: bool = False,
    kill_event: multiprocessing.Event = None,
):
    number_of_cameras = mediapipe_2d_data.shape[0]
    number_of_frames = mediapipe_2d_data.shape[1]
    number_of_tracked_points = mediapipe_2d_data.shape[2]
    number_of_spatial_dimensions = mediapipe_2d_data.shape[3]

    if not number_of_spatial_dimensions == 2:
        print(
            f"This is supposed to be 2D data but, number_of_spatial_dimensions: {number_of_spatial_dimensions}"
        )
        raise Exception

    # reshape data to collapse across 'frames' so it becomes [number_of_cameras,
    # number_of_2d_points(numFrames*numPoints), XY]
    data2d_flat = mediapipe_2d_data.reshape(number_of_cameras, -1, 2)

    print(
        f"Reconstructing 3d points from 2d points with shape: \n"
        f"number_of_cameras: {number_of_cameras},\n"
        f"number_of_frames: {number_of_frames}, \n"
        f"number_of_tracked_points: {number_of_tracked_points},\n"
        f"number_of_spatial_dimensions: {number_of_spatial_dimensions}"
    )


    data3d_flat = anipose_calibration_object.triangulate(data2d_flat, progress=True, kill_event=kill_event)

    spatial_data3d_numFrames_numTrackedPoints_XYZ_og = data3d_flat.reshape(
        number_of_frames, number_of_tracked_points, 3
    )

    data3d_reprojectionError_flat = anipose_calibration_object.reprojection_error(data3d_flat, data2d_flat, mean=True)

    reprojection_error_data3d_numFrames_numTrackedPoints = data3d_reprojectionError_flat.reshape(
        number_of_frames, number_of_tracked_points
    )

    spatial_data3d_numFrames_numTrackedPoints_XYZ = remove_3d_data_with_high_reprojection_error(
        data3d_numFrames_numTrackedPoints_XYZ=spatial_data3d_numFrames_numTrackedPoints_XYZ_og,
        data3d_numFrames_numTrackedPoints_reprojectionError=reprojection_error_data3d_numFrames_numTrackedPoints,
    )

    # TODO - don't output multiple variables, make this a dataclass/BAG pattern or something
    return (
        spatial_data3d_numFrames_numTrackedPoints_XYZ,
        reprojection_error_data3d_numFrames_numTrackedPoints,
    )



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



import itertools
import logging
from pathlib import Path
from typing import Tuple, Union
import numpy as np
from matplotlib import pyplot as plt

from utils.reconstruction.reconstruct_3d import triangulate_3d_data


logger = logging.getLogger(__name__)


def filter_by_reprojection_error(
    reprojection_error_frame_marker: np.ndarray,
    reprojection_error_threshold: float,
    mediapipe_2d_data: np.ndarray,
    raw_skel3d_frame_marker_xyz: np.ndarray,
    anipose_calibration_object,
    output_data_folder_path: Union[str, Path],
    use_triangulate_ransac: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    # create before plot for debugging
    plot_reprojection_error(
        reprojection_error_frame_marker=reprojection_error_frame_marker,
        reprojection_error_threshold=reprojection_error_threshold,
        output_folder_path=output_data_folder_path,
        after_filtering=False
    )

    # create combinations of cameras with 1 camera removed
    total_cameras = mediapipe_2d_data.shape[0]
    num_cameras_to_remove = 1
    camera_list = list(range(total_cameras))
    camera_combinations = list(itertools.combinations(camera_list, num_cameras_to_remove))

    frames_above_threshold = find_frames_with_reprojection_error_above_limit(
        reprojection_error_threshold=reprojection_error_threshold,
        reprojection_error_frames_markers=reprojection_error_frame_marker,
    )
    logger.info(
        f"Found {len(frames_above_threshold)} frames with reprojection error above threshold of {reprojection_error_threshold} mm"
    )

    # remove unused Z values for triangulate function
    mediapipe_2d_data = mediapipe_2d_data[:, :, :, :2]

    while len(frames_above_threshold) > 0:
        # if we've checked all combinations with n cameras removed, start checking with n+1 removed
        if len(camera_combinations) == total_cameras - 2:
            num_cameras_to_remove += 1
            camera_combinations = list(itertools.combinations(camera_list, num_cameras_to_remove))

        # pick a combination of cameras to rerun with
        cameras_to_remove = camera_combinations.pop()

        # don't triangulate with less than 2 cameras
        if len(cameras_to_remove) > total_cameras - 2:
            logging.info(
                f"There are still {len(frames_above_threshold)} frames with reprojection error above threshold with all camera combinations, converting data for those frames to NaNs"
            )
            raw_skel3d_frame_marker_xyz[frames_above_threshold, :, :] = np.nan
            reprojection_error_frame_marker[frames_above_threshold, :] = np.nan
            break

        logging.info(f"Retriangulating without cameras {cameras_to_remove}")
        data_to_reproject = set_unincluded_data_to_nans(
            mediapipe_2d_data=mediapipe_2d_data,
            frames_with_reprojection_error=frames_above_threshold,
            cameras_to_remove=cameras_to_remove,
        )

        retriangulated_data, new_reprojection_error = triangulate_3d_data(
            anipose_calibration_object=anipose_calibration_object,
            mediapipe_2d_data=data_to_reproject,
            output_data_folder_path=output_data_folder_path,
            use_triangulate_ransac=use_triangulate_ransac,
        )

        logging.info("Putting retriangulated data back into full session data")
        reprojection_error_frame_marker[frames_above_threshold, :] = new_reprojection_error
        raw_skel3d_frame_marker_xyz[frames_above_threshold, :, :] = retriangulated_data

        # it's messy that these are saved again, but only a slice is saved in the triangulate function
        # TODO: move the saving outside of the triangulate function (we can save these values after this function)
        # save_mediapipe_3d_data_to_npy(
        #     data3d_numFrames_numTrackedPoints_XYZ=raw_skel3d_frame_marker_xyz,
        #     data3d_numFrames_numTrackedPoints_reprojectionError=reprojection_error_frame_marker,
        #     path_to_folder_where_data_will_be_saved=output_data_folder_path,
        # )

        frames_above_threshold = find_frames_with_reprojection_error_above_limit(
            reprojection_error_threshold=reprojection_error_threshold,
            reprojection_error_frames_markers=reprojection_error_frame_marker,
        )
        logging.info(f"There are now {len(frames_above_threshold)} frames with reprojection error above threshold")

    plot_reprojection_error(
        reprojection_error_frame_marker=reprojection_error_frame_marker,
        reprojection_error_threshold=reprojection_error_threshold,
        output_folder_path=output_data_folder_path,
        after_filtering=True
    )

    return (raw_skel3d_frame_marker_xyz, reprojection_error_frame_marker)


def find_frames_with_reprojection_error_above_limit(
    reprojection_error_threshold: float,
    reprojection_error_frames_markers: np.ndarray,
) -> list:
    mean_reprojection_error_per_frame = np.nanmean(
        reprojection_error_frames_markers,
        axis=1,
    )
    return [
        i
        for i, reprojection_error in enumerate(mean_reprojection_error_per_frame)
        if reprojection_error > reprojection_error_threshold
    ]


def set_unincluded_data_to_nans(
    mediapipe_2d_data: np.ndarray,
    frames_with_reprojection_error: np.ndarray,
    cameras_to_remove: list[int],
) -> np.ndarray:
    data_to_reproject = mediapipe_2d_data[:, frames_with_reprojection_error, :, :]
    data_to_reproject[cameras_to_remove, :, :, :] = np.nan
    return data_to_reproject


def plot_reprojection_error(
    reprojection_error_frame_marker: np.ndarray,
    reprojection_error_threshold: float,
    output_folder_path: Union[str, Path],
    after_filtering: bool = False,
) -> None:
    title = "Mean Reprojection Error Per Frame"
    file_name = "debug_reprojection_error_filtering.png"
    # output_filepath = Path(output_folder_path) / file_name
    mean_reprojection_error_per_frame = np.nanmean(
        reprojection_error_frame_marker,
        axis=1,
    )
    plt.plot(mean_reprojection_error_per_frame)
    if after_filtering:
        plt.xlabel("Frame")
        plt.ylabel("Mean Reprojection Error Across Markers (mm)")
        plt.hlines(y=reprojection_error_threshold, xmin=0, xmax=len(mean_reprojection_error_per_frame), color="red")
        plt.title(title)
        plt.show()
        # logger.info(f"Saving debug plots to: {output_filepath}")
        # plt.savefig(output_filepath, dpi=300)
