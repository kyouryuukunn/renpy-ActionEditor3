
init -1600 python in _viewers:
    # If True, show rot default.
    default_rot = False
    # simulate defpth of field and focusing
    focusing = False
    # If True, set camera keymap FPS(wasd), otherwise vim(hjkl)
    fps_keymap = False
    tab_amount_in_page = 5
    _camera_blur_amount = 2.0 #The blur value where the distance from focus position is dof.
    _camera_blur_warper = "linear" #warper function name which is used for the distance from focus position and blur amount.

    int_range = 1500
    float_range = 7.0
    default_warper = "linear"
    props_set = [
        ("xpos", "ypos", "zpos", "rotate", "xanchor", "yanchor", "xoffset", "yoffset"), 
        ("xzoom", "yzoom", "zoom", "cropX", "cropY", "cropW", "cropH"), 
        ("offsetX", "offsetY", "offsetZ", "rotateX", "rotateY", "rotateZ", "dof", "focusing"),
        ("alpha", "blur", "additive", "invert", "contrast", "saturate", "bright", "hue")
    ]
    props_set_names = [
        "pos, rotate", 
        "zoom,crop  ", 
        "3D Matrix  ",
        "Effect     "
    ]

    props_groups = {
        "matrixtransform":["rotateX", "rotateY", "rotateZ", "offsetX", "offsetY", "offsetZ"], 
        "matrixcolor":["invert", "contrast", "saturate", "bright", "hue"], 
        "crop":["cropX", "cropY", "cropW", "cropH"], 
        "focusing":["focusing", "dof"], 
    }

    force_float = ["zoom", "xzoom", "yzoom", "alpha", "additive", "blur", "invert", "contrast", "saturate", "bright"]
    force_int_range = ["rotate", "rotateX", "rotateY", "rotateZ", "offsetX", "offsetY", "offsetZ", "zpos", "xoffset", "yoffset", "hue", "dof", "focusing"]
    force_plus = ["additive", "blur", "alpha", "invert", "contrast", "saturate", "cropW", "cropH", "dof", "focusing"]

    transform_props = (
    ("xpos", 0.5), 
    ("ypos", 1.), 
    ("zpos", 0.), 
    ("xanchor", 0.5), 
    ("yanchor", 1.), 
    ("xoffset", 0), 
    ("yoffset", 0), 
    ("rotate", 0,),
    ("xzoom", 1.), 
    ("yzoom", 1.), 
    ("zoom", 1.), 
    ("cropX", 0.), 
    ("cropY", 0.), 
    ("cropW", 1.), 
    ("cropH", 1.), 
    ("offsetX", 0.),
    ("offsetY", 0.),
    ("offsetZ", 0.),
    ("rotateX", 0.),
    ("rotateY", 0.),
    ("rotateZ", 0.),
    ("alpha", 1.), 
    ("additive", 0.), 
    ("blur", 0.), 
    ("hue", 0.), 
    ("bright", 0.), 
    ("saturate", 1.), 
    ("contrast", 1.), 
    ("invert", 0.), 
    )

    #perspetve competes crop
    camera_props = (
    ("xpos", 0.), 
    ("ypos", 0.), 
    ("zpos", 0.), 
    ("xanchor", 0.), 
    ("yanchor", 0.), 
    ("xoffset", 0), 
    ("yoffset", 0), 
    ("rotate", 0,),
    ("xzoom", 1.), 
    ("yzoom", 1.), 
    ("zoom", 1.), 
    # ("cropX", 0.), 
    # ("cropY", 0.), 
    # ("cropW", 1.), 
    # ("cropH", 1.), 
    ("offsetX", 0.),
    ("offsetY", 0.),
    ("offsetZ", 0.),
    ("rotateX", 0.),
    ("rotateY", 0.),
    ("rotateZ", 0.),
    ("dof", 400),
    ("focusing", renpy.config.perspective[1]), 
    ("alpha", 1.), 
    ("additive", 0.), 
    ("blur", 0.), 
    ("hue", 0.), 
    ("bright", 0.), 
    ("saturate", 1.), 
    ("contrast", 1.), 
    ("invert", 0.), 
    )
