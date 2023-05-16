

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
