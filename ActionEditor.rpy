#課題

#再現条件不明
#hideが動作しないときがある
#ホイールが片側動作しない, warper選択画面でのスクロールもできなかった

#新機能
#再生中に右クリックで再生停止可能に
#クリップボードデータを出来るだけ短いフォーマットに変更
#zzoomを追加
#perspectiveを追加
#optionページを追加
#perspectiveがNoneのときはcropを操作できるように

#変更
#レイアウトを調整
#x, ypos, xyanchor, xyoffsetをpos, anchor, offsetにまとめた
#表示ずみのタグの画像を追加するとタグ+数値として追加するように変更

#修正
#Ren'Py 8に対応

#既知の問題
#childのみならばparallelなくてよい
#perspectiveで数値を指定されていたらどうする?
#colormatrix, transformmatrixは十分再現できない

#課題
#キーフレームのマーカーを表示する スタイルによって位置が変わる

# tab="images"/"camera", layer="master",  
screen _action_editor(tab="camera", layer="master", opened=0, time=0, page=0):
    $play_action = [SensitiveIf(_viewers.sorted_keyframes[_viewers.current_scene] or len(_viewers.scene_keyframes) > 1), \
        SelectedIf(False), Function(_viewers.play, play=True), Hide("_action_editor"), \
        Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page, time=_viewers.get_animation_delay())]
    if _viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True):
        key "rollback"    action Function(_viewers.generate_changed("offsetZ"), _viewers.get_property("offsetZ")+100+persistent._wide_range)
        key "rollforward" action Function(_viewers.generate_changed("offsetZ"), _viewers.get_property("offsetZ")-100+persistent._wide_range)
    key "K_SPACE" action play_action
    key "action_editor" action NullAction()

    $offsetX, offsetY = _viewers.get_property("offsetX"), _viewers.get_property("offsetY")
    $range = persistent._wide_range
    $move_amount1 = 100
    $move_amount2 = 300
    if _viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True):
        if _viewers.fps_keymap:
            key "s" action Function(_viewers.generate_changed("offsetY"), offsetY + move_amount1 + range)
            key "w" action Function(_viewers.generate_changed("offsetY"), offsetY - move_amount1 + range)
            key "a" action Function(_viewers.generate_changed("offsetX"), offsetX - move_amount1 + range)
            key "d" action Function(_viewers.generate_changed("offsetX"), offsetX + move_amount1 + range)
            key "S" action Function(_viewers.generate_changed("offsetY"), offsetY + move_amount2 + range)
            key "W" action Function(_viewers.generate_changed("offsetY"), offsetY - move_amount2 + range)
            key "A" action Function(_viewers.generate_changed("offsetX"), offsetX - move_amount2 + range)
            key "D" action Function(_viewers.generate_changed("offsetX"), offsetX + move_amount2 + range)
        else:
            key "j" action Function(_viewers.generate_changed("offsetY"), offsetY + move_amount1 + range)
            key "k" action Function(_viewers.generate_changed("offsetY"), offsetY - move_amount1 + range)
            key "h" action Function(_viewers.generate_changed("offsetX"), offsetX - move_amount1 + range)
            key "l" action Function(_viewers.generate_changed("offsetX"), offsetX + move_amount1 + range)
            key "J" action Function(_viewers.generate_changed("offsetY"), offsetY + move_amount2 + range)
            key "K" action Function(_viewers.generate_changed("offsetY"), offsetY - move_amount2 + range)
            key "H" action Function(_viewers.generate_changed("offsetX"), offsetX - move_amount2 + range)
            key "L" action Function(_viewers.generate_changed("offsetX"), offsetX + move_amount2 + range)

    if time:
        timer time+1 action [Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page), \
                            Function(_viewers.change_time, _viewers.current_time), renpy.restart_interaction]
        key "game_menu" action [Show("_action_editor", tab=tab, layer=layer, opened=opened, page=page), \
                            Function(_viewers.change_time, _viewers.current_time)]
        key "hide_windows" action NullAction()
    else:
        key "game_menu" action Return()
    #camera transformはget_properyで所得できるようになるまで時間差があるので定期更新する
    # かなり動作が重くなる
    # camera transform properties need some times until being allowed to get property so I update screen.
    if not time:
        timer .2 action renpy.restart_interaction repeat True

    $state=_viewers.get_image_state(layer)
    $state_list = list(state)
    $page_list = []
    if len(state_list) > _viewers.tab_amount_in_page:
        for i in range(0, len(state_list)//_viewers.tab_amount_in_page):
            $page_list.append(state_list[i*_viewers.tab_amount_in_page:(i+1)*_viewers.tab_amount_in_page])
        if len(state_list)%_viewers.tab_amount_in_page != 0:
            $page_list.append(state_list[len(state_list)//_viewers.tab_amount_in_page*_viewers.tab_amount_in_page:])
    else:
        $page_list.append(state_list)
    if _viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True) == False and tab == "camera":
        $tab = state.keys()[0]

    if persistent._viewer_rot:
        on "show" action Show("_rot")

    frame:
        style_group "action_editor"
        if time:
            at _no_show()
        vbox:

            hbox:
                style_group "action_editor_a"
                textbutton _("time: [_viewers.current_time:>05.2f] s") action Function(_viewers.edit_time)
                textbutton _("<") action Function(_viewers.prev_time)
                textbutton _(">") action Function(_viewers.next_time)
                textbutton _("play") action play_action
                bar adjustment ui.adjustment(range=persistent._time_range, value=_viewers.current_time, changed=_viewers.change_time):
                    xalign 1. yalign .5 style "action_editor_bar"
            hbox:
                style_group "action_editor_a"
                textbutton _("option") action Show("_action_editor_option")
                textbutton _("remove keyframes") action [ \
                    SensitiveIf(_viewers.current_time in _viewers.sorted_keyframes[_viewers.current_scene]), \
                    Function(_viewers.remove_all_keyframe, _viewers.current_time), renpy.restart_interaction]
                textbutton _("move keyframes") action [ \
                    SensitiveIf(_viewers.current_time in _viewers.sorted_keyframes[_viewers.current_scene]), \
                    SelectedIf(False), SetField(_viewers, "moved_time", _viewers.current_time), Show("_move_keyframes")]
                textbutton _("hide") action HideInterface()
                textbutton _("clipboard") action Function(_viewers.put_clipboard)
                textbutton _("x") action Return()
            hbox:
                style_group "action_editor_a"
                textbutton _("scene") action [SensitiveIf(len(_viewers.scene_keyframes) > 1), Show("_scene_editor")]
                for i, ks in enumerate(_viewers.all_keyframes):
                    textbutton "[i]" action [SelectedIf(_viewers.current_scene == i), Function(_viewers.change_scene, i)]
                textbutton _("+") action _viewers.add_scene
            hbox:
                style_group "action_editor_a"
                xfill False
                textbutton _("<") action [SensitiveIf(page != 0), Show("_action_editor", tab=tab, layer=layer, page=page-1), renpy.restart_interaction]
                textbutton _("camera") action [\
                    SensitiveIf(_viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True) != False), \
                    SelectedIf(tab == "camera"), Show("_action_editor", tab="camera")]
                for n in page_list[page]:
                    textbutton "{}".format(n) action [SelectedIf(n == tab), Show("_action_editor", tab=n, layer=layer, page=page)]
                textbutton _("+") action Function(_viewers.add_image, layer)
                textbutton _(">") action [SensitiveIf(len(page_list) != page+1), Show("_action_editor", tab=tab, layer=layer, page=page+1), renpy.restart_interaction]

            if tab == "camera":
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i < opened:
                        hbox:
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
                textbutton "- " + _viewers.props_set_names[opened] action [SelectedIf(True), NullAction()]
                for p, d in _viewers.camera_props:
                    if p in _viewers.props_set[opened] and (p not in _viewers.props_groups["focusing"] or \
                        (persistent._viewer_focusing and _viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True))):
                        $value = _viewers.get_property(p)
                        $ f = _viewers.generate_changed(p)
                        $reset_action = [Function(_viewers.reset, p)]
                        if p in _viewers.props_groups["focusing"]:
                            for l in renpy.config.layers:
                                $reset_action += [Function(_viewers.reset, (tag, l, p)) for tag in _viewers.get_image_state(l)]
                        if p not in _viewers.force_float and (p in _viewers.force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                            hbox:
                                textbutton "  [p]" action [\
                                    SensitiveIf(p in _viewers.all_keyframes[_viewers.current_scene]), \
                                    SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", key=p, use_wide_range=True, edit_func=_viewers.edit_value, change_func=f)]
                                if isinstance(value, int):
                                    textbutton "[value:> ]":
                                        action [Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus)]
                                        alternate reset_action style_group "action_editor_b"
                                else:
                                    textbutton "[value:> .2f]" action Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus):
                                        alternate reset_action style_group "action_editor_b"
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._wide_range, value=value, page=1, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._wide_range*2, value=value+persistent._wide_range, page=1, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                        else:
                            hbox:
                                textbutton "  [p]" action [\
                                    SensitiveIf(p in _viewers.all_keyframes[_viewers.current_scene]), \
                                    SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", key=p, edit_func=_viewers.edit_value, change_func=f)]
                                textbutton "[value:> .2f]":
                                    action Function(_viewers.edit_value, f, default=value, force_plus=p in _viewers.force_plus)
                                    alternate reset_action style_group "action_editor_b"
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._narrow_range, value=value, page=.05, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._narrow_range*2, value=value+persistent._narrow_range, page=.05, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i > opened:
                        hbox:
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
            else:
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i < opened:
                        hbox:
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
                textbutton "- " + _viewers.props_set_names[opened] action [SelectedIf(True), NullAction()]
                for p, d in _viewers.transform_props:
                    if p in _viewers.props_set[opened] and (p not in _viewers.props_groups["focusing"] and (((persistent._viewer_focusing \
                        and _viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True)) and p != "blur") \
                        or (not persistent._viewer_focusing or not _viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True)))):
                        $value = _viewers.get_property((tab, layer, p))
                        $ f = _viewers.generate_changed((tab, layer, p))
                        if p == "child":
                            hbox:
                                textbutton "  [p]" action [\
                                    SensitiveIf((tab, layer, p) in _viewers.all_keyframes[_viewers.current_scene]), \
                                    SelectedIf(_viewers.keyframes_exist((tab, layer, p))), Show("_edit_keyframe", key=(tab, layer, p))]
                                textbutton "[value[0]]" action [\
                                    SelectedIf(_viewers.keyframes_exist((tab, layer, "child"))), \
                                    Function(_viewers.change_child, tab, layer, default=value[0])] size_group None
                                textbutton "with" action None size_group None
                                textbutton "[value[1]]" action [\
                                    SensitiveIf((tab, layer, p) in _viewers.all_keyframes[_viewers.current_scene]), \
                                    SelectedIf(_viewers.keyframes_exist((tab, layer, "child"))), \
                                    Function(_viewers.edit_transition, tab, layer)] size_group None
                        elif p not in _viewers.force_float and (p in _viewers.force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                            hbox:
                                textbutton "  [p]":
                                    action [SensitiveIf((tab, layer, p) in _viewers.all_keyframes[_viewers.current_scene]), \
                                    SelectedIf(_viewers.keyframes_exist((tab, layer, p))), \
                                    Show("_edit_keyframe", key=(tab, layer, p), use_wide_range=True, edit_func=_viewers.edit_value, change_func=f)]
                                if isinstance(value, int):
                                    textbutton "[value:> ]":
                                        action [Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus)]
                                        alternate Function(_viewers.reset, (tab, layer, p)) style_group "action_editor_b"
                                else:
                                    textbutton "[value:> .2f]":
                                        action Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus)
                                        alternate Function(_viewers.reset, (tab, layer, p)) style_group "action_editor_b"
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._wide_range, value=value, page=1, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._wide_range*2, value=value+persistent._wide_range, page=1, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                        else:
                            hbox:
                                textbutton "  [p]" action [\
                                    SensitiveIf((tab, layer, p) in _viewers.all_keyframes[_viewers.current_scene]), \
                                    SelectedIf(_viewers.keyframes_exist((tab, layer, p))), \
                                    Show("_edit_keyframe", key=(tab, layer, p), edit_func=_viewers.edit_value, change_func=f)]
                                textbutton "[value:> .2f]" action Function(_viewers.edit_value, f, default=value, force_plus=p in _viewers.force_plus):
                                    alternate Function(_viewers.reset, (tab, layer, p)) style_group "action_editor_b"
                                if p in _viewers.force_plus:
                                    bar adjustment ui.adjustment(range=persistent._narrow_range, value=value, page=.05, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                                else:
                                    bar adjustment ui.adjustment(range=persistent._narrow_range*2, value=value+persistent._narrow_range, page=.05, changed=f):
                                        xalign 1. yalign .5 style "action_editor_bar"
                for i, props_set_name in enumerate(_viewers.props_set_names):
                    if i > opened:
                        hbox:
                            textbutton "+ "+props_set_name action Show("_action_editor", tab=tab, layer=layer, opened=i, page=page)
            hbox:
                xfill False
                xalign 1.
                if tab == "camera":
                    textbutton _("perspective") action [\
                        SelectedIf(_viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True)), \
                        Function(_viewers.toggle_perspective)] size_group None
                    textbutton _("clipboard") action Function(_viewers.put_camera_clipboard) size_group None
                    # textbutton _("reset") action [_viewers.camera_reset, renpy.restart_interaction] size_group None
                else:
                    textbutton _("remove") action [\
                        SensitiveIf(tab in _viewers.image_state[_viewers.current_scene][layer]), \
                        Show("_action_editor", tab="camera", layer=layer, opened=opened, page=page), \
                        Function(_viewers.remove_image, layer, tab)] size_group None
                    textbutton _("zzoom") action [\
                        SelectedIf(_viewers.get_value((tab, layer, "zzoom"), _viewers.scene_keyframes[_viewers.current_scene][1], True)), \
                        Function(_viewers.toggle_zzoom, tab, layer)] size_group None
                    textbutton _("clipboard") action Function(_viewers.put_image_clipboard, tab, layer) size_group None
                    # textbutton _("reset") action [_viewers.image_reset, renpy.restart_interaction] size_group None

    if not time and persistent._show_camera_icon:
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
            text _("Show/Hide rule of thirds lines")
            textbutton _("rot") action [SelectedIf(persistent._viewer_rot), ToggleField(persistent, "_viewer_rot"), If(renpy.get_screen("_rot"), true=Hide("_rot"), false=Show("_rot"))]
            text _("Show/Hide camera icon")
            textbutton _("camera icon") action [SelectedIf(persistent._show_camera_icon), ToggleField(persistent, "_show_camera_icon")]
            text _("Show/Hide window during animation in clipboard(window is forced to be hide when the action has multi scene)")
            textbutton _("hide") action [SelectedIf(persistent._viewer_hide_window), ToggleField(persistent, "_viewer_hide_window")]
            text _("Allow/Disallow skipping animation in clipboard(be forced to allow when the action has multi scene)")
            text _("(*This doesn't work correctly when the animation include loops and that tag is already shown)")
            textbutton _("skippable") action [SelectedIf(persistent._viewer_allow_skip), ToggleField(persistent, "_viewer_allow_skip")]
            text _("Enable/Disable simulating camera blur(This is available when perspective is True)")
            textbutton _("focusing") action [SensitiveIf(_viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True)), SelectedIf(persistent._viewer_focusing), ToggleField(persistent, "_viewer_focusing"), Function(_viewers.change_time, _viewers.current_time)]
            text _("Assign default warper")
            textbutton "[persistent._viewer_warper]" action _viewers.select_default_warper
            text _("Assign default transition(example: dissolve, Dissolve(5), None)")
            textbutton "[persistent._viewer_transition]" action _viewers.edit_default_transition
            text _("the wide range of property bar which is mainly used for int values(type int)")
            textbutton "[persistent._wide_range]" action Function(_viewers.edit_range_value, persistent, "_wide_range", True)
            text _("the narrow range of property bar which is used for float values(type float)")
            textbutton "[persistent._narrow_range]" action Function(_viewers.edit_range_value, persistent, "_narrow_range", False)
            text _("the time range of property bar(type float)")
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
        style_group "action_editor_subscreen"
        has vbox
        textbutton _("time: [_viewers.moved_time:>.2f] s") action Function(_viewers.edit_move_all_keyframe)
        bar adjustment ui.adjustment(range=persistent._time_range, value=_viewers.moved_time, changed=renpy.curry(_viewers.move_all_keyframe)(old=_viewers.moved_time)):
            xalign 1. yalign .5 style "action_editor_bar"
        textbutton _("close") action Hide("_move_keyframes") xalign .98

screen _edit_keyframe(key, edit_func=None, change_func=None, use_wide_range=False):
    $check_points = _viewers.all_keyframes[_viewers.current_scene][key]
    if isinstance(key, tuple):
        $n, l, p = key
        $k_list = key
        $check_points_list = check_points
        $loop_button_action = [ToggleDict(_viewers.loops[_viewers.current_scene], key)]
        for gn, ps in _viewers.props_groups.items():
            if p in ps:
                $k_list = [(n, l, p) for p in _viewers.props_groups[gn]]
                $check_points_list = [_viewers.all_keyframes[_viewers.current_scene][k2] for k2 in k_list]
                $loop_button_action = [ToggleDict(_viewers.loops[_viewers.current_scene], k2) for k2 in k_list+[(n, l, gn)]]
    else:
        $k_list = key
        $p = key
        $check_points_list = check_points
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
            if t != _viewers.scene_keyframes[_viewers.current_scene][1]:
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
                                Show("_spline_editor", edit_func=edit_func, change_func=change_func, \
                                    key=key, prop=p, pre=check_points[i-1], post=check_points[i], default=v, \
                                    use_wide_range=use_wide_range, force_plus=p in _viewers.force_plus, time=t)]
                        textbutton _("{}".format(v)) action [\
                            Function(edit_func, change_func, default=v, use_wide_range=use_wide_range, force_plus=p in _viewers.force_plus, time=t), \
                            Function(_viewers.change_time, t)]
                    textbutton _("[t:>05.2f] s") action Function(_viewers.edit_move_keyframe, keys=k_list, old=t)
                    bar adjustment ui.adjustment(range=persistent._time_range, value=t, changed=renpy.curry(_viewers.move_keyframe)(old=t, keys=k_list)):
                        xalign 1. yalign .5 style "action_editor_bar"
        hbox:
            textbutton _("loop") action loop_button_action size_group None
            textbutton _("close") action Hide("_edit_keyframe") xalign .98 size_group None

screen _spline_editor(edit_func, change_func, key, prop, pre, post, default, use_wide_range, force_plus, time):

    modal True
    key "game_menu" action Hide("_spline_editor")
    $cs = _viewers.all_keyframes[_viewers.current_scene][key]
    if use_wide_range:
        $range = persistent._wide_range
        $_page = 0.05
    else:
        $range = persistent._narrow_range
        $_page = 1
    if not force_plus:
        default old_v = post[0] + range
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
                    textbutton "{}".format(v) action [Function(edit_func, renpy.curry(change_func)(time=time, knot_number=i), default=v, use_wide_range=use_wide_range, force_plus=force_plus, time=time)]
                    if force_plus:
                        $_range = range
                        $_v = v
                    else:
                        $_range = range*2
                        $_v = v + range
                    bar adjustment ui.adjustment(range=_range, value=_v, page=_page, changed=renpy.curry(change_func)(time=time, knot_number=i)):
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


init -1098 python:
    # Added keymap
    config.underlay.append(renpy.Keymap(
        action_editor = renpy.curry(renpy.invoke_in_new_context)(_viewers.open_action_editor),
        image_viewer = _viewers.open_image_viewer,
        ))


init -1598 python in _viewers:
    from copy import deepcopy
    from math import sin, asin, cos, acos, atan, pi, sqrt
    from collections import defaultdict

    moved_time = 0
    loops = [defaultdict(lambda:False)]
    splines = [defaultdict(lambda:{})]
    all_keyframes = [{}]
    sorted_keyframes = [[]]
    scene_keyframes = []


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
                self.x_range = renpy.store.persistent._wide_range
            else:
                self.x_range = renpy.store.persistent._narrow_range
            if self.int_y:
                self.y_range = renpy.store.persistent._wide_range
            else:
                self.y_range = renpy.store.persistent._narrow_range

            self.cx = self.x = (0.5 + get_property("offsetX")/(2.*self.x_range))*renpy.config.screen_width
            self.cy = self.y = (0.5 + get_property("offsetY")/(2.*self.y_range))*renpy.config.screen_height


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
                if self.x-self.width/2. <= x and x <= self.x+self.width/2. \
                    and self.y-self.height/2. <= y and y <= self.y+self.height/2.:
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

            if get_property("offsetX") != int(self.cx) or get_property("offsetY") != int(self.cy):
                self.x = (0.5 + get_property("offsetX")/(2.*self.x_range))*renpy.config.screen_width
                self.y = (0.5 + get_property("offsetY")/(2.*self.y_range))*renpy.config.screen_height
                renpy.redraw(self, 0)

            if self.dragging:
                if self.x != x or self.y != y:
                    self.cx = 2*self.x_range*float(x)/renpy.config.screen_width
                    self.cy = 2*self.y_range*float(y)/renpy.config.screen_height
                    if self.int_x:
                        self.cx = int(self.cx)
                    if self.int_y:
                        self.cy = int(self.cy)
                    if self.cx != get_property("offsetX") or self.cy != get_property("offsetY"):
                        generate_changed("offsetX")(self.cx)
                        generate_changed("offsetY")(self.cy)
                    self.x, self.y = x, y
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


    class FixedTimeDisplayable(renpy.Displayable):


        def __init__(self, d, st, at, **properties):
            super(FixedTimeDisplayable, self).__init__(**properties)

            self.d = d
            self.st = st
            self.at = at
        

        def render(self, width, height, st, at):
            #st, at is 0 allways?
            return self.d.render(width, height, self.st, self.at)


    class RenderToDisplayable(renpy.Displayable):


        def __init__(self, render, **properties):
            super(RenderToDisplayable, self).__init__(**properties)

            self.render = render
        

        def render(self, width, height, st, at):
            #st, at is 0 allways?
            return self.render


    def action_editor_init():
        global image_state, image_state_org, camera_state_org
        if not renpy.config.developer:
            return
        sle = renpy.game.context().scene_lists
        # layer->tag->property->value
        image_state_org = []
        image_state = []
        camera_state_org = []
        image_state_org.append({})
        image_state.append({})
        camera_state_org.append({})
        props = sle.camera_transform["master"]
        for p, d in camera_props:
            camera_state_org[current_scene][p] = getattr(props, p, None)
        for gn, ps in props_groups.items():
            p2 = get_group_property(gn, getattr(props, gn, None))
            if p2 is not None:
                for p, v in zip(ps, p2):
                    camera_state_org[current_scene][p] = v

        for layer in renpy.config.layers:
            image_state_org[current_scene][layer] = {}
            image_state[current_scene][layer] = {}
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
                    child = getattr(d, "raw_child", None)
                    image_name_tuple = getattr(child, "name", None)
                if image_name_tuple is None:
                    continue

                name = " ".join(image.name)
                try:
                    image_name = " ".join(image_name_tuple)
                except:
                    raise Exception(image_name_tuple)
                image_state_org[current_scene][layer][tag] = {}

                pos = renpy.get_placement(d)
                state = getattr(d, "state", None)
                for p in ["xpos", "ypos", "xanchor", "yanchor", "xoffset", "yoffset"]:
                    image_state_org[current_scene][layer][tag][p] = getattr(pos, p, None)
                for p, default in transform_props:
                    if p not in image_state_org[current_scene][layer][tag]:
                        if p == "child":
                            image_state_org[current_scene][layer][tag][p] = (image_name, None)
                        else:
                            image_state_org[current_scene][layer][tag][p] = getattr(state, p, None)
                for gn, ps in props_groups.items():
                    p2 = get_group_property(gn, getattr(d, gn, None))
                    if p2 is not None:
                        for p, v in zip(ps, p2):
                            image_state_org[current_scene][layer][tag][p] = v
        renpy.scene()
        kwargs = {}
        for p, d in camera_props:
            for gn, ps in props_groups.items():
                if p in ps:
                    break
            else:
                if p != "rotate":
                    kwargs[p]=d
        renpy.exports.show_layer_at(renpy.store.Transform(**kwargs), camera=True)


    def get_group_property(group_name, group):
        def decimal(a):
            from decimal import Decimal, ROUND_HALF_UP
            return Decimal(str(a)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

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
                if decimal(group.zdz) != decimal(cos(rx)*cos(ry)):
                    rx = 2*pi - rx
            
                cosrz = group.xdx/cos(ry)
                cosrz = 1.0 if cosrz > 1.0 else cosrz
                cosrz = -1.0 if cosrz < -1.0 else cosrz
                rz = acos(cosrz)
                if decimal(group.ydx) != decimal(cos(ry)*sin(rz)):
                    rz = 2*pi - rz

                if decimal(group.ydy) != decimal(cos(rx)*cos(rz)+sin(rx)*sin(ry)*sin(rz)):
                    ry = pi - ry
                else:
                    break
            if (decimal(group.xdy) != decimal(-cos(rx)*sin(rz)+cos(rz)*sin(rx)*sin(ry))) \
                or (decimal(group.xdz) != decimal(cos(rx)*cos(rz)*sin(ry)+sin(rx)*sin(rz))) \
                or (decimal(group.ydz) != decimal(cos(rx)*sin(ry)*sin(rz)-cos(rz)*sin(rx))):
                #no supported matrix is used.
                return 0., 0., 0., 0., 0., 0.

            if decimal(rx) >= decimal(2*pi):
                rx = rx - 2*pi
            if decimal(ry) >= decimal(2*pi):
                ry = ry - 2*pi
            if decimal(rz) >= decimal(2*pi):
                rz = rz - 2*pi

            if decimal(rx) <= -decimal(2*pi):
                rx = rx + 2*pi
            if decimal(ry) <= -decimal(2*pi):
                ry = ry + 2*pi
            if decimal(rz) <= -decimal(2*pi):
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


    def reset(key_list):
        if current_time < scene_keyframes[current_scene][1]:
            renpy.notify(_("can't change values before the start tiem of the current scene"))
            return
        if not isinstance(key_list, list):
            key_list = [key_list]
        for key in key_list:
            if isinstance(key, tuple):
                tag, layer, prop = key
                state = get_image_state(layer)[tag]
                props = transform_props
            else:
                prop = key
                state = camera_state_org[current_scene]
                props = camera_props
            for p, d in props:
                if p == prop:
                    if state[prop] is not None:
                        v = state[prop]
                    else:
                        v = d
            #もともとNoneでNoneとデフォルトで結果が違うPropertyはリセット時にずれるが、デフォルの値で入力すると考えてキーフレーム設定した方が自然
            set_keyframe(key, v)
        change_time(current_time)


    def image_reset():
        key_list = [(tag, layer, prop) for layer in renpy.config.layers for tag, props in get_image_state(layer).items() for prop in props]
        reset(key_list)


    def camera_reset():
        reset([p for p, d in camera_props])


    def generate_changed(key):
        if isinstance(key, tuple):
            tag, layer, prop = key
            state = get_image_state(layer)[tag]
        else:
            prop = key
            state = camera_state_org[current_scene]
        def changed(v, time=None, knot_number=None):
            if time is None:
                time = current_time
            if time < scene_keyframes[current_scene][1]:
                renpy.notify(_("can't change values before the start tiem of the current scene"))
                return
            default = get_default(prop, not isinstance(key, tuple))
            if prop not in force_float and (prop in force_wide_range \
                or ( (state[prop] is None and isinstance(default, int)) or isinstance(state[prop], int) )):
                if isinstance(get_property(key), float) and prop in force_wide_range:
                    if prop in force_plus:
                        v = float(v)
                    else:
                        v -= float(renpy.store.persistent._wide_range)
                else:
                    if prop not in force_plus:
                        v -= renpy.store.persistent._wide_range
            else:
                if prop in force_plus:
                    v = round(float(v), 2)
                else:
                    v = round(v -renpy.store.persistent._narrow_range, 2)

            set_keyframe(key, v, time=time)
            if knot_number is not None:
                splines[current_scene][key][time][knot_number] = v
            change_time(time)
        return changed


    def set_keyframe(key, value, recursion=False, time=None):
        if isinstance(key, tuple):
            tag, layer, prop = key
            state = get_image_state(layer)[tag]
        else:
            prop = key
            state = camera_state_org[current_scene]
        if time is None:
            time = current_time
        keyframes = all_keyframes[current_scene].get(key, [])
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
            if time == scene_keyframes[current_scene][1]:
                all_keyframes[current_scene][key] = [(value, time, renpy.store.persistent._viewer_warper)]
            else:
                org = state[prop]
                if org is None:
                    org = get_default(prop, not isinstance(key, tuple))
                if prop == "child" and \
                    ((current_scene == 0 and tag in image_state[current_scene][layer]) \
                    or (current_scene != 0 and time > scene_keyframes[current_scene][1])):
                    org = (None, None)
                all_keyframes[current_scene][key] = [(org, scene_keyframes[current_scene][1], renpy.store.persistent._viewer_warper), (value, time, renpy.store.persistent._viewer_warper)]
        sort_keyframes()
        
        for gn, ps in props_groups.items():
            ps_set = set(ps)
            if prop in ps_set and gn != "focusing" and not recursion:
                ps_set.remove(prop)
                for p in ps_set:
                    if isinstance(key, tuple):
                        key2 = (tag, layer, p)
                    else:
                        key2 = p
                    set_keyframe(key2, get_property(key2), True, time=time)
        if not recursion:
            for s in range(current_scene+1, len(scene_keyframes)):
                for i in range(s, -1, -1):
                    if camera_keyframes_exist(i):
                        break
                for p, d in camera_props:
                    middle_value = get_value(p, scene_keyframes[s][1], False, i)
                    if isinstance(middle_value, float):
                        camera_state_org[s][p] = round(middle_value, 3)
                    else:
                        camera_state_org[s][p] = middle_value


    def play(play):
        camera_check_points = []
        loop = []
        spline = []
        for s, (_, t, _) in enumerate(scene_keyframes):
            check_points = {}
            camera_is_used = False
            for prop, d in camera_props:
                if prop in all_keyframes[s]:
                    check_points[prop] = all_keyframes[s][prop]
                    camera_is_used = True
                else:
                    if prop not in not_used_by_default or camera_state_org[s][prop] is not None:
                        check_points[prop] = [(get_property(prop, True, scene_num=s), t, None)]
            if not camera_is_used and s > 0:
                loop.append(loop[s-1])
                spline.append(spline[s-1])
                camera_check_points.append(camera_check_points[s-1])
            else:
                #ひとつでもprops_groupsのプロパティがあればグループ単位で追加する
                for gn, ps in props_groups.items():
                    if gn != "focusing":
                        group_flag = False
                        for prop in ps:
                            if not prop in check_points:
                                if camera_state_org[s].get(prop, None) is not None:
                                    v = camera_state_org[s][prop]
                                else:
                                    v = get_default(prop, True)
                                check_points[prop] = [(v, t, None)]
                            else:
                                group_flag =  True
                        if not group_flag:
                            for prop in ps:
                                del check_points[prop]
                loop.append({prop+"_loop": loops[s][prop] for prop, d in camera_props})
                spline.append({prop+"_spline": splines[s][prop] for prop, d in camera_props})
                camera_check_points.append(check_points)

        image_check_points = []
        for s, (_, t, _) in enumerate(scene_keyframes):
            check_points = {}
            for layer in renpy.config.layers:
                state = get_image_state(layer, s)
                check_points[layer] = {}
                for tag in state:
                    check_points[layer][tag] = {}
                    for prop, d in transform_props:
                        if (tag, layer, prop) in all_keyframes[s]:
                            check_points[layer][tag][prop] = all_keyframes[s][(tag, layer, prop)]
                        elif prop in props_groups["focusing"] and prop in camera_check_points[s]:
                            check_points[layer][tag][prop] = camera_check_points[s][prop]
                        else:
                            if prop not in not_used_by_default or state[tag][prop] is not None:
                                check_points[layer][tag][prop] = [(get_property((tag, layer, prop), True, scene_num=s), t, None)]
                    #ひとつでもprops_groupsのプロパティがあればグループ単位で追加する
                    for gn, ps in props_groups.items():
                        group_flag = False
                        for prop in ps:
                            if not prop in check_points[layer][tag]:
                                if state[tag].get(prop, None) is not None:
                                    v = state[tag][prop]
                                else:
                                    v = get_default(prop, False)
                                check_points[layer][tag][prop] = [(v, t, None)]
                            else:
                                group_flag = True
                        if not group_flag:
                            for prop in ps:
                                del check_points[layer][tag][prop]
                    if renpy.store.persistent._viewer_focusing and get_value("perspective", t, True, scene_num=s):
                        if "blur" in check_points[layer][tag]:
                            del check_points[layer][tag]["blur"]
                        if "focusing" not in check_points[layer][tag]:
                            check_points[layer][tag]["focusing"] = [(get_default("focusing", False), t, None)]
                            check_points[layer][tag]["dof"] = [(get_default("dof", False), t, None)]
                    else:
                        for p in ["focusing", "dof"]:
                            if p in check_points[layer][tag]:
                                del check_points[layer][tag][p]
                        if "blur" not in check_points[layer][tag]:
                            blur = state[tag].get("blur", None)
                            if blur is None:
                                blur = get_default("blur", False)
                            check_points[layer][tag]["blur"] = [(blur, t, None)]
            image_check_points.append(check_points)

            for css in camera_check_points:
                for p in props_groups["focusing"]:
                    if p in css:
                        del css[p]
        if play:
            renpy.show("action_preview", what=renpy.store.Transform(function=renpy.curry(viewer_transform)( \
             camera_check_points=camera_check_points, image_check_points=image_check_points, \
             scene_checkpoints=deepcopy(scene_keyframes), zorder_list=zorder_list, loop=loop, spline=spline)))
        else:
            renpy.show("action_preview", what=renpy.store.Transform(function=renpy.curry(viewer_transform)( \
             camera_check_points=camera_check_points, image_check_points=image_check_points, \
             scene_checkpoints=deepcopy(scene_keyframes), zorder_list=zorder_list, loop=loop, spline=spline, time=current_time)))


    def viewer_transform(tran, st, at, camera_check_points, image_check_points, scene_checkpoints, zorder_list, loop, spline=None, subpixel=True, time=None):
        if time is None:
            time = st
        box = renpy.display.layout.MultiBox(layout='fixed')
        # box.add(renpy.store.Solid("#000", xsize=renpy.config.screen_width, ysize=10,     pos=(0., 0.), anchor=(0., 1.)))
        # box.add(renpy.store.Solid("#000", xsize=renpy.config.screen_width, ysize=10,     pos=(0., 1.), anchor=(0., 0.)))
        # box.add(renpy.store.Solid("#000", xsize=10, ysize=renpy.config.screen_height+20, pos=(0., 0.), anchor=(1., 10)))
        # box.add(renpy.store.Solid("#000", xsize=10, ysize=renpy.config.screen_height+20, pos=(1., 0.), anchor=(0., 10)))
        # tran.align = (1.0, 0.)
        # tran.zoom = 0.6
        for i in range(-1, -len(scene_checkpoints), -1):
            checkpoint = scene_checkpoints[i][1]
            if time >= checkpoint:
                goal = scene_checkpoints[i]
                if time - checkpoint >= get_transition_delay(goal[0]):
                    child = FixedTimeDisplayable(renpy.store.Transform(function=renpy.curry( \
                     camera_transform)(camera_check_points=camera_check_points[i], image_check_points=image_check_points[i], \
                     scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[i], spline=spline[i], \
                     subpixel=subpixel, time=time, scene_num=i)), time, at)
                else:
                    old_widget = FixedTimeDisplayable(renpy.store.Transform(function=renpy.curry( \
                     camera_transform)(camera_check_points=camera_check_points[i-1], image_check_points=image_check_points[i-1], \
                     scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[i-1], spline=spline[i-1], \
                     subpixel=subpixel, time=time, scene_num=i-1)), time, at)
                    new_widget = FixedTimeDisplayable(renpy.store.Transform(function=renpy.curry( \
                     camera_transform)(camera_check_points=camera_check_points[i], image_check_points=image_check_points[i], \
                     scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[i], spline=spline[i], \
                     subpixel=subpixel, time=time, scene_num=i)), time, at)
                    transition = renpy.python.py_eval("renpy.store."+goal[0])
                    during_transition_displayable = DuringTransitionDisplayble(transition(old_widget, new_widget), time - checkpoint, 0)
                    child = during_transition_displayable
                break
        else:
            child = renpy.store.Transform(function=renpy.curry(camera_transform)( \
             camera_check_points=camera_check_points[0], image_check_points=image_check_points[0], \
             scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[0], spline=spline[0], \
             subpixel=subpixel, time=time, scene_num=0))
        box.add(child)
        tran.set_child(box)
        return 0


    def camera_transform(tran, st, at, camera_check_points, image_check_points, scene_checkpoints, zorder_list, loop, spline=None, subpixel=True, time=None, scene_num=0):
        image_box = renpy.display.layout.MultiBox(layout='fixed')
        for layer in image_check_points:
            for tag, zorder in zorder_list[scene_num][layer]:
                if tag in image_check_points[layer]:
                    image_loop = {prop+"_loop": loops[scene_num][(tag, layer, prop)] for prop, d in transform_props}
                    image_spline = {prop+"_spline": splines[scene_num][(tag, layer, prop)] for prop, d in transform_props}
                    for p in props_groups["focusing"]:
                        image_loop[p+"_loop"] = loops[scene_num][p]
                        image_spline[p+"_spline"] = splines[scene_num][p]
                    image_box.add(renpy.store.Transform(function=renpy.curry(transform)( \
                     check_points=image_check_points[layer][tag], \
                     loop=image_loop, spline=image_spline, \
                     subpixel=subpixel, time=time, scene_num=scene_num, scene_checkpoints=scene_checkpoints)))
        camera_box = renpy.display.layout.MultiBox(layout='fixed')
        #camera position doesn't have effect whithout box
        camera_box.add(renpy.store.Transform(function=renpy.curry(transform)( \
         check_points=camera_check_points, loop=loop, spline=spline, \
         subpixel=subpixel, time=time, camera=True, scene_num=scene_num, scene_checkpoints=scene_checkpoints))(image_box))
        tran.set_child(camera_box)
        return 0


    def transform(tran, st, at, check_points, loop, spline=None, subpixel=True, crop_relative=True, time=None, camera=False, in_editor=True, scene_num=None, scene_checkpoints=None):
        # check_points = { prop: [ (value, time, warper).. ] }
        if subpixel is not None:
            tran.subpixel = subpixel
        if crop_relative is not None:
            tran.crop_relative = crop_relative
        if time is None:
            time = st
        group_cache = defaultdict(lambda:{})
        sle = renpy.game.context().scene_lists
        if in_editor and camera:
            tran.perspective = get_value("perspective", scene_checkpoints[scene_num][1], True, scene_num=scene_num)

        for p, cs in check_points.items():
            if not cs:
                break

            if loop[p+"_loop"] and cs[-1][1]:
                if time % cs[-1][1] != 0:
                    time = time % cs[-1][1]

            scene_start = cs[0][1]
            for i in range(1, len(cs)):
                checkpoint = cs[i][1]
                pre_checkpoint = cs[i-1][1]
                if time >= scene_start and time < checkpoint:
                    start = cs[i-1]
                    goal = cs[i]
                    if p != "child":
                        if checkpoint != pre_checkpoint:
                            g = renpy.atl.warpers[goal[2]]((time - pre_checkpoint) / float(checkpoint - pre_checkpoint))
                        else:
                            g = 1.
                        default = get_default(p, camera)
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
                                            if in_editor:
                                                    camera_zpos = get_property("zpos", True, scene_num=scene_num) - get_property("offsetZ", scene_num=scene_num)
                                            else:
                                                if "master" in sle.camera_transform:
                                                    props = sle.camera_transform["master"]
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
                if time < scene_start:
                    fixed_index = 0
                else:
                    fixed_index = -1
                for gn, ps in props_groups.items():
                    if p in ps:
                        group_cache[gn][p] = cs[fixed_index][0]
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
                                if in_editor:
                                        camera_zpos = get_property("zpos", True, scene_num=scene_num) - get_property("offsetZ", scene_num=scene_num)
                                else:
                                    if "master" in sle.camera_transform:
                                        props = sle.camera_transform["master"]
                                        if props.zpos:
                                            camera_zpos = props.zpos
                                        if props.matrixtransform:
                                            camera_zpos -= props.matrixtransform.zdw
                                result = camera_blur_amount(image_zpos, camera_zpos, dof, focusing)
                                setattr(tran, "blur", result)
                        break
                else:
                    if p != "child":
                        setattr(tran, p, cs[fixed_index][0])

        if "child" in check_points:
            cs = check_points["child"]
            if not cs:
                return 0
            for i in range(-1, -len(cs), -1):
                checkpoint = cs[i][1]
                pre_checkpoint = cs[i-1][1]
                if time >= scene_start and time >= checkpoint:
                    start = cs[i-1]
                    goal = cs[i]
                    if start[0][0] is None and goal[0][0] is None:
                        tran.set_child(renpy.store.Null())
                        break
                    elif start[0][0] is None:
                        new_widget = FixedTimeDisplayable(renpy.easy.displayable(goal[0][0]), time, at)
                        w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                        old_widget = renpy.store.Null(w, h)
                    elif goal[0][0] is None:
                        old_widget = FixedTimeDisplayable(renpy.easy.displayable(start[0][0]), time, at)
                        w, h = renpy.render(old_widget, 0, 0, 0, 0).get_size()
                        new_widget = renpy.store.Null(w, h)
                    else:
                        old_widget = FixedTimeDisplayable(renpy.easy.displayable(start[0][0]), time, at)
                        new_widget = FixedTimeDisplayable(renpy.easy.displayable(goal[0][0]), time, at)
                    if time - checkpoint >= get_transition_delay(goal[0][1]):
                        child = new_widget
                    else:
                        transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                        during_transition_displayable = DuringTransitionDisplayble(transition(old_widget, new_widget), time-checkpoint, 0)
                        child = during_transition_displayable
                    tran.set_child(child)
                    break
            else:
                start = ((None, None), 0, None)
                goal = cs[0]
                checkpoint = goal[1]
                if goal[0][0] is None:
                    child = renpy.store.Null()
                else:
                    fixed_time = time-checkpoint
                    if fixed_time < 0:
                        fixed_time = 0
                    new_widget = FixedTimeDisplayable(renpy.easy.displayable(goal[0][0]), time, at)
                    w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                    old_widget = renpy.store.Null(w, h)
                    if fixed_time >= get_transition_delay(goal[0][1]):
                        child = new_widget
                    else:
                        transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                        child = DuringTransitionDisplayble(transition(old_widget, new_widget), fixed_time, 0)
                tran.set_child(child)
        return 0


    def get_property(key, default=True, scene_num=None):
        if scene_num is None:
            scene_num = current_scene
        if isinstance(key, tuple):
            tag, layer, prop = key
            if prop in props_groups["focusing"]:
                key = prop
        if isinstance(key, tuple):
            tag, layer, prop = key
            state = get_image_state(layer, scene_num)[tag]
        else:
            prop = key
            state = camera_state_org[scene_num]
        if key in all_keyframes[scene_num]:
            return get_value(key, scene_num=scene_num)
        elif prop in state and state[prop] is not None:
                if prop == "child":
                    return state[prop][0], None
                else:
                    return state[prop]
        elif default:
            return get_default(prop, not isinstance(key, tuple))
        else:
            return None


    def edit_value(function, use_wide_range=False, default="", force_plus=False, time=None):
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=default)
        if v:
            try:
                v = renpy.python.py_eval(v)
            except:
                renpy.notify(_("Please type value"))
            if default != "":
                if isinstance(default, int):
                    v = int(v)
                else:
                    v = float(v)
            if force_plus:
                v = v
            else:
                if use_wide_range:
                    v = v + renpy.store.persistent._wide_range
                else:
                    v = v + renpy.store.persistent._narrow_range
            if not force_plus or 0 <= v:
                function(v, time=time)
            else:
                renpy.notify(_("Please type plus value"))


    def edit_default_transition():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", message="Type transition")
        if v:
            if v == "None":
                v = None
            renpy.store.persistent._viewer_transition = v
            return
        renpy.notify(_("Please Input Transition"))


    def edit_transition(tag, layer, time=None):
        if time is None:
            time = current_time
        if time < scene_keyframes[current_scene][1]:
            renpy.notify(_("can't change values before the start tiem of the current scene"))
            return
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen")
        if v:
            if v == "None":
                v = None
            cs = all_keyframes[current_scene][(tag, layer, "child")]
            for i in range(-1, -len(cs)-1, -1):
                if time >= cs[i][1]:
                    (n, tran), t, w = cs[i]
                    break
            set_keyframe((tag, layer, "child"), (n, v), time=time)
            change_time(time)
            return
        renpy.notify(_("Please Input Transition"))


    def add_image(layer):
        if current_time < scene_keyframes[current_scene][1]:
            renpy.notify(_("can't change values before the start tiem of the current scene"))
            return
        name = renpy.invoke_in_new_context(renpy.call_screen, "_image_selecter")
        state = get_image_state(layer)

        if not isinstance(name, tuple):
            name = tuple(name.split())
        for n in get_image_name_candidates():
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
                image_state[current_scene][layer][added_tag] = {}
                zorder_list[current_scene][layer].append((added_tag, 0))
                for p, d in transform_props:
                    if p == "child":
                        image_state[current_scene][layer][added_tag][p] = (image_name, None)
                        if current_scene == 0 or current_time > scene_keyframes[current_scene][1]:
                            set_keyframe((added_tag, layer, p), (image_name, renpy.store.persistent._viewer_transition))
                    else:
                        image_state[current_scene][layer][added_tag][p] = get_property((added_tag, layer, p), False)
                change_time(current_time)
                renpy.show_screen("_action_editor", tab=added_tag, layer=layer)
                return
        else:
            renpy.notify(_("Please type image name"))
            return


    def get_image_name_candidates():
        from itertools import combinations
        result = []
        for n, d in renpy.display.image.images.items():
            if isinstance(d, renpy.store.Live2D):
                name = n[0]
                expression = d.common.expressions
                nonexclusive = d.common.nonexclusive
                motions = d.common.motions
                attribute_filter = d.common.attribute_filter

                nonexclusive_sets = []
                for i in range(1,len(nonexclusive)+1):
                    for comb in combinations(nonexclusive, n):
                        nonexclusive_sets.append(comb)
                filtered_nonexclusive_sets = set()
                if attribute_filter is not None:
                    for nes in nonexclusive_sets:
                        filtered_nonexclusive_sets.add(attribute_filter(nes))

                for m in motions:
                    result.append((name, m))
                    for e in expression:
                        result.append((name, m, e))
                        for nes in filtered_nonexclusive_sets:
                            result.append((name, m, )+nes)
                            result.append((name, m, e)+nes)
            else:
                result.append(n)
        return result


    def change_child(tag, layer, time=None, default=None):
        if time is None:
            time = current_time
        if time < scene_keyframes[current_scene][1]:
            renpy.notify(_("can't change values before the start tiem of the current scene"))
            return
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
                set_keyframe((tag, layer, "child"), (string, renpy.store.persistent._viewer_transition), time=time)
                return
        else:
            if new_image and new_image[0] == "None" and org is not None:
                set_keyframe((tag, layer, "child"), (None, renpy.store.persistent._viewer_transition), time=time)
                return
            renpy.notify(_("Please type image name"))
            return


    def toggle_zzoom(tag, layer):
        zzoom = get_value((tag, layer, "zzoom"), scene_keyframes[current_scene][1], True)
        zzoom_org=get_image_state(layer)[tag]["zzoom"]
        if zzoom == zzoom_org or (not zzoom and not zzoom_org):
            set_keyframe((tag, layer, "zzoom"), not zzoom, time=scene_keyframes[current_scene][1])
        else:
            remove_keyframe(scene_keyframes[current_scene][1], (tag, layer, "zzoom"))
        change_time(current_time)


    def toggle_perspective():
        perspective = get_value("perspective", scene_keyframes[current_scene][1], True)
        if perspective:
            perspective = None
        elif perspective is None:
            perspective = True
        perspective_org=camera_state_org[current_scene]["perspective"]
        if perspective == perspective_org:
            remove_keyframe(scene_keyframes[current_scene][1], "perspective")
        else:
            set_keyframe("perspective", perspective, time=scene_keyframes[current_scene][1])
        change_time(current_time)


    def remove_image(layer, tag):
        def remove_keyframes(layer, tag):
            for k in [k for k in all_keyframes[current_scene] if isinstance(k, tuple) and k[0] == tag and k[1] == layer]:
                del all_keyframes[current_scene][k]

        renpy.hide(tag, layer)
        del image_state[current_scene][layer][tag]
        remove_keyframes(tag, layer)
        sort_keyframes()
        zorder_list[current_scene][layer] = [(ztag, z) for (ztag, z) in zorder_list[current_scene][layer] if ztag != tag]


    def get_default(prop, camera=False):
        if camera:
            props = camera_props
        else:
            props = transform_props
        for p, d in props:
            if p == prop:
                return d


    def get_value(key, time=None, default=False, scene_num=None):
        if scene_num is None:
            scene_num = current_scene
        if isinstance(key, tuple):
            tag, layer, prop = key
            if prop in props_groups["focusing"]:
                key = prop
        if isinstance(key, tuple):
            tag, layer, prop = key
            if key not in all_keyframes[scene_num]:
                v = get_image_state(layer)[tag][prop]
                if v is not None:
                    return v
                elif default:
                    return get_default(prop)
                else:
                    return None
        else:
            prop = key
            if key not in all_keyframes[scene_num]:
                v = camera_state_org[scene_num][prop]
                if v is not None:
                    return v
                elif default:
                    return get_default(prop, True)
                else:
                    return None
        cs = all_keyframes[scene_num][key]

        if time is None:
            time = current_time

        if prop == "child":
            for i in range(-1, -len(cs)-1, -1):
                if time >= cs[i][1]:
                    return cs[i][0]

        if loops[scene_num][key] and cs[-1][1]:
            if time % cs[-1][1] != 0:
                time = time % cs[-1][1]

        scene_start = cs[0][1]
        for i in range(1, len(cs)):
            checkpoint = cs[i][1]
            pre_checkpoint = cs[i-1][1]
            if time >= scene_start and time < checkpoint:
                start = cs[i-1]
                goal = cs[i]
                if checkpoint != pre_checkpoint:
                    g = renpy.atl.warpers[goal[2]]((time - pre_checkpoint) / float(checkpoint - pre_checkpoint))
                else:
                    g = 1.
                default_vault = get_default(prop, not isinstance(key, tuple))
                if goal[0] is not None:
                    if start[0] is None:
                        start_v = default_vault
                    else:
                        start_v = start[0]
                    knots = []
                    if checkpoint in splines[scene_num][key]:
                        knots = splines[scene_num][key][checkpoint]
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
            if time >= scene_start:
                return cs[-1][0]
            else:
                return cs[0][0]


    def put_camera_clipboard():
        camera_keyframes = {k:[(round(get_value(k, current_time), 3), 0, None)] for k, v in all_keyframes[current_scene].items() if not isinstance(k, tuple)}
        camera_keyframes = set_group_keyframes(camera_keyframes)
        camera_properties = []
        for p, d in camera_props:
            for gn, ps in props_groups.items():
                if p in ps:
                    if gn not in camera_properties:
                        camera_properties.append(gn)
                    break
            else:
                camera_properties.append(p)

        string = """
camera"""
        for p, cs in x_and_y_to_xy([(p, camera_keyframes[p]) for p in camera_properties if p in camera_keyframes]):
            if string.find(":") < 0:
                string += ":\n        "
            string += "{} {} ".format(p, cs[0][0])
        string += "\n\n"

        try:
            from pygame import scrap, locals
            scrap.put(locals.SCRAP_TEXT, string)
        except:
            renpy.notify(_("Can't open clipboard"))
        else:
            renpy.notify(__('Placed \n"%s"\n on clipboard') % string)


    def put_image_clipboard(tag, layer):
        image_keyframes = {k[2]:[(round(get_value(k, current_time), 3), 0, None)] for k, v in all_keyframes[current_scene].items() if isinstance(k, tuple) and k[0] == tag and k[1] == layer}
        image_keyframes = set_group_keyframes(image_keyframes)
        if (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[current_scene][1], True)) \
            and "blur" in image_keyframes:
            del image_keyframes["blur"]
        image_properties = []
        for p, d in transform_props:
            for gn, ps in props_groups.items():
                if p in ps:
                    if gn not in image_properties:
                        image_properties.append(gn)
                    break
            else:
                if p not in special_props:
                    image_properties.append(p)
        state = get_image_state(layer)

        child = state[tag]["child"][0]
        string = """
show %s""" % child
        if tag != child.split()[0]:
                string += " as %s" % tag
        if layer != "master":
                string += " onlayer %s" % layer
        if tag in image_state[current_scene][layer]:
            string += """:
    default """
        for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes]):
            if string.find(":") < 0:
                string += ":\n        "
            string += "{} {} ".format(p, cs[0][0])
        if renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[current_scene][1], True):
            focus = get_value("focusing", current_time, True)
            dof = get_value("dof", current_time, True)
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
                if v < scene_keyframes[current_scene][1]:
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
                if v < scene_keyframes[current_scene][1]:
                    return
                move_all_keyframe(v, moved_time)
            except:
                renpy.notify(_("Please type value"))


    def edit_time():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=current_time)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < scene_keyframes[current_scene][1]:
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
        if not sorted_keyframes[current_scene]:
            change_time(scene_keyframes[current_scene][1])
            return
        else:
            for t in sorted_keyframes[current_scene]:
                if current_time < t:
                    change_time(t)
                    return
            change_time(scene_keyframes[current_scene][1])


    def prev_time():
        if not sorted_keyframes[current_scene]:
            change_time(scene_keyframes[current_scene][1])
            return
        else:
            for t in reversed(sorted_keyframes[current_scene]):
                if t < current_time and scene_keyframes[current_scene][1] <= t:
                    change_time(t)
                    return
            else:
                if current_time == scene_keyframes[current_scene][1]:
                    change_time(sorted_keyframes[current_scene][-1])
                else:
                    change_time(scene_keyframes[current_scene][1])


    def add_scene():
        global current_scene
        for i, (v, t, _) in enumerate(scene_keyframes):
            if t > current_time:
                break
            elif t == current_time:
                i += 1
                break
        else:
            i = len(scene_keyframes)
        current_scene = i
        scene_keyframes.insert(current_scene, (renpy.store.persistent._viewer_transition, current_time, None))
        image_state.insert(current_scene, {})
        image_state_org.insert(current_scene, {})
        camera_state_org.insert(current_scene, {})
        zorder_list.insert(current_scene, {})
        all_keyframes.insert(current_scene, {})
        sorted_keyframes.insert(current_scene, [])
        for l in renpy.config.layers:
            image_state[current_scene][l] = {}
            image_state_org[current_scene][l] = {}
            zorder_list[current_scene][l] = []
        loops.insert(current_scene, defaultdict(lambda:False))
        splines.insert(current_scene, defaultdict(lambda:{}))
        for i in range(current_scene-1, -1, -1):
            if camera_keyframes_exist(i):
                break
        for p, d in camera_props:
            middle_value = get_value(p, scene_keyframes[current_scene][1], False, i)
            if isinstance(middle_value, float):
                camera_state_org[current_scene][p] = round(middle_value, 3)
            else:
                camera_state_org[current_scene][p] = middle_value
        renpy.show_screen("_action_editor")


    def camera_keyframes_exist(scene_num):
        for p, d in camera_props:
            if p in all_keyframes[scene_num]:
                break
        else:
            return False
        return True


    def remove_scene(scene_num):
        global current_scene
        if scene_num == 0:
            return
        current_scene -= 1
        del scene_keyframes[scene_num]
        del image_state[scene_num]
        del image_state_org[scene_num]
        del camera_state_org[scene_num]
        del zorder_list[scene_num]
        del all_keyframes[scene_num]
        del sorted_keyframes[scene_num]
        del loops[scene_num]
        del splines[scene_num]
        for s in range(scene_num, len(scene_keyframes)):
            for i in range(s, -1, -1):
                if camera_keyframes_exist(i):
                    break
            for p, d in camera_props:
                middle_value = get_value(p, scene_keyframes[s][1], False, i)
                if isinstance(middle_value, float):
                    camera_state_org[s][p] = round(middle_value, 3)
                else:
                    camera_state_org[s][p] = middle_value
        renpy.show_screen("_action_editor")
        change_time(current_time)


    def move_scene(new, scene_num):
        scene_num_scene_keyframes = scene_keyframes.pop(scene_num)
        scene_num_image_state = image_state.pop(scene_num)
        scene_num_image_state_org = image_state_org.pop(scene_num)
        scene_num_camera_state_org = camera_state_org.pop(scene_num)
        scene_num_zorder_list = zorder_list.pop(scene_num)
        scene_num_all_keyframes = all_keyframes.pop(scene_num)
        scene_num_sorted_keyframes = sorted_keyframes.pop(scene_num)
        scene_num_loops = loops.pop(scene_num)
        scene_num_splines = splines.pop(scene_num)
        for i, s in enumerate(scene_keyframes):
            if s[1] > new:
                scene_keyframes.insert(i, scene_num_scene_keyframes)
                image_state.insert(i, scene_num_image_state)
                image_state_org.insert(i, scene_num_image_state_org)
                camera_state_org.insert(i, scene_num_camera_state_org)
                zorder_list.insert(i, scene_num_zorder_list)
                all_keyframes.insert(i, scene_num_all_keyframes)
                sorted_keyframes.insert(i, scene_num_sorted_keyframes)
                loops.insert(i, scene_num_loops)
                splines.insert(i, scene_num_splines)
                new_scene_num = i
                break
            elif s[1] == new:
                scene_keyframes.insert(scene_num, scene_num_scene_keyframes)
                image_state.insert(scene_num, scene_num_image_state)
                image_state_org.insert(scene_num, scene_num_image_state_org)
                camera_state_org.insert(scene_num, scene_num_camera_state_org)
                zorder_list.insert(scene_num, scene_num_zorder_list)
                all_keyframes.insert(scene_num, scene_num_all_keyframes)
                sorted_keyframes.insert(scene_num, scene_num_sorted_keyframes)
                loops.insert(scene_num, scene_num_loops)
                splines.insert(scene_num, scene_num_splines)
                return
        else:
            scene_keyframes.append(scene_num_scene_keyframes)
            image_state.append(scene_num_image_state)
            image_state_org.append(scene_num_image_state_org)
            camera_state_org.append(scene_num_camera_state_org)
            zorder_list.append(scene_num_zorder_list)
            all_keyframes.append(scene_num_all_keyframes)
            sorted_keyframes.append(scene_num_sorted_keyframes)
            loops.append(scene_num_loops)
            splines.append(scene_num_splines)
            new_scene_num = len(scene_keyframes)-1
        new = round(new, 2)
        tran, old, w = scene_keyframes[new_scene_num]
        scene_keyframes[new_scene_num] = (tran, new, w)

        for s in range(new_scene_num, len(scene_keyframes)):
            for i in range(s, -1, -1):
                if camera_keyframes_exist(i):
                    break
            for p, d in camera_props:
                middle_value = get_value(p, scene_keyframes[s][1], False, i)
                if isinstance(middle_value, float):
                    camera_state_org[s][p] = round(middle_value, 3)
                else:
                    camera_state_org[s][p] = middle_value
        for k, cs in all_keyframes[new_scene_num].items():
            for (v, t, w) in cs:
                c = (v, t - (old - new), w)
                if splines[new_scene_num][k]:
                    for t in splines[new_scene_num][k]:
                        knots = splines[new_scene_num][k].pop(t)
                        splines[new_scene_num][k][t - (old - new)] = knots
        sorted_keyframes[new_scene_num] = [t-(old-new) for t in sorted_keyframes[new_scene_num]]
        
        renpy.show_screen("_action_editor")
        change_time(current_time)
        return


    def edit_move_scene(scene_num):
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=scene_keyframes[scene_num][1])
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < 0:
                    renpy.notify(_("Please type plus value"))
                    return
                move_scene(v, scene_num)
            except:
                renpy.notify(_("Please type value"))


    def edit_scene_transition(scene_num):
        default, t, w = scene_keyframes[scene_num]
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=default)
        if v:
            if v == "None":
                v = None
            scene_keyframes[scene_num] = (v, t, w)
            change_time(current_time)
            return
        renpy.notify(_("Please Input Transition"))


    def change_scene(scene_num):
        global current_scene, current_time
        current_scene = scene_num
        renpy.show_screen("_action_editor")
        change_time(current_time)


    def select_default_warper():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_warper_selecter")
        if v:
            renpy.store.persistent._viewer_warper = v


    def clear_keyframes():
        global all_keyframes, sorted_keyframes
        all_keyframes = [{}]
        sorted_keyframes = [[]]


    def remove_keyframe(remove_time, key):
        if not isinstance(key, list):
            key = [key]
        for k in key:
            remove_list = []
            if k in all_keyframes[current_scene]:
                for (v, t, w) in all_keyframes[current_scene][k]:
                    if t == remove_time:
                        if remove_time != scene_keyframes[current_scene][1] \
                            or (remove_time == scene_keyframes[current_scene][1] \
                             and len(all_keyframes[current_scene][k]) == 1):
                            remove_list.append((v, t, w))
            for c in remove_list:
                if c[1] in splines[current_scene][k]:
                    del splines[current_scene][k][c[1]]
                all_keyframes[current_scene][k].remove(c)
                if not all_keyframes[current_scene][k]:
                    del all_keyframes[current_scene][k]
        sort_keyframes()
        change_time(current_time)


    def remove_all_keyframe(time):
        keylist = [k for k in all_keyframes[current_scene]]
        remove_keyframe(time, keylist)


    def sort_keyframes():
        sorted_keyframes[current_scene][:] = []
        for keyframes in all_keyframes[current_scene].values():
            for (v, t, w) in keyframes:
                if t not in sorted_keyframes[current_scene]:
                    sorted_keyframes[current_scene].append(t)
        sorted_keyframes[current_scene].sort()


    def move_all_keyframe(new, old):
        global moved_time
        if new < scene_keyframes[current_scene][1]:
            new = scene_keyframes[current_scene][1]
        moved_time = round(new, 2)
        k_list = [k for k in all_keyframes[current_scene].keys()]
        move_keyframe(new, old, k_list)


    def move_keyframe(new, old, keys):
        if new < scene_keyframes[current_scene][1]:
            new = scene_keyframes[current_scene][1]
        new = round(new, 2)
        if new == old:
            renpy.restart_interaction()
            return
        if not isinstance(keys, list):
            keys = [keys]
        for k in keys:
            if keyframes_exist(k, new):
                break
            cs = all_keyframes[current_scene][k]
            for i, c in enumerate(cs):
                if c[1] == old:
                    (value, time, warper) = cs.pop(i)
                    for n, (v, t, w) in enumerate(cs):
                        if new < t:
                            cs.insert(n, (value, new, warper))
                            break
                    else:
                        cs.append((value, new, warper))
                    if old == scene_keyframes[current_scene][1] and new != scene_keyframes[current_scene][1]:
                        cs.insert(0, (value, scene_keyframes[current_scene][1], renpy.store.persistent._viewer_warper))
                    if old in splines[current_scene][k]:
                        knots = splines[current_scene][k][old]
                        splines[current_scene][k][new] = knots
                        del splines[current_scene][k][old]
        sort_keyframes()
        renpy.restart_interaction()


    def keyframes_exist(k, time=None):
        if time is None:
            time = current_time
        if k not in all_keyframes[current_scene]:
            return False
        check_points = all_keyframes[current_scene][k]
        for c in check_points:
            if c[1] == time:
                return True
        return False


    def add_knot(key, time, default, knot_number=None):
        if time in splines[current_scene][key]:
            if knot_number is not None:
                splines[current_scene][key][time].insert(knot_number, default)
            else:
                splines[current_scene][key][time].append(default)
        else:
            splines[current_scene][key][time] = [default]


    def remove_knot(key, time, i):
        if time in splines[current_scene][key]:
            splines[current_scene][key][time].pop(i)
            if not splines[current_scene][key][time]:
                del splines[current_scene][key][time]


    def change_time(v):
        global current_time
        current_time = round(v, 2)
        # if current_time < scene_keyframes[current_scene][1]:
        #     current_time = scene_keyframes[current_scene][1]
        play(False)
        renpy.restart_interaction()


    def open_action_editor():
        global current_time, current_scene, scene_keyframes, zorder_list
        if not renpy.config.developer:
            return
        current_time = 0
        current_scene = 0
        moved_time = 0
        loops = [defaultdict(lambda:False)]
        splines = [defaultdict(lambda:{})]
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
        if renpy.store.persistent._wide_range is None:
            renpy.store.persistent._wide_range = wide_range
        if renpy.store.persistent._narrow_range is None:
            renpy.store.persistent._narrow_range = narrow_range
        if renpy.store.persistent._time_range is None:
            renpy.store.persistent._time_range = time_range
        if renpy.store.persistent._show_camera_icon is None:
            renpy.store.persistent._show_camera_icon = default_show_camera_icon
        zorder_list = [{}]
        for l in renpy.config.layers:
            zorder_list[current_scene][l] = renpy.get_zorder_list(l)
        scene_keyframes = [(None, 0, None)]
        action_editor_init()
        dragged.init(True, True)
        _window = renpy.store._window
        renpy.store._window = False
        change_time(0)
        renpy.call_screen("_action_editor")
        renpy.store._window = _window


    def get_transition_delay(tran):
        if tran is None or tran == "None":
            return 0
        if isinstance(tran, str):
            tran = renpy.python.py_eval("renpy.store."+tran)
        delay = getattr(tran, "delay", None)
        if delay is None:
            delay = getattr(tran, "args")[0]
        return delay


    def get_animation_delay():
        animation_time = 0
        for s, (tran, scene_start, _) in enumerate(scene_keyframes):
            if scene_start > animation_time:
                animation_time = scene_start
            delay = get_transition_delay(tran)
            if delay + scene_start  > animation_time:
                animation_time = delay + scene_start
            for cs in all_keyframes[s].values():
                for (v, t, w) in cs:
                    if isinstance(v, tuple):
                        delay = get_transition_delay(v[1])
                        t += delay
                    if t > animation_time:
                        animation_time = t
        return animation_time


    def get_scene_delay(scene_num):
        animation_time = 0
        (tran, scene_start, _) = scene_keyframes[scene_num]
        delay = get_transition_delay(tran)
        animation_time = delay + scene_start
        for cs in all_keyframes[scene_num].values():
            for (v, t, w) in cs:
                if isinstance(v, tuple):
                    delay = get_transition_delay(v[1])
                    t += delay
                if t > animation_time:
                    animation_time = t
        return animation_time - scene_start


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


    def camera_blur_amount(image_zpos, camera_zpos, dof, focusing):
        # if camera_zpos is None:
        #     camera_zpos = get_property("offsetZ")+get_property("zpos")
        # if focusing is None:
        #     focusing = get_property("focusing")
        # if dof is None:
        #     dof = get_property("dof")
        distance_from_focus = camera_zpos - image_zpos - focusing + renpy.config.perspective[1]
        if dof == 0:
            dof = 0.1
        blur_amount = _camera_blur_amount * renpy.atl.warpers[_camera_blur_warper](distance_from_focus/(float(dof)/2))
        if blur_amount < 0:
            blur_amount = abs(blur_amount)
        return blur_amount


    def get_image_state(layer, scene_num=None):
        if scene_num is None:
            scene_num = current_scene
        result = dict(image_state_org[scene_num][layer])
        result.update(image_state[scene_num][layer])
        return result


    def sort_props(keyframes):
        return [(p, keyframes[p]) for p in sort_ref_list if p in keyframes]


    def put_prop_togetter(keyframes, layer=None, tag=None):
        #時間軸とx, yを纏める キーフレームが一つのみのものは含めない
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
                    if loops[current_scene][key] != loops[current_scene][key2]:
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
                if check_spline and (splines[current_scene][xkey] or splines[current_scene][ykey]):
                # don't put together when propaerty has spline
                    continue
                if check_loop and (loops[current_scene][xkey] != loops[current_scene][ykey]):
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


    def sort_zorder(state, layer, scene_num):
        zorder = zorder_list[scene_num][layer]
        return [(tag, state[tag]) for tag, _ in zorder]


    def put_clipboard():
        string = ""
        if (renpy.store.persistent._viewer_hide_window and get_animation_delay() > 0 \
            and len(scene_keyframes) == 1) \
            or len(scene_keyframes) > 1:
            if renpy.store._window_auto:
                window_mode = "window auto"
            else:
                window_mode = "window"
            string += """
    {} hide""".format(window_mode)
        for s, (scene_tran, scene_start, _) in enumerate(scene_keyframes):
            camera_keyframes = {k:v for k, v in all_keyframes[s].items() if not isinstance(k, tuple)}
            camera_keyframes = set_group_keyframes(camera_keyframes)
            camera_properties = []
            for p, d in camera_props:
                for gn, ps in props_groups.items():
                    if p in ps:
                        if gn not in camera_properties:
                            camera_properties.append(gn)
                        break
                else:
                    camera_properties.append(p)
            if s > 0:
                string += """
    scene"""
                
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
                    if len(sorted) > 1 or loops[s][xy_to_x(sorted[0][0][0])]:
                        add_tab = "    "
                    else:
                        add_tab = ""
                    for same_time_set in sorted:
                        if len(sorted) > 1 or loops[s][xy_to_x(sorted[0][0][0])]:
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
                                if cs2[i+1][1] in splines[s][xy_to_x(p2)] and splines[s][xy_to_x(p2)][cs2[i+1][1]]:
                                    for knot in splines[s][xy_to_x(p2)][cs2[i+1][1]]:
                                        string += " knot {} ".format(knot)
                        if loops[s][xy_to_x(p)]:
                            string += """
            repeat"""

            for layer in image_state_org[s]:
                state = get_image_state(layer, s)
                for tag, _ in zorder_list[s][layer]:
                    value_org = state[tag]
                    image_keyframes = {k[2]:v for k, v in all_keyframes[s].items() if isinstance(k, tuple) and k[0] == tag and k[1] == layer}
                    image_keyframes = set_group_keyframes(image_keyframes)
                    if (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)) \
                        and "blur" in image_keyframes:
                        del image_keyframes["blur"]
                    image_properties = []
                    for p, d in transform_props:
                        for gn, ps in props_groups.items():
                            if p in ps:
                                if gn not in image_properties:
                                    image_properties.append(gn)
                                break
                        else:
                            if p not in special_props:
                                image_properties.append(p)
                    if image_keyframes or (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)) \
                        or tag in image_state[s][layer]:
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
                        string += """:
        """
                        if tag in image_state[s][layer]:
                            string += "default "
                        string += "subpixel True "
                        if "crop" in image_keyframes:
                            string += "{} {} ".format("crop_relative", True)
                        for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes and len(image_keyframes[p]) == 1], layer, tag):
                                string += "{} {} ".format(p, cs[0][0])
                        sorted = put_prop_togetter(image_keyframes, layer, tag)
                        if "child" in image_keyframes:
                            if len(sorted) >= 1 or loops[s][(tag, layer, "child")] or (renpy.store.persistent._viewer_focusing \
                                 and get_value("perspective", scene_keyframes[s][1], True, s)):
                                add_tab = "    "
                                string += """
        parallel:"""
                            else:
                                add_tab = ""
                            last_time = scene_start
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
                                    t += get_transition_delay(transition)
                                last_time = t
                            if loops[s][(tag,layer,"child")]:
                                string += """
            repeat"""
                        if len(sorted):
                            if len(sorted) > 1 or loops[s][(tag, layer, xy_to_x(sorted[0][0][0]))] or "child" in image_keyframes \
                                or (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)):
                                add_tab = "    "
                            else:
                                add_tab = ""
                            for same_time_set in sorted:
                                if len(sorted) > 1 or loops[s][(tag, layer, xy_to_x(sorted[0][0][0]))] or "child" in image_keyframes \
                                    or (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)):
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
                                        if cs2[i+1][1] in splines[s][(tag, layer, xy_to_x(p2))] and splines[s][(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                            for knot in splines[s][(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                                string += " knot {} ".format(knot)
                                if loops[s][(tag,layer,xy_to_x(p))]:
                                    string += """
            repeat"""
                        if (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)):
                            focusing_cs = {"focusing":[(get_default("focusing"), 0, None)], "dof":[(get_default("dof"), 0, None)]}
                            for p, cs in image_keyframes.items():
                                if len(cs) > 1 or "child" in image_keyframes:
                                    string += """
        parallel:
            """
                                    break
                            else:
                                string += "\n        "
                            for p in props_groups["focusing"]:
                                if p in all_keyframes[s]:
                                    focusing_cs[p] = [(v, t-scene_start, w) for cs in all_keyframes[s][p] for (v, t, w) in cs]
                            if loops[s]["focusing"] or loops[s]["dof"]:
                                focusing_loop = {}
                                focusing_loop["focusing_loop"] = loops[s]["focusing"]
                                focusing_loop["dof_loop"] = loops[s]["dof"]
                                string += "{} camera_blur({}, {}) ".format("function", focusing_cs, focusing_loop)
                            else:
                                string += "{} camera_blur({}) ".format("function", focusing_cs)
            if s != 0:
                string += """
    with {}""".format(scene_tran)
            if len(scene_keyframes) > 1:
                if s < len(scene_keyframes)-1:
                    pause_time = scene_keyframes[s+1][1] - scene_start
                else:
                    pause_time = get_scene_delay(s)
                pause_time -= get_transition_delay(scene_tran)
                pause_time = round(pause_time, 2)
                if pause_time > 0:
                    string += """
    with Pause({})""".format(pause_time)

        if (renpy.store.persistent._viewer_hide_window and get_animation_delay() > 0) \
            and len(scene_keyframes) == 1:
            string += """
    with Pause({})""".format(get_animation_delay())
        if (renpy.store.persistent._viewer_hide_window and get_animation_delay() > 0 \
            and renpy.store.persistent._viewer_allow_skip) \
            or len(scene_keyframes) > 1:

            for i in range(-1, -len(scene_keyframes)-1, -1):
                if camera_keyframes_exist(i):
                    break
            last_camera_scene = i
            camera_keyframes = {k:v for k, v in all_keyframes[last_camera_scene].items() if not isinstance(k, tuple)}
            for p, d in camera_props:
                if p not in camera_keyframes:
                    if camera_state_org[last_camera_scene][p] is not None and camera_state_org[last_camera_scene][p] != camera_state_org[0][p]:
                        camera_keyframes[p] = [(camera_state_org[last_camera_scene][p], scene_keyframes[last_camera_scene][1], None)]
            camera_keyframes = set_group_keyframes(camera_keyframes)
            if camera_keyframes:
                for p, cs in camera_keyframes.items():
                    if len(cs) > 1:
                        string += """
    camera:"""
                        for p, cs in camera_keyframes.items():
                            if len(cs) > 1 and loops[last_camera_scene][p]:
                                string += """
        animation"""
                                break
                        first = True
                        for p, cs in x_and_y_to_xy(sort_props(camera_keyframes), check_loop=True):
                            if len(cs) > 1 and not loops[last_camera_scene][xy_to_x(p)]:
                                if first:
                                    first = False
                                    string += """
        """
                                string += "{} {} ".format(p, cs[-1][0])
                        for p, cs in sort_props(camera_keyframes):
                            if len(cs) > 1 and loops[last_camera_scene][p]:
                                string += """
        parallel:"""
                                string += """
            {} {}""".format(p, cs[0][0])
                                for i, c in enumerate(cs[1:]):
                                    string += """
            {} {} {} {}""".format(c[2], cs[i+1][1]-cs[i][1], p, c[0])
                                    if c[1] in splines[last_camera_scene][p] and splines[last_camera_scene][p][c[1]]:
                                        for knot in splines[last_camera_scene][p][c[1]]:
                                            string += " knot {}".format(knot)
                                string += """
            repeat"""
                        break

            last_scene = len(scene_keyframes)-1
            for layer in image_state_org[last_scene]:
                state = get_image_state(layer, last_scene)
                for tag, _ in zorder_list[last_scene][layer]:
                    image_keyframes = {k[2]:v for k, v in all_keyframes[last_scene].items() if isinstance(k, tuple) and k[0] == tag and k[1] == layer}
                    image_keyframes = set_group_keyframes(image_keyframes)
                    if (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[last_scene][1], True, last_scene)) \
                        and "blur" in image_keyframes:
                        del image_keyframes["blur"]
                    image_properties = []
                    for p, d in transform_props:
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
                        if len(cs) > 1 and (p != "child" or loops[last_scene][(tag, layer, "child")]):
                            break
                    else:
                        continue
                    string += ":"
                    for p, cs in image_keyframes.items():
                        if len(cs) > 1 and loops[last_scene][(tag, layer, p)]:
                            string += """
        animation"""
                            break
                    first = True
                    for p, cs in x_and_y_to_xy(sort_props(image_keyframes), layer, tag, check_loop=True):
                        if p not in special_props:
                            if len(cs) > 1 and not loops[last_scene][(tag, layer, xy_to_x(p))]:
                                if first:
                                    first = False
                                    string += """
        """
                                string += "{} {} ".format(p, cs[-1][0])

                    if (renpy.store.persistent._viewer_focusing and get_value("perspective", scene_keyframes[last_scene][1], True, last_scene)):
                        focusing_cs = {"focusing":[(get_default("focusing"), 0, None)], "dof":[(get_default("dof"), 0, None)]}
                        if "focusing" in all_keyframes[last_scene]:
                            focusing_cs["focusing"] = all_keyframes[last_scene]["focusing"]
                        if "dof" in all_keyframes[last_scene]:
                            focusing_cs["dof"] = all_keyframes[last_scene]["dof"]
                        if len(focusing_cs["focusing"]) > 1 or len(focusing_cs["dof"]) > 1:
                            if not loops[last_scene]["focusing"]:
                                focusing_cs["focusing"] = [focusing_cs["focusing"][-1]]
                            if not loops[last_scene]["dof"]:
                                focusing_cs["dof"] = [focusing_cs["dof"][-1]]
                            if loops[last_scene]["focusing"] or loops[last_scene]["dof"]:
                                focusing_loop = {}
                                focusing_loop["focusing_loop"] = loops[last_scene]["focusing"]
                                focusing_loop["dof_loop"] = loops[last_scene]["dof"]
                                string += "\n        {} camera_blur({}, {}) ".format("function", focusing_cs, focusing_loop)
                            else:
                                string += "\n        {} camera_blur({}) ".format("function", focusing_cs)

                    for p, cs in sort_props(image_keyframes):
                        if p not in special_props:
                            if len(cs) > 1 and loops[last_scene][(tag, layer, p)]:
                                string += """
        parallel:"""
                                string += """
            {} {}""".format(p, cs[0][0])
                                for i, c in enumerate(cs[1:]):
                                    string += """
            {} {} {} {}""".format(c[2], cs[i+1][1]-cs[i][1], p, c[0])
                                    if c[1] in splines[last_scene][(tag, layer, p)] and splines[last_scene][(tag, layer, p)][c[1]]:
                                        for knot in splines[last_scene][(tag, layer, p)][c[1]]:
                                            string += " knot {}".format(knot)
                                string += """
            repeat"""

                    if "child" in image_keyframes and loops[last_scene][(tag,layer,"child")]:
                        last_time = scene_keyframes[last_scene][1]
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
                                t += get_transition_delay(transition)
                            last_time = t
                        string += """
            repeat"""

        if (renpy.store.persistent._viewer_hide_window and get_animation_delay() > 0 \
            and len(scene_keyframes) == 1) \
            or len(scene_keyframes) > 1:
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
            check_points["focusing"] = [(_viewers.get_default("focusing"), 0, None)]
        if "dof" not in check_points:
            check_points["dof"] = [(_viewers.get_default("dof"), 0, None)]
        if loop is None:
            loop = {}
        if "focusing_loop" not in loop:
            loop["focusing_loop"] = False
        if "dof_loop" not in loop:
            loop["dof_loop"] = False
        return renpy.curry(_viewers.transform)(check_points=check_points, loop=loop, subpixel=None, crop_relative=None, in_editor=False)
