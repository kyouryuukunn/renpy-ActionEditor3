
screen _new_action_editor(opened=None, time=0):
    default layer = "master"
    $int_format = "{:> }" 
    $float_format = "{:> .2f}"

    $generate_changed = _viewers.generate_changed
    $get_property = _viewers.get_property
    $get_value = _viewers.get_value
    $current_scene = _viewers.current_scene
    $scene_keyframes = _viewers.scene_keyframes
    $all_keyframes = _viewers.all_keyframes
    $change_time = _viewers.change_time
    $sorted_keyframes = _viewers.sorted_keyframes
    $current_time = _viewers.current_time
    $edit_value = _viewers.edit_value
    $reset = _viewers.reset
    $force_plus = _viewers.force_plus
    $force_float = _viewers.force_float
    $force_wide_range = _viewers.force_wide_range
    $props_set = _viewers.props_set
    $props_set_names = _viewers.props_set_names
    $props_groups = _viewers.props_groups
    $keyframes_exist = _viewers.keyframes_exist
    $to_drag_pos = _viewers.to_drag_pos
    $generate_key_drag = _viewers.generate_key_drag

    if opened is None:
        $opened = {}
    for s in range(0, len(scene_keyframes)):
        if s not in opened:
            $opened[s] = []

    $indent = "  "
    $play_action = [SensitiveIf(sorted_keyframes[current_scene] or len(scene_keyframes) > 1), \
        SelectedIf(False), Function(_viewers.play, play=True), \
        Show("_new_action_editor", opened=opened, time=_viewers.get_animation_delay())]
    key "K_SPACE" action play_action
    key "action_editor" action NullAction()
    key "hide_windows" action NullAction()

    $offsetX, offsetY = get_property("offsetX"), get_property("offsetY")
    $value_range = persistent._wide_range
    $move_amount1 = 100
    $move_amount2 = 300
    if get_value("perspective", scene_keyframes[current_scene][1], True):
        if _viewers.fps_keymap:
            key "s" action Function(generate_changed("offsetY"), offsetY + move_amount1 + value_range)
            key "w" action Function(generate_changed("offsetY"), offsetY - move_amount1 + value_range)
            key "a" action Function(generate_changed("offsetX"), offsetX - move_amount1 + value_range)
            key "d" action Function(generate_changed("offsetX"), offsetX + move_amount1 + value_range)
            key "S" action Function(generate_changed("offsetY"), offsetY + move_amount2 + value_range)
            key "W" action Function(generate_changed("offsetY"), offsetY - move_amount2 + value_range)
            key "A" action Function(generate_changed("offsetX"), offsetX - move_amount2 + value_range)
            key "D" action Function(generate_changed("offsetX"), offsetX + move_amount2 + value_range)
        else:
            key "j" action Function(generate_changed("offsetY"), offsetY + move_amount1 + value_range)
            key "k" action Function(generate_changed("offsetY"), offsetY - move_amount1 + value_range)
            key "h" action Function(generate_changed("offsetX"), offsetX - move_amount1 + value_range)
            key "l" action Function(generate_changed("offsetX"), offsetX + move_amount1 + value_range)
            key "J" action Function(generate_changed("offsetY"), offsetY + move_amount2 + value_range)
            key "K" action Function(generate_changed("offsetY"), offsetY - move_amount2 + value_range)
            key "H" action Function(generate_changed("offsetX"), offsetX - move_amount2 + value_range)
            key "L" action Function(generate_changed("offsetX"), offsetX + move_amount2 + value_range)

    if time:
        timer time+1 action [Show("_new_action_editor", opened=opened), \
                            Function(change_time, current_time)]
        key "game_menu" action [Show("_new_action_editor", opened=opened), \
                            Function(change_time, current_time)]
    else:
        key "game_menu" action Confirm("Close Editor?", Return())

    $state=_viewers.get_image_state(layer)
    $tag_list =  []
    for tag, z in _viewers.zorder_list[s][layer]:
        if tag in state:
            $tag_list.append(tag)
    frame:
        style_group "new_action_editor"
        align (1., 0.)
        vbox:
            xfill False
            text "absolute" xalign 1.
            add DynamicDisplayable(_viewers.absolute_pos) xalign 1.
            text "fraction" xalign 1.
            add DynamicDisplayable(_viewers.rel_pos) xalign 1.

    frame:
        pos (1., _viewers.preview_size)
        align (1., 1.)
        style_group "new_action_editor"
        vbox:
            style_group "new_action_editor_a"
            textbutton _("option") action Show("_action_editor_option")
            textbutton _("scene editor") action [SensitiveIf(len(scene_keyframes) > 1), Show("_scene_editor")]
            hbox:
                xalign 1.
                textbutton _("remove keys") action [
                    SensitiveIf(current_time in sorted_keyframes[current_scene]), 
                    Function(_viewers.remove_all_keyframe, current_time), renpy.restart_interaction]
                textbutton _("move keys") action [
                    SensitiveIf(current_time in sorted_keyframes[current_scene]),
                    SelectedIf(False), SetField(_viewers, "moved_time", current_time), Show("_move_keyframes")]
            hbox:
                xalign 1.
                textbutton _("<") action Function(_viewers.prev_time)
                textbutton _(">") action Function(_viewers.next_time)
                textbutton _("play") action play_action
                textbutton _("clipboard") action Function(_viewers.put_clipboard)
                textbutton _("close") action Return()
    frame:
        style_group "new_action_editor"
        ymaximum 0.4
        yalign 1.0
        vbox:
            hbox:
                hbox:
                    style_group "new_action_editor_c"
                    textbutton _("time: [current_time:>05.2f] s"):
                        action Function(_viewers.edit_time)
                        xalign 1.
                        size_group None
                # fixed:
                #     drag:
                #         drag_name "time"
                #         child _viewers.key_child
                #         xpos to_drag_pos(current_time)
                #         dragged _viewers.drag_change_time
                bar adjustment ui.adjustment(range=persistent._time_range, value=current_time, changed=change_time):
                    xalign 1. yalign .5 style "new_action_editor_bar"
            viewport:
                mousewheel True
                scrollbars "vertical"
                has vbox
                for s, ks in enumerate(all_keyframes):
                    if s != current_scene:
                        hbox:
                            hbox:
                                style_group "new_action_editor_c"
                                textbutton "+ "+"scene[s]":
                                    action [SelectedIf(current_scene == s), Function(_viewers.change_scene, s)]
                            fixed:
                                add _viewers.time_line_background
                                $(v, t, w) = scene_keyframes[s]
                                drag:
                                    child _viewers.insensitive_key_child
                                    hover_child _viewers.insensitive_key_hovere_child
                                    xpos to_drag_pos(t)
                                    droppable False
                                    draggable False
                                    clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                                for key, cs in all_keyframes[s].items():
                                    if isinstance(key, tuple):
                                        $p = key[2]
                                    else:
                                        $p = key
                                    if (p not in props_groups["focusing"] or
                                        (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True))):
                                        for c in cs:
                                            $(v, t, w) = c
                                            drag:
                                                child _viewers.insensitive_key_child
                                                hover_child _viewers.insensitive_key_hovere_child
                                                xpos to_drag_pos(t)
                                                droppable False
                                                draggable False
                                                clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                    else:
                        hbox:
                            style_group "new_action_editor_c"
                            textbutton "- "+"scene[s]" action [SelectedIf(current_scene == s), Function(_viewers.change_scene, s)]

                        if "camera" not in opened[s]:
                            hbox:
                                hbox:
                                    style_group "new_action_editor_c"
                                    if persistent._open_only_one_page:
                                        $new_opened = {s:["camera"]}
                                    else:
                                        $new_opened = opened.copy()
                                        $new_opened[s] = new_opened[s] + ["camera"]
                                    textbutton _(indent+"+ "+"camera"):
                                        action [SensitiveIf(get_value("perspective", scene_keyframes[s][1], True) != False),
                                        Show("_new_action_editor", opened=new_opened)]
                                fixed:
                                    add _viewers.time_line_background
                                    for p, d in _viewers.camera_props:
                                        if (p not in props_groups["focusing"] or
                                            (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True))):
                                            for c in all_keyframes[s].get(p, []):
                                                $(v, t, w) = c
                                                drag:
                                                    child _viewers.insensitive_key_child
                                                    hover_child _viewers.insensitive_key_hovere_child
                                                    xpos to_drag_pos(t)
                                                    droppable False
                                                    draggable False
                                                    clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                        else:
                            hbox:
                                style_group "new_action_editor_c"
                                $new_opened = opened.copy()
                                $new_opened[s] = opened[s].copy()
                                $new_opened[s].remove("camera")
                                textbutton _(indent+"- "+"camera"):
                                    action Show("_new_action_editor", opened=new_opened)
                                textbutton _("clipboard"):
                                    action Function(_viewers.put_camera_clipboard)
                                    size_group None
                                    style_group "new_action_editor_b"
                            textbutton _(indent*2+"  perspective"):
                                action [SelectedIf(get_value("perspective", scene_keyframes[s][1], True)),
                                Function(_viewers.toggle_perspective)]
                            for i, props_set_name in enumerate(props_set_names):
                                if props_set_name in opened[s]:
                                    hbox:
                                        style_group "new_action_editor_c"
                                        $new_opened = opened.copy()
                                        $new_opened[s] = opened[s].copy()
                                        $new_opened[s].remove(props_set_name)
                                        textbutton indent*2+"- " + props_set_name action Show("_new_action_editor", opened=new_opened)
                                    for p in props_set[i]:
                                        if p != "child" and (p not in props_groups["focusing"] or \
                                            (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True))):
                                            $key = p
                                            $value = get_property(p)
                                            $d = _viewers.get_default(p, True)
                                            $f = generate_changed(p)
                                            $cs = all_keyframes[s].get(key, [])
                                            $use_wide_range = p not in force_float and (p in force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int)))
                                            if not use_wide_range or isinstance(value, float):
                                                $value_format = float_format
                                            else:
                                                $value_format = int_format
                                            hbox:
                                                hbox:
                                                    style_group "new_action_editor_c"
                                                    textbutton indent*3+"  [p]" action None text_color "#CCC"
                                                    add _viewers.DraggableValue(value_format, key, f, use_wide_range, p in force_plus,
                                                        clicked=Function(edit_value, f, use_wide_range=use_wide_range, default=value, force_plus=p in force_plus),
                                                        alternate=Function(reset, p),
                                                        text_size=16, text_color="#CCC", text_hover_underline=True)
                                                fixed:
                                                    add _viewers.time_line_background
                                                    for c in cs:
                                                        $(v, t, w) = c
                                                        drag:
                                                            child _viewers.key_child
                                                            hover_child _viewers.key_hovere_child
                                                            xpos to_drag_pos(t)
                                                            droppable False
                                                            dragged generate_key_drag(key, t)
                                                            clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                                                            alternate Show("_keyframe_altername_menu", key=key, check_point=c, use_wide_range=use_wide_range, change_func=f)
                                else:
                                    hbox:
                                        hbox:
                                            style_group "new_action_editor_c"
                                            if persistent._open_only_one_page:
                                                $new_opened = {s:["camera", props_set_name]}
                                            else:
                                                $new_opened = opened.copy()
                                                $new_opened[s] = new_opened[s] + [props_set_name]
                                            textbutton indent*2+"+ "+props_set_name action Show("_new_action_editor", opened=new_opened)
                                        fixed:
                                            add _viewers.time_line_background
                                            for p in props_set[i]:
                                                if (p not in props_groups["focusing"] or \
                                                    (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True))):
                                                    for c in all_keyframes[s].get(p, []):
                                                        $(v, t, w) = c
                                                        drag:
                                                            child _viewers.insensitive_key_child
                                                            hover_child _viewers.insensitive_key_hovere_child
                                                            xpos to_drag_pos(t)
                                                            droppable False
                                                            draggable False
                                                            clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                        for tag in tag_list:
                            if tag not in opened[s]:
                                hbox:
                                    hbox:
                                        style_group "new_action_editor_c"
                                        if persistent._open_only_one_page:
                                            $new_opened = {s:[tag]}
                                        else:
                                            $new_opened = opened.copy()
                                            $new_opened[s] = new_opened[s] + [tag]
                                        textbutton indent+"+ "+"{}".format(tag):
                                            action Show("_new_action_editor", opened=new_opened)
                                    fixed:
                                        add _viewers.time_line_background
                                        for p, d in _viewers.transform_props:
                                            for c in all_keyframes[s].get((tag, layer, p), []):
                                                $(v, t, w) = c
                                                drag:
                                                    child _viewers.insensitive_key_child
                                                    hover_child _viewers.insensitive_key_hovere_child
                                                    xpos to_drag_pos(t)
                                                    droppable False
                                                    draggable False
                                                    clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                            else:
                                hbox:
                                    style_group "new_action_editor_c"
                                    $new_opened = opened.copy()
                                    $new_opened[s] = opened[s].copy()
                                    $new_opened[s].remove(tag)
                                    textbutton indent+"- "+"{}".format(tag):
                                        action Show("_new_action_editor", opened=new_opened)
                                    textbutton _("clipboard"):
                                        action Function(_viewers.put_image_clipboard, tag, layer)
                                        style_group "new_action_editor_b"
                                        size_group None
                                textbutton _(indent*2+"  zzoom"):
                                    action [SelectedIf(get_value((tag, layer, "zzoom"), scene_keyframes[s][1], True)),
                                    Function(_viewers.toggle_boolean_property, (tag, layer, "zzoom"))]
                                for i, props_set_name in enumerate(props_set_names):
                                    if (tag, layer, props_set_name) not in opened[s]:
                                        hbox:
                                            hbox:
                                                style_group "new_action_editor_c"
                                                if persistent._open_only_one_page:
                                                    $new_opened = {s:[tag, (tag, layer, props_set_name)]}
                                                else:
                                                    $new_opened = opened.copy()
                                                    $new_opened[s] = new_opened[s] + [(tag, layer, props_set_name)]
                                                textbutton indent*2+"+ "+props_set_name:
                                                    action Show("_new_action_editor", opened=new_opened)
                                            fixed:
                                                add _viewers.time_line_background
                                                for p in props_set[i]:
                                                    for c in all_keyframes[s].get((tag, layer, p), []):
                                                        $(v, t, w) = c
                                                        drag:
                                                            child _viewers.insensitive_key_child
                                                            hover_child _viewers.insensitive_key_hovere_child
                                                            xpos to_drag_pos(t)
                                                            droppable False
                                                            draggable False
                                                            clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                                    else:
                                        hbox:
                                            style_group "new_action_editor_c"
                                            $new_opened = opened.copy()
                                            $new_opened[s] = opened[s].copy()
                                            $new_opened[s].remove((tag, layer, props_set_name))
                                            textbutton indent*2+"- " + props_set_names[i]:
                                                action Show("_new_action_editor", opened=new_opened)
                                        for p in props_set[i]:
                                            if (p not in props_groups["focusing"] and (((persistent._viewer_focusing
                                                and get_value("perspective", scene_keyframes[s][1], True)) and p != "blur")
                                                or (not persistent._viewer_focusing or not get_value("perspective", scene_keyframes[s][1], True)))):
                                                $key = (tag, layer, p)
                                                $d = _viewers.get_default(p)
                                                $value = get_property(key)
                                                $f = generate_changed(key)
                                                $cs = all_keyframes[s].get(key, [])
                                                $use_wide_range = p not in force_float and (p in force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int)))
                                                if not use_wide_range or isinstance(value, float):
                                                    $value_format = float_format
                                                else:
                                                    $value_format = int_format
                                                hbox:
                                                    if p == "child":
                                                        vbox:
                                                            xfill False
                                                            hbox:
                                                                style_group "new_action_editor_c"
                                                                textbutton indent*3+"  [value[0]]":
                                                                    action [SelectedIf(keyframes_exist((tag, layer, "child"))),
                                                                    Function(_viewers.change_child, tag, layer, default=value[0])]
                                                                    size_group None
                                                            hbox:
                                                                style_group "new_action_editor_c"
                                                                textbutton indent*3+"  with [value[1]]":
                                                                    action [SensitiveIf(key in all_keyframes[s]),
                                                                    SelectedIf(keyframes_exist((tag, layer, "child"))),
                                                                    Function(_viewers.edit_transition, tag, layer)]
                                                                    size_group None
                                                    else:
                                                        hbox:
                                                            style_group "new_action_editor_c"
                                                            textbutton indent*3+"  [p]":
                                                                action None text_color "#CCC"
                                                            add _viewers.DraggableValue(value_format, key, f, use_wide_range, p in force_plus,
                                                                clicked=Function(edit_value, f, use_wide_range=use_wide_range, default=value, force_plus=p in force_plus),
                                                                alternate=Function(reset, key),
                                                                text_size=16, text_color="#CCC", text_hover_underline=True)
                                                    fixed:
                                                        add _viewers.time_line_background
                                                        for c in cs:
                                                            $(v, t, w) = c
                                                            drag:
                                                                child _viewers.key_child
                                                                hover_child _viewers.key_hovere_child
                                                                xpos to_drag_pos(t)
                                                                droppable False
                                                                dragged generate_key_drag(key, t)
                                                                clicked [Function(change_time, t), QueueEvent("mouseup_1")]
                                                                alternate Show("_keyframe_altername_menu", key=key, check_point=c, use_wide_range=use_wide_range, change_func=f)
                                $new_opened = opened.copy()
                                $new_opened[s] = opened[s].copy()
                                $new_opened[s] = [o for o in opened if (not isinstance(o, tuple) or o[0] != tag) and o !=tag]
                                textbutton _(indent*3+"  remove"):
                                    action [SensitiveIf(tag in _viewers.image_state[s][layer]),
                                        Show("_new_action_editor", opened=new_opened),
                                        Function(_viewers.remove_image, layer, tag)]
                                    size_group None
                        textbutton _(indent+"+(add image)"):
                            action Function(_viewers.add_image, layer)
                            style_group "new_action_editor_c"
                textbutton _("+(add scene)"):
                    action _viewers.add_scene
                    style_group "new_action_editor_c"


screen _keyframe_altername_menu(key, check_point, use_wide_range=False, change_func=None):
    key ["game_menu", "dismiss"] action Hide("_keyframe_altername_menu")
    modal True

    $current_scene = _viewers.current_scene
    $all_keyframes = _viewers.all_keyframes
    $change_time = _viewers.change_time
    $edit_value = _viewers.edit_value
    $reset = _viewers.reset
    $force_plus = _viewers.force_plus
    $props_set = _viewers.props_set
    $props_groups = _viewers.props_groups

    $(x, y) = renpy.get_mouse_pos()
    $(width, height) = (config.screen_width, config.screen_height)

    style_group "new_action_editor"
    $check_points = all_keyframes[current_scene][key]
    $i = check_points.index(check_point)
    $(v, t, w) = check_point
    if isinstance(key, tuple):
        $n, l, p = key
        $k_list = [key]
        $check_points_list = [check_points]
        $loop_button_action = [ToggleDict(_viewers.loops[current_scene], key)]
        for gn, ps in props_groups.items():
            if p in ps:
                $k_list = [(n, l, p) for p in props_groups[gn]]
                $check_points_list = [all_keyframes[current_scene][k2] for k2 in k_list]
                $loop_button_action = [ToggleDict(_viewers.loops[current_scene], k2) for k2 in k_list+[(n, l, gn)]]
    else:
        $k_list = [key]
        $p = key
        $check_points_list = [check_points]
        $loop_button_action = [ToggleDict(_viewers.loops[current_scene], key)]
        for gn, ps in props_groups.items():
            if p in ps:
                if gn != "focusing":
                    $k_list = props_groups[gn]
                    $check_points_list = [all_keyframes[current_scene][k2] for k2 in k_list]
                    $loop_button_action = [ToggleDict(_viewers.loops[current_scene], k2) for k2 in k_list+[gn]]

    frame:
        background "#222"
        pos (x, y)
        if x + 300 > width:
            xanchor 1.0
        else:
            xanchor 0.0
        if y + 200 > height:
            yanchor 1.0
        else:
            yanchor 0.0
        vbox:
            xfill False
            on "unhovered" action Hide("_keyframe_altername_menu")
            if p == "child":
                textbutton "edit child: [v[0]]":
                    action [Function(_viewers.change_child, n, l, time=t, default=v[0]), Hide("_keyframe_altername_menu")]
                    size_group None
                textbutton "edit transform: [v[1]]":
                    action Function(_viewers.edit_transition, n, l, time=t)
                    size_group None
            else:
                textbutton _("edit value: [v]"):
                    action [Function(edit_value, change_func, default=v, use_wide_range=use_wide_range, force_plus=p in force_plus, time=t),
                    Function(change_time, t), Hide("_keyframe_altername_menu")]
                textbutton _("open warper selecter: [w]"):
                    action [Function(_viewers.edit_warper, check_points=check_points_list, old=t, value_org=w), Hide("_keyframe_altername_menu")]
                if p not in [prop for ps in props_groups.values() for prop in ps] and i > 0:
                    textbutton _("spline editor"):
                        action [SelectedIf(t in _viewers.splines[current_scene][key]), 
                        Show("_spline_editor", change_func=change_func, 
                            key=key, prop=p, pre=check_points[i-1], post=check_points[i], default=v, 
                            use_wide_range=use_wide_range, force_plus=p in force_plus, time=t), Hide("_keyframe_altername_menu")]
                textbutton _("reset") action [Function(reset, key), Hide("_keyframe_altername_menu")]
            textbutton _("edit time: [t]") action [Function(_viewers.edit_move_keyframe, keys=k_list, old=t), Hide("_keyframe_altername_menu")]
            textbutton _("remove"):
                action [SensitiveIf(t > 0 or len(check_points) == 1), Function(_viewers.remove_keyframe, remove_time=t, key=k_list), Hide("_keyframe_altername_menu")]
                size_group None
            textbutton _("toggle loop"):
                action [loop_button_action, Hide("_keyframe_altername_menu")]
                size_group None

init -1599 python in _viewers:
    key_xsize = 22
    key_ysize = 22
    key_half_xsize = 22 // 2
    key_half_ysize = 22 // 2
    time_line_background_color = "#222"
    box = Fixed(xsize=key_xsize, ysize=key_ysize)
    box.add(Solid(time_line_background_color+"1", xsize=key_xsize, ysize=key_ysize))
    box.add(Transform(rotate=45)(Solid("#77A", xsize=16, ysize=16)))
    key_child = box

    box = Fixed(xsize=key_xsize, ysize=key_ysize)
    box.add(Solid(time_line_background_color+"1", xsize=key_xsize, ysize=key_ysize))
    box.add(Transform(rotate=45)(Solid("#AAD", xsize=16, ysize=16)))
    key_hovere_child = box

    box = Fixed(xsize=key_xsize, ysize=key_ysize)
    box.add(Solid(time_line_background_color+"1", xsize=key_xsize, ysize=key_ysize))
    box.add(Transform(rotate=45)(Solid("#447", xsize=16, ysize=16)))
    insensitive_key_child = box

    box = Fixed(xsize=key_xsize, ysize=key_ysize)
    box.add(Solid(time_line_background_color+"1", xsize=key_xsize, ysize=key_ysize))
    box.add(Transform(rotate=45)(Solid("#669", xsize=16, ysize=16)))
    insensitive_key_hovere_child = box

    c_box_size = 320
    timeline_ysize = 27
    time_line_background = Solid(time_line_background_color, xsize=config.screen_width-c_box_size-50-key_half_xsize, ysize=key_ysize, xoffset=key_half_xsize)

init -1597:
    style new_action_editor_frame:
        background None
    style new_action_editor_button:
        size_group "action_editor"
        background None
        idle_background None
        insensitive_background None
        ysize None
        padding (1, 1, 1, 1)
        margin (1, 1)
    style new_action_editor_text:
        color "#CCC"
        outlines [ (absolute(2), "#000", absolute(0), absolute(0)) ]
        size 16
    style new_action_editor_button_text is new_action_editor_text:
        hover_underline True
        selected_color "#FFF"
        insensitive_color "#888"
    style new_action_editor_label:
        xminimum 110
    style new_action_editor_vbox xfill True
    style new_action_editor_bar is slider:
        # ysize _viewers.timeline_ysize
        xoffset _viewers.key_half_xsize
        xsize config.screen_width-_viewers.c_box_size-50-_viewers.key_half_xsize

    style new_action_editor_a_button:
        take new_action_editor_button
        size_group None
        xalign 1.
    style new_action_editor_a_button_text is new_action_editor_button_text
    style new_action_editor_a_bar is new_action_editor_bar

    style new_action_editor_fixed:
        xsize config.screen_width-_viewers.c_box_size-50+_viewers.key_half_xsize
        ysize _viewers.key_ysize
        yalign .5
    # style new_action_editor_drag:
    #     xanchor .5

    style new_action_editor_b_button:
        take new_action_editor_button
        size_group "new_action_editor_b"
        xminimum 90
    style new_action_editor_b_button_text is new_action_editor_button_text:
        xalign 1.0

    style new_action_editor_c_text is new_action_editor_text
    style new_action_editor_c_button is new_action_editor_button:
        size_group "new_action_editor_c"
    style new_action_editor_c_button_text is new_action_editor_button_text
    style new_action_editor_c_bar is new_action_editor_bar
    style new_action_editor_c_hbox:
        size_group "new_action_editor_c"
        xsize _viewers.c_box_size
        ysize _viewers.key_ysize

# tab="images"/"camera", layer="master",  
screen _action_editor(tab="camera", layer="master", opened=0, time=0, page=0):
    $int_format = "{:> }" 
    $float_format = "{:> .2f}"
    $generate_changed = _viewers.generate_changed
    $get_property = _viewers.get_property
    $get_value = _viewers.get_value
    $current_scene = _viewers.current_scene
    $scene_keyframes = _viewers.scene_keyframes
    $all_keyframes = _viewers.all_keyframes
    $change_time = _viewers.change_time
    $sorted_keyframes = _viewers.sorted_keyframes
    $current_time = _viewers.current_time
    $edit_value = _viewers.edit_value
    $reset = _viewers.reset
    $force_plus = _viewers.force_plus
    $force_float = _viewers.force_float
    $force_wide_range = _viewers.force_wide_range
    $props_set = _viewers.props_set
    $props_set_names = _viewers.props_set_names
    $props_groups = _viewers.props_groups
    $keyframes_exist = _viewers.keyframes_exist

    $play_action = [SensitiveIf(sorted_keyframes[current_scene] or len(scene_keyframes) > 1), \
        SelectedIf(False), Function(_viewers.play, play=True), \
        Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page, time=_viewers.get_animation_delay())]
    if get_value("perspective", scene_keyframes[current_scene][1], True):
        key "rollback"    action Function(generate_changed("offsetZ"), get_property("offsetZ")+100+persistent._wide_range)
        key "rollforward" action Function(generate_changed("offsetZ"), get_property("offsetZ")-100+persistent._wide_range)
    key "K_SPACE" action play_action
    key "action_editor" action NullAction()

    $offsetX, offsetY = get_property("offsetX"), get_property("offsetY")
    $value_range = persistent._wide_range
    $move_amount1 = 100
    $move_amount2 = 300
    if get_value("perspective", scene_keyframes[current_scene][1], True):
        if _viewers.fps_keymap:
            key "s" action Function(generate_changed("offsetY"), offsetY + move_amount1 + value_range)
            key "w" action Function(generate_changed("offsetY"), offsetY - move_amount1 + value_range)
            key "a" action Function(generate_changed("offsetX"), offsetX - move_amount1 + value_range)
            key "d" action Function(generate_changed("offsetX"), offsetX + move_amount1 + value_range)
            key "S" action Function(generate_changed("offsetY"), offsetY + move_amount2 + value_range)
            key "W" action Function(generate_changed("offsetY"), offsetY - move_amount2 + value_range)
            key "A" action Function(generate_changed("offsetX"), offsetX - move_amount2 + value_range)
            key "D" action Function(generate_changed("offsetX"), offsetX + move_amount2 + value_range)
        else:
            key "j" action Function(generate_changed("offsetY"), offsetY + move_amount1 + value_range)
            key "k" action Function(generate_changed("offsetY"), offsetY - move_amount1 + value_range)
            key "h" action Function(generate_changed("offsetX"), offsetX - move_amount1 + value_range)
            key "l" action Function(generate_changed("offsetX"), offsetX + move_amount1 + value_range)
            key "J" action Function(generate_changed("offsetY"), offsetY + move_amount2 + value_range)
            key "K" action Function(generate_changed("offsetY"), offsetY - move_amount2 + value_range)
            key "H" action Function(generate_changed("offsetX"), offsetX - move_amount2 + value_range)
            key "L" action Function(generate_changed("offsetX"), offsetX + move_amount2 + value_range)

    if time:
        timer time+1 action [Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page), \
                            Function(change_time, current_time), renpy.restart_interaction]
        key "game_menu" action [Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page), \
                            Function(change_time, current_time)]
        key "hide_windows" action NullAction()
    else:
        key "game_menu" action Return()

    $state_list = [tag for tag, z in _viewers.zorder_list[current_scene][layer]]
    $page_list = []
    if len(state_list) > _viewers.tab_amount_in_page:
        for i in range(0, len(state_list)//_viewers.tab_amount_in_page):
            $page_list.append(state_list[i*_viewers.tab_amount_in_page:(i+1)*_viewers.tab_amount_in_page])
        if len(state_list)%_viewers.tab_amount_in_page != 0:
            $page_list.append(state_list[len(state_list)//_viewers.tab_amount_in_page*_viewers.tab_amount_in_page:])
    else:
        $page_list.append(state_list)
    $state=_viewers.get_image_state(layer)
    if get_value("perspective", scene_keyframes[current_scene][1], True) == False and tab == "camera":
        $tab = state_list[0]

    frame:
        style_group "action_editor"
        if time:
            at _no_show()
        has vbox

        hbox:
            style_group "action_editor_a"
            textbutton _("time: [current_time:>05.2f] s") action Function(_viewers.edit_time)
            textbutton _("<") action Function(_viewers.prev_time)
            textbutton _(">") action Function(_viewers.next_time)
            textbutton _("play") action play_action
            bar adjustment ui.adjustment(range=persistent._time_range, value=current_time, changed=change_time):
                xalign 1. yalign .5 style "action_editor_bar"
        hbox:
            style_group "action_editor_a"
            textbutton _("option") action Show("_action_editor_option")
            textbutton _("remove keyframes"):
                action [SensitiveIf(current_time in sorted_keyframes[current_scene]), \
                Function(_viewers.remove_all_keyframe, current_time), renpy.restart_interaction]
            textbutton _("move keyframes"):
                action [SensitiveIf(current_time in sorted_keyframes[current_scene]), \
                SelectedIf(False), SetField(_viewers, "moved_time", current_time), Show("_move_keyframes")]
            textbutton _("hide") action HideInterface()
            textbutton _("clipboard") action Function(_viewers.put_clipboard)
            textbutton _("x") action Return()
        hbox:
            style_group "action_editor_a"
            textbutton _("scene") action [SensitiveIf(len(scene_keyframes) > 1), Show("_scene_editor")]
            for i, ks in enumerate(all_keyframes):
                textbutton "[i]" action [SelectedIf(current_scene == i), Function(_viewers.change_scene, i)]
            textbutton _("+") action _viewers.add_scene
        hbox:
            style_group "action_editor_a"
            xfill False
            textbutton _("<"):
                action [SensitiveIf(page != 0), Show("_action_editor", tab=tab, layer=layer, page=page-1), renpy.restart_interaction]
            textbutton _("camera"):
                action [SensitiveIf(get_value("perspective", scene_keyframes[current_scene][1], True) != False),
                SelectedIf(tab == "camera"), Show("_action_editor", tab="camera")]
            for n in page_list[page]:
                textbutton "{}".format(n):
                    action [SelectedIf(n == tab), Show("_action_editor", tab=n, layer=layer, page=page)]
            textbutton _("+"):
                action Function(_viewers.add_image, layer)
            textbutton _(">"):
                action [SensitiveIf(len(page_list) != page+1), Show("_action_editor", tab=tab, layer=layer, page=page+1), renpy.restart_interaction]

        if tab == "camera":
            for i, props_set_name in enumerate(props_set_names):
                if i < opened:
                    hbox:
                        textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
            textbutton "- " + props_set_names[opened] action [SelectedIf(True), NullAction()]
            for p, d in _viewers.camera_props:
                if p in props_set[opened] and (p not in props_groups["focusing"] or 
                    (persistent._viewer_focusing and get_value("perspective", scene_keyframes[current_scene][1], True))):
                    $value = get_property(p)
                    $f = generate_changed(p)
                    $use_wide_range = p not in force_float and (p in force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int)))
                    if use_wide_range:
                        $value_range = persistent._wide_range
                        $bar_page = 1
                    else:
                        $value_range = persistent._narrow_range
                        $bar_page = .05
                    if p in force_plus:
                        $bar_value = value
                    else:
                        $bar_value = value + value_range
                        $value_range = value_range*2
                    if not use_wide_range or isinstance(value, float):
                        $value_format = float_format
                    else:
                        $value_format = int_format
                    hbox:
                        textbutton "  [p]":
                            action [SensitiveIf(p in all_keyframes[current_scene]),
                            SelectedIf(keyframes_exist(p)), Show("_edit_keyframe", key=p, use_wide_range=use_wide_range, change_func=f)]
                        textbutton value_format.format(value):
                            action Function(edit_value, f, use_wide_range=use_wide_range, default=value, force_plus=p in force_plus)
                            alternate Function(reset, p) style_group "action_editor_b"
                        bar adjustment ui.adjustment(range=value_range, value=bar_value, page=bar_page, changed=f):
                            xalign 1. yalign .5 style "action_editor_bar"
            for i, props_set_name in enumerate(props_set_names):
                if i > opened:
                    hbox:
                        textbutton "+ "+props_set_name:
                            action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
        else:
            for i, props_set_name in enumerate(props_set_names):
                if i < opened:
                    hbox:
                        textbutton "+ "+props_set_name:
                            action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
            textbutton "- " + props_set_names[opened] action [SelectedIf(True), NullAction()]
            for p, d in _viewers.transform_props:
                if p in props_set[opened] and (p not in props_groups["focusing"] and (((persistent._viewer_focusing 
                    and get_value("perspective", scene_keyframes[current_scene][1], True)) and p != "blur") 
                    or (not persistent._viewer_focusing or not get_value("perspective", scene_keyframes[current_scene][1], True)))):
                    $key = (tab, layer, p)
                    $value = get_property(key)
                    $f = generate_changed(key)
                    $use_wide_range = p not in force_float and (p in force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int)))
                    if use_wide_range:
                        $value_range = persistent._wide_range
                        $bar_page = 1
                    else:
                        $value_range = persistent._narrow_range
                        $bar_page = .05
                    if not use_wide_range or isinstance(value, float):
                        $value_format = float_format
                    else:
                        $value_format = int_format
                    hbox:
                        textbutton "  [p]":
                            action [SensitiveIf(key in all_keyframes[current_scene]), 
                            SelectedIf(keyframes_exist(key)), 
                            Show("_edit_keyframe", key=key, use_wide_range=use_wide_range, change_func=f)]
                        if p == "child":
                            textbutton "[value[0]]":
                                action [SelectedIf(keyframes_exist((tab, layer, "child"))), 
                                Function(_viewers.change_child, tab, layer, default=value[0])]
                                size_group None
                            textbutton "with" action None size_group None
                            textbutton "[value[1]]":
                                action [SensitiveIf(key in all_keyframes[current_scene]), 
                                SelectedIf(keyframes_exist((tab, layer, "child"))), 
                                Function(_viewers.edit_transition, tab, layer)]
                                size_group None
                        else:
                            if p in force_plus:
                                $bar_value = value
                            else:
                                $bar_value = value + value_range
                                $value_range = value_range*2
                            textbutton value_format.format(value):
                                action Function(edit_value, f, use_wide_range=use_wide_range, default=value, force_plus=p in force_plus)
                                alternate Function(reset, key) style_group "action_editor_b"
                            bar adjustment ui.adjustment(range=value_range, value=bar_value, page=bar_page, changed=f):
                                xalign 1. yalign .5 style "action_editor_bar"
            for i, props_set_name in enumerate(props_set_names):
                if i > opened:
                    hbox:
                        textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
        hbox:
            xfill False
            xalign 1.
            if tab == "camera":
                textbutton _("perspective"):
                    action [SelectedIf(get_value("perspective", scene_keyframes[current_scene][1], True)), Function(_viewers.toggle_perspective)]
                    size_group None
                textbutton _("clipboard") action Function(_viewers.put_camera_clipboard) size_group None
                # textbutton _("reset") action [_viewers.camera_reset, renpy.restart_interaction] size_group None
            else:
                textbutton _("remove") action [
                    SensitiveIf(tab in _viewers.image_state[current_scene][layer]), 
                    Show("_action_editor", tab="camera", layer=layer, opened=opened, page=page), 
                    Function(_viewers.remove_image, layer, tab)] size_group None
                textbutton _("zzoom"):
                    action [SelectedIf(get_value((tab, layer, "zzoom"), scene_keyframes[current_scene][1], True)), 
                    Function(_viewers.toggle_boolean_property, (tab, layer, "zzoom"))]
                    size_group None
                textbutton _("clipboard"):
                    action Function(_viewers.put_image_clipboard, tab, layer)
                    size_group None
                # textbutton _("reset") action [_viewers.image_reset, renpy.restart_interaction] size_group None

    if not time and persistent._show_camera_icon:
        add _viewers.camera_icon

transform _no_show():
    alpha 0

init -1598:
    style action_editor_frame:
        background "#0003"
    style action_editor_button:
        size_group "action_editor"
        background None
        idle_background None
        insensitive_background None
        ysize None
    style action_editor_text:
        color "#CCC"
        outlines [ (absolute(2), "#000", absolute(0), absolute(0)) ]
        size 18
    style action_editor_button_text is action_editor_text:
        hover_underline True
        selected_color "#FFF"
        insensitive_color "#888"
    style action_editor_label:
        xminimum 110
    style action_editor_vbox xfill True
    style action_editor_bar is slider:
        ysize 20

    style action_editor_a_button:
        take action_editor_button
        size_group None
    style action_editor_a_button_text is action_editor_button_text
    style action_editor_a_bar is action_editor_bar

    style action_editor_b_button:
        take action_editor_button
        size_group "action_editor_b"
        xminimum 140
    style action_editor_b_button_text is action_editor_button_text:
        xalign 1.0

screen _input_screen(message="type value", default=""):
    modal True
    key "game_menu" action Return("")

    frame:
        style_group "action_editor_input"

        has vbox

        label message

        hbox:
            input default default

screen _action_editor_option():
    modal True
    key "game_menu" action Hide("_action_editor_option")
    frame:
        style_group "action_editor_modal"
        has vbox
        viewport:
            ymaximum 0.7
            mousewheel True
            scrollbars "vertical"

            has vbox
            text _("Use Legacy ActionEditor Screen(recommend legacy gui for the 4:3 or small window)")
            textbutton _("legacy gui") action [SelectedIf(persistent._viewer_legacy_gui), ToggleField(persistent, "_viewer_legacy_gui"), If(persistent._viewer_legacy_gui, true=[Hide("_action_editor"), Show("_new_action_editor")], false=[Hide("_new_action_editor"), Show("_action_editor")]), Hide("_action_editor_option")]
            text _("Show/Hide rule of thirds lines")
            textbutton _("show rot") action [SelectedIf(persistent._viewer_rot), ToggleField(persistent, "_viewer_rot")]
            text _("Show/Hide window during animation in clipboard(window is forced to be hide when the action has multi scene)")
            textbutton _("hide window") action [SelectedIf(persistent._viewer_hide_window), ToggleField(persistent, "_viewer_hide_window")]
            text _("Allow/Disallow skipping animation in clipboard(be forced to allow when the action has multi scene)")
            text _("(*This doesn't work correctly when the animation include loops and that tag is already shown)")
            textbutton _("skippable") action [SelectedIf(persistent._viewer_allow_skip), ToggleField(persistent, "_viewer_allow_skip")]
            text _("Enable/Disable simulating camera blur(This is available when perspective is True)")
            textbutton _("focusing") action [SensitiveIf(_viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True)), SelectedIf(persistent._viewer_focusing), ToggleField(persistent, "_viewer_focusing"), Function(_viewers.change_time, _viewers.current_time)]
            text _("One line includes only one property in clipboard data")
            textbutton _("one_line_one_property") action [ToggleField(persistent, "_one_line_one_prop")]
            text _("Assign default warper")
            textbutton "[persistent._viewer_warper]" action _viewers.select_default_warper
            text _("Assign default transition(example: dissolve, Dissolve(5), None)")
            textbutton "[persistent._viewer_transition]" action _viewers.edit_default_transition
            text _("the time range of property bar(type float)")
            textbutton "[persistent._time_range]" action Function(_viewers.edit_range_value, persistent, "_time_range", False)
            text _("")
            text _("Below options have effect for only New GUI")
            text _("Open only one page at once")
            textbutton _("open only one page") action [SelectedIf(persistent._open_only_one_page), ToggleField(persistent, "_open_only_one_page"), If(not persistent._viewer_legacy_gui, true=Show("_new_action_editor"))]
            text _("Set the amount of change per pixel when dragging the value of the integer property(In new GUI)")
            textbutton "[persistent._viewers_wide_dragg_speed]" action Function(_viewers.edit_range_value, persistent, "_viewers_wide_dragg_speed", True)
            text _("Set the amount of change per pixel when dragging the value of the float property(In new GUI)")
            textbutton "[persistent._viewers_narow_dragg_speed]" action Function(_viewers.edit_range_value, persistent, "_viewers_narow_dragg_speed", False)
            text _("")
            text _("Below options have effect for only Legacy GUI")
            text _("Show/Hide camera icon")
            textbutton _("camera icon") action [SelectedIf(persistent._show_camera_icon), ToggleField(persistent, "_show_camera_icon")]
            text _("the wide range of property bar which is mainly used for int values(type int)")
            textbutton "[persistent._wide_range]" action Function(_viewers.edit_range_value, persistent, "_wide_range", True)
            text _("the narrow range of property bar which is used for float values(type float)")
            textbutton "[persistent._narrow_range]" action Function(_viewers.edit_range_value, persistent, "_narrow_range", False)

        textbutton _("Return") action Hide("_action_editor_option") xalign .9

screen _warper_selecter(current_warper=""):
    modal True
    key "game_menu" action Return("")

    frame:
        style_group "action_editor_subscreen"

        has vbox

        label _("Select a warper function")
        viewport:
            mousewheel True
            edgescroll (100, 100)
            xsize config.screen_width-500
            ysize config.screen_height-200
            scrollbars "vertical"
            vbox:
                for warper in sorted(renpy.atl.warpers.keys()):
                    textbutton warper:
                        action [SelectedIf((persistent._viewer_warper == warper and not current_warper) or warper == current_warper), Return(warper)]
                        hovered Show("_warper_graph", warper=warper) unhovered Hide("_warper")
        hbox:
            textbutton _("add") action OpenURL("http://renpy.org/wiki/renpy/doc/cookbook/Additional_basic_move_profiles")
            textbutton _("close") action Return("")

screen _warper_graph(warper):
    $ t=120
    $ length=300
    $ xpos=config.screen_width-400
    $ ypos=100
    # add Solid("#000", xsize=3, ysize=1.236*length, xpos=xpos+length/2, ypos=length/2+xpos, rotate=45, anchor=(.5, .5)) 
    add Solid("#CCC", xsize=length, ysize=length, xpos=xpos, ypos=ypos ) 
    add Solid("#000", xsize=length, ysize=3, xpos=xpos, ypos=length+ypos ) 
    add Solid("#000", xsize=length, ysize=3, xpos=xpos, ypos=ypos ) 
    add Solid("#000", xsize=3, ysize=length, xpos=xpos+length, ypos=ypos)
    add Solid("#000", xsize=3, ysize=length, xpos=xpos, ypos=ypos)
    for i in range(1, t):
        $ysize=int(length*renpy.atl.warpers[warper](i/float(t)))
        if ysize >= 0:
            add Solid("#000", xsize=length//t, ysize=ysize, xpos=xpos+i*length//t, ypos=length+ypos, yanchor=1.) 
        else:
            add Solid("#000", xsize=length//t, ysize=-ysize, xpos=xpos+i*length//t, ypos=length+ypos-ysize, yanchor=1.) 

screen _move_keyframes:
    modal True
    key "game_menu" action Hide("_move_keyframes")
    frame:
        yalign .5
        style_group "action_editor_subscreen"
        has vbox
        textbutton _("time: [_viewers.moved_time:>.2f] s") action Function(_viewers.edit_move_all_keyframe)
        bar adjustment ui.adjustment(range=persistent._time_range, value=_viewers.moved_time, changed=renpy.curry(_viewers.move_all_keyframe)(old=_viewers.moved_time)):
            xalign 1. yalign .5 style "action_editor_bar"
        textbutton _("close") action Hide("_move_keyframes") xalign .98

screen _edit_keyframe(key, change_func=None, use_wide_range=False):
    $check_points = _viewers.all_keyframes[_viewers.current_scene][key]
    if isinstance(key, tuple):
        $n, l, p = key
        $k_list = [key]
        $check_points_list = [check_points]
        $loop_button_action = [ToggleDict(_viewers.loops[_viewers.current_scene], key)]
        for gn, ps in _viewers.props_groups.items():
            if p in ps:
                $k_list = [(n, l, p) for p in _viewers.props_groups[gn]]
                $check_points_list = [_viewers.all_keyframes[_viewers.current_scene][k2] for k2 in k_list]
                $loop_button_action = [ToggleDict(_viewers.loops[_viewers.current_scene], k2) for k2 in k_list+[(n, l, gn)]]
    else:
        $k_list = [key]
        $p = key
        $check_points_list = [check_points]
        $loop_button_action = [ToggleDict(_viewers.loops[_viewers.current_scene], key)]
        for gn, ps in _viewers.props_groups.items():
            if key in ps:
                if gn != "focusing":
                    $k_list = _viewers.props_groups[gn]
                    $check_points_list = [_viewers.all_keyframes[_viewers.current_scene][k2] for k2 in k_list]
                    $loop_button_action = [ToggleDict(_viewers.loops[_viewers.current_scene], k2) for k2 in k_list+[gn]]

    modal True
    key "game_menu" action Hide("_edit_keyframe")
    frame:
        style_group "action_editor_subscreen"
        xfill True
        has vbox
        label _("KeyFrames") xalign .5
        for i, (v, t, w) in enumerate(check_points):
            if t == _viewers.scene_keyframes[_viewers.current_scene][1]:
                hbox:
                    textbutton _("x") action [SensitiveIf(len(check_points) == 1), Function(_viewers.remove_keyframe, remove_time=t, key=k_list), Hide("_edit_keyframe")] size_group None
                    if p == "child":
                        textbutton "[v[0]]" action Function(_viewers.change_child, n, l, time=t, default=v[0]) size_group None
                        textbutton "with" action None size_group None
                        textbutton "[v[1]]" action Function(_viewers.edit_transition, n, l, time=t) size_group None
                    else:
                        textbutton _("{}".format(w)) action None
                        if p not in [prop for ps in _viewers.props_groups.values() for prop in ps]:
                            textbutton _("spline") action None
                        textbutton _("{}".format(v)) action [\
                            Function(_viewers.edit_value, change_func, default=v, use_wide_range=use_wide_range, force_plus=p in _viewers.force_plus, time=t), \
                            Function(_viewers.change_time, t)]
                    textbutton _("[t:>05.2f] s") action None
            else:
                hbox:
                    textbutton _("x") action [Function(_viewers.remove_keyframe, remove_time=t, key=k_list), renpy.restart_interaction] size_group None
                    if p == "child":
                        textbutton "[v[0]]" action Function(_viewers.change_child, n, l, time=t, default=v[0]) size_group None
                        textbutton "with" action None size_group None
                        textbutton "[v[1]]" action Function(_viewers.edit_transition, n, l, time=t) size_group None
                    else:
                        textbutton _("{}".format(w)) action Function(_viewers.edit_warper, check_points=check_points_list, old=t, value_org=w)
                        if p not in [prop for ps in _viewers.props_groups.values() for prop in ps]:
                            textbutton _("spline") action [\
                                SelectedIf(t in _viewers.splines[_viewers.current_scene][key]), \
                                Show("_spline_editor", change_func=change_func, \
                                    key=key, prop=p, pre=check_points[i-1], post=check_points[i], default=v, \
                                    use_wide_range=use_wide_range, force_plus=p in _viewers.force_plus, time=t)]
                        textbutton _("{}".format(v)) action [\
                            Function(_viewers.edit_value, change_func, default=v, use_wide_range=use_wide_range, force_plus=p in _viewers.force_plus, time=t), \
                            Function(_viewers.change_time, t)]
                    textbutton _("[t:>05.2f] s") action Function(_viewers.edit_move_keyframe, keys=k_list, old=t)
                    bar adjustment ui.adjustment(range=persistent._time_range, value=t, changed=renpy.curry(_viewers.move_keyframe)(old=t, keys=k_list)):
                        xalign 1. yalign .5 style "action_editor_bar"
        hbox:
            textbutton _("loop") action loop_button_action size_group None
            textbutton _("close") action Hide("_edit_keyframe") xalign .98 size_group None

screen _spline_editor(change_func, key, prop, pre, post, default, use_wide_range, force_plus, time):

    modal True
    key "game_menu" action Hide("_spline_editor")
    $cs = _viewers.all_keyframes[_viewers.current_scene][key]
    if use_wide_range:
        $value_range = persistent._wide_range
        $_page = 1
    else:
        $value_range = persistent._narrow_range
        $_page = 0.05
    if not force_plus:
        default old_v = post[0] + value_range
    else:
        default old_v = post[0]
    on "show" action [Function(_viewers.change_time, time)]
    on "hide" action [Function(change_func, old_v), Function(_viewers.change_time, time)]

    frame:
        style_group "spline_editor"
        xfill True
        has vbox
        label _("spline_editor") xalign .5
        hbox:
            null width 50
            text " "
            text "Start"
            text "[pre[0]]"
        if time in _viewers.splines[_viewers.current_scene][key]:
            for i, v in enumerate(_viewers.splines[_viewers.current_scene][key][time]):
                textbutton _("+") action [Function(_viewers.add_knot, key, time, pre[0], knot_number=i), renpy.restart_interaction]
                hbox:
                    null width 50
                    textbutton _("x") action [Function(_viewers.remove_knot, key, time, i), renpy.restart_interaction] size_group None
                    textbutton "Knot{}".format(i+1) action None
                    textbutton "{}".format(v) action [Function(_viewers.edit_value, renpy.curry(change_func)(time=time, knot_number=i), default=v, use_wide_range=use_wide_range, force_plus=force_plus, time=time)]
                    if force_plus:
                        $_v = v
                    else:
                        $_v = v + value_range
                        $_value_range = value_range*2
                    bar adjustment ui.adjustment(range=_value_range, value=_v, page=_page, changed=renpy.curry(change_func)(time=time, knot_number=i)):
                        xalign 1. yalign .5 style "action_editor_bar"
        textbutton _("+") action [Function(_viewers.add_knot, key, time, pre[0]), renpy.restart_interaction]
        hbox:
            null width 50
            text " "
            text "End"
            text "[post[0]]"
        hbox:
            xfill True
            textbutton _("close") action Hide("_spline_editor") xalign .9

screen _scene_editor():

    modal True
    key "game_menu" action Hide("_scene_editor")
    # on "hide" action Show("_action_editor")

    frame:
        style_group "scene_editor"
        xfill True
        has vbox
        label _("scene_editor") xalign .5
        text "    Scene0"
        for i, (tran, t, w) in enumerate(_viewers.scene_keyframes):
            if i > 0:
                hbox:
                    textbutton _("x") action Function(_viewers.remove_scene, i)
                    textbutton "Scene[i]" action None
                    textbutton "with" action None
                    textbutton "[tran]" action Function(_viewers.edit_scene_transition, i)
                    textbutton "[t:>.2f] s" action Function(_viewers.edit_move_scene, i)
                    bar adjustment ui.adjustment(range=persistent._time_range, value=t, changed=renpy.curry(_viewers.move_scene)(scene_num=i)) xalign 1. yalign .5 style "action_editor_bar"
        hbox:
            xfill True
            textbutton _("close") action Hide("_scene_editor") xalign .9

init -1598:
    style action_editor_modal_frame background "#000D"
    style action_editor_modal_text is action_editor_text color "#AAA"
    style action_editor_modal_button is action_editor_button
    style action_editor_modal_button_text is action_editor_button_text

    style action_editor_input_frame xfill True ypos .1 xmargin .05 ymargin .05 background "#000B"
    style action_editor_input_vbox xfill True spacing 30
    style action_editor_input_label xalign .5
    style action_editor_input_hbox  xalign .5

    style action_editor_subscreen_frame is action_editor_modal_frame
    style action_editor_subscreen_text is action_editor_modal_text
    style action_editor_subscreen_button_text is action_editor_modal_button_text
    style action_editor_subscreen_button is action_editor_modal_button:
        size_group "action_editor_subscreen"

    style spline_editor_frame is action_editor_modal_frame
    style spline_editor_text is action_editor_text size_group "spline_editor"
    style spline_editor_button is action_editor_modal_button size_group "spline_editor"
    style spline_editor_button_text is action_editor_modal_button_text

    style scene_editor_frame is action_editor_modal_frame
    style scene_editor_text is action_editor_text size_group None
    style scene_editor_button is action_editor_modal_button size_group None
    style scene_editor_button_text is action_editor_modal_button_text



init -1598 python in _viewers:
    def drag_change_time(drags, drops):
        barsize = config.screen_width-c_box_size-50+key_half_xsize
        frac = drags[0].x/float(barsize)
        goal_frac = (frac - float(key_half_xsize)/barsize)*float(barsize)/(barsize-2*key_half_xsize)
        change_time(goal_frac*renpy.store.persistent._time_range)
        return None


    def generate_key_drag(key, t):
        key_list = [key]
        if isinstance(key, tuple):
            n, l, p = key
            for gn, ps in props_groups.items():
                if p in ps:
                    key_list = [(n, l, p) for p in props_groups[gn]]
        else:
            p = key
            for gn, ps in props_groups.items():
                if key in ps:
                    if gn != "focusing":
                        key_list = props_groups[gn]

        def changed(drags, drops):
            x = drags[0].x
            y = drags[0].y
            barsize = config.screen_width - c_box_size-50 + key_half_xsize
            frac = float(x)/(barsize-key_xsize)
            goal = frac*renpy.store.persistent._time_range
            if not move_keyframe(new=goal, old=t, keys=key_list):
                drags[0].snap(to_drag_pos(t), y)

        return changed


    def absolute_pos(st, at):
        (x, y) = renpy.get_mouse_pos()
        if round(float(config.screen_width)/config.screen_height, 2) == 1.78:
            x = int((x-config.screen_width*(1.-preview_size)/2)/preview_size)
            y = int(y/preview_size)
        else:
            (x, y) = (x/preview_size, y/preview_size)
        return Text("({:>4}, {:>4})".format(x, y), size=16), 0.1


    def rel_pos(st, at):
        (x, y) = renpy.get_mouse_pos()
        if round(float(config.screen_width)/config.screen_height, 2) == 1.78:
            x = int((x-config.screen_width*(1.-preview_size)/2)/preview_size)
            y = int(y/preview_size)
        else:
            (x, y) = (x/preview_size, y/preview_size)
        rx = x/float(config.screen_width)
        ry = y/float(config.screen_height)
        return Text("({:>.3}, {:>.3})".format(rx, ry), size=16), 0.1


    def to_drag_pos(time):
        pos = time/renpy.store.persistent._time_range
        barsize = config.screen_width-c_box_size-50+key_half_xsize
        return pos*float(barsize-key_xsize)/barsize


    class DraggableValue(renpy.Displayable):


        def __init__(self, format, key, changed, use_wide_range, force_plus, clicked=None, alternate=None, **properties):
            super(DraggableValue, self).__init__(**properties)
            from pygame import MOUSEMOTION, KMOD_CTRL, KMOD_SHIFT
            from pygame.key import get_mods
            # The child.
            self.format = format
            self.key = key
            self.changed = changed
            self.use_wide_range = use_wide_range
            self.force_plus = force_plus
            self.clicked = clicked
            self.alternate = alternate
            self.dragging = False
            self.kwargs = {}
            for k, v in properties.items():
                if k.startswith("text_") and not k.startswith("text_hover_"):
                    self.kwargs[k[5:]] = v
            self.hover_kwargs = dict(self.kwargs)
            for k, v in properties.items():
                if k.startswith("text_hover_"):
                    self.hover_kwargs[k[11:]] = v
            if isinstance(key, tuple):
                self.prop = key[2]
            else:
                self.prop = key

            if self.use_wide_range:
                self.change_per_pix = int(persistent._viewers_wide_dragg_speed)
            else:
                self.change_per_pix = float(persistent._viewers_narow_dragg_speed)
            self.clicking = False
            self.hovered = False

            self.MOUSEMOTION = MOUSEMOTION
            self.SLOW = 0.33
            self.NORMAL = 1.0
            self.FAST = 3.0
            self.KMOD_SHIFT = KMOD_SHIFT
            self.KMOD_CTRL = KMOD_CTRL
            self.get_mods = get_mods


            self.speed = 1.0


        def __eq__(self, other):
            return True


        def render(self, width, height, st, at):
            value = get_property(self.key)
            if self.hovered:
                kwargs = self.hover_kwargs
            else:
                kwargs = self.kwargs
            # kwargs = self.kwargs
            d = Text(self.format.format(value), align=(.5, .5), **kwargs)
            box = Fixed()
            box.add(d)
            render = box.render(width, height, st, at)
            self.width, self.height = render.get_size()
            return render


        def event(self, ev, x, y, st):
            if ev.type == self.MOUSEMOTION and self.clicking:
                self.dragging = True
                v = ((x - self.last_x)*self.change_per_pix)*self.speed+self.value
                if self.use_wide_range:
                    v = int(v)
                self.changed(convert_to_changed_value(v, self.force_plus, self.use_wide_range))

            self.hovered = False
            if not self.dragging and x >= 0 and x <= self.width and y >= 0 and y <= self.height:
                self.hovered = True
                if renpy.map_event(ev, "mousedown_1"):
                    if self.get_mods() & self.KMOD_CTRL:
                        self.speed = self.SLOW
                    elif self.get_mods() & self.KMOD_SHIFT:
                        self.speed = self.FAST
                    else:
                        self.speed = self.NORMAL
                    self.clicking = True
                    self.last_x = x
                    self.last_y = y
                    self.value = get_property(self.key)
                    raise renpy.display.core.IgnoreEvent()
                elif not self.dragging and renpy.map_event(ev, "mouseup_1"):
                    self.dragging = False
                    if self.clicking == True:
                        self.clicking = False
                        if self.clicked is not None:
                            rv = renpy.run(self.clicked)
                        if rv is not None:
                            return rv
                        raise renpy.display.core.IgnoreEvent()
                elif renpy.map_event(ev, "button_alternate"):
                    if self.alternate is not None:
                        rv = renpy.run(self.alternate)
                    if rv is not None:
                        return rv
                    raise renpy.display.core.IgnoreEvent()
            elif self.clicking and renpy.map_event(ev, "mouseup_1"):
                self.dragging = False
                self.clicking = False
                self.last_x = None
                self.last_y = None
                raise renpy.display.core.IgnoreEvent()
            renpy.redraw(self, 0)


        def per_interact(self):
            renpy.redraw(self, 0)


    class CameraIcon(renpy.Displayable):

        def __init__(self, child, **properties):
            super(CameraIcon, self).__init__(**properties)
            # The child.
            self.child = renpy.displayable(child)
            self.dragging = False


        def init(self, int_x=True, int_y=True):
            self.int_x = int_x
            self.int_y = int_y
            if self.int_x:
                self.x_range = renpy.store.persistent._wide_range
            else:
                self.x_range = renpy.store.persistent._narrow_range
            if self.int_y:
                self.y_range = renpy.store.persistent._wide_range
            else:
                self.y_range = renpy.store.persistent._narrow_range

            self.cx = self.x = (0.5 + get_property("offsetX")/(2.*self.x_range))*config.screen_width
            self.cy = self.y = (0.5 + get_property("offsetY")/(2.*self.y_range))*config.screen_height


        def render(self, width, height, st, at):
            # Create a render from the child.
            child_render = renpy.render(self.child, width, height, st, at)
            # Get the size of the child.
            self.width, self.height = child_render.get_size()
            # Create the render we will return.
            render = renpy.Render(config.screen_width, config.screen_height)
            # Blit (draw) the child's render to our render.
            render.blit(child_render, (self.x-self.width/2., self.y-self.height/2.))
            # Return the render.
            return render


        def event(self, ev, x, y, st):

            if renpy.map_event(ev, "mousedown_1"):
                if self.x-self.width/2. <= x and x <= self.x+self.width/2. \
                    and self.y-self.height/2. <= y and y <= self.y+self.height/2.:
                    self.dragging = True
            elif renpy.map_event(ev, "mouseup_1"):
                self.dragging = False

            if get_property("offsetX") != int(self.cx) or get_property("offsetY") != int(self.cy):
                self.x = (0.5 + get_property("offsetX")/(2.*self.x_range))*config.screen_width
                self.y = (0.5 + get_property("offsetY")/(2.*self.y_range))*config.screen_height
                renpy.redraw(self, 0)

            if self.dragging:
                if self.x != x or self.y != y:
                    self.cx = 2*self.x_range*float(x)/config.screen_width
                    self.cy = 2*self.y_range*float(y)/config.screen_height
                    if self.int_x:
                        self.cx = int(self.cx)
                    if self.int_y:
                        self.cy = int(self.cy)
                    if self.cx != get_property("offsetX") or self.cy != get_property("offsetY"):
                        generate_changed("offsetX")(self.cx)
                        generate_changed("offsetY")(self.cy)
                    self.x, self.y = x, y
                    renpy.redraw(self, 0)


        def per_interact(self):
            renpy.redraw(self, 0)


        def visit(self):
            return [ self.child ]
    camera_icon = CameraIcon("camera.png")
