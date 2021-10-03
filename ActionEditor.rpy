#TODO
#spline,  expression,  last_moves, DOF
screen _action_editor(tab="images", layer="master", name="", time=0):
    key "game_menu" action Return()
    key "rollback"    action Function(_viewers.camera_viewer.generate_changed("zpos"), _viewers.camera_viewer.get_property("zpos")+100+_viewers.camera_viewer.int_range)
    key "rollforward" action Function(_viewers.camera_viewer.generate_changed("zpos"), _viewers.camera_viewer.get_property("zpos")-100+_viewers.camera_viewer.int_range)
    if _viewers.sorted_keyframes:
        key "K_SPACE" action [SensitiveIf(_viewers.sorted_keyframes), Function(_viewers.camera_viewer.play, play=True), Function(_viewers.transform_viewer.play, play=True), Hide("_action_editor"), Show("_action_editor", tab=tab, layer=layer, name=name, time=_viewers.sorted_keyframes[-1]), renpy.restart_interaction]
    else:
        key "K_SPACE" action [SensitiveIf(_viewers.sorted_keyframes), Function(_viewers.camera_viewer.play, play=True), Function(_viewers.transform_viewer.play, play=True), Hide("_action_editor"), Show("_action_editor", tab=tab, layer=layer, name=name), renpy.restart_interaction]
    $xpos, ypos = _viewers.camera_viewer.get_property("xpos"), _viewers.camera_viewer.get_property("ypos")
    if isinstance(xpos, int):
        $range = _viewers.camera_viewer.int_range
        $move_amount1 = 100
        $move_amount2 = 300
    else:
        $range = _viewers.camera_viewer.float_range
        $move_amount1 = 0.1
        $move_amount2 = 0.3

    if _viewers.fps_keymap:
        key "s" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos + move_amount1 + range)
        key "w" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos - move_amount1 + range)
        key "a" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos - move_amount1 + range)
        key "d" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos + move_amount1 + range)
        key "S" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos + move_amount2 + range)
        key "W" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos - move_amount2 + range)
        key "A" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos - move_amount2 + range)
        key "D" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos + move_amount2 + range)
    else:
        key "j" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos + move_amount1 + range)
        key "k" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos - move_amount1 + range)
        key "h" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos - move_amount1 + range)
        key "l" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos + move_amount1 + range)
        key "J" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos + move_amount2 + range)
        key "K" action Function(_viewers.camera_viewer.generate_changed("ypos"), ypos - move_amount2 + range)
        key "H" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos - move_amount2 + range)
        key "L" action Function(_viewers.camera_viewer.generate_changed("xpos"), xpos + move_amount2 + range)

    if time:
        timer time+1 action Function(_viewers.change_time, _viewers.time)
    #camera transformはget_properyで所得できるようになるまで時間差があるので定期更新する
    #camera transform properties need some times until being allowed to get property so I update screen.
    timer .1 action renpy.restart_interaction repeat True
    $state={k: v for dic in [_viewers.transform_viewer.state_org[layer], _viewers.transform_viewer.state[layer]] for k, v in dic.items()}

    if _viewers.default_rot and store._first_load:
        $store._first_load = False
        on "show" action Show("_rot")

    frame:
        background "#0006"
        if time:
            at _delay_show(time + 1)
        vbox:

            hbox:
                style_group "action_editor_a"
                textbutton _("time: [_viewers.time:>.2f] s") action Function(_viewers.edit_time)
                textbutton _("<") action Function(_viewers.prev_time)
                textbutton _(">") action Function(_viewers.next_time)
                bar adjustment ui.adjustment(range=7.0, value=_viewers.time, changed=_viewers.change_time) xalign 1. yalign .5
            hbox:
                style_group "action_editor_a"
                hbox:
                    textbutton _("default warper") action _viewers.select_default_warper
                    textbutton _("rot") action [SelectedIf(renpy.get_screen("_rot")), If(renpy.get_screen("_rot"), true=Hide("_rot"), false=Show("_rot"))]
                    textbutton _("hide") action HideInterface()
                    # textbutton _("window") action _viewers.AddWindow() #renpy.config.empty_window
                    if _viewers.sorted_keyframes:
                        textbutton _("play") action [SensitiveIf(_viewers.sorted_keyframes), Function(_viewers.camera_viewer.play, play=True), Function(_viewers.transform_viewer.play, play=True), Hide("_action_editor"), Show("_action_editor", tab=tab, layer=layer, name=name, time=_viewers.sorted_keyframes[-1]), renpy.restart_interaction]
                    else:
                        textbutton _("play") action [SensitiveIf(_viewers.sorted_keyframes), Function(_viewers.camera_viewer.play, play=True), Function(_viewers.transform_viewer.play, play=True), Hide("_action_editor"), Show("_action_editor", tab=tab, layer=layer, name=name), renpy.restart_interaction]
                    textbutton _("clipboard") action Function(_viewers.put_clipboard)
                hbox:
                    xalign 1.
                    textbutton _("close") action Return()
            hbox:
                style_group "action_editor_a"
                textbutton _("clear keyframes") action [SensitiveIf(_viewers.sorted_keyframes), Function(_viewers.clear_keyframes), renpy.restart_interaction]
                textbutton _("remove keyframes") action [SensitiveIf(_viewers.time in _viewers.sorted_keyframes), Function(_viewers.remove_keyframes, _viewers.time), renpy.restart_interaction]
                textbutton _("move keyframes") action [SensitiveIf(_viewers.time in _viewers.sorted_keyframes), SetField(_viewers, "moved_time", _viewers.time), Show("_move_keyframes")]
                # textbutton _("last moves") action [SensitiveIf(_last_camera_arguments), Function(_viewers.last_moves), renpy.restart_interaction]
            null height 10
            hbox:
                style_group "action_editor_a"
                xfill False
                textbutton _("Images") action [SelectedIf(tab == "images"), Show("_action_editor", tab="images")]
                textbutton _("Camera") action [SelectedIf(tab == "Camera"), Show("_action_editor", tab="Camera")]
            if tab == "images":
                hbox:
                    style_group "action_editor_a"
                    for l in config.layers:
                        if l not in ["screens", "transient", "overlay"]:
                            textbutton "[l]" action [SelectedIf(l == layer), Show("_action_editor", tab=tab, layer=l)]
                hbox:
                    style_group "action_editor_a"
                    textbutton _("+") action Function(_viewers.transform_viewer.add_image, layer)
                    for n in state:
                        textbutton "{}".format(n.split()[0]) action [SelectedIf(n == name), Show("_action_editor", tab=tab, layer=layer, name=n)]

                if name in state:
                    for p, d in _viewers.transform_viewer.props:
                        $value = _viewers.transform_viewer.get_property(layer, name.split()[0], p)
                        $ f = _viewers.transform_viewer.generate_changed(layer, name, p)
                        if p not in _viewers.transform_viewer.force_float and (p in _viewers.transform_viewer.force_int_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                            hbox:
                                style_group "action_editor"
                                textbutton "[p]" action [SensitiveIf((name, layer, p) in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist((name, layer, p))), Show("_edit_keyframe", k=(name, layer, p), int=True)]
                                if isinstance(value, int):
                                    textbutton "[value]" action Function(_viewers.transform_viewer.edit_value, f, int=True, default=value, force_plus=p in _viewers.transform_viewer.force_plus) alternate Function(_viewers.transform_viewer.reset, name, layer, p)
                                else:
                                    textbutton "[value:>.2f]" action Function(_viewers.transform_viewer.edit_value, f, int=True, default=value, force_plus=p in _viewers.transform_viewer.force_plus) alternate Function(_viewers.transform_viewer.reset, name, layer, p)
                                if p in _viewers.transform_viewer.force_plus:
                                    bar adjustment ui.adjustment(range=_viewers.transform_viewer.int_range, value=value, page=1, changed=f) xalign 1. yalign .5
                                else:
                                    bar adjustment ui.adjustment(range=_viewers.transform_viewer.int_range*2, value=value+_viewers.transform_viewer.int_range, page=1, changed=f) xalign 1. yalign .5
                        else:
                            hbox:
                                style_group "action_editor"
                                textbutton "[p]" action [SensitiveIf((name, layer, p) in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist((name, layer, p))), Show("_edit_keyframe", k=(name, layer, p))]
                                textbutton "[value:>.2f]" action Function(_viewers.transform_viewer.edit_value, f, int=False, default=value, force_plus=p in _viewers.transform_viewer.force_plus) alternate Function(_viewers.transform_viewer.reset, name, layer, p)
                                if p in _viewers.transform_viewer.force_plus:
                                    bar adjustment ui.adjustment(range=_viewers.transform_viewer.float_range, value=value, page=.05, changed=f) xalign 1. yalign .5
                                else:
                                    bar adjustment ui.adjustment(range=_viewers.transform_viewer.float_range*2, value=value+_viewers.transform_viewer.float_range, page=.05, changed=f) xalign 1. yalign .5
            elif tab == "Camera":
                for p, d in _viewers.camera_viewer.props:
                    $value = _viewers.camera_viewer.get_property(p)
                    $ f = _viewers.camera_viewer.generate_changed(p)
                    if p not in _viewers.camera_viewer.force_float and (p in _viewers.camera_viewer.force_int_range or ((value is None and isinstance(d, int)) or isinstance(value, int))):
                        hbox:
                            style_group "action_editor"
                            textbutton "[p]" action [SensitiveIf(p in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", k=p, int=True)]
                            if isinstance(value, int):
                                textbutton "[value]" action Function(_viewers.camera_viewer.edit_value, f, int=True, default=value, force_plus=p in _viewers.camera_viewer.force_plus) alternate Function(_viewers.camera_viewer.reset, p)
                            else:
                                textbutton "[value:>.2f]" action Function(_viewers.camera_viewer.edit_value, f, int=True, default=value, force_plus=p in _viewers.camera_viewer.force_plus) alternate Function(_viewers.camera_viewer.reset, p)
                            if p in _viewers.camera_viewer.force_plus:
                                bar adjustment ui.adjustment(range=_viewers.camera_viewer.int_range, value=value, page=1, changed=f) xalign 1. yalign .5
                            else:
                                bar adjustment ui.adjustment(range=_viewers.camera_viewer.int_range*2, value=value+_viewers.camera_viewer.int_range, page=1, changed=f) xalign 1. yalign .5
                    else:
                        hbox:
                            style_group "action_editor"
                            textbutton "[p]" action [SensitiveIf(p in _viewers.all_keyframes), SelectedIf(_viewers.keyframes_exist(p)), Show("_edit_keyframe", k=p)]
                            textbutton "[value:>.2f]" action Function(_viewers.camera_viewer.edit_value, f, int=False, default=value, force_plus=p in _viewers.camera_viewer.force_plus) alternate Function(_viewers.camera_viewer.reset, p)
                            if p in _viewers.camera_viewer.force_plus:
                                bar adjustment ui.adjustment(range=_viewers.camera_viewer.float_range, value=value, page=.05, changed=f) xalign 1. yalign .5
                            else:
                                bar adjustment ui.adjustment(range=_viewers.camera_viewer.float_range*2, value=value+_viewers.camera_viewer.float_range, page=.05, changed=f) xalign 1. yalign .5
            hbox:
                style_group "action_editor"
                xfill False
                xalign 1.
                if tab == "images":
                    if name:
                        textbutton _("remove") action [SensitiveIf(name in _viewers.transform_viewer.state[layer]), Show("_action_editor", tab=tab, layer=layer), Function(renpy.hide, name, layer), Function(_viewers.transform_viewer.state[layer].pop, name, layer), Function(_viewers.transform_viewer.remove_keyframes, name=name, layer=layer), _viewers.sort_keyframes]
                        textbutton _("clipboard") action Function(_viewers.transform_viewer.put_clipboard, name, layer)
                    textbutton _("reset") action [_viewers.transform_viewer.image_reset, renpy.restart_interaction]
                elif tab == "Camera":
                    textbutton _("clipboard") action Function(_viewers.camera_viewer.put_clipboard)
                    textbutton _("reset") action [_viewers.camera_viewer.camera_reset, renpy.restart_interaction]

    if time:
        add _viewers.dragged at _delay_show(time + 1)
    else:
        add _viewers.dragged

init -1598:
    style action_editor_button:
        size_group "action_editor"
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]
        idle_background None
        insensitive_background None
    style action_editor_button_text:
        color "#aaa"
        selected_color "#fff"
        insensitive_color "#777"
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]
    style action_editor_a_button:
        take action_editor_button
        size_group None
    style action_editor_a_button_text take action_editor_button_text

    style action_editor_label:
        xminimum 110
    style action_editor_vbox xfill True

screen _input_screen(message="type value", default=""):
    modal True
    key "game_menu" action Return("")

    frame:
        background "#0006"
        style_group "input_screen"

        has vbox

        label message

        hbox:
            input default default

init -1598:
    style input_screen_frame xfill True ypos .1 xmargin .05 ymargin .05
    style input_screen_vbox xfill True spacing 30
    style input_screen_label xalign .5
    style input_screen_hbox  xalign .5

transform _delay_show(time):
    alpha 0
    pause time
    alpha 1

screen _rot(): #show rule of thirds
    for i in range(1, 3):
        add Solid("#F00", xsize=config.screen_width, ysize=1, ypos=config.screen_height*i//3)
        add Solid("#F00", xsize=1, ysize=config.screen_height, xpos=config.screen_width*i//3)

screen _warper_selecter(current_warper=""):
    modal True
    key "game_menu" action Return("")

    frame:
        background "#0006"
        style_group "warper_selecter"

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
                    textbutton warper action [SelectedIf((_viewers.warper == warper and not current_warper) or warper == current_warper), Return(warper)] hovered Show("_warper_graph", warper=warper) unhovered Hide("_warper")
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
        background "#0006"
        has vbox
        textbutton _("time: [_viewers.moved_time:>.2f] s") action Function(_viewers.edit_move_all_keyframes)
        bar adjustment ui.adjustment(range=7.0, value=_viewers.moved_time, changed=renpy.curry(_viewers.move_keyframes)(old=_viewers.moved_time)) xalign 1. yalign .5
        textbutton _("close") action Hide("_move_keyframes") xalign .98

# _edit_keyframe((name, layer), "xpos")
# _edit_keyframe(_camera_x)
screen _edit_keyframe(k, int=False):
    $check_points = _viewers.all_keyframes[k]
    modal True
    key "game_menu" action Hide("_edit_keyframe")
    frame:
        background "#0009"
        xfill True
        has vbox
        label _("KeyFrames") xalign .5
        for v, t, w in check_points:
            if t != 0:
                hbox:
                    textbutton _("x") action [Function(_viewers.remove_keyframe, remove_time=t, k=k), renpy.restart_interaction] background None
                    textbutton _("{}".format(v)) action Function(_viewers.edit_value, check_points=check_points, old=t, value_org=v, int=int)
                    textbutton _("{}".format(w)) action Function(_viewers.edit_warper, check_points=check_points, old=t, value_org=w)
                    textbutton _("[t:>.2f] s") action Function(_viewers.edit_move_keyframes, check_points=check_points, old=t)
                    bar adjustment ui.adjustment(range=7.0, value=t, changed=renpy.curry(_viewers.move_keyframe)(old=t, check_points=check_points)) xalign 1. yalign .5
        hbox:
            textbutton _("loop") action ToggleDict(_viewers.loops, k)
            # if k[:8] == "_camera_":
            #     textbutton _("expression") action Function(_viewers.edit_expression, k)
            #     textbutton _("spline") action ToggleDict(_viewers.splines, "camera")
            # elif not isinstance(k, tuple):
            #     textbutton _("expression") action Function(_viewers.edit_expression, k)
            #     textbutton _("spline") action ToggleDict(_viewers.splines, k)
            textbutton _("close") action Hide("_edit_keyframe") xalign .98

init -1098 python:
    # Added keymap
    config.underlay.append(renpy.Keymap(
        # self_voicing = Preference("self voicing", "toggle"), #TODO ???
        action_editor = _viewers.action_editor,
        image_viewer = _open_image_viewer,
        ))

init -1598 python in _viewers:
    # TransformViewer
    class TransformViewer(object):
        def __init__(self):

            self.int_range = 1500
            self.float_range = 7.0
            # layer->tag->property->value
            self.state_org = {}
            self.state = {}
            # ((property, default)...), default is used when property can't be got.
            self.props = transform_props
            self.force_float = force_float
            self.force_int_range = force_int_range
            self.force_plus = force_plus

        def init(self):
            if not renpy.config.developer:
                return
            sle = renpy.game.context().scene_lists
            # back up for reset()
            for layer in renpy.config.layers:
                self.state_org[layer] = {}
                self.state[layer] = {}
                for tag in sle.layers[layer]:
                    if not tag[0]:
                        continue
                    d = sle.get_displayable_by_tag(layer, tag[0])
                    if isinstance(d, renpy.display.screen.ScreenDisplayable):
                        continue
                    pos = renpy.get_placement(d)
                    state = getattr(d, "state", None)

                    string = ""
                    for e in tag.name:
                        string += str(e) + " "
                    name = string[:-1]
                    self.state_org[layer][name] = {}
                    for p in ["xpos", "ypos", "xanchor", "yanchor"]:
                        self.state_org[layer][name][p] = getattr(pos, p, None)
                    for p, d in self.props:
                        if p not in self.state_org[layer][name]:
                            self.state_org[layer][name][p] = getattr(state, p, None)

        def reset(self, name, layer, prop):
            state_org={k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}[name][prop]
            kwargs = {}
            for p, d in self.props:
                value = self.get_property(layer, name.split()[0], p, False)
                if value is not None:
                    kwargs[p] = value
                elif p != "rotate":
                    kwargs[p] = d
            kwargs[prop] = state_org
            renpy.show(name, [renpy.store.Transform(**kwargs)], layer=layer)
            renpy.restart_interaction()

        def image_reset(self):
            for layer in renpy.config.layers:
                for name, props in {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}.iteritems():
                    for prop in props:
                        self.reset(name, layer, prop)

        def set_keyframe(self, layer, name, prop, value):

            keyframes = all_keyframes.get((name, layer, prop), [])
            if keyframes:
                for i, (v, t, w) in enumerate(keyframes):
                    if time < t:
                        keyframes.insert(i, (value, time, warper))
                        break
                    elif time == t:
                        keyframes[i] = ( value, time, warper)
                        break
                else:
                    keyframes.append((value, time, warper))
            else:
                if time == 0:
                    all_keyframes[(name, layer, prop)] = [(value, time, warper)]
                else:
                    org = {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}[name][prop]
                    all_keyframes[(name, layer, prop)] = [(org, 0, None), (value, time, warper)]
            sort_keyframes()

        def play(self, play):
            for layer in renpy.config.layers:
                for name in {k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}:
                    check_points = {}
                    for prop, d in self.props:
                        if (name, layer, prop) in all_keyframes:
                            check_points[prop] = all_keyframes[(name, layer, prop)]
                    if not check_points: # ビューワー上でのアニメーション(フラッシュ等)の誤動作を抑制
                        continue
                    loop = {prop+"_loop": loops[(name, layer, prop)] for prop, d in self.props}
                    if play:
                        renpy.show(name, [renpy.store.Transform(function=renpy.curry(self.transform)(check_points=check_points, loop=loop))], layer=layer)
                    else:
                        # check_points = { prop: ( (value, time, warper).. ) }
                        kwargs = {}
                        kwargs["subpixel"] = True
                        # kwargs.transform_anchor = True
                        st = renpy.store._viewers.time

                        for p, cs in check_points.items():
                            time = st
                            if loop[p+"_loop"] and cs[-1][1]:
                                time = time % cs[-1][1]

                            for i in xrange(1, len(cs)):
                                checkpoint = cs[i][1]
                                pre_checkpoint = cs[i-1][1]
                                if time < checkpoint:
                                    start = cs[i-1]
                                    goal = cs[i]
                                    if checkpoint != pre_checkpoint:
                                        g = renpy.atl.warpers[goal[2]]((time - pre_checkpoint) / float(checkpoint - pre_checkpoint))
                                    else:
                                        g = 1.
                                    for p2, d in self.props:
                                        if p2 == p:
                                            default = d
                                    if goal[0] is not None:
                                        if (prop in self.force_int_range or isinstance(goal[0], int)) and p not in self.force_float:
                                            if start[0] is None:
                                                v = g*(goal[0]-default)+default
                                            else:
                                                v = g*(goal[0]-start[0])+start[0]
                                            v = int(v)
                                        else:
                                            if start[0] is None:
                                                v = g*(goal[0]-default)+default
                                            else:
                                                v = g*(goal[0]-start[0])+start[0]
                                        kwargs[p] = v
                                    break
                            else:
                                kwargs[p] = cs[-1][0]

                        renpy.show(name, [renpy.store.Transform(**kwargs)], layer=layer)

        def transform(self, tran, st, at, check_points, loop, subpixel=True):
            # check_points = { prop: [ (value, time, warper).. ] }
            tran.subpixel = subpixel
            # tran.transform_anchor = True

            for p, cs in check_points.items():
                time = st
                if loop[p+"_loop"] and cs[-1][1]:
                    time = st % cs[-1][1]

                for i in xrange(1, len(cs)):
                    checkpoint = cs[i][1]
                    pre_checkpoint = cs[i-1][1]
                    if time < checkpoint:
                        start = cs[i-1]
                        goal = cs[i]
                        if checkpoint != pre_checkpoint:
                            g = renpy.atl.warpers[goal[2]]((time - pre_checkpoint) / float(checkpoint - pre_checkpoint))
                        else:
                            g = 1.
                        for p2, d in self.props:
                            if p2 == p:
                                default = d
                        if goal[0] is not None:
                            if start[0] is None:
                                v = g*(goal[0]-default)+default
                            else:
                                v = g*(goal[0]-start[0])+start[0]
                            if isinstance(goal[0], int) and p not in self.force_float:
                                v = int(v)
                            setattr(tran, p, v)
                        break
                else:
                    setattr(tran, p, cs[-1][0])
            return .005


        def generate_changed(self, layer, name, prop):
            state={k: v for dic in [self.state_org[layer], self.state[layer]] for k, v in dic.items()}[name][prop]
            def changed(v):
                kwargs = {}
                for p, d in self.props:
                    value = self.get_property(layer, name.split()[0], p, False)
                    if value is not None:
                        kwargs[p] = value
                    elif p != "rotate":
                        kwargs[p] = d
                    if p == prop:
                        default = d
                if prop not in self.force_float and (prop in self.force_int_range or ( (state is None and isinstance(default, int)) or isinstance(state, int) )):
                    if isinstance(self.get_property(layer, name.split()[0], prop), float) and prop in self.force_int_range:
                        if prop in self.force_plus:
                            kwargs[prop] = float(v)
                        else:
                            kwargs[prop] = v - float(self.int_range)
                    else:
                        if prop in self.force_plus:
                            kwargs[prop] = v
                        else:
                            kwargs[prop] = v - self.int_range
                else:
                    if prop in self.force_plus:
                        kwargs[prop] = round(float(v), 2)
                    else:
                        kwargs[prop] = round(v -self.float_range, 2)

                self.set_keyframe(layer, name, prop, kwargs[prop])
                renpy.show(name, [renpy.store.Transform(**kwargs)], layer=layer)
                renpy.restart_interaction()
            return changed

        def get_property(self, layer, tag, prop, default=True):
            sle = renpy.game.context().scene_lists
            # if tag in self.state[layer]:
            #     #TODO
            #     default = True
            if tag:
                d = sle.get_displayable_by_tag(layer, tag)
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

        def put_clipboard(self, name, layer):
            string = """
    show %s onlayer %s""" % (name, layer)
            for p, d in self.props:
                value = self.get_property(layer, name.split()[0], p)
                if value != d:
                    if string.find(":") < 0:
                        string += ":\n        "
                    string += "%s %s " % (p, value)
            try:
                from pygame import scrap, locals
                scrap.put(locals.SCRAP_TEXT, string)
            except:
                renpy.notify(_("Can't open clipboard"))
            else:
                renpy.notify(__('Placed \n"%s"\n on clipboard') % string)

        def edit_value(self, function, int=False, default="", force_plus=False):
            v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=default)
            if v:
                try:
                    if force_plus:
                        if int:
                            v = renpy.python.py_eval(v)
                        else:
                            v = float(renpy.python.py_eval(v))
                    else:
                        if int:
                            v = renpy.python.py_eval(v) + self.int_range
                        else:
                            v = renpy.python.py_eval(v) + self.float_range
                    if not force_plus or 0 <= v:
                        function(v)
                    else:
                        renpy.notify(_("Please type plus value"))
                except:
                    renpy.notify(_("Please type value"))

        def add_image(self, layer):
            default = ()
            while True:
                name = renpy.invoke_in_new_context(renpy.call_screen, "_image_selecter", default=default)
                if isinstance(name, tuple): #press button
                    for n in renpy.display.image.images:
                        if set(n) == set(name):
                            string=""
                            for e in n:
                                string += e + " "
                            self.state[layer][string] = {}
                            renpy.show(string, layer=layer)
                            for p, d in self.props:
                                self.state[layer][string][p] = self.get_property(layer, string.split()[0], p, False)
                            all_keyframes[(string, layer, "xpos")] = [(self.state[layer][string]["xpos"], 0, None)]
                            remove_list = [n_org for n_org in self.state_org[layer] if n_org.split()[0] == n[0]]
                            for n_org in remove_list:
                                del self.state_org[layer][n_org]
                                for k in [k for k in all_keyframes if isinstance(k, tuple) and k[0] == n_org and k[1] == layer]:
                                    del all_keyframes[k]
                            sort_keyframes()
                            renpy.show_screen("_action_editor", tab="images", layer=layer, name=string)
                            return
                    else:
                        default = name
                elif name: #from input text
                    # for n in renpy.display.image.images: #テキスト入力からはいきなり表示しないようにする。
                    #     if set(n) == set(name.split()):
                    #         self.state[layer][name] = {}
                    #         renpy.show(name, layer=layer)
                    #         for p, d in self.props:
                    #             self.state[layer][name][p] = self.get_property(layer, name.split()[0], p, False)
                    #         all_keyframes[(name, layer, "xpos")] = [(self.state[layer][name]["xpos"], 0, None)]
                    #         remove_list = [n_org for n_org in self.state_org[layer] if n_org.split()[0] == n[0]]
                    #         for n_org in remove_list:
                    #             del self.state_org[layer][n_org]
                    #             transform_viewer.remove_keyframes(n_org, layer)
                    #         sort_keyframes()
                    #         renpy.show_screen("_action_editor", tab="images", layer=layer, name=name)
                    #         return
                    default = tuple(name.split())
                else:
                    renpy.notify(_("Please type image name"))
                    return

        def remove_keyframes(self, name, layer):
            for k in [k for k in all_keyframes if isinstance(k, tuple) and k[0] == name and k[1] == layer]:
                del all_keyframes[k]
    transform_viewer = TransformViewer()

    ##########################################################################
    # CameraViewer
    class CameraViewer(TransformViewer):

        def __init__(self):
            super(CameraViewer, self).__init__()
            self.state_org = {}
            self.props = camera_props

        def init(self):
            if not renpy.config.developer:
                return
            for p, d in self.props:
                self.state_org[p] = self.get_property(p)

        def reset(self, prop):
            kwargs = {}
            for p, d in self.props:
                value = self.get_property(p, False)
                if value is not None:
                    kwargs[p] = value
            kwargs[prop] = self.state_org[prop]
            renpy.exports.show_layer_at(renpy.store.Transform(**kwargs), camera=True)
            renpy.restart_interaction()

        def camera_reset(self):
            renpy.exports.show_layer_at(renpy.store.Transform(**self.state_org), camera=True)
            renpy.restart_interaction()

        def set_keyframe(self, prop, value):
            keyframes = all_keyframes.get(prop, [])
            if keyframes:
                for i, (v, t, w) in enumerate(keyframes):
                    if time < t:
                        keyframes.insert(i, (value, time, warper))
                        break
                    elif time == t:
                        keyframes[i] = (value, time, warper)
                        break
                else:
                    keyframes.append((value, time, warper))
            else:
                if time == 0:
                    all_keyframes[prop] = [(value, time, warper)]
                else:
                    all_keyframes[prop] = [(self.state_org[prop], 0, None), (value, time, warper)]
            sort_keyframes()

        def play(self, play):
            check_points = {}
            for prop, d in self.props:
                if prop in all_keyframes:
                    check_points[prop] = all_keyframes[prop]
            if not check_points: # ビューワー上でのアニメーション(フラッシュ等)の誤動作を抑制
                return
            loop = {prop+"_loop": loops[prop] for prop, d in self.props}
            if play:
                renpy.exports.show_layer_at(renpy.store.Transform(function=renpy.curry(self.transform)(check_points=check_points, loop=loop)), camera=True)
            else:
                # check_points = { prop: ( (value, time, warper).. ) }
                kwargs = {}
                kwargs["subpixel"] = True
                # kwargs.transform_anchor = True
                st = renpy.store._viewers.time

                for p, cs in check_points.items():
                    time = st
                    if loop[p+"_loop"] and cs[-1][1]:
                        time = time % cs[-1][1]

                    for i in xrange(1, len(cs)):
                        checkpoint = cs[i][1]
                        pre_checkpoint = cs[i-1][1]
                        if time < checkpoint:
                            start = cs[i-1]
                            goal = cs[i]
                            if checkpoint != pre_checkpoint:
                                g = renpy.atl.warpers[goal[2]]((time - pre_checkpoint) / float(checkpoint - pre_checkpoint))
                            else:
                                g = 1.
                            for p2, d in self.props:
                                if p2 == p:
                                    default = d
                            if goal[0] is not None:
                                if start[0] is None:
                                    v = g*(goal[0]-default)+default
                                else:
                                    v = g*(goal[0]-start[0])+start[0]
                                if isinstance(goal[0], int) and p not in self.force_float:
                                    v = int(v)
                                kwargs[p] = v
                            break
                    else:
                        kwargs[p] = cs[-1][0]
                renpy.store.test=kwargs

                renpy.exports.show_layer_at(renpy.store.Transform(**kwargs), camera=True)

        def generate_changed(self, prop):
            value_org = self.state_org[prop]
            def changed(v):
                kwargs = {}
                for p, d in self.props:
                    value = self.get_property(p, False)
                    if value is not None:
                        kwargs[p] = value
                    else:
                        kwargs[p] = d
                    if p == prop:
                        default = d
                if prop not in self.force_float and (prop in self.force_int_range or ( (value_org is None and isinstance(default, int)) or isinstance(value_org, int) )):
                    if isinstance(self.get_property(prop), float) and prop in self.force_int_range:
                        if prop in self.force_plus:
                            kwargs[prop] = float(v)
                        else:
                            kwargs[prop] = float(v - self.int_range)
                    else:
                        if prop in self.force_plus:
                            kwargs[prop] = v
                        else:
                            kwargs[prop] = v - self.int_range
                else:
                    if prop in self.force_plus:
                        kwargs[prop] = round(float(v), 2)
                    else:
                        kwargs[prop] = round(v - self.float_range, 2)

                self.set_keyframe(prop, kwargs[prop])
                renpy.exports.show_layer_at(renpy.store.Transform(**kwargs), camera=True)
                renpy.restart_interaction()
            return changed

        def get_property(self, prop, default=True):
            if "master" in renpy.game.context().scene_lists.camera_transform:
                props = renpy.game.context().scene_lists.camera_transform["master"]
                value = getattr(props, prop, None)
            else:
                value = None
            if value is None and default:
                for p, v in self.props:
                    if p == prop:
                        value = v
            return value

        # def focus_changed(self, v):
        #     v=int(v)
        #     renpy.store.focus_set(v)
        #     self.set_camera_keyframe("_camera_focus", v)
        #     renpy.restart_interaction()
        #
        # def dof_changed(self, v):
        #     v=int(v)
        #     renpy.store.dof_set(v)
        #     self.set_camera_keyframe("_camera_dof", v)
        #     renpy.restart_interaction()
        #
        # def generate_layer_z_changed(self, l):
        #     def layer_z_changed(v):
        #         renpy.store.layer_move(l, int(v))
        #         self.set_layer_keyframe(l)
        #         renpy.restart_interaction()
        #     return layer_z_changed

        def put_clipboard(self):
            string = """
    camera"""
            for p, d in self.props:
                value = self.get_property(p)
                if value != d:
                    if string.find(":") < 0:
                        string += ":\n        "
                    string += "%s %s " % (p, value)
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
                self.x_range = camera_viewer.int_range
            else:
                self.x_range = camera_viewer.float_range
            if self.int_y:
                self.y_range = camera_viewer.int_range
            else:
                self.y_range = camera_viewer.float_range

            self.cx = self.x = (0.5 + camera_viewer.get_property("xpos")/(2.*self.x_range))*renpy.config.screen_width
            self.cy = self.y = (0.5 + camera_viewer.get_property("ypos")/(2.*self.y_range))*renpy.config.screen_height

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

            if camera_viewer.get_property("xpos") != int(self.cx) or camera_viewer.get_property("ypos") != int(self.cy):
                self.x = (0.5 + camera_viewer.get_property("xpos")/(2.*self.x_range))*renpy.config.screen_width
                self.y = (0.5 + camera_viewer.get_property("ypos")/(2.*self.y_range))*renpy.config.screen_height
                renpy.redraw(self, 0)

            if self.dragging:
                if self.x != x or self.y != y:
                    self.cx = 2*self.x_range*( float(x)/renpy.config.screen_width - 0.5)
                    self.cy = 2*self.y_range*( float(y)/renpy.config.screen_height - 0.5)
                    if self.int_x:
                        self.cx = int(self.cx)
                    if self.int_y:
                        self.cy = int(self.cy)
                    if self.cx != camera_viewer.get_property("xpos"):
                        camera_viewer.set_keyframe("xpos", self.cx)
                    if self.cy != camera_viewer.get_property("ypos"):
                        camera_viewer.set_keyframe("ypos", self.cy)
                    renpy.exports.show_layer_at(renpy.store.Transform(xpos=self.cx, ypos=self.cy), camera=True)
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

    ##########################################################################
    from collections import defaultdict
    loops = defaultdict(lambda:False)
    expressions = defaultdict(lambda:None)
    splines = defaultdict(lambda:False)
    all_keyframes = {}
    time = 0
    moved_time = 0
    sorted_keyframes = []
    warper = default_warper

    # def edit_expression(k):
    #     value = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=expressions[k])
    #     try:
    #         result = renpy.python.py_eval(value)(0, 0)
    #         if isinstance(result, float) or isinstance(result, int):
    #             expressions[k] = value
    #         else:
    #             raise
    #     except:
    #         renpy.notify(_("This isn't a valid expression"))
    #     renpy.restart_interaction()

    def edit_value(check_points, old, value_org, int=False):
        value = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=value_org)
        try:
            value = renpy.python.py_eval(value)
            if int:
                value = int(value)
            else:
                value = float(value)
            for i, (v, t, w) in enumerate(check_points):
                if t == old:
                    check_points[i] = (value, t, w)
                    break
        except:
            renpy.notify(_("Please type value"))
        renpy.restart_interaction()

    def edit_warper(check_points, old, value_org):
        warper = renpy.invoke_in_new_context(renpy.call_screen, "_warper_selecter", current_warper=value_org)
        if warper:
            for i, (v, t, w) in enumerate(check_points):
                if t == old:
                    check_points[i] = (v, t, warper)
                    break
        renpy.restart_interaction()

    def edit_move_keyframes(check_points, old):
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=old)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < 0:
                    return
                move_keyframe(v, old, check_points)
            except:
                renpy.notify(_("Please type value"))

    def edit_move_all_keyframes():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=moved_time)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < 0:
                    return
                move_keyframes(v, moved_time)
            except:
                renpy.notify(_("Please type value"))

    def edit_time():
        global time
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=time)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < 0:
                    return
                change_time(v)
            except:
                renpy.notify(_("Please type value"))

    def next_time():
        if not sorted_keyframes:
            change_time(0)
            return
        else:
            for i, t in enumerate(sorted_keyframes):
                if time < t:
                    change_time(sorted_keyframes[i])
                    return
            change_time(sorted_keyframes[0])

    def prev_time():
        if not sorted_keyframes:
            change_time(0)
            return
        else:
            for i, t in enumerate(sorted_keyframes):
                if time <= t:
                    change_time(sorted_keyframes[i-1])
                    break
            else:
                change_time(sorted_keyframes[-1])

    def select_default_warper():
        global warper
        v = renpy.invoke_in_new_context(renpy.call_screen, "_warper_selecter")
        if v:
            warper = v

    # @renpy.pure
    # class AddWindow(renpy.store.Action, renpy.store.DictEquality):
    #     def __init__(self):
    #         pass
    #     def __call__(self):
    #         if renpy.shown_window():
    #             renpy.scene("window")
    #         else:
    #             renpy.add_layer("window", below="screens")
    #             renpy.config.empty_window()
    #         renpy.restart_interaction()
    #     def get_selected(self):
    #         if renpy.shown_window():
    #             return True
    #         return False

    def clear_keyframes():
        all_keyframes.clear()
        sorted_keyframes[:]=[]

    def remove_keyframe(remove_time, k):
        remove_list = []
        for (v, t, w) in all_keyframes[k]:
            if t == remove_time:
                if remove_time != 0 or (remove_time == 0 and len(all_keyframes[k]) == 1):
                    remove_list.append((v, t, w))
        for c in remove_list:
            all_keyframes[k].remove(c)
            if not all_keyframes[k]:
                del all_keyframes[k]
        sort_keyframes()
        change_time(time)

    def remove_keyframes(time):
        keylist = [k for k in all_keyframes]
        for k in keylist:
            remove_keyframe(time, k)

    def sort_keyframes():
        global sorted_keyframes
        sorted_keyframes[:] = []
        for keyframes in all_keyframes.values():
            for (v, t, w) in keyframes:
                if t not in sorted_keyframes:
                    sorted_keyframes.append(t)
        sorted_keyframes.sort()

    def move_keyframes(new, old):
        global moved_time
        moved_time = round(new, 2)
        for k, v in all_keyframes.items():
            move_keyframe(new, old, v)
        renpy.restart_interaction()

    def move_keyframe(new, old, check_points):
        new = round(new, 2)
        for i, c in enumerate(check_points):
            if c[1] == old:
                (value, time, warper) = check_points.pop(i)
                for n, (v, t, w) in enumerate(check_points):
                    if new < t:
                        check_points.insert(n, (value, new, warper))
                        break
                    elif new == t:
                        # check_points[n] = (new, (value, new, w))
                        check_points.insert(n, (value, new, warper))
                        break
                else:
                    check_points.append((value, new, warper))
                if old == 0 and new != 0:
                    check_points.insert(0, (value, 0, None))
        sort_keyframes()
        renpy.restart_interaction()

    def keyframes_exist(k):
        if k not in all_keyframes:
            return False
        check_points = all_keyframes[k]
        for c in check_points:
            if c[1] == time:
                return True
        return False

    def change_time(v):
        global time
        time = round(v, 2)
        transform_viewer.play(False)
        camera_viewer.play(False)
        renpy.restart_interaction()

    def action_editor():
        global time
        if not renpy.config.developer:
            return
        transform_viewer.init()
        camera_viewer.init()
        dragged.init(isinstance(camera_viewer.get_property("xpos"), int), isinstance(camera_viewer.get_property("ypos"), int))
        loops.clear()
        # expressions.clear()
        renpy.store._first_load = True
        renpy.invoke_in_new_context(renpy.call_screen, "_action_editor")
        clear_keyframes()
        time = 0
        # camera_viewer.layer_reset()
        camera_viewer.camera_reset()

    def put_clipboard():
        string = ""
        kwargs = {k:v for k, v in all_keyframes.items() if not isinstance(k, tuple)}
        if kwargs:
            string += """
    camera:
        subpixel True """
            for p, d in camera_viewer.props:
                if p in kwargs and len(kwargs[p]) == 1:
                    string += "{} {} ".format(p, kwargs[p][0][0])
                elif d != camera_viewr.state_org[p]:
                    string += "{} {} ".format(p, camera_viewer.state_org[p])
            for p, check_points in kwargs.items():
                if len(check_points) > 1:
                    string += """
        parallel:"""
                    string += """
            {} {}""".format(p, check_points[0][0])
                    for i, check_point in enumerate(check_points[1:]):
                        string += """
            {} {} {} {}""".format(check_point[2], check_points[i+1][1]-check_points[i][1], p, check_point[0])
                    if loops[p]:
                        string += """
            repeat"""

        for layer in transform_viewer.state_org:
            for name, kwargs_org in {k: v for dic in [transform_viewer.state_org[layer], transform_viewer.state[layer]] for k, v in dic.items()}.items():
                kwargs = {k[2]:v for k, v in all_keyframes.items() if isinstance(k, tuple) and k[0] == name and k[1] == layer}
                if kwargs:
                    string += """
    show {} onlayer {}:
        subpixel True """.format(name, layer)
                    for p, d in transform_viewer.props:
                        if p in kwargs and len(kwargs[p]) == 1:
                            string += "{} {} ".format(p, kwargs[p][0][0])
                        elif d != {k2: v2 for dic in [transform_viewer.state_org[layer], transform_viewer.state[layer]] for k2, v2 in dic.items()}[name][p]:
                            string += "{} {} ".format(p, {k2: v2 for dic in [transform_viewer.state_org[layer], transform_viewer.state[layer]] for k2, v2 in dic.items()}[name][p])
                    for p, check_points in kwargs.items():
                        if len(check_points) > 1:
                            string += """
        parallel:"""
                            string += """
            {} {}""".format(p, check_points[0][0])
                            for i, check_point in enumerate(check_points[1:]):
                                string += """
            {} {} {} {}""".format(check_point[2], check_points[i+1][1]-check_points[i][1], p, check_point[0])
                            if loops[(name,layer,p)]:
                                string += """
            repeat"""

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
