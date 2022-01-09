#課題

#再現条件不明
#hideが動作しないときがある
#ホイールが片側動作しない, warper選択画面でのスクロールもできなかった
#childのみならばparallelなくてよい

#新機能
#再生中に右クリックで再生停止可能に
#クリップボードデータを出来るだけ短いフォーマットに変更
#zzoomを追加
#optionページを追加

#変更
#レイアウトを調整
#x, ypos, xyanchor, xyoffsetをpos, anchor, offsetにまとめた
#表示ずみのタグの画像を追加するとタグ+数値として追加するように変更

#修正
#Ren'Py 8に対応

#既知の問題
#colormatrix, transformmatrixは十分再現できない

# tab="images"/"3Dstage", layer="master",  
screen _action_editor(tab="3Dstage", layer="master", opened=0, time=0, page=0):
    $play_action = [SensitiveIf(_viewers.sorted_keyframes), SelectedIf(False), Function(_viewers.camera_viewer.play, play=True), Function(_viewers.transform_viewer.play, play=True), Hide("_action_editor"), Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page, time=_viewers.get_animation_delay())]
    key "rollback"    action Function(_viewers.camera_viewer.generate_changed("offsetZ"), _viewers.camera_viewer.get_property("offsetZ")+100+persistent._int_range)
    key "rollforward" action Function(_viewers.camera_viewer.generate_changed("offsetZ"), _viewers.camera_viewer.get_property("offsetZ")-100+persistent._int_range)
    key "K_SPACE" action play_action

    $offsetX, offsetY = _viewers.camera_viewer.get_property("offsetX"), _viewers.camera_viewer.get_property("offsetY")
    $range = persistent._int_range
    $move_amount1 = 100
    $move_amount2 = 300
    if _viewers.fps_keymap:
        key "s" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY + move_amount1 + range)
        key "w" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY - move_amount1 + range)
        key "a" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX - move_amount1 + range)
        key "d" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX + move_amount1 + range)
        key "S" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY + move_amount2 + range)
        key "W" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY - move_amount2 + range)
        key "A" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX - move_amount2 + range)
        key "D" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX + move_amount2 + range)
    else:
        key "j" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY + move_amount1 + range)
        key "k" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY - move_amount1 + range)
        key "h" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX - move_amount1 + range)
        key "l" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX + move_amount1 + range)
        key "J" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY + move_amount2 + range)
        key "K" action Function(_viewers.camera_viewer.generate_changed("offsetY"), offsetY - move_amount2 + range)
        key "H" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX - move_amount2 + range)
        key "L" action Function(_viewers.camera_viewer.generate_changed("offsetX"), offsetX + move_amount2 + range)

    if time:
        timer time+1 action [Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page), Function(_viewers.change_time, _viewers.current_time)]
        key "game_menu" action [Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page), Function(_viewers.change_time, _viewers.current_time)]
        key "hide_windows" action NullAction()
    else:
        key "game_menu" action Return()
    #camera transformはget_properyで所得できるようになるまで時間差があるので定期更新する
    # かなり動作が重くなる
    # camera transform properties need some times until being allowed to get property so I update screen.
    if not time:
        timer .2 action renpy.restart_interaction repeat True

    $state={k: v for dic in [_viewers.transform_viewer.state_org[layer], _viewers.transform_viewer.state[layer]] for k, v in dic.items()}
    $state_list = list(state)
    $page_list = []
    if len(state_list) > _viewers.tab_amount_in_page:
        for i in range(0, len(state_list)//_viewers.tab_amount_in_page):
            $page_list.append(state_list[i*_viewers.tab_amount_in_page:(i+1)*_viewers.tab_amount_in_page])
        if len(state_list)%_viewers.tab_amount_in_page != 0:
            $page_list.append(state_list[len(state_list)//_viewers.tab_amount_in_page*_viewers.tab_amount_in_page:])
    else:
        $page_list.append(state_list)

    if persistent._viewer_rot:
        on "show" action Show("_rot")

    frame:
        style_group "action_editor"
        if time:
            at _no_show()
        vbox:

            hbox:
                style_group "action_editor_a"
                textbutton _("time: [_viewers.current_time:>.2f] s") action Function(_viewers.edit_time)
                textbutton _("<") action Function(_viewers.prev_time)
                textbutton _(">") action Function(_viewers.next_time)
                bar adjustment ui.adjustment(range=persistent._time_range, value=_viewers.current_time, changed=_viewers.change_time) xalign 1. yalign .5 style "action_editor_bar"
            hbox:
                style_group "action_editor_a"
                hbox:
                    textbutton _("option") action Show("_action_editor_option")
                    textbutton _("hide") action HideInterface()
                    textbutton _("play") action play_action
                    textbutton _("clipboard") action Function(_viewers.put_clipboard)
                hbox:
                    xalign 1.
                    textbutton _("x") action Return()
            hbox:
                style_group "action_editor_a"
                # textbutton _("clear keyframes") action [SensitiveIf(_viewers.sorted_keyframes), Function(_viewers.clear_keyframes), renpy.restart_interaction]
                textbutton _("remove keyframes") action [SensitiveIf(_viewers.current_time in _viewers.sorted_keyframes), Function(_viewers.remove_all_keyframe, _viewers.current_time), renpy.restart_interaction]
                textbutton _("move keyframes") action [SensitiveIf(_viewers.current_time in _viewers.sorted_keyframes), SelectedIf(False), SetField(_viewers, "moved_time", _viewers.current_time), Show("_move_keyframes")]
                # textbutton _("last moves") action [SensitiveIf(_last_camera_arguments), Function(_viewers.last_moves), renpy.restart_interaction]
            null height 10
            hbox:
                style_group "action_editor_a"
                xfill False
                textbutton _("<") action [SensitiveIf(page != 0), Show("_action_editor", tab=tab, layer=layer, page=page-1), renpy.restart_interaction]
                textbutton _("3Dstage") action [SelectedIf(tab == "3Dstage"), Show("_action_editor", tab="3Dstage")]
                for n in page_list[page]:
                    textbutton "{}".format(n) action [SelectedIf(n == tab), Show("_action_editor", tab=n, layer=layer, page=page)]
                textbutton _("+") action Function(_viewers.transform_viewer.add_image, layer)
                textbutton _(">") action [SensitiveIf(len(page_list) != page+1), Show("_action_editor", tab=tab, layer=layer, page=page+1), renpy.restart_interaction]

            if tab == "3Dstage":
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i < opened:
                        hbox:
                            style_group "action_editor"
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
                textbutton "- " + _viewers.props_set_names[opened] action [SelectedIf(True), NullAction()] style_group "action_editor"
                for p, d in _viewers.camera_viewer.props:
                    if p in _viewers.props_set[opened] and (p not in _viewers.props_groups["focusing"] or persistent._viewer_focusing):
                        $value = _viewers.camera_viewer.get_property(p)
                        $ f = _viewers.camera_viewer.generate_changed(p)
                        $reset_action = [Function(_viewers.camera_viewer.reset, p)]
                        if p in _viewers.props_groups["focusing"]:
                            for l in renpy.config.layers:
                                $state={n: v for dic in [_viewers.transform_viewer.state_org[l], _viewers.transform_viewer.state[l]] for n, v in dic.items()}
                                $reset_action += [Function(_viewers.transform_viewer.reset, (tag, l, p)) for tag in state]
                        if p not in _viewers.force_float and (p in _viewers.force_int_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                            hbox:
                                style_group "action_editor"
                                textbutton "[p]" action [SensitiveIf(p in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", k=p, force_int=True, edit_func=_viewers.camera_viewer.edit_value, change_func=f, range=persistent._int_range, int=True)]
                                if isinstance(value, int):
                                    textbutton "[value]" action Function(_viewers.camera_viewer.edit_value, f, force_int=True, default=value, force_plus=p in _viewers.force_plus) alternate reset_action
                                else:
                                    textbutton "[value:>.2f]" action Function(_viewers.camera_viewer.edit_value, f, force_int=True, default=value, force_plus=p in _viewers.force_plus) alternate reset_action
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._int_range, value=value, page=1, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._int_range*2, value=value+persistent._int_range, page=1, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                        else:
                            hbox:
                                style_group "action_editor"
                                textbutton "[p]" action [SensitiveIf(p in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", k=p, edit_func=_viewers.camera_viewer.edit_value, change_func=f, range=persistent._float_range, int=False)]
                                textbutton "[value:>.2f]" action Function(_viewers.camera_viewer.edit_value, f, force_int=False, default=value, force_plus=p in _viewers.force_plus) alternate reset_action
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._float_range, value=value, page=.05, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._float_range*2, value=value+persistent._float_range, page=.05, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i > opened:
                        hbox:
                            style_group "action_editor"
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
            else:
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i < opened:
                        hbox:
                            style_group "action_editor"
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
                textbutton "- " + _viewers.props_set_names[opened] action [SelectedIf(True), NullAction()] style_group "action_editor"
                for p, d in _viewers.transform_viewer.props:
                    if p in _viewers.props_set[opened] and (p not in _viewers.props_groups["focusing"] and ((persistent._viewer_focusing and p != "blur") or (not persistent._viewer_focusing))):
                        $value = _viewers.transform_viewer.get_property(layer, tab, p)
                        $ f = _viewers.transform_viewer.generate_changed(layer, tab, p)
                        if p == "child":
                            hbox:
                                style_group "action_editor"
                                textbutton "[p]" action [SensitiveIf((tab, layer, p) in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist((tab, layer, p))), Show("_edit_keyframe", k=(tab, layer, p), force_int=True)]
                                textbutton "[value[0]]" action [SelectedIf(_viewers.keyframes_exist((tab, layer, "child"))), Function(_viewers.transform_viewer.change_child, layer, tab, default=value[0])] size_group None
                                textbutton "with" action None size_group None
                                textbutton "[value[1]]" action [SensitiveIf((tab, layer, p) in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist((tab, layer, "child"))), Function(_viewers.transform_viewer.edit_transition, layer, tab)] size_group None
                        elif p not in _viewers.force_float and (p in _viewers.force_int_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                            hbox:
                                style_group "action_editor"
                                textbutton "[p]" action [SensitiveIf((tab, layer, p) in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist((tab, layer, p))), Show("_edit_keyframe", k=(tab, layer, p), force_int=True, edit_func=_viewers.transform_viewer.edit_value, change_func=f, range=persistent._int_range, int=True)]
                                if isinstance(value, int):
                                    textbutton "[value]" action Function(_viewers.transform_viewer.edit_value, f, force_int=True, default=value, force_plus=p in _viewers.force_plus) alternate Function(_viewers.transform_viewer.reset, (tab, layer, p))
                                else:
                                    textbutton "[value:>.2f]" action Function(_viewers.transform_viewer.edit_value, f, force_int=True, default=value, force_plus=p in _viewers.force_plus) alternate Function(_viewers.transform_viewer.reset, (tab, layer, p))
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._int_range, value=value, page=1, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._int_range*2, value=value+persistent._int_range, page=1, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                        else:
                            hbox:
                                style_group "action_editor"
                                textbutton "[p]" action [SensitiveIf((tab, layer, p) in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist((tab, layer, p))), Show("_edit_keyframe", k=(tab, layer, p), edit_func=_viewers.transform_viewer.edit_value, change_func=f, range=persistent._float_range, int=False)]
                                textbutton "[value:>.2f]" action Function(_viewers.transform_viewer.edit_value, f, force_int=False, default=value, force_plus=p in _viewers.force_plus) alternate Function(_viewers.transform_viewer.reset, (tab, layer, p))
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._float_range, value=value, page=.05, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._float_range*2, value=value+persistent._float_range, page=.05, changed=f) xalign 1. yalign .5 style "action_editor_bar"
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i > opened:
                        hbox:
                            style_group "action_editor"
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
            hbox:
                style_group "action_editor"
                xfill False
                xalign 1.
                if tab == "3Dstage":
                    textbutton _("clipboard") action Function(_viewers.camera_viewer.put_clipboard)
                    textbutton _("reset") action [_viewers.camera_viewer.camera_reset, renpy.restart_interaction]
                else:
                    textbutton _("remove") action [SensitiveIf(tab in _viewers.transform_viewer.state[layer]), Show("_action_editor", tab="3Dstage", layer=layer, opened=opened, page=page), Function(_viewers.transform_viewer.remove_image, layer, tab)] size_group None
                    $state={n: v for dic in [_viewers.transform_viewer.state_org[layer], _viewers.transform_viewer.state[layer]] for n, v in dic.items()}
                    textbutton _("zzoom") action [SelectedIf(_viewers.transform_viewer.get_zzoom(tab, layer)), Function(_viewers.transform_viewer.toggle_zzoom, tab, layer)] size_group None
                    textbutton _("clipboard") action Function(_viewers.transform_viewer.put_clipboard, tab, layer) size_group None
                    textbutton _("reset") action [_viewers.transform_viewer.image_reset, renpy.restart_interaction] size_group None

    if not time:
        add _viewers.dragged

screen _rot(): #show rule of thirds
    #線の特定のypos 240-265で表示されない
    for i in range(1, 3):
        add Solid("#F00", xsize=config.screen_width, ysize=1, ypos=config.screen_height*i//3)
        add Solid("#F00", xsize=1, ysize=config.screen_height, xpos=config.screen_width*i//3)

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
    style action_editor_text:
        color "#CCC"
        outlines [ (absolute(2), "#000", absolute(0), absolute(0)) ]
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
        text _("Show/Hide rule of thirds lines")
        textbutton _("rot") action [SelectedIf(persistent._viewer_rot), ToggleField(persistent, "_viewer_rot"), If(renpy.get_screen("_rot"), true=Hide("_rot"), false=Show("_rot"))]
        text _("Show/Hide window during animation in clipboard")
        textbutton _("hide") action [SelectedIf(persistent._viewer_hide_window), ToggleField(persistent, "_viewer_hide_window")]
        text _("Allow/Disallow skipping animation in clipboard(*This doesn't work when the animation include loops and that tag is already shown)")
        textbutton _("skippable") action [SelectedIf(persistent._viewer_allow_skip), ToggleField(persistent, "_viewer_allow_skip")]
        text _("Enable/Disable simulating camera blur(This causes crash when perspective is False)")
        textbutton _("focusing") action [SelectedIf(persistent._viewer_focusing), ToggleField(persistent, "_viewer_focusing"), Function(_viewers.change_time, _viewers.current_time)]
        text _("Assign default warper")
        textbutton "[persistent._viewer_warper]" action _viewers.select_default_warper
        text _("Assign default transition(example: dissolve, Dissolve(5), None)")
        textbutton "[persistent._viewer_transition]" action _viewers.transform_viewer.edit_default_transition
        text _("the int range of property bar")
        textbutton "[persistent._int_range]" action Function(_viewers.edit_range_value, persistent, "_int_range", True)
        text _("the float range of property bar")
        textbutton "[persistent._float_range]" action Function(_viewers.edit_range_value, persistent, "_float_range", False)
        text _("the time range of property bar")
        textbutton "[persistent._time_range]" action Function(_viewers.edit_range_value, persistent, "_time_range", False)

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
                    textbutton warper action [SelectedIf((persistent._viewer_warper == warper and not current_warper) or warper == current_warper), Return(warper)] hovered Show("_warper_graph", warper=warper) unhovered Hide("_warper")
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
        style_group "action_editor_subscreen"
        has vbox
        textbutton _("time: [_viewers.moved_time:>.2f] s") action Function(_viewers.edit_move_all_keyframe)
        bar adjustment ui.adjustment(range=persistent._time_range, value=_viewers.moved_time, changed=renpy.curry(_viewers.move_all_keyframe)(old=_viewers.moved_time)) xalign 1. yalign .5 style "action_editor_bar"
        textbutton _("close") action Hide("_move_keyframes") xalign .98

screen _edit_keyframe(k, force_int=False, edit_func=None, change_func=None, range=None, int):
    $check_points = _viewers.all_keyframes[k]
    if isinstance(k, tuple):
        $n, l, p = k
        $k_list = k
        $check_points_list = check_points
        $loop_button_action = [ToggleDict(_viewers.loops, k)]
        for gn, ps in _viewers.props_groups.items():
            if p in ps:
                $k_list = [(n, l, p) for p in _viewers.props_groups[gn]]
                $check_points_list = [_viewers.all_keyframes[k2] for k2 in k_list]
                $loop_button_action = [ToggleDict(_viewers.loops, k2) for k2 in k_list+[(n, l, gn)]]
    else:
        $k_list = k
        $p = k
        $check_points_list = check_points
        $loop_button_action = [ToggleDict(_viewers.loops, k)]
        for gn, ps in _viewers.props_groups.items():
            if k in ps:
                if gn == "focusing":
                    $k_list = [k]
                    for layer in renpy.config.layers:
                        $state={n: v for dic in [_viewers.transform_viewer.state_org[layer], _viewers.transform_viewer.state[layer]] for n, v in dic.items()}
                        $k_list += [(n, layer, k) for n in state]
                    $check_points_list = [_viewers.all_keyframes[k2] for k2 in k_list]
                    $loop_button_action = [ToggleDict(_viewers.loops, k2) for k2 in k_list]
                else:
                    $k_list = _viewers.props_groups[gn]
                    $check_points_list = [_viewers.all_keyframes[k2] for k2 in k_list]
                    $loop_button_action = [ToggleDict(_viewers.loops, k2) for k2 in k_list+[gn]]

    modal True
    key "game_menu" action Hide("_edit_keyframe")
    frame:
        style_group "action_editor_subscreen"
        xfill True
        has vbox
        label _("KeyFrames") xalign .5
        for i, (v, t, w) in enumerate(check_points):
            if t != 0:
                hbox:
                    textbutton _("x") action [Function(_viewers.remove_keyframe, remove_time=t, key=k_list), renpy.restart_interaction] size_group None
                    if p == "child":
                        textbutton "[v[0]]" action Function(_viewers.transform_viewer.change_child, l, n, time=t, default=v[0]) size_group None
                        textbutton "with" action None size_group None
                        textbutton "[v[1]]" action Function(_viewers.transform_viewer.edit_transition, l, n, time=t) size_group None
                    else:
                        textbutton _("{}".format(w)) action Function(_viewers.edit_warper, check_points=check_points_list, old=t, value_org=w)
                        textbutton _("spline") action [SelectedIf(t in _viewers.splines[k]), Show("_spline_editor", edit_func=edit_func, change_func=change_func, key=k, prop=p, pre=check_points[i-1], post=check_points[i], default=v, force_int=force_int, force_plus=p in _viewers.force_plus, time=t, range=range, int=int)]
                        textbutton _("{}".format(v)) action [Function(edit_func, change_func, default=v, force_int=force_int, force_plus=p in _viewers.force_plus, time=t), Function(_viewers.change_time, t)]
                    textbutton _("[t:>.2f] s") action Function(_viewers.edit_move_keyframe, keys=k_list, old=t)
                    bar adjustment ui.adjustment(range=persistent._time_range, value=t, changed=renpy.curry(_viewers.move_keyframe)(old=t, keys=k_list)) xalign 1. yalign .5 style "action_editor_bar"
        hbox:
            textbutton _("loop") action loop_button_action size_group None
            textbutton _("close") action Hide("_edit_keyframe") xalign .98 size_group None

screen _spline_editor(edit_func, change_func, key, prop, pre, post, default, force_int, force_plus, time, range, int):

    modal True
    key "game_menu" action Hide("_spline_editor")
    $cs = _viewers.all_keyframes[key]
    if not force_plus:
        default old_v = post[0] + range
    else:
        default old_v = post[0]
    on "show" action [Function(_viewers.change_time, time)]
    on "hide" action [Function(change_func, old_v), Function(_viewers.change_time, time)]
    if int:
        $_page = 0.05
    else:
        $_page = 1

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
        if time in _viewers.splines[key]:
            for i, v in enumerate(_viewers.splines[key][time]):
                textbutton _("+") action [Function(_viewers.add_knot, key, time, pre[0], knot_number=i), renpy.restart_interaction]
                hbox:
                    null width 50
                    textbutton _("x") action [Function(_viewers.remove_knot, key, time, i), renpy.restart_interaction] size_group None
                    textbutton "Knot{}".format(i+1) action None
                    textbutton "{}".format(v) action [Function(edit_func, renpy.curry(change_func)(time=time, knot_number=i), default=v, force_int=force_int, force_plus=force_plus, time=time)]
                    if force_plus:
                        $_range = range
                        $_v = v
                    else:
                        $_range = range*2
                        $_v = v + range
                    bar adjustment ui.adjustment(range=_range, value=_v, page=_page, changed=renpy.curry(change_func)(time=time, knot_number=i)) xalign 1. yalign .5 style "action_editor_bar"
        textbutton _("+") action [Function(_viewers.add_knot, key, time, pre[0]), renpy.restart_interaction]
        hbox:
            null width 50
            text " "
            text "End"
            text "[post[0]]"
        hbox:
            xfill True
            textbutton _("close") action Hide("_spline_editor") xalign .9

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


init -1098 python:
    # Added keymap
    config.underlay.append(renpy.Keymap(
        action_editor = _viewers.action_editor,
        image_viewer = _viewers.open_image_viewer,
        ))


init -1598 python in _viewers:
    from math import sin, asin, cos, acos, pi
    from decimal import Decimal, ROUND_HALF_UP
    from collections import defaultdict

    # TransformViewer
    class TransformViewer(object):
        def __init__(self):

            # ((property, default)...), default is used when property can't be got.
            self.props = transform_props

        def init(self):
            if not renpy.config.developer:
                return
            sle = renpy.game.context().scene_lists
            # layer->tag->property->value
            self.state_org = {}
            self.state = {}
            # back up for reset()
            for layer in renpy.config.layers:
                self.state_org[layer] = {}
                self.state[layer] = {}
                for image in sle.layers[layer]:
                    if not image[0]:
                        continue
                    tag = image[0]
                    d = sle.get_displayable_by_tag(layer, tag)
                    if isinstance(d, renpy.display.screen.ScreenDisplayable):
                        continue
                    image_name_tuple = getattr(d, "name", None)
                    if image_name_tuple is None:
                        child = getattr(d, "child", None)
                        image_name_tuple = getattr(child, "name", None)
                    if image_name_tuple is None:
                        continue

                    name = " ".join(image.name)
                    image_name = " ".join(image_name_tuple)
                    self.state_org[layer][tag] = {}

                    pos = renpy.get_placement(d)
                    state = getattr(d, "state", None)
                    for p in ["xpos", "ypos", "xanchor", "yanchor", "xoffset", "yoffset"]:
                        self.state_org[layer][tag][p] = getattr(pos, p, None)
                    for p, default in self.props:
                        if p not in self.state_org[layer][tag]:
                            if p == "child":
                                self.state_org[layer][tag][p] = (image_name, None)
                            else:
                                self.state_org[layer][tag][p] = getattr(state, p, None)
                    for gn, ps in props_groups.items():
                        p2 = self.get_group_property(gn, getattr(d, gn, None))
                        if p2 is not None:
                            for p, v in zip(ps, p2):
                                self.state_org[layer][tag][p] = v

        def get_group_property(self, group_name, group):
            if group is None:
                return None

            if group_name == "matrixtransform":
                # can't get correct value If any other transform_matrix than below Matrixes is used
                #OffsetMatrix * RotateMatrix
                #OffsetMatrix
                #RotateMatrix
                ox = group.xdw
                oy = group.ydw
                oz = group.zdw

                sinry = (-group.zdx)
                sinry = 1.0 if sinry > 1.0 else sinry
                sinry = -1.0 if sinry < -1.0 else sinry
                ry = asin(sinry)

                for i in range(2):
                    sinrx = group.zdy/cos(ry)
                    sinrx = 1.0 if sinrx > 1.0 else sinrx
                    sinrx = -1.0 if sinrx < -1.0 else sinrx
                    rx = asin(sinrx)
                    if self.decimal(group.zdz) != self.decimal(cos(rx)*cos(ry)):
                        rx = 2*pi - rx
                
                    cosrz = group.xdx/cos(ry)
                    cosrz = 1.0 if cosrz > 1.0 else cosrz
                    cosrz = -1.0 if cosrz < -1.0 else cosrz
                    rz = acos(cosrz)
                    if self.decimal(group.ydx) != self.decimal(cos(ry)*sin(rz)):
                        rz = 2*pi - rz

                    if self.decimal(group.ydy) != self.decimal(cos(rx)*cos(rz)+sin(rx)*sin(ry)*sin(rz)):
                        ry = pi - ry
                    else:
                        break
                if (self.decimal(group.xdy) != self.decimal(-cos(rx)*sin(rz)+cos(rz)*sin(rx)*sin(ry))) or (self.decimal(group.xdz) != self.decimal(cos(rx)*cos(rz)*sin(ry)+sin(rx)*sin(rz))) or (self.decimal(group.ydz) != self.decimal(cos(rx)*sin(ry)*sin(rz)-cos(rz)*sin(rx))):
                    #no supported matrix is used.
                    return 0., 0., 0., 0., 0., 0.

                if self.decimal(rx) >= self.decimal(2*pi):
                    rx = rx - 2*pi
                if self.decimal(ry) >= self.decimal(2*pi):
                    ry = ry - 2*pi
                if self.decimal(rz) >= self.decimal(2*pi):
                    rz = rz - 2*pi

                if self.decimal(rx) <= -self.decimal(2*pi):
                    rx = rx + 2*pi
                if self.decimal(ry) <= -self.decimal(2*pi):
                    ry = ry + 2*pi
                if self.decimal(rz) <= -self.decimal(2*pi):
                    rz = rz + 2*pi

                return rx*180.0/pi, ry*180.0/pi, rz*180.0/pi, ox, oy, oz

            elif group_name == "matrixanchor":
                return group
            elif group_name == "matrixcolor":
                #can't get properties from matrixcolor
                return 0., 1., 1., 0., 0.

            elif group_name == "crop":
                return group
            else:
                return None

        def decimal(self, a):
            return Decimal(str(a)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

        def reset(self, key_list):
            if not isinstance(key_list, list):
                key_list = [key_list]
            for key in key_list:
                tag, layer, prop = key
                state = {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}
                kwargs = {}
                for p, d in self.props:
                    value = self.get_property(layer, tag, p, False)
                    if value is not None:
                        kwargs[p] = value
                    # elif p != "rotate":
                    #     kwargs[p] = d
                    if p == prop:
                        if state[tag][prop] is not None:
                            v = state[tag][prop]
                        else:
                            v = d
                kwargs[prop] = v
                #もともとNoneでNoneとデフォルトで結果が違うPropertyはリセット時にずれるが、デフォルの値で入力すると考えてキーフレーム設定した方が自然
                self.set_keyframe(layer, tag, prop, v)
            change_time(current_time)

        def image_reset(self):
            key_list = [(tag, layer, prop) for layer in renpy.config.layers for tag, props in {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}.items() for prop in props]
            self.reset(key_list)

        def set_keyframe(self, layer, tag, prop, value, recursion=False, time=None):
            if time is None:
                time = renpy.store._viewers.current_time
            keyframes = all_keyframes.get((tag, layer, prop), [])
            if keyframes:
                for i, (v, t, w) in enumerate(keyframes):
                    if time < t:
                        keyframes.insert(i, (value, time, renpy.store.persistent._viewer_warper))
                        break
                    elif time == t:
                        keyframes[i] = ( value, time, renpy.store.persistent._viewer_warper)
                        break
                else:
                    keyframes.append((value, time, renpy.store.persistent._viewer_warper))
            else:
                if time == 0:
                    all_keyframes[(tag, layer, prop)] = [(value, time, renpy.store.persistent._viewer_warper)]
                else:
                    org = {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}[tag][prop]
                    if org is None:
                        org = self.get_default(prop)
                    if prop == "child" and tag in self.state[layer]:
                        org = (None, None)
                    all_keyframes[(tag, layer, prop)] = [(org, 0, renpy.store.persistent._viewer_warper), (value, time, renpy.store.persistent._viewer_warper)]
            sort_keyframes()
            
            for gn, ps in props_groups.items():
                ps_set = set(ps)
                if prop in ps_set and gn != "focusing" and recursion == False:
                    ps_set.remove(prop)
                    for p in ps_set:
                        self.set_keyframe(layer, tag, p, self.get_property(layer, tag, p), True, time=time)

        def play(self, play):
            for layer in renpy.config.layers:
                state = {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}
                for tag in state:
                    check_points = {}
                    for prop, d in self.props:
                        if (tag, layer, prop) in all_keyframes:
                            check_points[prop] = all_keyframes[(tag, layer, prop)]
                    # if not check_points: # ビューワー上でのアニメーション(フラッシュ等)の誤動作を抑制
                    #     continue
                    #ひとつでもprops_groupsのプロパティがあればグループ単位で追加する
                    for gn, ps in props_groups.items():
                        group_flag = False
                        for prop in ps:
                            if not prop in check_points:
                                if state[tag].get(prop, None) is not None:
                                    v = state[tag][prop]
                                else:
                                    v = self.get_default(prop)
                                check_points[prop] = [(v, 0, None)]
                            else:
                                group_flag = True
                        if not group_flag:
                            for prop in ps:
                                del check_points[prop]
                    if renpy.store.persistent._viewer_focusing:
                        if "blur" in check_points:
                            del check_points["blur"]
                        if "focusing" not in check_points:
                            check_points["focusing"] = [(self.get_default("focusing"), 0, None)]
                            check_points["dof"] = [(self.get_default("dof"), 0, None)]
                    else:
                        for p in ["focusing", "dof"]:
                            if p in check_points:
                                del check_points[p]
                        if "blur" not in check_points:
                            blur = state[tag].get("blur", None)
                            if blur is None:
                                blur = self.get_default("blur")
                            check_points["blur"] = [(blur, 0, None)]
                    loop = {prop+"_loop": loops[(tag, layer, prop)] for prop, d in self.props}
                    spline = {prop+"_spline": splines[(tag, layer, prop)] for prop, d in self.props}
                    image_name = state[tag]["child"][0]
                    if play:
                        renpy.show(image_name, [renpy.store.Transform(function=renpy.curry(self.transform)(check_points=check_points, loop=loop, spline=spline))], layer=layer, tag=tag)
                    else:
                        renpy.show(image_name, [renpy.store.Transform(function=renpy.curry(self.transform)(check_points=check_points, loop=loop, spline=spline, time=renpy.store._viewers.current_time))], layer=layer, tag=tag)

        def transform(self, tran, st, at, check_points, loop, spline=None, subpixel=True, crop_relative=True, time=None):
            # check_points = { prop: [ (value, time, warper).. ] }
            if subpixel is not None:
                tran.subpixel = subpixel
            if crop_relative is not None:
                tran.crop_relative = crop_relative
            if time is None:
                time = st
            # tran.transform_anchor = True
            group_cache = defaultdict(lambda:{})

            for p, cs in check_points.items():
                if not cs:
                    break
                    
                if loop[p+"_loop"] and cs[-1][1]:
                    if time % cs[-1][1] != 0:
                        time = time % cs[-1][1]

                for i in range(1, len(cs)):
                    checkpoint = cs[i][1]
                    pre_checkpoint = cs[i-1][1]
                    if time < checkpoint:
                        start = cs[i-1]
                        goal = cs[i]
                        if p != "child":
                            if checkpoint != pre_checkpoint:
                                g = renpy.atl.warpers[goal[2]]((time - pre_checkpoint) / float(checkpoint - pre_checkpoint))
                            else:
                                g = 1.
                            default = self.get_default(p)
                            if goal[0] is not None:
                                if start[0] is None:
                                    start_v = default
                                else:
                                    start_v = start[0]
                                knots = []
                                if checkpoint in spline[p+"_spline"]:
                                    knots = spline[p+"_spline"][checkpoint]
                                    if knots:
                                        knots = [start_v] + knots + [goal[0]]
                                if knots:
                                    v = renpy.atl.interpolate_spline(g, knots)
                                else:
                                    v = g*(goal[0]-start_v)+start_v
                                if isinstance(goal[0], int) and p not in force_float:
                                    v = int(v)
                                for gn, ps in props_groups.items():
                                    if p in ps:
                                        group_cache[gn][p] = v
                                        if len(group_cache[gn]) == len(props_groups[gn]):
                                            if gn == "matrixtransform":
                                                rx, ry, rz = group_cache[gn]["rotateX"], group_cache[gn]["rotateY"], group_cache[gn]["rotateZ"]
                                                ox, oy, oz = group_cache[gn]["offsetX"], group_cache[gn]["offsetY"], group_cache[gn]["offsetZ"]
                                                result = renpy.store.Matrix.offset(ox, oy, oz)*renpy.store.Matrix.rotate(rx, ry, rz)
                                                setattr(tran, gn, result)
                                            elif gn == "matrixanchor":
                                                mxa, mya = group_cache[gn]["matrixanchorX"], group_cache[gn]["matrixanchorY"]
                                                result = (mxa, mya)
                                                setattr(tran, gn, result)
                                            elif gn ==  "matrixcolor":
                                                i, c, s, b, h = group_cache[gn]["invert"], group_cache[gn]["contrast"], group_cache[gn]["saturate"], group_cache[gn]["bright"], group_cache[gn]["hue"]
                                                result = renpy.store.InvertMatrix(i)*renpy.store.ContrastMatrix(c)*renpy.store.SaturationMatrix(s)*renpy.store.BrightnessMatrix(b)*renpy.store.HueMatrix(h)
                                                setattr(tran, gn, result)
                                            elif gn == "crop":
                                                result = (group_cache[gn]["cropX"], group_cache[gn]["cropY"], group_cache[gn]["cropW"], group_cache[gn]["cropH"])
                                                setattr(tran, gn, result)
                                            elif gn == "focusing":
                                                focusing = group_cache["focusing"]["focusing"]
                                                dof = group_cache["focusing"]["dof"]
                                                image_zpos = 0
                                                if tran.zpos:
                                                    image_zpos = tran.zpos
                                                if tran.matrixtransform:
                                                    image_zpos += tran.matrixtransform.zdw
                                                camera_zpos = 0
                                                if "master" in renpy.game.context().scene_lists.camera_transform:
                                                    props = renpy.game.context().scene_lists.camera_transform["master"]
                                                    if props.zpos:
                                                        camera_zpos = props.zpos
                                                    if props.matrixtransform:
                                                        camera_zpos -= props.matrixtransform.zdw
                                                result = camera_blur_amount(image_zpos, camera_zpos, dof, focusing)
                                                setattr(tran, "blur", result)
                                        break
                                else:
                                    setattr(tran, p, v)
                        break
                else:
                    for gn, ps in props_groups.items():
                        if p in ps:
                            group_cache[gn][p] = cs[-1][0]
                            if len(group_cache[gn]) == len(props_groups[gn]):
                                if gn == "matrixtransform":
                                    rx, ry, rz = group_cache[gn]["rotateX"], group_cache[gn]["rotateY"], group_cache[gn]["rotateZ"]
                                    ox, oy, oz = group_cache[gn]["offsetX"], group_cache[gn]["offsetY"], group_cache[gn]["offsetZ"]
                                    result = renpy.store.Matrix.offset(ox, oy, oz)*renpy.store.Matrix.rotate(rx, ry, rz)
                                    setattr(tran, gn, result)
                                elif gn == "matrixanchor":
                                    mxa, mya = group_cache[gn]["matrixanchorX"], group_cache[gn]["matrixanchorY"]
                                    result = (mxa, mya)
                                    setattr(tran, gn, result)
                                elif gn ==  "matrixcolor":
                                    i, c, s, b, h = group_cache[gn]["invert"], group_cache[gn]["contrast"], group_cache[gn]["saturate"], group_cache[gn]["bright"], group_cache[gn]["hue"]
                                    result = renpy.store.InvertMatrix(i)*renpy.store.ContrastMatrix(c)*renpy.store.SaturationMatrix(s)*renpy.store.BrightnessMatrix(b)*renpy.store.HueMatrix(h)
                                    setattr(tran, gn, result)
                                elif gn == "crop":
                                    result = (group_cache[gn]["cropX"], group_cache[gn]["cropY"], group_cache[gn]["cropW"], group_cache[gn]["cropH"])
                                    setattr(tran, gn, result)
                                elif gn == "focusing":
                                    focusing = group_cache["focusing"]["focusing"]
                                    dof = group_cache["focusing"]["dof"]
                                    image_zpos = 0
                                    if tran.zpos:
                                        image_zpos = tran.zpos
                                    if tran.matrixtransform:
                                        image_zpos += tran.matrixtransform.zdw
                                    camera_zpos = 0
                                    if "master" in renpy.game.context().scene_lists.camera_transform:
                                        props = renpy.game.context().scene_lists.camera_transform["master"]
                                        if props.zpos:
                                            camera_zpos = props.zpos
                                        if props.matrixtransform:
                                            camera_zpos -= props.matrixtransform.zdw
                                    result = camera_blur_amount(image_zpos, camera_zpos, dof, focusing)
                                    setattr(tran, "blur", result)
                            break
                    else:
                        if p != "child":
                            setattr(tran, p, cs[-1][0])

            if "child" in check_points:
                cs = check_points["child"]
                if not cs:
                    return 0
                for i in range(-1, -len(cs), -1):
                    checkpoint = cs[i][1]
                    pre_checkpoint = cs[i-1][1]
                    if time >= checkpoint:
                        start = cs[i-1]
                        goal = cs[i]
                        if start[0][0] is None and goal[0][0] is None:
                            tran.set_child(renpy.store.Null())
                            break
                        elif start[0][0] is None:
                            new_widget = renpy.easy.displayable(goal[0][0])
                            w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                            old_widget = renpy.store.Null(w, h)
                        elif goal[0][0] is None:
                            old_widget = renpy.easy.displayable(start[0][0])
                            w, h = renpy.render(old_widget, 0, 0, 0, 0).get_size()
                            new_widget = renpy.store.Null(w, h)
                        else:
                            old_widget = renpy.easy.displayable(start[0][0])
                            new_widget = renpy.easy.displayable(goal[0][0])
                        if goal[0][1] is not None and goal[0][1] != "None":
                            transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                            during_transition_displayable = DuringTransitionDisplayble(transition(old_widget, new_widget), time-checkpoint, 0)
                            tran.set_child(during_transition_displayable)
                        else:
                            tran.set_child(new_widget)
                        break
                else:
                    start = ((None, None), 0, None)
                    goal = cs[0]
                    if goal[0][0] is None:
                        tran.set_child(renpy.store.Null())
                    else:
                        new_widget = renpy.easy.displayable(goal[0][0])
                        w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                        old_widget = renpy.store.Null(w, h)
                        if goal[0][1] is not None and goal[0][1] != "None":
                            transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                            during_transition_displayable = DuringTransitionDisplayble(transition(old_widget, new_widget), time-goal[1], 0)
                            tran.set_child(during_transition_displayable)
                        else:
                            tran.set_child(new_widget)

            return 0

        def generate_changed(self, layer, tag, prop):
            state = {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}
            def changed(v, time=None, knot_number=None):
                if time is None:
                    time = renpy.store._viewers.current_time
                default = self.get_default(prop)
                if prop not in force_float and (prop in force_int_range or ( (state[tag][prop] is None and isinstance(default, int)) or isinstance(state[tag][prop], int) )):
                    if isinstance(self.get_property(layer, tag, prop), float) and prop in force_int_range:
                        if prop in force_plus:
                            v = float(v)
                        else:
                            v -= float(renpy.store.persistent._int_range)
                    else:
                        if prop not in force_plus:
                            v -= renpy.store.persistent._int_range
                else:
                    if prop in force_plus:
                        v = round(float(v), 2)
                    else:
                        v = round(v -renpy.store.persistent._float_range, 2)

                self.set_keyframe(layer, tag, prop, v, time=time)
                if knot_number is not None:
                    splines[(tag, layer, prop)][time][knot_number] = v
                change_time(time)
            return changed

        def get_property(self, layer, tag, prop, default=True):
            sle = renpy.game.context().scene_lists
            state = {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}

            if tag:
                d = sle.get_displayable_by_tag(layer, tag)
                #get_group_property can't return correct vault if a MatrixRotate argument is other than 0~90deg.
                for gn, ps in props_groups.items():
                    if prop in ps:
                        if (tag, layer, prop) in all_keyframes:
                            return self.get_value((tag, layer, prop))
                        elif prop in state[tag] and state[tag][prop] is not None:
                            return state[tag][prop]
                        elif default:
                            return self.get_default(prop)
                        else:
                            return None
                else:
                    if prop == "child":
                        if (tag, layer, prop) in all_keyframes:
                            return self.get_value((tag, layer, prop))
                        else:
                            return state[tag][prop][0], None
                    pos = renpy.get_placement(d)
                    value = getattr(pos, prop, None)
                    if value is None:
                        value = getattr(getattr(d, "state", None), prop, None)
                    if value is None and default:
                        for p, v in self.props:
                            if p == prop:
                                value = v
                    return value
            return None

        def put_clipboard(self, tag, layer):
            group_cache = defaultdict(lambda:{})
            group_flag = {}
            state = {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}

            for gn, ps in props_groups.items():
                group_flag[gn] = False
            child = state[tag]["child"][0]
            string = """
    show %s""" % child
            if tag != child.split()[0]:
                    string += " as %s" % tag
            if layer != "master":
                    string += " onlayer %s" % layer
            for p, d in self.props:
                value = self.get_property(layer, tag, p)
                for gn, ps in props_groups.items():
                    if p in ps:
                        if value != d:
                            group_flag[gn] = True
                        group_cache[gn][p] = value
                        if len(group_cache[gn]) == len(props_groups[gn]) and group_flag[gn]:
                            result = None
                            if gn == "matrixtransform":
                                rx, ry, rz = group_cache[gn]["rotateX"], group_cache[gn]["rotateY"], group_cache[gn]["rotateZ"]
                                ox, oy, oz = group_cache[gn]["offsetX"], group_cache[gn]["offsetY"], group_cache[gn]["offsetZ"]
                                result = "matrixtransform  OffsetMatrix(%s, %s, %s)*RotateMatrix(%s, %s, %s) " % (ox, oy, oz, rx, ry, rz)
                            elif gn == "matrixanchor":
                                mxa, mya = group_cache[gn]["matrixanchorX"], group_cache[gn]["matrixanchorY"]
                                result = "matrixanchor (%s, %s) " % (mxa, mya)
                            elif gn == "matrixcolor":
                                i, c, s, b, h = group_cache[gn]["invert"], group_cache[gn]["contrast"], group_cache[gn]["saturate"], group_cache[gn]["bright"], group_cache[gn]["hue"]
                                result = "matrixcolor InvertMatrix(%s)*ContrastMatrix(%s)*SaturationMatrix(%s)*BrightnessMatrix(%s)*HueMatrix(%s) " % (i, c, s, b, h)
                            elif gn == "crop":
                                result = "crop_relative True crop (%s, %s, %s, %s) " % (group_cache[gn]["cropX"], group_cache[gn]["cropY"], group_cache[gn]["cropW"], group_cache[gn]["cropH"])
                            if result:
                                if string.find(":") < 0:
                                    string += ":\n        "
                                string += result
                        break
                else:
                    if p not in special_props:
                        value = self.get_property(layer, tag, p, False)
                        if value is not None and value != d and (p != "blur" or not renpy.store.persistent._viewer_focusing) or (tag in self.state[layer] and p in ["xpos", "ypos", "xanchor", "yanchor"]):
                            if string.find(":") < 0:
                                string += ":\n        "
                            string += "%s %s " % (p, value)
            if renpy.store.persistent._viewer_focusing:
                focus = self.get_default("focusing")
                if "focusing" in group_cache["focusing"]:
                    focus = group_cache["focusing"]["focusing"]
                dof = self.get_default("dof")
                if "dof" in group_cache["focusing"]:
                    dof = group_cache["focusing"]["dof"]
                result = "function camera_blur({'focusing':[(%s, 0, None)], 'dof':[(%s, 0, None)]})" % (focus, dof)
                string += "\n        "
                string += result
            string += "\n\n"
            try:
                from pygame import scrap, locals
                scrap.put(locals.SCRAP_TEXT, string)
            except:
                renpy.notify(_("Can't open clipboard"))
            else:
                renpy.notify(__('Placed \n"%s"\n on clipboard') % string)

        def edit_value(self, function, force_int=False, default="", force_plus=False, time=None):
            v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=default)
            if v:
                try:
                    if force_plus:
                        if force_int:
                            v = renpy.python.py_eval(v)
                        else:
                            v = float(renpy.python.py_eval(v))
                    else:
                        if force_int:
                            v = renpy.python.py_eval(v) + renpy.store.persistent._int_range
                        else:
                            v = renpy.python.py_eval(v) + renpy.store.persistent._float_range
                    if not force_plus or 0 <= v:
                        function(v, time=time)
                    else:
                        renpy.notify(_("Please type plus value"))
                except:
                    renpy.notify(_("Please type value"))

        def edit_default_transition(self):
            v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", message="Type transition")
            if v:
                if v == "None":
                    v = None
                renpy.store.persistent._viewer_transition = v
                return
            renpy.notify(_("Please Input Transition"))

        def edit_transition(self, layer, tag, time=None):
            if time is None:
                time = renpy.store._viewers.current_time
            v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen")
            if v:
                if v == "None":
                    v = None
                cs = all_keyframes[(tag, layer, "child")]
                for i in range(-1, -len(cs)-1, -1):
                    if time >= cs[i][1]:
                        (n, tran), t, w = cs[i]
                        break
                self.set_keyframe(layer, tag, "child", (n, v), time=time)
                change_time(time)
                return
            renpy.notify(_("Please Input Transition"))

        def add_image(self, layer):
            name = renpy.invoke_in_new_context(renpy.call_screen, "_image_selecter")
            state = {k: v2 for dic in [self.state_org[layer], self.state[layer]] for k, v2 in dic.items()}

            if not isinstance(name, tuple):
                name = tuple(name.split())
            for n in renpy.display.image.images:
                if set(n) == set(name):
                    for tag in state:
                        if tag == n[0]:
                            for i in range(2, 999):
                                for tag2 in state:
                                    if n[0]+str(i) == tag2:
                                        break
                                else:
                                    name = n[0]+str(i)+" "+" ".join(n[1:])
                                    break
                            else:
                                renpy.notify(_("too many same tag images is used"))
                                return
                            break
                    else:
                        name = " ".join(n)
                    image_name = " ".join(n)
                    added_tag = name.split()[0]
                    self.state[layer][added_tag] = {}
                    renpy.show(image_name, layer=layer, at_list=[], tag=added_tag)
                    for p, d in self.props:
                        if p == "child":
                            self.state[layer][added_tag][p] = (image_name, None)
                            self.set_keyframe(layer, added_tag, p, (image_name, renpy.store.persistent._viewer_transition))
                        else:
                            self.state[layer][added_tag][p] = self.get_property(layer, added_tag, p, False)
                    change_time(current_time)
                    return
            else:
                renpy.notify(_("Please type image name"))
                return

        def change_child(self, layer, tag, time=None, default=None):
            org = default
            if org is None:
                default = tag
            new_image = renpy.invoke_in_new_context(renpy.call_screen, "_image_selecter", default=default)
            if not isinstance(new_image, tuple): #press button
                new_image = tuple(new_image.split())
            for n in renpy.display.image.images:
                if set(n) == set(new_image) and n[0] == new_image[0]:
                    if org is not None and set(new_image) == set(org.split()):
                        return
                    string = " ".join(n)
                    self.set_keyframe(layer, tag, "child", (string, renpy.store.persistent._viewer_transition), time=time)
                    return
            else:
                if new_image and new_image[0] == "None" and org is not None:
                    self.set_keyframe(layer, tag, "child", (None, renpy.store.persistent._viewer_transition), time=time)
                    return
                renpy.notify(_("Please type image name"))
                return

        def get_zzoom(self, tag, layer):
            state={n: v for dic in [self.state_org[layer], self.state[layer]] for n, v in dic.items()}
            zzoom = state[tag]["zzoom"]
            if (tag, layer, "zzoom") in all_keyframes:
                zzoom = all_keyframes[tag, layer, "zzoom"][0][0]
            return zzoom

        def toggle_zzoom(self, tag, layer):
            zzoom = self.get_zzoom(tag, layer)
            self.set_keyframe(layer, tag, "zzoom", not zzoom, time=0)
            change_time(current_time)

        def remove_image(self, layer, tag):
            renpy.hide(tag, layer)
            del self.state[layer][tag]
            self.remove_keyframes(tag, layer)
            sort_keyframes()

        def remove_keyframes(self, layer, tag):
            for k in [k for k in all_keyframes if isinstance(k, tuple) and k[0] == tag and k[1] == layer]:
                del all_keyframes[k]

        def get_default(self, prop):
            for p, d in self.props:
                if p == prop:
                    return d

        def get_value(self, key, time=None):
            if isinstance(key, tuple):
                prop = key[2]
            else:
                prop = key
            cs = all_keyframes[key]

            if time is None:
                time = renpy.store._viewers.current_time

            if prop == "child":
                for i in range(-1, -len(cs)-1, -1):
                    if time >= cs[i][1]:
                        return cs[i][0]

            if loops[key] and cs[-1][1]:
                if time % cs[-1][1] != 0:
                    time = time % cs[-1][1]

            for i in range(1, len(cs)):
                checkpoint = cs[i][1]
                pre_checkpoint = cs[i-1][1]
                if time < checkpoint:
                    start = cs[i-1]
                    goal = cs[i]
                    if checkpoint != pre_checkpoint:
                        g = renpy.atl.warpers[goal[2]]((time - pre_checkpoint) / float(checkpoint - pre_checkpoint))
                    else:
                        g = 1.
                    default_vault = self.get_default(prop)
                    if goal[0] is not None:
                        if start[0] is None:
                            start_v = default_vault
                        else:
                            start_v = start[0]
                        knots = []
                        if checkpoint in splines[key]:
                            knots = splines[key][checkpoint]
                            if knots:
                                knots = [start_v] + knots + [goal[0]]
                        if knots:
                            v = renpy.atl.interpolate_spline(g, knots)
                        else:
                            v = g*(goal[0]-start_v)+start_v
                        if isinstance(goal[0], int) and prop not in force_float:
                            v = int(v)
                        return v
                    break
            else:
                return cs[-1][0]

    transform_viewer = TransformViewer()

    ##########################################################################
    # CameraViewer
    class CameraViewer(TransformViewer):

        def __init__(self):
            super(CameraViewer, self).__init__()
            self.props = camera_props

        def init(self):
            if not renpy.config.developer:
                return
            self.state_org = {}
            for p, d in self.props:
                self.state_org[p] = self.get_property(p, False)
            disp = renpy.game.context().scene_lists.camera_transform["master"]
            for gn, ps in props_groups.items():
                p2 = self.get_group_property(gn, getattr(disp, gn, None))
                if p2 is not None:
                    for p, v in zip(ps, p2):
                        self.state_org[p] = v

        def reset(self, prop_list):
            if not isinstance(prop_list, list):
                prop_list = [prop_list]
            for prop in prop_list:
                for p, d in self.props:
                    if p == prop:
                        if self.state_org[prop] is not None:
                            v = self.state_org[prop]
                        else:
                            v = d
                self.set_keyframe(prop, v)
            change_time(current_time)

        def camera_reset(self):
            self.reset([p for p, d in self.props])

        def set_keyframe(self, prop, value, recursion=False, time=None):
            if time is None:
                time = renpy.store._viewers.current_time
            keyframes = all_keyframes.get(prop, [])
            if keyframes:
                for i, (v, t, w) in enumerate(keyframes):
                    if time < t:
                        keyframes.insert(i, (value, time, renpy.store.persistent._viewer_warper))
                        break
                    elif time == t:
                        keyframes[i] = (value, time, renpy.store.persistent._viewer_warper)
                        break
                else:
                    keyframes.append((value, time, renpy.store.persistent._viewer_warper))
            else:
                if time == 0:
                    all_keyframes[prop] = [(value, time, renpy.store.persistent._viewer_warper)]
                else:
                    org = self.state_org[prop]
                    if org is None:
                        org = self.get_default(prop)
                    all_keyframes[prop] = [(org, 0, renpy.store.persistent._viewer_warper), (value, time, renpy.store.persistent._viewer_warper)]
            sort_keyframes()

            for gn, ps in props_groups.items():
                ps_set = set(ps)
                if prop in ps_set and gn != "focusing" and recursion == False:
                    ps_set.remove(prop)
                    for p in ps_set:
                        self.set_keyframe(p, self.get_property(p), True, time=time)

        def play(self, play):
            check_points = {}
            for prop, d in self.props:
                if prop in all_keyframes:
                    check_points[prop] = all_keyframes[prop]
            if not check_points: # ビューワー上でのアニメーション(フラッシュ等)の誤動作を抑制
                return
            #ひとつでもprops_groupsのプロパティがあればグループ単位で追加する
            for gn, ps in props_groups.items():
                if gn != "focusing":
                    group_flag = False
                    for prop in ps:
                        if not prop in check_points:
                            if self.state_org.get(prop, None) is not None:
                                v = self.state_org[prop]
                            else:
                                v = self.get_default(prop)
                            check_points[prop] = [(v, 0, None)]
                        else:
                            group_flag =  True
                    if not group_flag:
                        for prop in ps:
                            del check_points[prop]
            for p in props_groups["focusing"]:
                if p in check_points:
                    del check_points[p]
            loop = {prop+"_loop": loops[prop] for prop, d in self.props}
            spline = {prop+"_spline": splines[prop] for prop, d in self.props}
            if play:
                renpy.exports.show_layer_at(renpy.store.Transform(function=renpy.curry(self.transform)(check_points=check_points, loop=loop, spline=spline)), camera=True)
            else:
                renpy.exports.show_layer_at(renpy.store.Transform(function=renpy.curry(self.transform)(check_points=check_points, loop=loop, spline=spline, time=renpy.store._viewers.current_time)), camera=True)

        def generate_changed(self, prop):
            value_org = self.state_org[prop]
            def changed(v, time=None, knot_number=None):
                if time is None:
                    time = renpy.store._viewers.current_time
                default = self.get_default(prop)
                if prop not in force_float and (prop in force_int_range or ( (value_org is None and isinstance(default, int)) or isinstance(value_org, int) )):
                    if isinstance(self.get_property(prop), float) and prop in force_int_range:
                        if prop in force_plus:
                            v = float(v)
                        else:
                            v = float(v - renpy.store.persistent._int_range)
                    else:
                        if prop not in force_plus:
                            v -= renpy.store.persistent._int_range
                else:
                    if prop in force_plus:
                        v = round(float(v), 2)
                    else:
                        v = round(v - renpy.store.persistent._float_range, 2)

                self.set_keyframe(prop, v, time=time)
                if prop in props_groups["focusing"]:
                    for l in transform_viewer.state_org:
                        state={k: v2 for dic in [transform_viewer.state_org[l], transform_viewer.state[l]] for k, v2 in dic.items()}
                        for n, v2 in state.items():
                            if prop == "dof":
                                transform_viewer.generate_changed(l, n, "dof")(v, time=time)
                            elif prop == "focusing":
                                transform_viewer.generate_changed(l, n, "focusing")(v, time=time)
                if knot_number is not None:
                    splines[prop][time][knot_number] = v
                change_time(time)
            return changed

        def get_property(self, prop, default=True):
            if "master" in renpy.game.context().scene_lists.camera_transform:
                props = renpy.game.context().scene_lists.camera_transform["master"]
                #get_group_property can't return correct vault if a MatrixRotate argument is other than 0~90deg.
                for gn, ps in props_groups.items():
                    if prop in ps:
                        if prop in all_keyframes:
                            return self.get_value(prop)
                        elif prop in self.state_org and self.state_org[prop] is not None:
                            return self.state_org[prop] #
                        elif default:
                            return self.get_default(prop)
                        else:
                            return None
                else:
                    value = getattr(props, prop, None)
            else:
                value = None
            if value is None and default:
                for p, v in self.props:
                    if p == prop:
                        value = v
            return value

        def put_clipboard(self):
            group_cache = defaultdict(lambda:{})
            group_flag = {}
            for gn, ps in props_groups.items():
                group_flag[gn] = False
            string = """
    camera"""
            for p, d in self.props:
                value = self.get_property(p)
                for gn, ps in props_groups.items():
                    if p in ps:
                        if value != d:
                            group_flag[gn] = True
                        group_cache[gn][p] = value
                        if len(group_cache[gn]) == len(props_groups[gn]) and group_flag[gn]:
                            result = None
                            if gn == "matrixtransform":
                                rx, ry, rz = group_cache[gn]["rotateX"], group_cache[gn]["rotateY"], group_cache[gn]["rotateZ"]
                                ox, oy, oz = group_cache[gn]["offsetX"], group_cache[gn]["offsetY"], group_cache[gn]["offsetZ"]
                                result = "matrixtransform OffsetMatrix(%s, %s, %s)*RotateMatrix(%s, %s, %s) " % (ox, oy, oz, rx, ry, rz)
                            elif gn == "matrixanchor":
                                mxa, mya = group_cache[gn]["matrixanchorX"], group_cache[gn]["matrixanchorY"]
                                result = "matrixanchor (%s, %s) " % (mxa, mya)
                            elif gn == "matrixcolor":
                                i, c, s, b, h = group_cache[gn]["invert"], group_cache[gn]["contrast"], group_cache[gn]["saturate"], group_cache[gn]["bright"], group_cache[gn]["hue"]
                                result = "matrixcolor InvertMatrix(%s)*ContrastMatrix(%s)*SaturationMatrix(%s)*BrightnessMatrix(%s)*HueMatrix(%s) " % (i, c, s, b, h)
                            elif gn == "crop":
                                result = "crop_relative True crop (%s, %s, %s, %s) " % (group_cache[gn]["cropX"], group_cache[gn]["cropY"], group_cache[gn]["cropW"], group_cache[gn]["cropH"])
                            if result:
                                if string.find(":") < 0:
                                    string += ":\n        "
                                string += result
                        break
                else:
                    value = self.get_property(p, False)
                    if value is not None and value != d:
                        if string.find(":") < 0:
                            string += ":\n        "
                        string += "%s %s " % (p, value)
            string += "\n\n"
            try:
                from pygame import scrap, locals
                scrap.put(locals.SCRAP_TEXT, string)
            except:
                renpy.notify(_("Can't open clipboard"))
            else:
                renpy.notify(__('Placed \n"%s"\n on clipboard') % string)

    camera_viewer = CameraViewer()

    class Dragged(renpy.Displayable):

        def __init__(self, child, **properties):
            super(Dragged, self).__init__(**properties)
            # The child.
            self.child = renpy.displayable(child)
            self.dragging = False

        def init(self, int_x=True, int_y=True):
            self.int_x = int_x
            self.int_y = int_y
            if self.int_x:
                self.x_range = renpy.store.persistent._int_range
            else:
                self.x_range = renpy.store.persistent._float_range
            if self.int_y:
                self.y_range = renpy.store.persistent._int_range
            else:
                self.y_range = renpy.store.persistent._float_range

            self.cx = self.x = (0.5 + camera_viewer.get_property("offsetX")/(2.*self.x_range))*renpy.config.screen_width
            self.cy = self.y = (0.5 + camera_viewer.get_property("offsetY")/(2.*self.y_range))*renpy.config.screen_height

        def render(self, width, height, st, at):

            # Create a render from the child.
            child_render = renpy.render(self.child, width, height, st, at)

            # Get the size of the child.
            self.width, self.height = child_render.get_size()

            # Create the render we will return.
            render = renpy.Render(renpy.config.screen_width, renpy.config.screen_height)

            # Blit (draw) the child's render to our render.
            render.blit(child_render, (self.x-self.width/2., self.y-self.height/2.))

            # Return the render.
            return render

        def event(self, ev, x, y, st):

            if renpy.map_event(ev, "mousedown_1"):
                if self.x-self.width/2. <= x and x <= self.x+self.width/2. and self.y-self.height/2. <= y and y <= self.y+self.height/2.:
                    self.dragging = True
            elif renpy.map_event(ev, "mouseup_1"):
                self.dragging = False

            # if x <= 0:
            #     x = 0
            # if renpy.config.screen_width <= x:
            #     x = renpy.config.screen_width
            # if y <= 0:
            #     y = 0
            # if renpy.config.screen_height <= y:
            #     y = renpy.config.screen_height

            if camera_viewer.get_property("offsetX") != int(self.cx) or camera_viewer.get_property("offsetY") != int(self.cy):
                self.x = (0.5 + camera_viewer.get_property("offsetX")/(2.*self.x_range))*renpy.config.screen_width
                self.y = (0.5 + camera_viewer.get_property("offsetY")/(2.*self.y_range))*renpy.config.screen_height
                renpy.redraw(self, 0)

            if self.dragging:
                if self.x != x or self.y != y:
                    self.cx = 2*self.x_range*( float(x)/renpy.config.screen_width - 0.5)
                    self.cy = 2*self.y_range*( float(y)/renpy.config.screen_height - 0.5)
                    if self.int_x:
                        self.cx = int(self.cx)
                    if self.int_y:
                        self.cy = int(self.cy)
                    if self.cx != camera_viewer.get_property("offsetX"):
                        camera_viewer.set_keyframe("offsetX", self.cx)
                    if self.cy != camera_viewer.get_property("offsetY"):
                        camera_viewer.set_keyframe("offsetY", self.cy)
                    cz = camera_viewer.get_property("offsetZ")
                    rx = camera_viewer.get_property("rotateX")
                    ry = camera_viewer.get_property("rotateY")
                    rz = camera_viewer.get_property("rotateZ")
                    renpy.exports.show_layer_at(renpy.store.Transform(matrixtransform=renpy.store.Matrix.offset(self.cx, self.cy, cz)*renpy.store.Matrix.rotate(rx, ry, rz)), camera=True)
                    self.x, self.y = x, y
                    renpy.restart_interaction()
                    renpy.redraw(self, 0)

            # Pass the event to our child.
            # return self.child.event(ev, x, y, st)

        def per_interact(self):
            renpy.redraw(self, 0)

        def visit(self):
            return [ self.child ]
    dragged = Dragged("camera.png")


    class DuringTransitionDisplayble(renpy.Displayable):
    # create the image which is doing transition at the given time.
    # TransitionDisplayble(dissolve(old_widget, new_widget), 0, 0)

        def __init__(self, transition, st, at, **properties):
            super(DuringTransitionDisplayble, self).__init__(**properties)

            self.transition = transition
            self.st = st
            self.at = at
        
        def render(self, width, height, st, at):
            #st, at is 0 allways?
            return self.transition.render(width, height, self.st, self.at)

    ##########################################################################
    moved_time = 0
    loops = defaultdict(lambda:False)
    splines = defaultdict(lambda:{})
    all_keyframes = {}
    sorted_keyframes = []

    def edit_warper(check_points, old, value_org):
        warper = renpy.invoke_in_new_context(renpy.call_screen, "_warper_selecter", current_warper=value_org)
        if warper:
            if not isinstance(check_points[0], list):
                check_points = [check_points]
            for cs in check_points:
                for i, (v, t, w) in enumerate(cs):
                    if t == old:
                        cs[i] = (v, t, warper)
                        break
        renpy.restart_interaction()

    def edit_move_keyframe(keys, old):
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=old)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < 0:
                    return
                if not isinstance(keys, list):
                    keys = [keys]
                move_keyframe(v, old, keys)
            except:
                renpy.notify(_("Please type value"))

    def edit_move_all_keyframe():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=moved_time)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < 0:
                    return
                move_all_keyframe(v, moved_time)
            except:
                renpy.notify(_("Please type value"))

    def edit_time():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=current_time)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < 0:
                    return
                change_time(v)
            except:
                renpy.notify(_("Please type value"))

    def edit_range_value(object, field, use_int):
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=getattr(object, field))
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v <= 0:
                    renpy.notify(_("Please type plus value"))
                    return
                if (isinstance(v, int) and use_int) or (isinstance(v, float) and not use_int):
                    setattr(object, field, v)
                else:
                    if use_int:
                        renpy.notify(_("Please type float value"))
                    else:
                        renpy.notify(_("Please type int value"))
            except:
                renpy.notify(_("Please type value"))

    def next_time():
        if not sorted_keyframes:
            change_time(0)
            return
        else:
            for i, t in enumerate(sorted_keyframes):
                if current_time < t:
                    change_time(sorted_keyframes[i])
                    return
            change_time(sorted_keyframes[0])

    def prev_time():
        if not sorted_keyframes:
            change_time(0)
            return
        else:
            for i, t in enumerate(sorted_keyframes):
                if current_time <= t:
                    change_time(sorted_keyframes[i-1])
                    break
            else:
                change_time(sorted_keyframes[-1])

    def select_default_warper():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_warper_selecter")
        if v:
            renpy.store.persistent._viewer_warper = v

    def clear_keyframes():
        all_keyframes.clear()
        sorted_keyframes[:]=[]

    def remove_keyframe(remove_time, key):
        if not isinstance(key, list):
            key = [key]
        for k in key:
            remove_list = []
            if k in all_keyframes:
                for (v, t, w) in all_keyframes[k]:
                    if t == remove_time:
                        if remove_time != 0 or (remove_time == 0 and len(all_keyframes[k]) == 1):
                            remove_list.append((v, t, w))
            for c in remove_list:
                if c[1] in splines[k]:
                    del splines[k][c[1]]
                all_keyframes[k].remove(c)
                if not all_keyframes[k]:
                    del all_keyframes[k]
        sort_keyframes()
        change_time(current_time)

    def remove_all_keyframe(time):
        keylist = [k for k in all_keyframes]
        remove_keyframe(time, keylist)

    def sort_keyframes():
        global sorted_keyframes
        sorted_keyframes[:] = []
        for keyframes in all_keyframes.values():
            for (v, t, w) in keyframes:
                if t not in sorted_keyframes:
                    sorted_keyframes.append(t)
        sorted_keyframes.sort()

    def move_all_keyframe(new, old):
        global moved_time
        moved_time = round(new, 2)
        k_list = [k for k in all_keyframes.keys()]
        move_keyframe(new, old, k_list)

    def move_keyframe(new, old, keys):
        new = round(new, 2)
        if new == old:
            return
        if not isinstance(keys, list):
            keys = [keys]
        for k in keys:
            cs = all_keyframes[k]
            for i, c in enumerate(cs):
                if c[1] == old:
                    (value, time, warper) = cs.pop(i)
                    for n, (v, t, w) in enumerate(cs):
                        if new < t:
                            cs.insert(n, (value, new, warper))
                            break
                    else:
                        cs.append((value, new, warper))
                    if old == 0 and new != 0:
                        cs.insert(0, (value, 0, renpy.store.persistent._viewer_warper))
                    if old in splines[k]:
                        knots = splines[k][old]
                        splines[k][new] = knots
                        del splines[k][old]
        sort_keyframes()
        renpy.restart_interaction()

    def keyframes_exist(k):
        if k not in all_keyframes:
            return False
        check_points = all_keyframes[k]
        for c in check_points:
            if c[1] == current_time:
                return True
        return False

    def add_knot(key, time, default, knot_number=None):
        if time in splines[key]:
            if knot_number is not None:
                splines[key][time].insert(knot_number, default)
            else:
                splines[key][time].append(default)
        else:
            splines[key][time] = [default]

    def remove_knot(key, time, i):
        if time in splines[key]:
            splines[key][time].pop(i)
            if not splines[key][time]:
                del splines[key][time]

    def change_time(v):
        global current_time
        current_time = round(v, 2)
        transform_viewer.play(False)
        camera_viewer.play(False)
        renpy.restart_interaction()

    def action_editor():
        global current_time
        if not renpy.config.developer:
            return
        current_time = 0
        moved_time = 0
        loops.clear()
        splines.clear()
        clear_keyframes()
        if renpy.store.persistent._viewer_transition is None:
            renpy.store.persistent._viewer_transition = default_transition
        if renpy.store.persistent._viewer_warper is None:
            renpy.store.persistent._viewer_warper = default_warper
        if renpy.store.persistent._viewer_hide_window is None:
            renpy.store.persistent._viewer_hide_window = hide_window_in_animation
        if renpy.store.persistent._viewer_allow_skip is None:
            renpy.store.persistent._viewer_allow_skip = allow_animation_skip
        if renpy.store.persistent._viewer_rot is None:
            renpy.store.persistent._viewer_rot = default_rot
        if renpy.store.persistent._viewer_focusing is None:
            renpy.store.persistent._viewer_focusing = focusing
        if renpy.store.persistent._int_range is None:
            renpy.store.persistent._int_range = int_range
        if renpy.store.persistent._float_range is None:
            renpy.store.persistent._float_range = float_range
        if renpy.store.persistent._time_range is None:
            renpy.store.persistent._time_range = time_range
        transform_viewer.init()
        camera_viewer.init()
        dragged.init(True, True)
        _window = renpy.store._window
        renpy.store._window = False
        renpy.invoke_in_new_context(renpy.call_screen, "_action_editor")
        renpy.store._window = _window

    def get_animation_delay():
        animation_time = 0
        for cs in all_keyframes.values():
            for (v, t, w) in cs:
                if isinstance(v, tuple):
                    if isinstance(v[1], str):
                        transition = renpy.python.py_eval("renpy.store."+v[1])
                        delay = getattr(transition, "delay", None)
                        if delay is None:
                            delay = getattr(transition, "args")[0]
                        t += delay
                if t > animation_time:
                    animation_time = t
        return animation_time

    def set_group_keyframes(keyframes):
        result = {}
        group_cache = defaultdict(lambda:{})
        for p, cs in keyframes.items():
            for gn, ps in props_groups.items():
                if p in ps:
                    group_cache[gn][p] = cs
                    if len(group_cache[gn]) == len(props_groups[gn]):
                        r = None
                        if gn == "matrixtransform":
                            v = "OffsetMatrix(%s, %s, %s)*RotateMatrix(%s, %s, %s)"
                            r = [(v%(oxc[0], oyc[0], ozc[0], rxc[0], ryc[0], rzc[0]), oxc[1], oxc[2]) for oxc, oyc, ozc, rxc, ryc, rzc  in zip(group_cache[gn]["offsetX"], group_cache[gn]["offsetY"], group_cache[gn]["offsetZ"], group_cache[gn]["rotateX"], group_cache[gn]["rotateY"], group_cache[gn]["rotateZ"])]
                        elif gn == "matrixanchor":
                            v = "(%s, %s)"
                            r = [(v%(mxa[0], mya[0]), mxa[1], mxa[2]) for mxa, mya  in zip(group_cache[gn]["matrixanchorX"], group_cache[gn]["matrixanchorY"])]
                        elif gn ==  "matrixcolor":
                            v = "InvertMatrix(%s)*ContrastMatrix(%s)*SaturationMatrix(%s)*BrightnessMatrix(%s)*HueMatrix(%s)"
                            r = [(v%(ic[0], cc[0], sc[0], bc[0], hc[0]), ic[1], ic[2]) for ic, cc, sc, bc, hc in zip(group_cache[gn]["invert"], group_cache[gn]["contrast"], group_cache[gn]["saturate"], group_cache[gn]["bright"], group_cache[gn]["hue"])]
                        elif gn == "crop":
                            v = "(%s, %s, %s, %s)"
                            r = [(v%(xc[0], yc[0], wc[0], hc[0]), xc[1], xc[2]) for xc, yc, wc, hc in zip(group_cache[gn]["cropX"], group_cache[gn]["cropY"], group_cache[gn]["cropW"], group_cache[gn]["cropH"])]
                        if r:
                            result[gn] = r
                    break
            else:
                result[p] = cs
        return result

    def camera_blur_amount(image_zpos, camera_zpos=None, dof=None, focusing=None):
        if camera_zpos is None:
            camera_zpos = camera_viewer.get_property("offsetZ")+camera_viewer.get_property("zpos")
        if focusing is None:
            focusing = camera_viewer.get_property("focusing")
        if dof is None:
            dof = camera_viewer.get_property("dof")
        distance_from_focus = camera_zpos - image_zpos - focusing + renpy.config.perspective[1]
        if dof == 0:
            dof = 0.1
        blur_amount = _camera_blur_amount * renpy.atl.warpers[_camera_blur_warper](distance_from_focus/(float(dof)/2))
        if blur_amount < 0:
            blur_amount = abs(blur_amount)
        return blur_amount

    def sort_props(keyframes):
        sorted = []
        for p in sort_ref_list:
            if p in keyframes:
                sorted.append((p, keyframes[p]))
        return sorted

    def put_prop_togetter(keyframes, layer=None, tag=None):
        sorted = []
        for p in sort_ref_list:
            if p in keyframes:
                sorted.append((p, keyframes[p]))
        result = []
        already_added = []
        for i, (p, cs) in enumerate(sorted):
            same_time_set = []
            if p in already_added or len(cs) == 1:
                continue
            else:
                same_time_set = [(p, cs)]
                already_added.append(p)
                if layer is not None and tag is not None:
                    key = (tag, layer, p)
                else:
                    key = p
            for (p2, cs2) in sorted[i+1:]:
                if p2 not in already_added and len(cs) == len(cs2):
                    if layer is not None and tag is not None:
                        key2 = (tag, layer, p2)
                    else:
                        key2 = p2
                    if loops[key] != loops[key2]:
                        continue
                    for c1, c2 in zip(cs, cs2):
                        if c1[1] != c2[1] or c1[2] != c2[2]:
                            break
                    else:
                            same_time_set.append((p2, cs2))
                            already_added.append(p2)
            result.append(same_time_set)
            for ks in result:
                ks = x_and_y_to_xy(ks, layer=layer, tag=tag, check_spline=True)
        return result

    def x_and_y_to_xy(keyframe_list, layer=None, tag=None, check_spline=False, check_loop=False):
        for xy, (x, y) in xygroup.items():
            if x in [p for p, cs in keyframe_list] and y in [p for p, cs in keyframe_list]:
                if layer is not None and tag is not None:
                    xkey = (tag, layer, x)
                    ykey = (tag, layer, y)
                else:
                    xkey = x
                    ykey = y
                if check_spline and (splines[xkey] or splines[ykey]):
                # don't put together when propaerty has spline
                    continue
                if check_loop and (loops[xkey] != loops[ykey]):
                    continue
                for xi in range(len(keyframe_list)):
                    if keyframe_list[xi][0] == x:
                        xcs = keyframe_list[xi][1]
                        break
                for yi in range(len(keyframe_list)):
                    if keyframe_list[yi][0] == y:
                        ycs = keyframe_list[yi][1]
                        break
                xcs2 = xcs[:]
                ycs2 = ycs[:]
                if len(xcs) > len(ycs):
                    for i in range(len(xcs)-len(ycs)):
                        ycs2.append(ycs[-1])
                if len(ycs) > len(xcs):
                    for i in range(len(ycs)-len(xcs)):
                        xcs2.append(xcs[-1])
                keyframe_list[xi] = (xy, [((xc[0], yc[0]), xc[1], xc[2]) for xc, yc in zip(xcs2, ycs2)])
                keyframe_list.pop(yi)
        return keyframe_list

    def xy_to_x(prop):
        if prop in xygroup:
            return xygroup[prop][0]
        else:
            return prop

    def put_clipboard():
        string = ""
        camera_keyframes = {k:v for k, v in all_keyframes.items() if not isinstance(k, tuple)}
        camera_keyframes = set_group_keyframes(camera_keyframes)
        camera_properties = []
        for p, d in camera_viewer.props:
            for gn, ps in props_groups.items():
                if p in ps:
                    if gn not in camera_properties:
                        camera_properties.append(gn)
                    break
            else:
                camera_properties.append(p)
        if renpy.store.persistent._viewer_hide_window and get_animation_delay() > 0:
            if renpy.store._window_auto:
                window_mode = "window auto"
            else:
                window_mode = "window"
            string += """
    {} hide""".format(window_mode)
        if camera_keyframes:
            string += """
    camera:
        subpixel True """
            if "crop" in camera_keyframes:
                string += "{} {} ".format("crop_relative", True)
            #デフォルトと違っても出力しない方が以前の状態の変化に柔軟だが、
            #xposのような元がNoneやmatrixtransformのような元のマトリックスの順番が違うとアニメーションしない
            #rotateは設定されればキーフレームに入り、されてなければ問題ない
            #アニメーションしないなら出力しなくてよいのでここでは不要
            for p, cs in x_and_y_to_xy([(p, camera_keyframes[p]) for p in camera_properties if p in camera_keyframes and len(camera_keyframes[p]) == 1]):
                    string += "{} {} ".format(p, cs[0][0])
            sorted = put_prop_togetter(camera_keyframes)
            if len(sorted):
                if len(sorted) > 1 or loops[xy_to_x(sorted[0][0][0])]:
                    add_tab = "    "
                else:
                    add_tab = ""
                for same_time_set in sorted:
                    if len(sorted) > 1 or loops[xy_to_x(sorted[0][0][0])]:
                        string += """
        parallel:
            """
                    else:
                        string += """
        """
                    for p, cs in same_time_set:
                        string += "{} {} ".format(p, cs[0][0])
                    cs = same_time_set[0][1]
                    for i, c in enumerate(cs[1:]):
                        string += """
        {}{} {} """.format(add_tab, c[2], cs[i+1][1]-cs[i][1])
                        for p2, cs2 in same_time_set:
                            string += "{} {} ".format(p2, cs2[i+1][0])
                            if cs2[i+1][1] in splines[xy_to_x(p2)] and splines[xy_to_x(p2)][cs2[i+1][1]]:
                                for knot in splines[xy_to_x(p2)][cs2[i+1][1]]:
                                    string += " knot {} ".format(knot)
                    if loops[xy_to_x(p)]:
                        string += """
            repeat"""

        for layer in transform_viewer.state_org:
            state = {k: v for dic in [transform_viewer.state_org[layer], transform_viewer.state[layer]] for k, v in dic.items()}
            for tag, value_org in state.items():
                image_keyframes = {k[2]:v for k, v in all_keyframes.items() if isinstance(k, tuple) and k[0] == tag and k[1] == layer}
                image_keyframes = set_group_keyframes(image_keyframes)
                if renpy.store.persistent._viewer_focusing and "blur" in image_keyframes:
                    del image_keyframes["blur"]
                image_properties = []
                for p, d in transform_viewer.props:
                    for gn, ps in props_groups.items():
                        if p in ps:
                            if gn not in image_properties:
                                image_properties.append(gn)
                            break
                    else:
                        if p not in special_props:
                            image_properties.append(p)
                if image_keyframes or renpy.store.persistent._viewer_focusing or tag in transform_viewer.state[layer]:
                    image_name = state[tag]["child"][0]
                    if "child" in image_keyframes:
                        last_child = image_keyframes["child"][-1][0][0]
                        if last_child is not None:
                            last_tag = last_child.split()[0]
                            if last_tag == image_name.split()[0]:
                                image_name = last_child
                    string += """
    show {}""".format(image_name)
                    if image_name.split()[0] != tag:
                        string += " as {}".format(tag)
                    if layer != "master":
                        string += " onlayer {}".format(layer)
                    if tag in transform_viewer.state[layer]:
                        string += " at default"
                    string += """:
        subpixel True """
                    if "crop" in image_keyframes:
                        string += "{} {} ".format("crop_relative", True)
                    for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes and len(image_keyframes[p]) == 1], layer, tag):
                            string += "{} {} ".format(p, cs[0][0])
                    sorted = put_prop_togetter(image_keyframes, layer, tag)
                    if "child" in image_keyframes:
                        if len(sorted) >= 1 or loops[(tag, layer, "child")] or renpy.store.persistent._viewer_focusing:
                            add_tab = "    "
                            string += """
        parallel:"""
                        else:
                            add_tab = ""
                        last_time = 0.0
                        for i in range(0, len(image_keyframes["child"]), 1):
                            (image, transition), t, w = image_keyframes["child"][i]
                            widget = None
                            if i > 0:
                                old_widget = image_keyframes["child"][i-1][0][0]
                                if old_widget is not None:
                                    widget = old_widget
                            if i < len(image_keyframes["child"])-1:
                                new_widget = image_keyframes["child"][i+1][0][0]
                                if new_widget is not None:
                                    widget = new_widget
                            if widget is None:
                                if image is not None:
                                    widget = image
                            if widget is None:
                                null = "Null()"
                            else:
                                w, h = renpy.render(renpy.easy.displayable(widget), 0, 0, 0, 0).get_size()
                                null = "Null({}, {})".format(w, h)
                            if (t - last_time) > 0:
                                string += """
        {}{}""".format(add_tab, t-last_time)
                            if i == 0 and (image is not None and transition is not None):
                                string += """
        {}{}""".format(add_tab, null)
                            if image is None:
                                string += """
        {}{}""".format(add_tab, null)
                            else:
                                string += """
        {}'{}'""".format(add_tab, image)
                            if transition is not None:
                                string += " with {}".format(transition)

                                transition = renpy.python.py_eval("renpy.store."+transition)
                                delay = getattr(transition, "delay", None)
                                if delay is None:
                                    delay = getattr(transition, "args")[0]
                                t += delay
                            last_time = t
                        if loops[(tag,layer,p)]:
                            string += """
            repeat"""
                    if len(sorted):
                        if len(sorted) > 1 or loops[(tag, layer, xy_to_x(sorted[0][0][0]))] or "child" in image_keyframes or renpy.store.persistent._viewer_focusing:
                            add_tab = "    "
                        else:
                            add_tab = ""
                        for same_time_set in sorted:
                            if len(sorted) > 1 or loops[(tag, layer, xy_to_x(sorted[0][0][0]))] or "child" in image_keyframes or renpy.store.persistent._viewer_focusing:
                                string += """
        parallel:"""
                            string += """
        """+add_tab
                            for p, cs in same_time_set:
                                string += "{} {} ".format(p, cs[0][0])
                            cs = same_time_set[0][1]
                            for i, c in enumerate(cs[1:]):
                                string += """
        {}{} {} """.format(add_tab, c[2], cs[i+1][1]-cs[i][1])
                                for p2, cs2 in same_time_set:
                                    string += "{} {} ".format(p2, cs2[i+1][0])
                                    if cs2[i+1][1] in splines[(tag, layer, xy_to_x(p2))] and splines[(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                        for knot in splines[(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                            string += " knot {} ".format(knot)
                            if loops[(tag,layer,xy_to_x(p))]:
                                string += """
            repeat"""
                    if renpy.store.persistent._viewer_focusing:
                        focusing_cs = {"focusing":[(camera_viewer.get_default("focusing"), 0, None)], "dof":[(camera_viewer.get_default("dof"), 0, None)]}
                        for p, cs in image_keyframes.items():
                            if len(cs) > 1 or "child" in image_keyframes:
                                string += """
        parallel:
            """
                                break
                        else:
                            string += "\n        "
                        if "focusing" in all_keyframes:
                            focusing_cs["focusing"] = all_keyframes["focusing"]
                        if "dof" in all_keyframes:
                            focusing_cs["dof"] = all_keyframes["dof"]
                        if loops["focusing"] or loops["dof"]:
                            focusing_loop = {}
                            focusing_loop["focusing_loop"] = loops["focusing"]
                            focusing_loop["dof_loop"] = loops["dof"]
                            string += "{} camera_blur({}, {}) ".format("function", focusing_cs, focusing_loop)
                        else:
                            string += "{} camera_blur({}) ".format("function", focusing_cs)

        if renpy.store.persistent._viewer_hide_window and get_animation_delay() > 0:
            string += """
    with Pause({})""".format(get_animation_delay())
            if renpy.store.persistent._viewer_allow_skip:

                if camera_keyframes:
                    for p, cs in camera_keyframes.items():
                        if len(cs) > 1:
                            string += """
    camera:"""
                            for p, cs in camera_keyframes.items():
                                if len(cs) > 1 and loops[p]:
                                    string += """
        animation"""
                                    break
                            first = True
                            for p, cs in x_and_y_to_xy(sort_props(camera_keyframes), check_loop=True):
                                if len(cs) > 1 and not loops[xy_to_x(p)]:
                                    if first:
                                        first = False
                                        string += """
        """
                                    string += "{} {} ".format(p, cs[-1][0])
                            for p, cs in sort_props(camera_keyframes):
                                if len(cs) > 1 and loops[p]:
                                    string += """
        parallel:"""
                                    string += """
            {} {}""".format(p, cs[0][0])
                                    for i, c in enumerate(cs[1:]):
                                        string += """
            {} {} {} {}""".format(c[2], cs[i+1][1]-cs[i][1], p, c[0])
                                        if c[1] in splines[p] and splines[p][c[1]]:
                                            for knot in splines[p][c[1]]:
                                                string += " knot {}".format(knot)
                                    string += """
            repeat"""
                            break

                for layer in transform_viewer.state_org:
                    state = {k: v for dic in [transform_viewer.state_org[layer], transform_viewer.state[layer]] for k, v in dic.items()}
                    for tag, value_org in state.items():
                        image_keyframes = {k[2]:v for k, v in all_keyframes.items() if isinstance(k, tuple) and k[0] == tag and k[1] == layer}
                        image_keyframes = set_group_keyframes(image_keyframes)
                        if renpy.store.persistent._viewer_focusing and "blur" in image_keyframes:
                            del image_keyframes["blur"]
                        image_properties = []
                        for p, d in transform_viewer.props:
                            for gn, ps in props_groups.items():
                                if p in ps:
                                    if gn not in image_properties:
                                        image_properties.append(gn)
                                    break
                            else:
                                if p not in special_props:
                                    image_properties.append(p)

                        if not image_keyframes:
                            continue
                        for p, cs in image_keyframes.items():
                            if len(cs) > 1:
                                break
                        else:
                            continue

                        image_name = state[tag]["child"][0]
                        if "child" in image_keyframes:
                            last_child = image_keyframes["child"][-1][0][0]
                            if last_child is not None:
                                last_tag = last_child.split()[0]
                                if last_tag == tag:
                                    image_name = last_child
                        string += """
    show {}""".format(image_name)
                        if image_name.split()[0] != tag:
                            string += " as {}".format(tag)
                        if layer != "master":
                            string += " onlayer {}".format(layer)

                        for p, cs in image_keyframes.items():
                            if len(cs) > 1 and (p != "child" or loops[(tag, layer, "child")]):
                                break
                        else:
                            continue
                        string += ":"
                        for p, cs in image_keyframes.items():
                            if len(cs) > 1 and loops[(tag, layer, p)]:
                                string += """
        animation"""
                                break
                        first = True
                        for p, cs in x_and_y_to_xy(sort_props(image_keyframes), layer, tag, check_loop=True):
                            if p not in special_props:
                                if len(cs) > 1 and not loops[(tag, layer, xy_to_x(p))]:
                                    if first:
                                        first = False
                                        string += """
        """
                                    string += "{} {} ".format(p, cs[-1][0])

                        if renpy.store.persistent._viewer_focusing:
                            focusing_cs = {"focusing":[(camera_viewer.get_default("focusing"), 0, None)], "dof":[(camera_viewer.get_default("dof"), 0, None)]}
                            if "focusing" in all_keyframes:
                                focusing_cs["focusing"] = all_keyframes["focusing"]
                            if "dof" in all_keyframes:
                                focusing_cs["dof"] = all_keyframes["dof"]
                            if len(focusing_cs["focusing"]) > 1 or len(focusing_cs["dof"]) > 1:
                                if not loops["focusing"]:
                                    focusing_cs["focusing"] = [focusing_cs["focusing"][-1]]
                                if not loops["dof"]:
                                    focusing_cs["dof"] = [focusing_cs["dof"][-1]]
                                if loops["focusing"] or loops["dof"]:
                                    focusing_loop = {}
                                    focusing_loop["focusing_loop"] = loops["focusing"]
                                    focusing_loop["dof_loop"] = loops["dof"]
                                    string += "\n        {} camera_blur({}, {}) ".format("function", focusing_cs, focusing_loop)
                                else:
                                    string += "\n        {} camera_blur({}) ".format("function", focusing_cs)

                        for p, cs in sort_props(image_keyframes):
                            if p not in special_props:
                                if len(cs) > 1 and loops[(tag, layer, p)]:
                                    string += """
        parallel:"""
                                    string += """
            {} {}""".format(p, cs[0][0])
                                    for i, c in enumerate(cs[1:]):
                                        string += """
            {} {} {} {}""".format(c[2], cs[i+1][1]-cs[i][1], p, c[0])
                                        if c[1] in splines[(tag, layer, p)] and splines[(tag, layer, p)][c[1]]:
                                            for knot in splines[(tag, layer, p)][c[1]]:
                                                string += " knot {}".format(knot)
                                    string += """
            repeat"""

                        if "child" in image_keyframes and loops[(tag,layer,"child")]:
                            last_time = 0.0
                            string += """
        parallel:"""
                            for i in range(0, len(image_keyframes["child"]), 1):
                                (image, transition), t, w = image_keyframes["child"][i]
                                widget = None
                                if i > 0:
                                    old_widget = image_keyframes["child"][i-1][0][0]
                                    if old_widget is not None:
                                        widget = old_widget
                                if i < len(image_keyframes["child"])-1:
                                    new_widget = image_keyframes["child"][i+1][0][0]
                                    if new_widget is not None:
                                        widget = new_widget
                                if widget is None:
                                    if image is not None:
                                        widget = image
                                if widget is None:
                                    null = "Null()"
                                else:
                                    w, h = renpy.render(renpy.easy.displayable(widget), 0, 0, 0, 0).get_size()
                                    null = "Null({}, {})".format(w, h)
                                if (t - last_time) > 0:
                                    string += """
            {}""".format(t-last_time)
                                if i == 0 and (image is not None and transition is not None):
                                    string += """
            {}""".format(null)
                                if image is None:
                                    string += """
            {}""".format(null)
                                else:
                                    string += """
            '{}'""".format(image)
                                if transition is not None:
                                    string += " with {}".format(transition)

                                    transition = renpy.python.py_eval("renpy.store."+transition)
                                    delay = getattr(transition, "delay", None)
                                    if delay is None:
                                        delay = getattr(transition, "args")[0]
                                    t += delay
                                last_time = t
                            string += """
            repeat"""

            string += """
    {} show""".format(window_mode)
        string += "\n\n"

        if string:
            string = string.replace("u'", "'", 999)
            try:
                from pygame import scrap, locals
                scrap.put(locals.SCRAP_TEXT, string)
            except:
                renpy.notify(_("Can't open clipboard"))
            else:
                #syntax hilight error in vim
                renpy.notify("Placed\n{}\n\non clipboard".format(string).replace("{", "{{").replace("[", "[["))
        else:
            renpy.notify(_("Nothing to put"))

init python:
    def camera_blur(check_points, loop=None):
        if "focusing" not in check_points:
            check_points["focusing"] = [(_viewers.camera_viewer.get_default("focusing"), 0, None)]
        if "dof" not in check_points:
            check_points["dof"] = [(_viewers.camera_viewer.get_default("dof"), 0, None)]
        if loop is None:
            loop = {}
        if "focusing_loop" not in loop:
            loop["focusing_loop"] = False
        if "dof_loop" not in loop:
            loop["dof_loop"] = False
        return renpy.curry(_viewers.transform_viewer.transform)(check_points=check_points, loop=loop, subpixel=None, crop_relative=None)
