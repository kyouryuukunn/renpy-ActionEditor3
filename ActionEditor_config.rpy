# init -1600 python:
#
#     ##########################################################################
#     # Camera functions
#     _camera_focus = 1848.9 #default camera WD
#     _camera_dof = 9999999 #default dof value
#     _camera_blur_amount = 1.0 #The blur value where the distance from focus position is dof.
#     _camera_blur_warper = "linear" #warper function name which is used for the distance from focus position and blur amount.
#     _FOCAL_LENGTH = 147.40 #default focus position
#     _LAYER_Z = 1848.9 #default z value of 3D layer

init -1600 python in _viewers:
    # If True, show rot default.
    default_rot = False
    # If True, set camera keymap FPS(wasd), otherwise vim(hjkl)
    fps_keymap = False
    default_warper = "linear"

    transform_props = (
    ("xpos", 0.), 
    ("ypos", 0.), 
    ("zpos", 0), 
    ("xanchor", 0.), 
    ("yanchor", 0.), 
    # ("xoffset", 0.), 
    # ("yoffset", 0.), 
    ("xzoom", 1.), 
    ("yzoom", 1.), 
    ("zoom", 1.), 
    ("rotate", 0,),
    ("alpha", 1.), 
    ("additive", 0.), 
    ("blur", 0.), 
    )
    force_float = ["zoom", "xzoom", "yzoom", "alpha", "additive", "blur"]
    force_int_range = ["rotate", "zpos"]
    force_plus = ["additive", "blur", "alpha"]

    camera_props = (
    ("xpos", 0.), 
    ("ypos", 0.), 
    ("zpos", 0), 
    ("rotate", 0),
    ("blur", 0.)
    )
