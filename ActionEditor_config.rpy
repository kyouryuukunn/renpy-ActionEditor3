init 1600 python in _viewers:
    #this is used for default transition
    #デフォルトで使用されるトランジションの文字列です。Noneも指定可能です。
    default_transition = "dissolve"
init -1600 python in _viewers:
    #hide winodw during animation in clipboard data
    #アニメーション中ウィンドウを隠すようにクリップボードを出力するか決定します
    #シーンが1つのとき動作します。
    hide_window_in_animation = True
    #If this is True and hide_window_in_animation is True, allow animation to be skipped
    #アニメーションをスキップできる形式でクリップボードに出力します。hide_window_in_animationがTrueかつ
    #シーンが1つのとき動作します。
    allow_animation_skip = True
    #this is used for default warper
    #デフォルトで使用されるwarper関数名の文字列を指定します。
    default_warper = "linear"
    # If True, show rot default.
    #True, なら格子をデフォルトで表示します。
    default_rot = True
    # If True, simulate defpth of field and focusing is enable by default.
    # Trueならカメラブラーを再現するフォーカシングをデフォルトで有効にします。
    focusing = False
    # If True, show icons which is dragged to move camera or iamges by default
    # Trueならドラッグでカメラや画像を移動できるアイコンをデフォルトで表示します。
    default_show_camera_icon = True
    # If True, One line includes only one property in clipboard data
    # Trueならクリップボードデータで一行に1つのプロパティーのみ記述します。
    default_one_line_one_prop = False
    # If True, use legacy action editor screen
    # Trueなら以前のレイアウトでActionEditorを表示します。
    default_legacy_gui = False
    # If True, set camera keymap FPS(wasd), otherwise vim(hjkl)
    #Trueなら、カメラはWASD, wasdで、Falseならhjkl, HJKLで移動します。
    fps_keymap = True
    # If True, only one page is opened at once. this has no effect for legacy gui
    #Trueなら、一度に１つの項目のみ開きます。これはレガシーGUIでは無効です。
    default_open_only_one_page = False
    # the number of tabs shown at onece(In legacy GUI).
    #一度に表示する画像タグ数を設定します(レガシーGUIのみ)。
    tab_amount_in_page = 5
    #The blur value where the distance from focus position is dof.
    #フォーカシングでフォーカス位置からDOF離れた場所でのブラー量を設定します。
    _camera_blur_amount = 2.0 
    #warper function name which is used for the distance from focus position and blur amount.
    #フォーカス位置からの距離とカメラブラーの効きを決定するwarper関数名の文字列です
    _camera_blur_warper = "linear" 
    # the range of values of properties for int type(In legacy GUI)
    #エディターのバーに表示する整数の範囲です(レガシーGUIのみ)。
    wide_range = 1500
    # the range of values of properties for float type(In legacy GUI)
    #エディターのバーに表示する浮動小数の範囲です(レガシーGUIのみ)。
    narrow_range = 7.0
    # change per pix
    #Set the amount of change per pixel when dragging the value of the float property(In new GUI)
    narrow_drag_speed = 1./200
    #Set the amount of change per pixel when dragging the value of the integer property(In new GUI)
    #整数プロパティーの値をドラッグしたときの1pixelごとの変化量を設定します(新GUIのみ)。
    wide_drag_speed = int(config.screen_width/200)
    # the range of time
    #エディターのバーに表示する時間の範囲です。
    time_range = 7.0
    # the list of channel for playing
    # ActionEditorで使用するチャンネルのリストです
    default_channel_list = ["sound"]
    #default side view.
    default_sideview = True
    #Not included layers
    not_included_layer = ("transient", "screens", "overlay")

    default_graphic_editor_narrow_range = 2.
    default_graphic_editor_wide_range = 2000

    preview_size=0.6
    preview_background_color="#111"

    props_sets = (
            ("Child/Pos    ", ("child", "xpos", "ypos", "zpos", "xaround", "yaround", "radius", "angle", "rotate",
                               "xrotate", "yrotate", "zrotate", "xorientation", "yorientation", "zorientation", "point_to",)), 
            ("3D Matrix    ", ("matrixtransform",)),
            ("Anchor/Offset", ("xanchor", "yanchor", "matrixanchorX", "matrixanchorY", "xoffset", "yoffset")), 
            ("Zoom/Crop    ", ("xzoom", "yzoom", "zoom", "cropX", "cropY", "cropW", "cropH")), 
            ("Effect       ", ("blend", "alpha", "blur", "additive", "matrixcolor", "dof", "focusing")),
            ("Misc         ", ("zzoom", "perspective", "function", "xpan", "ypan", "xtile", "ytile")),
            )

    props_groups = {
        "around":["xaround", "yaround"], 
        "matrixanchor":["matrixanchorX", "matrixanchorY"], 
        "crop":["cropX", "cropY", "cropW", "cropH"], 
        "focusing":["focusing", "dof"], 
        "orientation":["xorientation", "yorientation", "zorientation"], 
    }

    #These variables are always wide range even if it is float type.
    #浮動小数であっても整数と同じスケールで表示される変数です。
    force_wide_range = {"rotate", "rotateX", "rotateY", "rotateZ", "offsetX", "offsetY", "offsetZ", "zpos", "xoffset", "yoffset", "hue", "dof", "focusing", "angle", "xpan", "ypan", "xrotate", "yrotate", "zrotate", "xorientation", "yorientation", "zorientation"}
    force_narrow_range = {"xtile", "ytile"}
    #These variables are always plus
    #常に正数になる変数です。
    force_plus = {"additive", "blur", "alpha", "invert", "contrast", "saturate", "cropW", "cropH", "dof", "focusing", "xtile", "ytile"}
    #These varialbes aren't setted without keyframe.
    #crop doesn't work when perspective True and rotate change the pos of image when perspective is not True
    #キーフレームを設定しなければ適用されない変数です。
    not_used_by_default = {"rotate", "cropX", "cropY", "cropW", "cropH", "xpan", "ypan", "function"}
    #These variables are always float type.
    #常に浮動小数になる変数です。
    force_float = ("zoom", "xzoom", "yzoom", "alpha", "additive", "blur", "invert", "contrast", "saturate", "bright", "xaround", "yaround", "scaleX", "scaleY", "scaleZ", "xrotate", "yrotate", "zrotate", "xorientation", "yorientation", "zorientation")

    boolean_props = {"zzoom"}
    any_props = {"blend", "point_to"}
    def check_perspective(v):
        if isinstance(v, (int, float)):
            return True
        if isinstance(v, tuple) and len(v) == 3:
            for i in v:
                if not isinstance(v, (int, float)):
                    return False
            else:
                return True
    check_any_props = {"perspective":check_perspective}
    def check_poi(v):
        if isinstance(v, tuple) and len(v) == 3:
            x, y, z = v
            if isinstance(x, (int, float)) and isinstance(y, (int, float)) and isinstance(z, (int, float)):
                return True
        elif isinstance(v, renpy.display.transform.Camera):
            return True
        elif v is None:
            return True
        else:
            return False
    check_any_props = {"point_to":check_poi}
    #properties which is included in any_props and is choiced by menu.
    menu_props = {"blend":[None] + [key for key in config.gl_blend_func]}

    #disallow properties to edit at sametime.
    #Editorの都合で同時に編集されたくないプロパティー
    exclusive = (
             ({"xpos", "ypos"}, {"xaround", "yaround", "radius", "angle"}), 
            # ({"xpan", "ypan"}, {"xtile", "ytile"}), 
        )
    disallow_spline = ("focusing", "matrixtransform", "matrixcolor", "orientation")
    xygroup = {"pos": ("xpos", "ypos"), "anchor": ("xanchor", "yanchor"), "offset": ("xoffset", "yoffset")}
    default_matrixtransform = [
        ("matrixtransform_1_1_scaleX", 1.),  ("matrixtransform_1_2_scaleY", 1.),  ("matrixtransform_1_3_scaleZ", 1.),
        ("matrixtransform_2_1_offsetX", 0.), ("matrixtransform_2_2_offsetY", 0.), ("matrixtransform_2_3_offsetZ", 0.),
        ("matrixtransform_3_1_rotateX", 0.), ("matrixtransform_3_2_rotateY", 0.), ("matrixtransform_3_3_rotateZ", 0.),
        ("matrixtransform_4_1_offsetX", 0.), ("matrixtransform_4_2_offsetY", 0.), ("matrixtransform_4_3_offsetZ", 0.),
        ("matrixtransform_5_1_offsetX", 0.), ("matrixtransform_5_2_offsetY", 0.), ("matrixtransform_5_3_offsetZ", 0.),
    ]
    default_matrixcolor = [
        ("matrixcolor_1_1_invert", 0.), 
        ("matrixcolor_2_1_contrast", 1.), 
        ("matrixcolor_3_1_saturate", 1.),
        ("matrixcolor_4_1_bright", 0.),
        ("matrixcolor_5_1_hue", 0.), 
    ]
    #The order of properties in clipboard data.
    #この順番でクリップボードデータが出力されます
    #ないものは出力されません
    sort_order_list = (
    "blend",
    "pos",
    "anchor",
    "offset",
    "xpos", 
    "xanchor", 
    "xoffset", 
    "ypos", 
    "yanchor", 
    "yoffset", 
    "around",
    "radius",
    "angle",
    "zpos", 
    "xrotate",
    "yrotate",
    "zrotate",
    "orientation",
    "point_to",
    "matrixtransform", 
    "matrixanchor", 
    "rotate", 
    "xzoom", 
    "yzoom", 
    "zoom", 
    "crop", 
    "alpha", 
    "additive", 
    "blur", 
    "matrixcolor", 
    "xpan", 
    "ypan", 
    "xtile", 
    "ytile", 
    )


    #clipboardで個別に出力するプロパティー
    special_props = {"child", "function"}
    in_editor = False
    aspect_16_9 = round(float(config.screen_width)/config.screen_height, 2) == 1.78

init 1600 python in _viewers:
    #The properties used in image tag tab
    #画像タブに表示されるプロパティー
    #(property name,  default value)
    transform_props = [
    "child",
    "xpos",
    "ypos",
    "zpos",
    "xaround",
    "yaround",
    "radius",
    "angle",
    "xanchor",
    "yanchor",
    "matrixanchorX",
    "matrixanchorY",
    "xoffset",
    "yoffset",
    "rotate",
    "xzoom",
    "yzoom",
    "zoom",
    "cropX",
    "cropY",
    "cropW",
    "cropH",
    "matrixtransform",
    "dof",
    "focusing",
    "alpha",
    "additive",
    "blur",
    "matrixcolor",
    "zzoom",
    "xpan",
    "ypan",
    "xtile",
    "ytile",
    "blend",
    "function",
    ]

    #The properties used in camera tab
    #カメラタブに表示されるプロパティー
    #(property name,  default value)
    camera_props = [
    "xpos",
    "ypos",
    "zpos",
    "xaround",
    "yaround",
    "radius",
    "angle",
    "xanchor",
    "yanchor",
    "matrixanchorX",
    "matrixanchorY",
    "xoffset",
    "yoffset",
    "rotate",
    "xzoom",
    "yzoom",
    "zoom",
    "cropX",
    "cropY",
    "cropW",
    "cropH",
    "matrixtransform",
    "dof",
    "focusing",
    "alpha",
    "additive",
    "blur",
    "matrixcolor",
    "xpan",
    "ypan",
    "xtile",
    "ytile",
    "perspective",
    "function",
    ]

    if check_version(23032300):
        transform_props += [
        "xrotate",
        "yrotate",
        "zrotate",
        "xorientation",
        "yorientation",
        "zorientation",
        "point_to"]

        camera_props += [
        "xrotate",
        "yrotate",
        "zrotate",
        "xorientation",
        "yorientation",
        "zorientation",
        "point_to"]

    property_default_value = {
    "child": (None, None), 
    "xpos": 0, 
    "ypos": 0, 
    "zpos": 0., 
    "xaround": 0.,
    "yaround": 0.,
    "around": (0., 0.),
    "radius": 0,
    "angle": 0,
    "xanchor": 0, 
    "yanchor": 0, 
    "matrixanchorX": 0.5, 
    "matrixanchorY": 0.5, 
    "matrixanchor": (0.5, 0.5),
    "xoffset": 0, 
    "yoffset": 0, 
    "rotate": 0.,
    "xzoom": 1., 
    "yzoom": 1., 
    "zoom": 1., 
    "cropX": 0., 
    "cropY": 0., 
    "cropW": 1., 
    "cropH": 1., 
    "crop": (0., 0., 1., 1.), 
    "xrotate":0.,
    "yrotate":0.,
    "zrotate":0.,
    "xorientation": 0.,
    "yorientation": 0.,
    "zorientation": 0.,
    "orientation": (0., 0., 0.),
    "point_to": None,
    "offsetX": 0.,
    "offsetY": 0.,
    "offsetZ": 0.,
    "rotateX": 0.,
    "rotateY": 0.,
    "rotateZ": 0.,
    "scaleX": 1.,
    "scaleY": 1.,
    "scaleZ": 1.,
    "dof": 400,
    "focusing": round(renpy.config.perspective[1], 2), 
    "alpha": 1., 
    "additive": 0., 
    "blur": 0., 
    "hue": 0., 
    "bright": 0., 
    "saturate": 1., 
    "contrast": 1., 
    "invert": 0., 
    "zzoom": False,
    "xpan": 0., 
    "ypan": 0., 
    "xtile": 1, 
    "ytile": 1, 
    "function": (None, None), 
    "perspective": None, #Falseならカメラ動作せず、Noneなら普通の画像として動作
    "blend": "normal",
    }
