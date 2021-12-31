
init 1600 python in _viewers:
    #this is used for default transition
    default_transition = "dissolve"
init -1600 python in _viewers:
    #hide winodw during animation in clipboard data
    hide_window_in_animation = True
    #If this is True and hide_window_in_animation is True, allow animation to be skipped
    allow_animation_skip = True
    #this is used for default warper
    default_warper = "linear"
    # If True, show rot default.
    default_rot = False
    # If True, simulate defpth of field and focusing is enable by default.
    focusing = False
    # If True, set camera keymap FPS(wasd), otherwise vim(hjkl)
    fps_keymap = False
    # the number of tabs shown at onece.
    tab_amount_in_page = 5
    #The blur value where the distance from focus position is dof.
    _camera_blur_amount = 2.0 
    #warper function name which is used for the distance from focus position and blur amount.
    _camera_blur_warper = "linear" 
    # the range of values of properties for int type
    int_range = 1500
    # the range of values of properties for float type
    float_range = 7.0
    # the range of time
    time_range = 7.0


    props_set = [
        ("child", "xpos", "ypos", "zpos", "rotate"), 
        ("offsetX", "offsetY", "offsetZ", "rotateX", "rotateY", "rotateZ", "dof", "focusing"),
        ("xanchor", "yanchor", "matrixanchorX", "matrixanchorY", "xoffset", "yoffset"), 
        ("xzoom", "yzoom", "zoom", "cropX", "cropY", "cropW", "cropH"), 
        ("alpha", "blur", "additive", "invert", "contrast", "saturate", "bright", "hue")
    ]
    props_set_names = [
        "Child/Pos    ", 
        "3D Matrix    ",
        "Anchor/Offset", 
        "Zoom/Crop    ", 
        "Effect       "
    ]

    props_groups = {
        "matrixtransform":["rotateX", "rotateY", "rotateZ", "offsetX", "offsetY", "offsetZ"], 
        "matrixanchor":["matrixanchorX", "matrixanchorY"], 
        "matrixcolor":["invert", "contrast", "saturate", "bright", "hue"], 
        "crop":["cropX", "cropY", "cropW", "cropH"], 
        "focusing":["focusing", "dof"], 
    }

    special_props = ["child"]

    force_float = ["zoom", "xzoom", "yzoom", "alpha", "additive", "blur", "invert", "contrast", "saturate", "bright"]
    force_int_range = ["rotate", "rotateX", "rotateY", "rotateZ", "offsetX", "offsetY", "offsetZ", "zpos", "xoffset", "yoffset", "hue", "dof", "focusing"]
    force_plus = ["additive", "blur", "alpha", "invert", "contrast", "saturate", "cropW", "cropH", "dof", "focusing"]

    transform_props = (
    ("child", (None, None)), 
    ("xpos", 0.5), 
    ("ypos", 1.), 
    ("zpos", 0.), 
    ("xanchor", 0.5), 
    ("yanchor", 1.), 
    ("matrixanchorX", 0.5), 
    ("matrixanchorY", 0.5), 
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
    # ("zzoom", False)
    )

    #perspetve competes crop
    camera_props = (
    ("xpos", 0.), 
    ("ypos", 0.), 
    ("zpos", 0.), 
    ("xanchor", 0.), 
    ("yanchor", 0.), 
    ("matrixanchorX", 0.5), 
    ("matrixanchorY", 0.5), 
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
