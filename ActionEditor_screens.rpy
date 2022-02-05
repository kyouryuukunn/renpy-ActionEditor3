# tab="images"/"camera", layer="master",  
screen _new_action_editor(tab=None, layer="master", opened=None, time=0):
    $indent = "  "
    $play_action = [SensitiveIf(_viewers.sorted_keyframes[_viewers.current_scene] or len(_viewers.scene_keyframes) > 1), \
        SelectedIf(False), Function(_viewers.play, play=True), Hide("_new_action_editor"), \
        Show("_new_action_editor", tab=tab, layer=layer, opened=opened, time=_viewers.get_animation_delay())]
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
        timer time+1 action [Show("_new_action_editor", tab=tab, layer=layer, opened=opened), \
                            Function(_viewers.change_time, _viewers.current_time), renpy.restart_interaction]
        key "game_menu" action [Show("_new_action_editor", tab=tab, layer=layer, opened=opened), \
                            Function(_viewers.change_time, _viewers.current_time)]
        key "hide_windows" action NullAction()
    else:
        key "game_menu" action Return()
    #camera transformはget_properyで所得できるようになるまで時間差があるので定期更新する
    # かなり動作が重くなる
    # camera transform properties need some times until being allowed to get property so I update screen.
    if not time:
        timer .1 action renpy.restart_interaction repeat True

    $state=_viewers.get_image_state(layer)
    if _viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True) == False and tab == "camera":
        $tab = state.keys()[0]

    frame:
        $(x, y) = renpy.get_mouse_pos()
        if round(float(config.screen_width)/config.screen_height, 2) == 1.78:
            $x = int((x-config.screen_width*(1.-_viewers.preview_size)/2)/_viewers.preview_size)
            $y = int(y/_viewers.preview_size)
        else:
            $(x, y) = (x/_viewers.preview_size, y/_viewers.preview_size)
        $rx = x/float(config.screen_width)
        $ry = y/float(config.screen_height)
        style_group "new_action_editor"
        align (1., 0.)
        vbox:
            xfill False
            text "absolute" xalign 1.
            text "([x:>4], [y:>4])" xalign 1.
            text "fraction" xalign 1.
            text "([rx:>.3], [ry:>.3])" xalign 1.

    frame:
        pos (1., _viewers.preview_size)
        align (1., 1.)
        style_group "new_action_editor"
        if time:
            at _no_show()
        vbox:
            style_group "new_action_editor_a"
            textbutton _("option") action Show("_action_editor_option")
            textbutton _("scene list") action [SensitiveIf(len(_viewers.scene_keyframes) > 1), Show("_scene_editor")]
            hbox:
                xalign 1.
                textbutton _("remove keys") action [ \
                    SensitiveIf(_viewers.current_time in _viewers.sorted_keyframes[_viewers.current_scene]), \
                    Function(_viewers.remove_all_keyframe, _viewers.current_time), renpy.restart_interaction]
                textbutton _("move keys") action [ \
                    SensitiveIf(_viewers.current_time in _viewers.sorted_keyframes[_viewers.current_scene]), \
                    SelectedIf(False), SetField(_viewers, "moved_time", _viewers.current_time), Show("_move_keyframes")]
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
                    textbutton _("time: [_viewers.current_time:>05.2f] s") action Function(_viewers.edit_time) xalign 1. size_group None
                bar adjustment ui.adjustment(range=persistent._time_range, value=_viewers.current_time, changed=_viewers.change_time):
                    xalign 1. yalign .5 style "new_action_editor_bar"
            viewport:
                mousewheel True
                scrollbars "vertical"
                has vbox
                for s, ks in enumerate(_viewers.all_keyframes):
                    if s != _viewers.current_scene:
                        hbox:
                            style_group "new_action_editor_c"
                            textbutton "+ "+"scene[s]" action [SelectedIf(_viewers.current_scene == s), Function(_viewers.change_scene, s)]
                    else:
                        hbox:
                            style_group "new_action_editor_c"
                            textbutton "- "+"scene[s]" action [SelectedIf(_viewers.current_scene == s), Function(_viewers.change_scene, s)]

                        if tab != "camera":
                            hbox:
                                style_group "new_action_editor_c"
                                textbutton _(indent+"+ "+"camera") action [\
                                    SensitiveIf(_viewers.get_value("perspective", _viewers.scene_keyframes[s][1], True) != False), \
                                    SelectedIf(tab == "camera"), Show("_new_action_editor", tab="camera")]
                        else:
                            hbox:
                                style_group "new_action_editor_c"
                                textbutton _(indent+"- "+"camera") action [\
                                    SelectedIf(tab == "camera"), Show("_new_action_editor", tab=None)]
                                textbutton _("clipboard") action Function(_viewers.put_camera_clipboard) size_group None style_group "new_action_editor_b"
                            textbutton _(indent*2+"  perspective") action [\
                                SelectedIf(_viewers.get_value("perspective", _viewers.scene_keyframes[_viewers.current_scene][1], True)), \
                                Function(_viewers.toggle_perspective)]
                            if opened is None:
                                for i, props_set_name in enumerate(_viewers.props_set_names):
                                    hbox:
                                        style_group "new_action_editor_c"
                                        textbutton indent*2+"+ "+props_set_name action Show("_new_action_editor", tab=tab, layer=layer, opened=i)
                            else:
                                for i, props_set_name in enumerate(_viewers.props_set_names):
                                    if i < opened:
                                        hbox:
                                            style_group "new_action_editor_c"
                                            textbutton indent*2+"+ "+props_set_name action Show("_new_action_editor", tab=tab, layer=layer, opened=i)
                                hbox:
                                    style_group "new_action_editor_c"
                                    textbutton indent*2+"- " + _viewers.props_set_names[opened] action [SelectedIf(True), Show("_new_action_editor", tab=tab, layer=layer, opened=None)]
                                for p, d in _viewers.camera_props:
                                    if p in _viewers.props_set[opened] and (p not in _viewers.props_groups["focusing"] or \
                                        (persistent._viewer_focusing and _viewers.get_value("perspective", _viewers.scene_keyframes[s][1], True))):
                                        $value = _viewers.get_property(p)
                                        $ f = _viewers.generate_changed(p)
                                        if p not in _viewers.force_float and (p in _viewers.force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                                            hbox:
                                                hbox:
                                                    style_group "new_action_editor_c"
                                                    textbutton indent*3+"  [p]" action [\
                                                        SensitiveIf(p in _viewers.all_keyframes[s]), \
                                                        SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", key=p, use_wide_range=True, edit_func=_viewers.edit_value, change_func=f)]
                                                    if isinstance(value, int):
                                                        textbutton "[value:> ]":
                                                            action [Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus)]
                                                            alternate Function(_viewers.reset, p) style_group "new_action_editor_b"
                                                    else:
                                                        textbutton "[value:> .2f]" action Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus):
                                                            alternate Function(_viewers.reset, p) style_group "new_action_editor_b"
                                                if p in _viewers.force_plus:
                                                    bar adjustment ui.adjustment(range=persistent._wide_range, value=value, page=1, changed=f):
                                                        xalign 1. yalign .5 style "new_action_editor_bar"
                                                else:
                                                    bar adjustment ui.adjustment(range=persistent._wide_range*2, value=value+persistent._wide_range, page=1, changed=f):
                                                        xalign 1. yalign .5 style "new_action_editor_bar"
                                        else:
                                            hbox:
                                                hbox:
                                                    style_group "new_action_editor_c"
                                                    textbutton indent*3+"  [p]" action [\
                                                        SensitiveIf(p in _viewers.all_keyframes[s]), \
                                                        SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", key=p, edit_func=_viewers.edit_value, change_func=f)]
                                                    textbutton "[value:> .2f]":
                                                        action Function(_viewers.edit_value, f, default=value, force_plus=p in _viewers.force_plus)
                                                        alternate Function(_viewers.reset, p) style_group "new_action_editor_b"
                                                if p in _viewers.force_plus:
                                                    bar adjustment ui.adjustment(range=persistent._narrow_range, value=value, page=.05, changed=f):
                                                        xalign 1. yalign .5 style "new_action_editor_bar"
                                                else:
                                                    bar adjustment ui.adjustment(range=persistent._narrow_range*2, value=value+persistent._narrow_range, page=.05, changed=f):
                                                        xalign 1. yalign .5 style "new_action_editor_bar"
                                for i, props_set_name in enumerate(_viewers.props_set_names):
                                    if i > opened:
                                        hbox:
                                            style_group "new_action_editor_c"
                                            textbutton indent*2+"+ "+props_set_name action Show("_new_action_editor", tab=tab, layer=layer, opened=i)
                        for tag in _viewers.get_image_state(layer, s):
                            if tag != tab:
                                hbox:
                                    style_group "new_action_editor_c"
                                    textbutton indent+"+ "+"{}".format(tag) action [SelectedIf(tag == tab), Show("_new_action_editor", tab=tag, layer=layer)]
                            else:
                                hbox:
                                    style_group "new_action_editor_c"
                                    textbutton indent+"- "+"{}".format(tag) action [SelectedIf(tag == tab), Show("_new_action_editor", tab=None, layer=layer)]
                                    textbutton _("clipboard") action Function(_viewers.put_image_clipboard, tab, layer) style_group "new_action_editor_b" size_group None
                                textbutton _(indent*2+"  zzoom") action [\
                                    SelectedIf(_viewers.get_value((tab, layer, "zzoom"), _viewers.scene_keyframes[_viewers.current_scene][1], True)), \
                                    Function(_viewers.toggle_zzoom, tab, layer)]
                                if tab == tag:
                                    if opened is None:
                                        for i, props_set_name in enumerate(_viewers.props_set_names):
                                            hbox:
                                                style_group "new_action_editor_c"
                                                textbutton indent*2+"+ "+props_set_name action Show("_new_action_editor", tab=tab, layer=layer, opened=i)
                                    else:
                                        for i, props_set_name in enumerate(_viewers.props_set_names):
                                            if i < opened:
                                                hbox:
                                                    style_group "new_action_editor_c"
                                                    textbutton indent*2+"+ "+props_set_name action Show("_new_action_editor", tab=tab, layer=layer, opened=i)
                                        hbox:
                                            style_group "new_action_editor_c"
                                            textbutton indent*2+"- " + _viewers.props_set_names[opened] action [SelectedIf(True), Show("_new_action_editor", tab=tab, layer=layer, opened=None)]
                                        for p, d in _viewers.transform_props:
                                            if p in _viewers.props_set[opened] and (p not in _viewers.props_groups["focusing"] and (((persistent._viewer_focusing \
                                                and _viewers.get_value("perspective", _viewers.scene_keyframes[s][1], True)) and p != "blur") \
                                                or (not persistent._viewer_focusing or not _viewers.get_value("perspective", _viewers.scene_keyframes[s][1], True)))):
                                                $value = _viewers.get_property((tab, layer, p))
                                                $ f = _viewers.generate_changed((tab, layer, p))
                                                if p == "child":
                                                    vbox:
                                                        hbox:
                                                            style_group "new_action_editor_c"
                                                            textbutton indent*3+"  [p]" action [\
                                                                SensitiveIf((tab, layer, p) in _viewers.all_keyframes[s]), \
                                                                SelectedIf(_viewers.keyframes_exist((tab, layer, p))), Show("_edit_keyframe", key=(tab, layer, p))]
                                                            textbutton "[value[0]]" action [\
                                                                SelectedIf(_viewers.keyframes_exist((tab, layer, "child"))), \
                                                                Function(_viewers.change_child, tab, layer, default=value[0])] size_group None
                                                        hbox:
                                                            textbutton "" action None
                                                            style_group "new_action_editor_c"
                                                            hbox:
                                                                xsize None
                                                                textbutton "with" action None size_group None
                                                                textbutton "[value[1]]" action [\
                                                                    SensitiveIf((tab, layer, p) in _viewers.all_keyframes[s]), \
                                                                    SelectedIf(_viewers.keyframes_exist((tab, layer, "child"))), \
                                                                    Function(_viewers.edit_transition, tab, layer)] size_group None
                                                elif p not in _viewers.force_float and (p in _viewers.force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                                                    hbox:
                                                        hbox:
                                                            style_group "new_action_editor_c"
                                                            textbutton indent*3+"  [p]":
                                                                action [SensitiveIf((tab, layer, p) in _viewers.all_keyframes[s]), \
                                                                SelectedIf(_viewers.keyframes_exist((tab, layer, p))), \
                                                                Show("_edit_keyframe", key=(tab, layer, p), use_wide_range=True, edit_func=_viewers.edit_value, change_func=f)]
                                                            if isinstance(value, int):
                                                                textbutton "[value:> ]":
                                                                    action [Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus)]
                                                                    alternate Function(_viewers.reset, (tab, layer, p)) style_group "new_action_editor_b"
                                                            else:
                                                                textbutton "[value:> .2f]":
                                                                    action Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus)
                                                                    alternate Function(_viewers.reset, (tab, layer, p)) style_group "new_action_editor_b"
                                                        if p in _viewers.force_plus:
                                                            bar adjustment ui.adjustment(range=persistent._wide_range, value=value, page=1, changed=f):
                                                                xalign 1. yalign .5 style "new_action_editor_bar"
                                                        else:
                                                            bar adjustment ui.adjustment(range=persistent._wide_range*2, value=value+persistent._wide_range, page=1, changed=f):
                                                                xalign 1. yalign .5 style "new_action_editor_bar"
                                                else:
                                                    hbox:
                                                        hbox:
                                                            style_group "new_action_editor_c"
                                                            textbutton indent*3+"  [p]" action [\
                                                                SensitiveIf((tab, layer, p) in _viewers.all_keyframes[s]), \
                                                                SelectedIf(_viewers.keyframes_exist((tab, layer, p))), \
                                                                Show("_edit_keyframe", key=(tab, layer, p), edit_func=_viewers.edit_value, change_func=f)]
                                                            textbutton "[value:> .2f]" action Function(_viewers.edit_value, f, default=value, force_plus=p in _viewers.force_plus):
                                                                alternate Function(_viewers.reset, (tab, layer, p)) style_group "new_action_editor_b"
                                                        if p in _viewers.force_plus:
                                                            bar adjustment ui.adjustment(range=persistent._narrow_range, value=value, page=.05, changed=f):
                                                                xalign 1. yalign .5 style "new_action_editor_bar"
                                                        else:
                                                            bar adjustment ui.adjustment(range=persistent._narrow_range*2, value=value+persistent._narrow_range, page=.05, changed=f):
                                                                xalign 1. yalign .5 style "new_action_editor_bar"
                                        for i, props_set_name in enumerate(_viewers.props_set_names):
                                            if i > opened:
                                                hbox:
                                                    style_group "new_action_editor_c"
                                                    textbutton indent*2+"+ "+props_set_name action Show("_new_action_editor", tab=tab, layer=layer, opened=i)
                                    textbutton _(indent*3+"  remove") action [\
                                        SensitiveIf(tab in _viewers.image_state[_viewers.current_scene][layer]), \
                                        Show("_new_action_editor", tab="camera", layer=layer, opened=opened), \
                                        Function(_viewers.remove_image, layer, tab)] size_group None
                        textbutton _(indent+"+") action Function(_viewers.add_image, layer)
                textbutton _("+") action _viewers.add_scene

init -1597:
    style new_action_editor_frame:
        background None
    style new_action_editor_button:
        size_group "action_editor"
        background None
        idle_background None
        insensitive_background None
        ysize None
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
        ysize 20
        xsize config.screen_width-320-50

    style new_action_editor_a_button:
        take new_action_editor_button
        size_group None
        xalign 1.
    style new_action_editor_a_button_text is new_action_editor_button_text
    style new_action_editor_a_bar is new_action_editor_bar

    style new_action_editor_b_button:
        take new_action_editor_button
        size_group "new_action_editor_b"
        xminimum 90
    style new_action_editor_b_button_text is new_action_editor_button_text:
        xalign 1.0

    style new_action_editor_c_button is new_action_editor_button:
        size_group "new_action_editor_c"
    style new_action_editor_c_button_text is new_action_editor_button_text
    style new_action_editor_c_bar is new_action_editor_bar
    style new_action_editor_c_hbox:
        size_group "new_action_editor_c"
        xsize 320

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

    frame:
        style_group "action_editor"
        if time:
            at _no_show()
        has vbox

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
                    if p not in _viewers.force_float and (p in _viewers.force_wide_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                        hbox:
                            textbutton "  [p]" action [\
                                SensitiveIf(p in _viewers.all_keyframes[_viewers.current_scene]), \
                                SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", key=p, use_wide_range=True, edit_func=_viewers.edit_value, change_func=f)]
                            if isinstance(value, int):
                                textbutton "[value:> ]":
                                    action [Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus)]
                                    alternate Function(_viewers.reset, p) style_group "action_editor_b"
                            else:
                                textbutton "[value:> .2f]" action Function(_viewers.edit_value, f, use_wide_range=True, default=value, force_plus=p in _viewers.force_plus):
                                    alternate Function(_viewers.reset, p) style_group "action_editor_b"
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
                                alternate Function(_viewers.reset, p) style_group "action_editor_b"
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
            text _("Use Legacy ActionEditor Screen(recommend legacy gui for the 4:3 window)")
            textbutton _("legacy gui") action [SelectedIf(persistent._viewer_legacy_gui), ToggleField(persistent, "_viewer_legacy_gui"), If(persistent._viewer_legacy_gui, true=[Hide("_action_editor"), Show("_new_action_editor")], false=[Hide("_new_action_editor"), Show("_action_editor")]), Hide("_action_editor_option")]
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
            text _("One line includes only one property in clipboard data")
            textbutton _("one_line_one_property") action [ToggleField(persistent, "_one_line_one_prop")]
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
                            Function(edit_func, change_func, default=v, use_wide_range=use_wide_range, force_plus=p in _viewers.force_plus, time=t), \
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



