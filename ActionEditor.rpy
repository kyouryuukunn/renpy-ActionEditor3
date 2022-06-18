
#変更

#修正


#既知の問題
#childのみならばparallelなくてよい
#colormatrix, transformmatrixは十分再現できない
#warper後の時間が丸められていない場合がある

#課題
#orientationが採用されたら補間方法に追加する
#複数画像をグループに纏めてプロパティー相対操作変更 (intとfloatが混ざらないように)
#removeボタンを上記とともに画像タグの右クリックメニューへ
#動画と同期できない(用本体の最適化)
#vpunch等Move transtion, ATLtranstionが動作しない
#ATLtransitionのdelayを所得できない
#ベジュ曲線

#極座標表示対応
#ATLではalignaroundはradius, angle変更時に参照されて始めて効果を持ち、単独で動かしても反映されない
#posも同時に動かせるが基準が不明(未定義?) Editorではalignaroundを動かしている間radiusかangleを動かし続けるか
#functionプロパティーでalignaroundを動かしても反映されない。最小構成では動く、最初の一回は反映されている
#グループにせず直接編集しても効果なし boxの影響?

init -1098 python:
    # Added keymap
    config.underlay.append(renpy.Keymap(
        action_editor = renpy.curry(renpy.invoke_in_new_context)(_viewers.open_action_editor),
        image_viewer = _viewers.open_image_viewer,
        sound_viewer = _viewers.open_sound_viewer,
        ))


init -1600 python in _viewers:
    from renpy.store import Solid, Fixed, Transform, persistent, Null, Matrix, config, Movie
    from renpy import config
init python in _viewers:
    from renpy.store import RotateMatrix, OffsetMatrix, ScaleMatrix, _MultiplyMatrix
    from renpy.store import InvertMatrix, ContrastMatrix, SaturationMatrix, BrightnessMatrix, HueMatrix 
    # coordinate_icon = Fixed()
    # coordinate_icon.add(Solid("#00F", xsize=50, ysize=6, anchor=(0., .5)))
    # coordinate_icon.add(Solid("#0F0", xsize=6, ysize=50, anchor=(.5, 1.)))
    # coordinate_icon.add(Transform(matrixtransform=renpy.store.Matrix.offset(0, 25, -25)*renpy.store.Matrix.rotate(90, 0, 0))(Solid("#F00", xsize=6, ysize=50, anchor=(.5, 1.))))
    # coordinate_icon = Transform(xpos=0.05, ypos=0.1)(coordinate_icon)
    #
    # stage = Fixed()
    # # step = 200
    # # max_num = 100
    # # for i in range(1, max_num):
    # #     stage.add(Solid("#000", xsize=5, ysize=step*max_num, xpos=i*50,  ypos=0, anchor=(.5, .5)))
    # #     stage.add(Solid("#000", xsize=5, ysize=step*max_num, xpos=-i*50, ypos=0, anchor=(.5, .5)))
    # #     stage.add(Solid("#000", xsize=step*max_num, ysize=5, xpos=0, ypos=i*50, anchor=(.5, .5)))
    # #     stage.add(Solid("#000", xsize=step*max_num, ysize=5, xpos=0, ypos=-i*50, anchor=(.5, .5)))
    # stage.add(Solid("#000"))
    # stage = Transform(matrixtransform=renpy.store.Matrix.offset(0, config.screen_width/2, 0)*renpy.store.Matrix.rotate(90, 0, 0))(stage)

init -1598 python in _viewers:
    from copy import deepcopy
    from math import sin, asin, cos, acos, atan, pi, sqrt
    from collections import defaultdict
    from renpy.display.image import images
    import traceback

    moved_time = 0
    loops = [defaultdict(lambda:False)]
    splines = [defaultdict(lambda:{})]
    all_keyframes = [{}]
    scene_keyframes = []


    class DuringTransitionDisplayble(renpy.Displayable):
    # create the image which is doing transition at the given time.
    # TransitionDisplayble(dissolve(old_widget, new_widget), 0, 0)


        def __init__(self, transition, old, new, st, at, **properties):
            super(DuringTransitionDisplayble, self).__init__(**properties)

            self.transition = transition(old_widget=old, new_widget=new)
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
        global image_state, image_state_org, camera_state_org, movie_cache

        sle = renpy.game.context().scene_lists
        # layer->tag->property->value
        image_state_org = []
        image_state = []
        camera_state_org = []
        image_state_org.append({})
        image_state.append({})
        camera_state_org.append({})
        movie_cache = {}
        props = sle.camera_transform["master"]
        for p in camera_props:
            camera_state_org[current_scene][p] = getattr(props, p, None)
        for gn, ps in props_groups.items():
            for p in camera_props:
                if p in ps:
                    pvs = getattr(props, gn, None)
                    if pvs is not None:
                        for gp, v in zip(ps, pvs):
                            camera_state_org[current_scene][gp] = v
                    break

        for layer in config.layers:
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
                for p in {"xpos", "ypos", "xanchor", "yanchor", "xoffset", "yoffset"}:
                    image_state_org[current_scene][layer][tag][p] = getattr(pos, p, None)
                for p in transform_props:
                    if p not in image_state_org[current_scene][layer][tag]:
                        if p == "child":
                            image_state_org[current_scene][layer][tag][p] = (image_name, None)
                        else:
                            image_state_org[current_scene][layer][tag][p] = getattr(state, p, None)
                for gn, ps in props_groups.items():
                    for p in transform_props:
                        if p in ps:
                            pvs = getattr(d, gn, None)
                            if pvs is not None:
                                for gp, v in zip(ps, pvs):
                                    image_state_org[current_scene][layer][tag][gp] = v
                            break

        # init camera, layer and images
        renpy.scene()
        for layer in config.layers:
            sle.set_layer_at_list(layer, [], camera=True)
            sle.set_layer_at_list(layer, [])


    def get_matrix_info(matrix):
        matrix_info = []
        def _get_matrix_info(origin):
            if isinstance(origin, _MultiplyMatrix):
                args = getattr(origin.right, "args", None)
                if args is None:
                    args = getattr(origin.right, "value")
                matrix_info.append((type(origin.right), args))
                _get_matrix_info(origin.left)
            else:
                args = getattr(origin, "args", None)
                if args is None:
                    args = getattr(origin, "value")
                matrix_info.append((type(origin), args))

        origin = getattr(matrix, "origin", False)
        if not origin:
            return matrix_info
        else:
            _get_matrix_info(origin)
            matrix_info.reverse()
        return matrix_info

    def get_group_property(group_name, group):
        def decimal(a):
            from decimal import Decimal, ROUND_HALF_UP
            return Decimal(str(a)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

        if group is None:
            return None

        if group_name == "matrixtransform":

            matrix_info = get_matrix_info(group)
            matrix_order = tuple(i[0] for i in matrix_info)
            matrix_args = tuple(i[1] for i in matrix_info)
            if matrix_order == (OffsetMatrix, RotateMatrix):
                ox = matrix_args[0][0]
                oy = matrix_args[0][1]
                oz = matrix_args[0][2]
                rx = matrix_args[1][0]
                ry = matrix_args[1][1]
                rz = matrix_args[1][2]
            elif matrix_order == (OffsetMatrix,):
                ox = matrix_args[0][0]
                oy = matrix_args[0][1]
                oz = matrix_args[0][2]
                rx = 0.0
                ry = 0.0
                rz = 0.0
            elif matrix_order == (RotateMatrix,):
                ox = 0.0
                oy = 0.0
                oz = 0.0
                rx = matrix_args[0][0]
                ry = matrix_args[0][1]
                rz = matrix_args[0][2]
            else:
                rx = 0.0
                ry = 0.0
                rz = 0.0
                ox = 0.0
                oy = 0.0
                oz = 0.0
            return rx, ry, rz, ox, oy, oz

        elif group_name == "matrixcolor":

            matrix_info = get_matrix_info(group)
            matrix_order = tuple(i[0] for i in matrix_info)
            matrix_args = tuple(i[1] for i in matrix_info)
            if matrix_order == (InvertMatrix, ContrastMatrix, SaturationMatrix, BrightnessMatrix, HueMatrix):
                i = matrix_args[0]
                c = matrix_args[1]
                s = matrix_args[2]
                b = matrix_args[3]
                h = matrix_args[4]
            elif matrix_order == (InvertMatrix,):
                i = matrix_args[0]
                c = 1.
                s = 1.
                b = 0.
                h = 0.
            elif matrix_order == (ContrastMatrix,):
                i = 0.
                c = matrix_args[0]
                s = 1.
                b = 0.
                h = 0.
            elif matrix_order == (SaturationMatrix,):
                i = 0.
                c = 1.
                s = matrix_args[0]
                b = 0.
                h = 0.
            elif matrix_order == (BrightnessMatrix,):
                i = 0.
                c = 1.
                s = 1.
                b = matrix_args[0]
                h = 0.
            elif matrix_order == (HueMatrix, ):
                i = 0.
                c = 1.
                s = 1.
                b = 0.
                h = matrix_args[0]
            else:
                i = 0.
                c = 1.
                s = 1.
                b = 0.
                h = 0.
            return i, c, s, b, h

        else:
            return group


    def is_force_plus(prop):
        if prop is None:
            return False
        # if is_matrix_paras(prop):
        #     prop = prop[:-1]
        return prop in force_plus


    def is_wide_range(key):
        if isinstance(key, tuple):
            _, _, prop = key
        else:
            prop = key
        if prop in force_wide_range:
            return True
        if prop in force_narrow_range:
            return False
        value = get_value(key, default=True)
        return isinstance(value, int)


    def reset(key_list, time=None):
        if time is None:
            time = current_time
        if time < scene_keyframes[current_scene][1]:
            renpy.notify(_("can't change values before the start tiem of the current scene"))
            return
        if not isinstance(key_list, list):
            key_list = [key_list]
        for key in key_list:
            if isinstance(key, tuple):
                tag, layer, prop = key
                state = get_image_state(layer)[tag]
            else:
                prop = key
                state = camera_state_org[current_scene]
            v = state[prop]
            if v is None:
                v = get_default(prop)
            #もともとNoneでNoneとデフォルトで結果が違うPropertyはリセット時にずれるが、デフォルの値で入力すると考えてキーフレーム設定した方が自然
            set_keyframe(key, v, time=time)
        change_time(time)


    def image_reset():
        key_list = [(tag, layer, prop) for layer in config.layers for tag, props in get_image_state(layer).items() for prop in props]
        reset(key_list)


    def camera_reset():
        reset([p for p in camera_state_org[current_scene]])


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
            time = round(float(time), 2)
            if time < scene_keyframes[current_scene][1]:
                renpy.notify(_("can't change values before the start tiem of the current scene"))
                return
            default = get_default(prop)
            if is_wide_range(key):
                if isinstance(get_value(key, default=True), float):
                    if not is_force_plus(prop):
                        v -= persistent._wide_range
                    elif v < 0:
                        v = 0
                    v = round(float(v), 2)
                else:
                    if not is_force_plus(prop):
                        v -= persistent._wide_range
                    elif v < 0:
                        v = 0
                    v = int(v)
            else:
                if isinstance(get_value(key, default=True), float):
                    if not is_force_plus(prop):
                        v -= persistent._narrow_range
                    elif v < 0:
                        v = 0
                    v = round(float(v), 2)
                else:
                    if not is_force_plus(prop):
                        v -= persistent._narrow_range
                    elif v < 0:
                        v = 0
                    v = int(v)

            if knot_number is None:
                default_warper_org = persistent._viewer_warper
                if key in all_keyframes[current_scene]:
                    for _, t, w in all_keyframes[current_scene][key]:
                        if t == time:
                            persistent._viewer_warper = w
                set_keyframe(key, v, time=time)
                persistent._viewer_warper = default_warper_org
            else:
                splines[current_scene][key][time][knot_number] = v
            change_time(time)
        return changed


    def to_changed_value(value, force_plus, use_wide_range):
        if use_wide_range:
            range = persistent._wide_range
        else:
            range = persistent._narrow_range
        if force_plus:
            return value
        else:
            return value + range


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
                    keyframes.insert(i, (value, time, persistent._viewer_warper))
                    break
                elif time == t:
                    keyframes[i] = ( value, time, persistent._viewer_warper)
                    break
            else:
                keyframes.append((value, time, persistent._viewer_warper))
        else:
            if time == scene_keyframes[current_scene][1]:
                all_keyframes[current_scene][key] = [(value, time, persistent._viewer_warper)]
            else:
                org = state[prop]
                if org is None:
                    org = get_default(prop)
                if prop == "child" and ((current_scene == 0 and tag in image_state[current_scene][layer])
                    or (current_scene != 0 and time > scene_keyframes[current_scene][1])):
                    org = (None, None)
                all_keyframes[current_scene][key] = [
                    (org, scene_keyframes[current_scene][1], persistent._viewer_warper),
                    (value, time, persistent._viewer_warper)]
        
        for gn, ps in props_groups.items():
            ps_set = set(ps)
            if prop in ps_set and gn != "focusing" and not recursion:
                ps_set.remove(prop)
                for p in ps_set:
                    if isinstance(key, tuple):
                        key2 = (tag, layer, p)
                    else:
                        key2 = p
                    set_keyframe(key2, get_value(key2, default=True), True, time=time)
        if not recursion:
            for s in range(current_scene+1, len(scene_keyframes)):
                for i in range(s, -1, -1):
                    if camera_keyframes_exist(i):
                        break
                for p in camera_state_org[i]:
                    if p in camera_state_org[s]:
                        middle_value = get_value(p, scene_keyframes[s][1], False, i)
                        if isinstance(middle_value, float):
                            camera_state_org[s][p] = round(middle_value, 3)
                        else:
                            camera_state_org[s][p] = middle_value


    def play(play):
        if play:
            for channel, times in sound_keyframes.items():
                time = 0
                files = []
                sorted_times = sorted(list(times.keys()))
                if sorted_times:
                    for t in sorted_times:
                        duration = t - time
                        if duration > 0:
                            files.append("<silence {}>".format(duration))
                        file = renpy.python.py_eval(times[t], locals=renpy.python.store_dicts["store.audio"])
                        files += file
                        time = t
                        for f in file:
                            time += get_file_duration(f)
                    renpy.music.play(files, channel, loop=False)
        else:
            for channel, times in sound_keyframes.items():
                if current_time in times:
                    files = renpy.python.py_eval(times[current_time], locals=renpy.python.store_dicts["store.audio"])
                    renpy.music.play(files, channel, loop=False)
        camera_check_points = []
        loop = []
        spline = []
        for s, (_, t, _) in enumerate(scene_keyframes):
            check_points = {}
            camera_is_used = False
            for prop in camera_state_org[s]:
                if not exclusive_check(prop, s):
                    continue
                if prop in all_keyframes[s]:
                    check_points[prop] = all_keyframes[s][prop]
                    camera_is_used = True
                else:
                    if prop not in not_used_by_default or camera_state_org[s][prop] is not None:
                        check_points[prop] = [(get_value(prop, default=True, scene_num=s), t, None)]
            if not camera_is_used and s > 0:
                loop.append(loop[s-1])
                spline.append(spline[s-1])
                camera_check_points.append(camera_check_points[s-1])
            else:
                loop.append({prop+"_loop": loops[s][prop] for prop in camera_state_org[s]})
                spline.append({prop+"_spline": splines[s][prop] for prop in camera_state_org[s]})
                camera_check_points.append(check_points)

        image_check_points = []
        for s, (_, t, _) in enumerate(scene_keyframes):
            check_points = {}
            for layer in config.layers:
                state = get_image_state(layer, s)
                check_points[layer] = {}
                for tag in state:
                    check_points[layer][tag] = {}
                    for prop in state[tag]:
                        if not exclusive_check((tag, layer, prop), s):
                            continue
                        if (tag, layer, prop) in all_keyframes[s]:
                            check_points[layer][tag][prop] = all_keyframes[s][(tag, layer, prop)]
                        elif prop in props_groups["focusing"] and prop in camera_check_points[s]:
                            check_points[layer][tag][prop] = camera_check_points[s][prop]
                        else:
                            if prop not in not_used_by_default or state[tag][prop] is not None:
                                check_points[layer][tag][prop] = [(get_value((tag, layer, prop), default=True, scene_num=s), t, None)]
                    if persistent._viewer_focusing and perspective_enabled(s, time=t):
                        if "blur" in check_points[layer][tag]:
                            del check_points[layer][tag]["blur"]
                    else:
                        for p in ["focusing", "dof"]:
                            if p in check_points[layer][tag]:
                                del check_points[layer][tag][p]
            image_check_points.append(check_points)

            for css in camera_check_points:
                for p in props_groups["focusing"]:
                    if p in css:
                        del css[p]
        if play:
            renpy.show("action_preview", what=Transform(function=renpy.curry(viewer_transform)(
             camera_check_points=camera_check_points, image_check_points=image_check_points,
             scene_checkpoints=deepcopy(scene_keyframes), zorder_list=zorder_list, loop=loop, spline=spline, start_time=0., end_time=get_animation_delay())))
        else:
            renpy.show("action_preview", what=Transform(function=renpy.curry(viewer_transform)(
             camera_check_points=camera_check_points, image_check_points=image_check_points,
             scene_checkpoints=deepcopy(scene_keyframes), zorder_list=zorder_list, loop=loop, spline=spline, time=current_time)))


    def viewer_transform(tran, st, at, camera_check_points, image_check_points, scene_checkpoints, zorder_list, loop, spline=None, subpixel=True, time=None, start_time=None, end_time=None):
        global current_time, playing
        if time is None:
            time = st
            if st <= end_time + return_margin+.1:
                playing = True
                if st <= end_time:
                    current_time = st + start_time
            else:
                playing = False
        else:
            playing = False
        box = renpy.display.layout.MultiBox(layout='fixed')
        for i in range(-1, -len(scene_checkpoints), -1):
            checkpoint = scene_checkpoints[i][1]
            if time >= checkpoint:
                goal = scene_checkpoints[i]
                if time - checkpoint >= get_transition_delay(goal[0]):
                    child = FixedTimeDisplayable(Transform(function=renpy.curry(
                     camera_transform)(camera_check_points=camera_check_points[i], image_check_points=image_check_points[i],
                     scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[i], spline=spline[i],
                     subpixel=subpixel, time=time, scene_num=i)), time, at)
                else:
                    old_widget = FixedTimeDisplayable(Transform(function=renpy.curry(
                     camera_transform)(camera_check_points=camera_check_points[i-1], image_check_points=image_check_points[i-1],
                     scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[i-1], spline=spline[i-1],
                     subpixel=subpixel, time=time, scene_num=i-1)), time, at)
                    new_widget = FixedTimeDisplayable(Transform(function=renpy.curry(
                     camera_transform)(camera_check_points=camera_check_points[i], image_check_points=image_check_points[i],
                     scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[i], spline=spline[i],
                     subpixel=subpixel, time=time, scene_num=i)), time, at)
                    transition = renpy.python.py_eval("renpy.store."+goal[0])
                    during_transition_displayable = DuringTransitionDisplayble(transition, old_widget, new_widget, time - checkpoint, 0)
                    child = during_transition_displayable
                break
        else:
            child = Transform(function=renpy.curry(camera_transform)(
             camera_check_points=camera_check_points[0], image_check_points=image_check_points[0],
             scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[0], spline=spline[0],
             subpixel=subpixel, time=time, scene_num=0))
        if not persistent._viewer_legacy_gui:
            if aspect_16_9():
                box.add(Transform(zoom=preview_size, xpos=(1 - preview_size)/2)(child))
                if persistent._viewer_rot:
                    for i in range(1, 3):
                        box.add(Solid("#F00", xsize=preview_size, ysize=1, xpos=(1-preview_size)/2, ypos=preview_size*i/3))
                        box.add(Solid("#F00", xsize=1, ysize=preview_size, xpos=preview_size*i/3+(1-preview_size)/2))
            else:
                box.add(Transform(zoom=preview_size)(child))
                if persistent._viewer_rot:
                    for i in range(1, 3):
                        box.add(Solid("#F00", xsize=preview_size, ysize=1, ypos=preview_size*i/3))
                        box.add(Solid("#F00", xsize=1, ysize=preview_size, xpos=preview_size*i/3))
        else:
            box.add(child)
            if persistent._viewer_rot:
                for i in range(1, 3):
                    box.add(Solid("#F00", xsize=1., ysize=1, ypos=config.screen_height*i//3))
                    box.add(Solid("#F00", xsize=1, ysize=1., xpos=config.screen_width*i//3))
        tran.set_child(box)
        return 0


    def aspect_16_9():
        return round(float(config.screen_width)/config.screen_height, 2) == 1.78


    def camera_transform(tran, st, at, camera_check_points, image_check_points, scene_checkpoints, zorder_list, loop, spline=None, subpixel=True, time=None, scene_num=0):
        image_box = renpy.display.layout.MultiBox(layout='fixed')
        for layer in image_check_points:
            for tag, zorder in zorder_list[scene_num][layer]:
                if tag in image_check_points[layer]:
                    state = get_image_state(layer, scene_num)[tag]
                    image_loop = {prop+"_loop": loops[scene_num][(tag, layer, prop)] for prop in state}
                    image_spline = {prop+"_spline": splines[scene_num][(tag, layer, prop)] for prop in state}
                    for p in props_groups["focusing"]:
                        image_loop[p+"_loop"] = loops[scene_num][p]
                        image_spline[p+"_spline"] = splines[scene_num][p]
                    image_box.add(Transform(function=renpy.curry(transform)(
                     check_points=image_check_points[layer][tag],
                     loop=image_loop, spline=image_spline,
                     subpixel=subpixel, time=time, scene_num=scene_num, scene_checkpoints=scene_checkpoints)))
        camera_box = renpy.display.layout.MultiBox(layout='fixed')
        #camera position doesn't have effect whithout box
        camera_box.add(Transform(function=renpy.curry(transform)(
         check_points=camera_check_points, loop=loop, spline=spline,
         subpixel=subpixel, time=time, camera=True, scene_num=scene_num, scene_checkpoints=scene_checkpoints))(image_box))
        tran.set_child(camera_box)
        return 0


    def transform(tran, st, at, check_points, loop, spline=None, subpixel=True, crop_relative=True, time=None, camera=False, scene_num=None, scene_checkpoints=None):
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
            tran.perspective = get_value("perspective", scene_keyframes[scene_num][1], True)

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
                    if p not in ("child", "function"):
                        if checkpoint != pre_checkpoint:
                            if goal[2].startswith("warper_generator"):
                                warper = renpy.python.py_eval(goal[2])
                            else:
                                warper = renpy.atl.warpers[goal[2]]
                            g = warper((time - pre_checkpoint) / (checkpoint - pre_checkpoint))
                        else:
                            g = 1.
                        default = get_default(p)
                        if goal[0] is not None or p in boolean_props | any_props:
                            if start[0] is None:
                                start_v = default
                            else:
                                start_v = start[0]
                            knots = []
                            if spline is not None and checkpoint in spline[p+"_spline"]:
                                knots = spline[p+"_spline"][checkpoint]
                                if knots:
                                    knots = [start_v] + knots + [goal[0]]
                            if knots:
                                v = renpy.atl.interpolate_spline(g, knots)
                            elif p in boolean_props | any_props:
                                v = renpy.atl.interpolate(g, start[0], goal[0], renpy.atl.PROPERTIES[p])
                            else:
                                v = g*(goal[0]-start_v)+start_v
                            if isinstance(goal[0], int):
                                v = int(v)
                            for gn, ps in props_groups.items():
                                if p in ps:
                                    group_cache[gn][p] = v
                                    if len(group_cache[gn]) == len(props_groups[gn]):
                                        if gn != "focusing":
                                            setattr(tran, gn, generate_groups_value[gn](**group_cache[gn]))
                                        else:
                                            focusing = group_cache["focusing"]["focusing"]
                                            dof = group_cache["focusing"]["dof"]
                                            image_zpos = 0
                                            if tran.zpos:
                                                image_zpos = tran.zpos
                                            if tran.matrixtransform:
                                                image_zpos += tran.matrixtransform.zdw
                                            camera_zpos = 0
                                            if in_editor:
                                                camera_zpos = get_value("zpos", default=True, scene_num=scene_num) - get_value("offsetZ", default=True, scene_num=scene_num)
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
                            if gn != "focusing":
                                setattr(tran, gn, generate_groups_value[gn](**group_cache[gn]))
                            else:
                                focusing = group_cache["focusing"]["focusing"]
                                dof = group_cache["focusing"]["dof"]
                                image_zpos = 0
                                if tran.zpos:
                                    image_zpos = tran.zpos
                                if tran.matrixtransform:
                                    image_zpos += tran.matrixtransform.zdw
                                camera_zpos = 0
                                if in_editor:
                                    camera_zpos = get_value("zpos", default=True, scene_num=scene_num) - get_value("offsetZ", default=True, scene_num=scene_num)
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
                    if p not in ("child", "function"):
                        setattr(tran, p, cs[fixed_index][0])

        if "child" in check_points and check_points["child"]:
            cs = check_points["child"]
            for i in range(-1, -len(cs), -1):
                checkpoint = cs[i][1]
                pre_checkpoint = cs[i-1][1]
                scene_start = cs[0][1]
                if time >= scene_start and time >= checkpoint:
                    start = cs[i-1]
                    goal = cs[i]
                    if start[0][0] is None and goal[0][0] is None:
                        tran.set_child(Null())
                        break
                    elif start[0][0] is None:
                        new_widget = get_widget(goal[0][0], time, at)
                        w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                        old_widget = Null(w, h)
                    elif goal[0][0] is None:
                        old_widget = get_widget(start[0][0], time, at)
                        w, h = renpy.render(old_widget, 0, 0, 0, 0).get_size()
                        new_widget = Null(w, h)
                    else:
                        old_widget = get_widget(start[0][0], time, at)
                        new_widget = get_widget(goal[0][0], time, at)
                    if time - checkpoint >= get_transition_delay(goal[0][1]):
                        child = new_widget
                    else:
                        transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                        during_transition_displayable = DuringTransitionDisplayble(transition, old_widget, new_widget, time-checkpoint, 0)
                        child = during_transition_displayable
                    tran.set_child(child)
                    break
            else:
                start = ((None, None), 0, None)
                goal = cs[0]
                checkpoint = goal[1]
                if goal[0][0] is None:
                    child = Null()
                else:
                    fixed_time = time-checkpoint
                    if fixed_time < 0:
                        fixed_time = 0
                    new_widget = get_widget(goal[0][0], time, at)
                    w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                    old_widget = Null(w, h)
                    if fixed_time >= get_transition_delay(goal[0][1]):
                        child = new_widget
                    else:
                        transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                        child = DuringTransitionDisplayble(transition, old_widget, new_widget, fixed_time, 0)
                tran.set_child(child)

        if "function" in check_points and check_points["function"]:
            f = check_points["function"][0][0][1]
            if f is not None:
                f(tran, time, at)
        # if not camera:
        #     showing_pool = {
        #         "scene_num":scene_num
        #         "tag":tag
        #         "pos": getattr(tran, "pos")
        #     }
        # if not camera:
        #     tran.alignaround = (0.5+time*0.1, 0.5)
        #     tran.angle = 0
        #     tran.alignaround = (0.5, 0.5)
        #     tran.angle = 315
        #     tran.radius=0.71
        #     renpy.store.test = tran.alignaround
        return 0


    def get_widget(name, time, at):
        name_tuple = tuple(name.split())
        if name_tuple in images and isinstance(images[name_tuple], Movie):
            d_org = images[name_tuple]
            file_name = d_org._play
            mask_file_name = d_org.mask

            prefix_org = ""
            if file_name.find(">") > 0:
                prefix_org = file_name[:file_name.find(">")+1]
                file_name = file_name[file_name.find(">")+1:]

            if mask_file_name:
                mask_prefix_org = ""
                if mask_file_name.find(">") > 0:
                    mask_prefix_org = file_name[:mask_file_name.find(">")+1]
                    mask_file_name = file_name[mask_file_name.find(">")+1:]

            prefix = "<from {} to {}>".format(time, time)
            if mask_file_name:
                mask_prefix = "<from {} to {}>".format(time, time)

            play = prefix + file_name
            if mask_file_name:
                mask = mask_prefix + mask_file_name
            else:
                mask = None

            if name_tuple in movie_cache:
                d = movie_cache[name_tuple]
            else:
                d = deepcopy(d_org)
                movie_cache[name_tuple] = d

            d._play = play
            d.mask = None
            d.loop = False
            # d = FixedTimeDisplayable(Movie(play=prefix+file_name, mask=None, loop=False), time, at)
            widget = d
            # raise Exception((d._play, d.mask))
        elif name_tuple in images:
            widget = FixedTimeDisplayable(images[name_tuple], time, at)
        else:
            widget = FixedTimeDisplayable(renpy.easy.displayable(name), time, at)
        return widget


    def exclusive_check(key, scene_num=None):
        if scene_num is None:
            scene_num = current_scene
        if isinstance(key, tuple):
            tag, layer, prop = key
            state = get_image_state(layer, scene_num)
            camera = False
        else:
            prop = key
            state = camera_state_org[scene_num]
            camera = True

        for set1, set2 in exclusive:
            if prop in set1 or prop in set2:
                if prop in set1:
                    one_set = set1
                    other_set = set2
                else:
                    one_set = set2
                    other_set = set1
                for p in one_set:
                    if camera:
                        key2 = p
                    else:
                        key2 = (tag, layer, p)
                    if key2 in all_keyframes[scene_num]:
                        return True
                    if key2 in state and (state[key2] is not None and state[key2] != get_default(p)):
                        return True
                for p in other_set:
                    if camera:
                        key2 = p
                    else:
                        key2 = (tag, layer, p)
                    if key2 in all_keyframes[scene_num]:
                        return False
                    if key2 in state and (state[key2] is not None and state[key2] != get_default(p)):
                        return False
                else:
                    if prop in set1:
                        return True
                    else:
                        return False
        else:
            return True


    def edit_value(function, default, use_wide_range=False, force_plus=False, time=None):
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=default)
        if v:
            try:
                v = renpy.python.py_eval(v)
                v = to_changed_value(v, force_plus, use_wide_range)
            except Exception as e:
                message = _("Please type value") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)
                return
            function(v, time=time)


    def edit_default_transition():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", message=_("Type transition"))
        if v:
            if v == "None":
                v = None
            else:
                try:
                    renpy.python.py_eval(v)
                except Exception as e:
                    message = _("Please Input Transition") + "\n" \
                    + traceback.format_exc()
                    renpy.notify(message)
                    return
            persistent._viewer_transition = v
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
            if (tag, layer, "child") in all_keyframes[current_scene]:
                cs = all_keyframes[current_scene][(tag, layer, "child")]
                for i in range(-1, -len(cs)-1, -1):
                    if time >= cs[i][1]:
                        (n, tran), t, w = cs[i]
                        break
            else:
                n = get_value((tag, layer, "child"), default=True)[0]
            if v == "None":
                v = None
            else:
                try:
                    renpy.python.py_eval(v)
                except Exception as e:
                    message = _("Please Input Transition") + "\n" \
                    + traceback.format_exc()
                    renpy.notify(message)
                    return
            set_keyframe((tag, layer, "child"), (n, v), time=time)
            change_time(time)
            return
        renpy.notify(_("Please Input Transition"))


    def edit_channel_list():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=persistent._viewer_channel_list , message=_("Please type the list of channel names(ex [['sound', 'sound2'])"))
        message1 = _("Please type the list of channel names(ex ['sound', 'sound2'])")
        try:
            v = renpy.python.py_eval(v)
        except:
            renpy.notify(message1)
            return
        if v and isinstance(v, list):
            for c in v:
                try:
                    renpy.audio.music.get_channel(c)
                except:
                    break
                if c == "audio":
                    renpy.notify(_("can't include audio channel"))
                    
            else:
                for c in v:
                    if c not in persistent._viewer_channel_list:
                        sound_keyframes[c] = {}
                for c in persistent._viewer_channel_list:
                    if c not in v:
                        del sound_keyframes[c]
                persistent._viewer_channel_list = v
                return
        renpy.notify(message1)


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
                for p in transform_props:
                    if p == "child":
                        image_state[current_scene][layer][added_tag][p] = (image_name, None)
                        if current_scene == 0 or current_time > scene_keyframes[current_scene][1]:
                            set_keyframe((added_tag, layer, p), (image_name, persistent._viewer_transition))
                    else:
                        image_state[current_scene][layer][added_tag][p] = getattr(renpy.store.default, p, None)
                change_time(current_time)
                # if persistent._viewer_legacy_gui:
                #     renpy.show_screen("_action_editor")
                # else:
                #     renpy.show_screen("_new_action_editor")
                return
        else:
            renpy.notify(_("Please type image name"))
            return


    def get_image_name_candidates():
        from itertools import combinations
        result = []
        for n, d in images.items():
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
        for n in images:
            if set(n) == set(new_image) and n[0] == new_image[0]:
                # if org is not None and set(new_image) == set(org.split()):
                #     renpy.notify(_("That is already shown"))
                #     return
                string = " ".join(n)
                set_keyframe((tag, layer, "child"), (string, persistent._viewer_transition), time=time)
                return
        else:
            if new_image and new_image[0] == "None" and org is not None:
                set_keyframe((tag, layer, "child"), (None, persistent._viewer_transition), time=time)
                return
            renpy.notify(_("Please type image name"))
            return


    def edit_function(key):
        value = get_value(key)
        if isinstance(value, tuple):
            value = value[0]
        value = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=value)
        if value:
            if value == "None":
                remove_keyframe(scene_keyframes[current_scene][1], key)
            else:
                try:
                    f = renpy.python.py_eval("renpy.store."+value)
                    if not callable(f):
                        renpy.notify(_(value + " is not callable."))
                        return
                except Exception as e:
                    message = _("Please type a valid data") + "\n" \
                    + traceback.format_exc()
                    renpy.notify(message)
                    return
                set_keyframe(key, (value, f), time=scene_keyframes[current_scene][1])
                change_time(current_time)


    def edit_any(key, time=None):
        if time is None:
            time = current_time
        value = get_value(key, time)
        if isinstance(value, str):
            value = "'" + value + "'"
        value = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=value)
        if value:
            try:
                value = renpy.python.py_eval(value)
            except Exception as e:
                message = _("Please type a valid data") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)
                return
            set_keyframe(key, value, time=time)
            change_time(current_time)


    def toggle_boolean_property(key):
        if isinstance(key, tuple):
            tag, layer, prop = key
            value_org = get_image_state(layer)[tag][prop]
        else:
            value_org = camera_state_org[current_scene][key]
        value = get_value(key, scene_keyframes[current_scene][1], True)
        #assume default is False
        if value == value_org or (not value and not value_org):
            set_keyframe(key, not value, time=scene_keyframes[current_scene][1])
        else:
            remove_keyframe(scene_keyframes[current_scene][1], key)
        change_time(current_time)


    def perspective_enabled(scene_num=None, time=None):
        if scene_num is None:
            scene_num = current_scene
        if time is None:
            time = scene_keyframes[scene_num][1]
        v = get_value("perspective", scene_keyframes[scene_num][1], True, scene_num)
        return v or (v is not False and v == 0)


    def remove_image(layer, tag):
        def remove_keyframes(layer, tag):
            for k in (k for k in all_keyframes[current_scene] if isinstance(k, tuple) and k[0] == tag and k[1] == layer):
                del all_keyframes[current_scene][k]

        renpy.hide(tag, layer)
        del image_state[current_scene][layer][tag]
        remove_keyframes(tag, layer)
        zorder_list[current_scene][layer] = [(ztag, z) for (ztag, z) in zorder_list[current_scene][layer] if ztag != tag]


    def get_default(prop):
        return property_default_value[prop]


    def get_value(key, time=None, default=False, scene_num=None):
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
        if key not in all_keyframes[scene_num]:
            v = state[prop]
            if v is not None or prop in boolean_props | any_props:
                if prop == "child":
                    return v[0], None
                else:
                    return v
            elif default:
                return get_default(prop)
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
                    if goal[2].startswith("warper_generator"):
                        warper = renpy.python.py_eval(goal[2])
                    else:
                        warper = renpy.atl.warpers[goal[2]]
                    g = warper((time - pre_checkpoint) / (checkpoint - pre_checkpoint))
                else:
                    g = 1.
                default_vault = get_default(prop)
                if goal[0] is not None or prop in boolean_props | any_props:
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
                    elif prop in boolean_props | any_props:
                        v = renpy.atl.interpolate(g, start[0], goal[0], renpy.atl.PROPERTIES[prop])
                    else:
                        v = g*(goal[0]-start_v)+start_v
                    if isinstance(goal[0], int):
                        v = int(v)
                    return v
                break
        else:
            if time >= scene_start:
                return cs[-1][0]
            else:
                return cs[0][0]


    def put_camera_clipboard():
        camera_keyframes = {}
        for k in all_keyframes[current_scene]:
            if not isinstance(k, tuple) and k != "function":
                value = get_value(k, current_time)
                if isinstance(value, float):
                    value = round(value, 3)
                elif k in any_props and isinstance(value, str):
                    value = "'" + value + "'"
                camera_keyframes[k] = [(value, 0, None)]
        camera_keyframes = set_group_keyframes(camera_keyframes)
        camera_properties = []
        for p in camera_state_org[current_scene]:
            for gn, ps in props_groups.items():
                if p in ps:
                    if gn not in camera_properties:
                        camera_properties.append(gn)
                    break
            else:
                if p not in special_props:
                    camera_properties.append(p)

        string = """
camera"""
        for p, cs in x_and_y_to_xy([(p, camera_keyframes[p]) for p in camera_properties if p in camera_keyframes]):
            if string.find(":") < 0:
                string += ":\n        "
            string += "{property} {value}".format(property=p, value=cs[0][0])
            if persistent._one_line_one_prop:
                string += "\n        "
            else:
                string += " "

        string = '\n'.join(filter(lambda x: x.strip(), string.split('\n')))
        string = "\n"+ string + "\n\n"

        try:
            from pygame import scrap, locals
            scrap.put(locals.SCRAP_TEXT, string.encode("utf-8"))
        except Exception as e:
            message = _("Can't open clipboard") + "\n" \
            + traceback.format_exc()
            renpy.notify(message)
        else:
            renpy.notify(__('Placed \n"%s"\n on clipboard') % string)


    def put_image_clipboard(tag, layer):
        image_keyframes = {}
        for k in all_keyframes[current_scene]:
            if isinstance(k, tuple) and k[0] == tag and k[1] == layer and k[2] != "function":
                value = get_value(k, current_time)
                if isinstance(value, float):
                    value = round(value, 3)
                elif k[2] in any_props and isinstance(value, str):
                    value = "'" + value + "'"
                image_keyframes[k[2]] = [(value, 0, None)]
        image_keyframes = set_group_keyframes(image_keyframes)
        if check_focusing_used() and "blur" in image_keyframes:
            del image_keyframes["blur"]
        image_properties = []
        for p in get_image_state(layer)[tag]:
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
show {imagename}""".format(imagename=child)
        if tag != child.split()[0]:
                string += " as {tagname}".format(tagname=tag)
        if layer != "master":
                string += " onlayer {layer}".format(layer=layer)
        if tag in image_state[current_scene][layer]:
            string += """:
    default"""
            if persistent._one_line_one_prop:
                string += "\n        "
            else:
                string += " "
        for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes]):
            if string.find(":") < 0:
                string += ":\n        "
            string += "{property} {value}".format(property=p, value=cs[0][0])
            if persistent._one_line_one_prop:
                string += "\n        "
            else:
                string += " "
        if check_focusing_used():
            focus = get_value("focusing", current_time, True)
            dof = get_value("dof", current_time, True)
            result = "function camera_blur({'focusing':[({}, 0, None)], 'dof':[({}, 0, None)]})".format(focus, dof)
            string += "\n        "
            string += result

        string = '\n'.join(filter(lambda x: x.strip(), string.split('\n')))
        string = "\n"+ string + "\n\n"
        try:
            from pygame import scrap, locals
            scrap.put(locals.SCRAP_TEXT, string.encode("utf-8"))
        except Exception as e:
            message = _("Can't open clipboard") + "\n" \
            + traceback.format_exc()
            renpy.notify(message)
        else:
            renpy.notify(__('Placed \n"%s"\n on clipboard') % string)


    def put_sound_clipboard():

        string = ""
        for channel, times in sound_keyframes.items():
            time = 0
            files = "[\n        " #]"
            sorted_times = sorted(list(times.keys()))
            if sorted_times:
                for t in sorted_times:
                    duration = t - time
                    if duration > 0:
                        files += "'<silence {}>',\n        ".format(duration)
                    fs = times[t]
                    files += fs[1:-1] + ",\n        "

                    file = renpy.python.py_eval(fs, locals=renpy.python.store_dicts["store.audio"])
                    time = t
                    for f in file:
                        time += get_file_duration(f)
                files = files[:-4] + "]\n"
                string += "\n    play {} {}".format(channel, files)

        string = string.replace("u'", "'", 999)
        try:
            from pygame import scrap, locals
            scrap.put(locals.SCRAP_TEXT, string.encode("utf-8"))
        except Exception as e:
            message = _("Can't open clipboard") + "\n" \
            + traceback.format_exc()
            renpy.notify(message)
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


    def edit_move_keyframe(keys, old, is_sound=False):
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=old)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < scene_keyframes[current_scene][1]:
                    return
                if not isinstance(keys, list):
                    keys = [keys]
                move_keyframe(v, old, keys, is_sound)
            except Exception as e:
                message = _("Please type value") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)


    def edit_move_all_keyframe():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=moved_time)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < scene_keyframes[current_scene][1]:
                    return
                move_all_keyframe(v, moved_time)
            except Exception as e:
                message = _("Please type value") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)


    def edit_time():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=current_time)
        if v:
            try:
                v = renpy.python.py_eval(v)
                if v < scene_keyframes[current_scene][1]:
                    return
                change_time(v)
            except Exception as e:
                message = _("Please type value") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)


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
            except Exception as e:
                message = _("Please type value") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)


    def next_time():
        if not get_sorted_keyframes(current_scene):
            change_time(scene_keyframes[current_scene][1])
            return
        else:
            for t in get_sorted_keyframes(current_scene):
                if current_time < t:
                    change_time(t)
                    return
            change_time(scene_keyframes[current_scene][1])


    def prev_time():
        if not get_sorted_keyframes(current_scene):
            change_time(scene_keyframes[current_scene][1])
            return
        else:
            for t in reversed(get_sorted_keyframes(current_scene)):
                if t < current_time and scene_keyframes[current_scene][1] <= t:
                    change_time(t)
                    return
            else:
                if current_time == scene_keyframes[current_scene][1]:
                    change_time(get_sorted_keyframes(current_scene)[-1])
                else:
                    change_time(scene_keyframes[current_scene][1])


    def add_scene():
        global current_scene
        # 途中にシーンも挟めるがスクリーンの画面で末尾に+ボタンがあるので末尾追加でないと挙動に違和感
        # 名前も連番なので、見失う
        # for i, (v, t, _) in enumerate(scene_keyframes):
        #     if t > current_time:
        #         break
        #     elif t == current_time:
        #         i += 1
        #         break
        # else:
        #     i = len(scene_keyframes)
        if scene_keyframes[-1][1] >= current_time:
            renpy.notify(_("the new scene must be later than the start time of the previous scene."))
            return
        i = len(scene_keyframes)
        current_scene = i
        scene_keyframes.insert(current_scene, (persistent._viewer_transition, current_time, None))
        image_state.insert(current_scene, {})
        image_state_org.insert(current_scene, {})
        camera_state_org.insert(current_scene, {})
        zorder_list.insert(current_scene, {})
        all_keyframes.insert(current_scene, {})
        for l in config.layers:
            image_state[current_scene][l] = {}
            image_state_org[current_scene][l] = {}
            zorder_list[current_scene][l] = []
        loops.insert(current_scene, defaultdict(lambda:False))
        splines.insert(current_scene, defaultdict(lambda:{}))
        for i in range(current_scene-1, -1, -1):
            if camera_keyframes_exist(i):
                break
        for p in camera_props:
            middle_value = get_value(p, scene_keyframes[current_scene][1], False, i)
            if isinstance(middle_value, float):
                camera_state_org[current_scene][p] = round(middle_value, 3)
            else:
                camera_state_org[current_scene][p] = middle_value
        # if persistent._viewer_legacy_gui:
        #     renpy.show_screen("_action_editor")
        # elif persistent._open_only_one_page:
        #     renpy.show_screen("_new_action_editor")
        renpy.restart_interaction()


    def camera_keyframes_exist(scene_num):
        for p in camera_state_org[scene_num]:
            if p in all_keyframes[scene_num]:
                break
        else:
            return False
        return True


    def remove_scene(scene_num):
        global current_scene
        if scene_num == 0:
            return
        if current_scene >= scene_num:
            current_scene -= 1
        del scene_keyframes[scene_num]
        del image_state[scene_num]
        del image_state_org[scene_num]
        del camera_state_org[scene_num]
        del zorder_list[scene_num]
        del all_keyframes[scene_num]
        del loops[scene_num]
        del splines[scene_num]
        for s in range(scene_num, len(scene_keyframes)):
            for i in range(s, -1, -1):
                if camera_keyframes_exist(i):
                    break
            for p in camera_state_org[i]:
                middle_value = get_value(p, scene_keyframes[s][1], False, i)
                if isinstance(middle_value, float):
                    camera_state_org[s][p] = round(middle_value, 3)
                else:
                    camera_state_org[s][p] = middle_value
        # if persistent._viewer_legacy_gui:
        #     renpy.show_screen("_action_editor")
        # elif persistent._open_only_one_page:
        #     renpy.show_screen("_new_action_editor")
        change_time(current_time)


    def move_scene(new, scene_num):
        scene_num_scene_keyframes = scene_keyframes.pop(scene_num)
        scene_num_image_state = image_state.pop(scene_num)
        scene_num_image_state_org = image_state_org.pop(scene_num)
        scene_num_camera_state_org = camera_state_org.pop(scene_num)
        scene_num_zorder_list = zorder_list.pop(scene_num)
        scene_num_all_keyframes = all_keyframes.pop(scene_num)
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
            loops.append(scene_num_loops)
            splines.append(scene_num_splines)
            new_scene_num = len(scene_keyframes)-1
        new = round(float(new), 2)
        tran, old, w = scene_keyframes[new_scene_num]
        scene_keyframes[new_scene_num] = (tran, new, w)

        for s in range(new_scene_num, len(scene_keyframes)):
            for i in range(s, -1, -1):
                if camera_keyframes_exist(i):
                    break
            for p in camera_state_org[i]:
                middle_value = get_value(p, scene_keyframes[s][1], False, i)
                if isinstance(middle_value, float):
                    camera_state_org[s][p] = round(middle_value, 3)
                else:
                    camera_state_org[s][p] = middle_value
        for k, cs in all_keyframes[new_scene_num].items():
            for i, (v, t, w) in enumerate(cs):
                cs[i] = (v, t - (old - new), w)
                if splines[new_scene_num][k]:
                    for t in splines[new_scene_num][k]:
                        knots = splines[new_scene_num][k].pop(t)
                        splines[new_scene_num][k][t - (old - new)] = knots
        
        # if persistent._viewer_legacy_gui:
        #     renpy.show_screen("_action_editor")
        # else:
        #     renpy.show_screen("_new_action_editor")
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
            except Exception as e:
                message = _("Please type value") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)


    def edit_scene_transition(scene_num):
        default, t, w = scene_keyframes[scene_num]
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=default)
        if v:
            if v == "None":
                v = None
            else:
                try:
                    renpy.python.py_eval(v)
                except Exception as e:
                    message = _("Please Input Transition") + "\n" \
                    + traceback.format_exc()
                    renpy.notify(message)
                    return
            scene_keyframes[scene_num] = (v, t, w)
            change_time(current_time)
            return
        renpy.notify(_("Please Input Transition"))


    def edit_playing_file(channel, time=None):
        if time is None:
            time = current_time
        if time not in sound_keyframes[channel] and is_playing(channel, time, time):
            renpy.notify(_("This channel is already used in this time"))
            return
        default = ""
        if time in sound_keyframes[channel]:
            default = sound_keyframes[channel][time]
        v = renpy.invoke_in_new_context(renpy.call_screen, "_sound_selector", default=default)
        if "[" not in v:  #]"
            v = "[" + v   #]"
        if "]" not in v:
            v += "]"
        try:
            for f in v[1:-1].split(","):
                if "<silence" not in f:
                    evaled = renpy.python.py_eval(f, locals=renpy.python.store_dicts["store.audio"])
                    if not renpy.loadable(evaled):
                        raise
        except Exception as e:
            message = _("Please Input filenames") + "\n" \
            + traceback.format_exc()
            renpy.notify(message)
            return
        duration = 0
        for f in renpy.python.py_eval(v, locals=renpy.python.store_dicts["store.audio"]):
            duration += get_file_duration(f)
        for t in sound_keyframes[channel].keys():
            if t <= time + duration and t > time:
                renpy.notify(_("This channel is already used in this time"))
                return
        sound_keyframes[channel][time] = v
        return


    def change_scene(scene_num):
        global current_scene, current_time
        current_scene = scene_num
        # if persistent._viewer_legacy_gui:
        #     renpy.show_screen("_action_editor")
        # elif persistent._open_only_one_page:
        #     renpy.show_screen("_new_action_editor")
        change_time(current_time)


    def select_default_warper():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_warper_selecter")
        if v:
            persistent._viewer_warper = v


    def remove_keyframe(remove_time, key, is_sound=False):
        if not isinstance(key, list):
            key = [key]
        for k in key:
            if is_sound:
                if remove_time in sound_keyframes[k]:
                    del sound_keyframes[k][remove_time]
            else:
                if k in all_keyframes[current_scene]:
                    for (v, t, w) in all_keyframes[current_scene][k][:]:
                        if (t == remove_time) and (remove_time != scene_keyframes[current_scene][1] \
                            or (remove_time == scene_keyframes[current_scene][1] and len(all_keyframes[current_scene][k]) == 1)):
                            all_keyframes[current_scene][k].remove((v, t, w))
                            if not all_keyframes[current_scene][k]:
                                del all_keyframes[current_scene][k]
                            if t in splines[current_scene][k]:
                                del splines[current_scene][k][t]
        change_time(current_time)


    def remove_all_keyframe(time):
        keylist = [k for k in all_keyframes[current_scene]]
        remove_keyframe(time, keylist)
        keylist = list(sound_keyframes.keys())
        remove_keyframe(time, keylist, True)


    def get_sorted_keyframes(scene_num):
        sorted_keyframes = []
        for keyframes in all_keyframes[scene_num].values():
            for (v, t, w) in keyframes:
                if t not in sorted_keyframes:
                    sorted_keyframes.append(t)
        for c, cs in sound_keyframes.items():
            for t in cs:
                if t not in sorted_keyframes:
                    sorted_keyframes.append(t)
        return sorted(sorted_keyframes)


    def move_all_keyframe(new, old):
        global moved_time
        if new < scene_keyframes[current_scene][1]:
            new = scene_keyframes[current_scene][1]
        moved_time = round(new, 2)
        k_list = [k for k in all_keyframes[current_scene].keys()]
        move_keyframe(new, old, k_list)
        k_list = list(sound_keyframes.keys())
        move_keyframe(new, old, k_list, True)


    def move_keyframe(new, old, keys, is_sound=False):
        if not is_sound:
            if new < scene_keyframes[current_scene][1]:
                new = scene_keyframes[current_scene][1]
        new = round(float(new), 2)
        if new == old:
            renpy.restart_interaction()
            if persistent._viewer_legacy_gui:
                return
            else:
                return False
        if not isinstance(keys, list):
            keys = [keys]
        if is_sound:
            for k in keys:
                if is_playing(k, new, old):
                    renpy.notify(_("This channel is already used in this time"))
                    if persistent._viewer_legacy_gui:
                        return
                    else:
                        return False
        for k in keys:
            if keyframes_exist(k, new, is_sound):
                if persistent._viewer_legacy_gui:
                    return
                else:
                    return False
        for k in keys:
            if is_sound:
                if old in sound_keyframes[k]:
                    files = sound_keyframes[k][old]
                    sound_keyframes[k][new] = files
                    del sound_keyframes[k][old]
            else:
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
                            cs.insert(0, (value, scene_keyframes[current_scene][1], persistent._viewer_warper))
                        if old in splines[current_scene][k]:
                            knots = splines[current_scene][k][old]
                            splines[current_scene][k][new] = knots
                            del splines[current_scene][k][old]
        renpy.restart_interaction()
        if not persistent._viewer_legacy_gui:
            return True


    def keyframes_exist(k, time=None, is_sound=False):
        if time is None:
            time = current_time

        if is_sound:
            if time in sound_keyframes[k]:
                return True
            else:
                return False
        else:
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
        for c in persistent._viewer_channel_list:
            renpy.music.stop(c, False)
        play(False)
        renpy.restart_interaction()


    def get_file_duration(filename):
        if filename.startswith("<silence "):
            return renpy.python.py_eval(filename.split()[1][:-1])
        else:
            #互換性で残っている未使用のチャンネルで再生
            #doesn't work during mute
            mute_org = renpy.store._preferences.get_mute("sfx")
            renpy.store._preferences.set_mute("sfx", False)
            renpy.music.play(filename, channel=1, fadeout=0, loop=False)
            duration = None
            while duration is None:
                renpy.audio.audio.interact()
                if renpy.music.is_playing(1) and renpy.music.get_duration(1) != 0:
                    duration = renpy.music.get_duration(1)
            renpy.store._preferences.set_mute("sfx", mute_org)
            renpy.music.stop(1)
            return duration


    def is_playing(channel, new_time, old_time):
        times = sorted(list(sound_keyframes[channel].keys()))
        if new_time in times:
            return True
        if old_time in times:
            times.remove(old_time)
            for t in times:
                if t > new_time:
                    duration = 0
                    files = renpy.python.py_eval(sound_keyframes[channel][old_time], locals=renpy.python.store_dicts["store.audio"])
                    for f in files:
                        duration += get_file_duration(f)
                    if new_time+duration >= t:
                        return True
                    break
        times.reverse()
        for t in times:
            if t < new_time:
                duration = 0
                files = renpy.python.py_eval(sound_keyframes[channel][t], locals=renpy.python.store_dicts["store.audio"])
                for f in files:
                    duration += get_file_duration(f)
                if t+duration >= new_time:
                    return True
                break
        return False


    def open_action_editor():
        global current_time, current_scene, scene_keyframes, zorder_list, sound_keyframes, all_keyframes, playing, in_editor
        if not config.developer:
            return
        playing = False
        current_time = 0.0 #current_time is always float
        current_scene = 0
        moved_time = 0
        loops = [defaultdict(lambda:False)]
        splines = [defaultdict(lambda:{})]
        sound_keyframes = {}
        all_keyframes = [{}]
        zorder_list = [{}]
        for l in config.layers:
            zorder_list[current_scene][l] = renpy.get_zorder_list(l)
        scene_keyframes = [(None, 0, None)]
        if persistent._viewer_legacy_gui is None:
            persistent._viewer_legacy_gui = default_legacy_gui
        if persistent._viewer_transition is None:
            persistent._viewer_transition = default_transition
        if persistent._viewer_warper is None:
            persistent._viewer_warper = default_warper
        if persistent._viewer_hide_window is None:
            persistent._viewer_hide_window = hide_window_in_animation
        if persistent._viewer_allow_skip is None:
            persistent._viewer_allow_skip = allow_animation_skip
        if persistent._viewer_rot is None:
            persistent._viewer_rot = default_rot
        if persistent._viewer_focusing is None:
            persistent._viewer_focusing = focusing
        if persistent._wide_range is None:
            persistent._wide_range = wide_range
        if persistent._narrow_range is None:
            persistent._narrow_range = narrow_range
        if persistent._viewers_wide_dragg_speed is None:
            persistent._viewers_wide_dragg_speed = wide_drag_speed
        if persistent._viewers_narow_dragg_speed is None:
            persistent._viewers_narow_dragg_speed = narrow_drag_speed
        if persistent._time_range is None:
            persistent._time_range = time_range
        if persistent._show_camera_icon is None:
            persistent._show_camera_icon = default_show_camera_icon
        if persistent._one_line_one_prop is None:
            persistent._one_line_one_prop = default_one_line_one_prop
        if persistent._open_only_one_page is None:
            persistent._open_only_one_page = default_open_only_one_page
        if persistent._graphic_editor_wide_range is None:
            persistent._graphic_editor_wide_range = default_graphic_editor_wide_range
        if persistent._graphic_editor_narrow_range is None:
            persistent._graphic_editor_narrow_range = default_graphic_editor_narrow_range
        if persistent._viewer_channel_list is None:
            persistent._viewer_channel_list = default_channel_list
        for c in persistent._viewer_channel_list:
            sound_keyframes[c] = {}
        for c in renpy.audio.audio.channels:
            renpy.music.stop(c)
        action_editor_init()
        in_editor = True
        camera_icon.init(True, True)
        _window = renpy.store._window
        renpy.store._window = False
        _skipping_org = renpy.store._skipping
        renpy.store._skipping = False
        change_time(0)
        if persistent._viewer_legacy_gui:
            renpy.call_screen("_action_editor")
        else:
            renpy.call_screen("_new_action_editor")
        renpy.store._skipping = _skipping_org
        renpy.store._window = _window


    def get_transition_delay(tran):
        if tran is None or tran == "None":
            return 0
        if isinstance(tran, str):
            tran = renpy.python.py_eval("renpy.store."+tran)
        delay = getattr(tran, "delay", None)
        if delay is None:
            delay = tran().delay
        #can't get delay of ATL transition
        return delay


    def get_animation_delay():
        animation_time = 0
        for s, (tran, scene_start, _) in enumerate(scene_keyframes):
            if scene_start > animation_time:
                animation_time = scene_start
            delay = get_transition_delay(tran)
            if delay + scene_start  > animation_time:
                animation_time = delay + scene_start
            for key, cs in all_keyframes[s].items():
                if isinstance(key, tuple):
                    prop = key[2]
                else:
                    prop = key
                for (v, t, w) in cs:
                    if prop == "child":
                        delay = get_transition_delay(v[1])
                        t += delay
                    if t > animation_time:
                        animation_time = t
        for channel, times in sound_keyframes.items():
            if times:
                time_list = sorted(list(times.keys()))
                start_time = time_list[-1]
                files = times[start_time]
                try:
                    for f in renpy.python.py_eval(files, locals=renpy.python.store_dicts["store.audio"]):
                        start_time += get_file_duration(f)
                except:
                    raise Exception(files)
                if start_time > animation_time:
                    animation_time = start_time

        return animation_time


    def get_scene_delay(scene_num):
        animation_time = 0
        (tran, scene_start, _) = scene_keyframes[scene_num]
        delay = get_transition_delay(tran)
        animation_time = delay + scene_start
        for key, cs in all_keyframes[scene_num].items():
            if isinstance(key, tuple):
                prop = key[2]
            else:
                prop = key
            for (v, t, w) in cs:
                if prop == "child":
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
                        if gn != "focusing":
                            r = []
                            sample = list(group_cache[gn].values())[0]
                            for i in range(len(sample)):
                                kwargs = {k:v[i][0] for k, v in group_cache[gn].items()}
                                t = sample[i][1]
                                w = sample[i][2]
                                try:
                                    r.append((generate_groups_clipboard[gn](**kwargs), t, w))
                                except:
                                    raise Exception(gn)
                        if r:
                            result[gn] = r
                    break
            else:
                result[p] = cs
        return result


    def camera_blur_amount(image_zpos, camera_zpos, dof, focusing):
        distance_from_focus = camera_zpos - image_zpos - focusing + config.perspective[1]
        if dof == 0:
            dof = 0.1
        if _camera_blur_warper.startswith("warper_generator"):
            warper = renpy.python.py_eval(_camera_blur_warper)
        else:
            warper = renpy.atl.warpers[_camera_blur_warper]
        blur_amount = _camera_blur_amount * warper(distance_from_focus/(float(dof)/2))
        if blur_amount < 0:
            blur_amount = abs(blur_amount)
        if blur_amount < 0.1:
            blur_amount = 0
        return blur_amount


    def get_image_state(layer, scene_num=None):
        if scene_num is None:
            scene_num = current_scene
        result = dict(image_state_org[scene_num][layer])
        result.update(image_state[scene_num][layer])
        return result


    def sort_props(keyframes):
        return [(p, keyframes[p]) for p in sort_order_list if p in keyframes]


    def put_prop_togetter(keyframes, layer=None, tag=None):
        #時間軸とx, yを纏める キーフレームが一つのみのものは含めない
        sorted_list = []
        for p in sort_order_list:
            if p in keyframes:
                sorted_list.append((p, keyframes[p]))
        result = []
        already_added = []
        for i, (p, cs) in enumerate(sorted_list):
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
            for (p2, cs2) in sorted_list[i+1:]:
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
        if persistent._one_line_one_prop:
            result_dict = {k:v for same_time_set in result for (k, v) in same_time_set}
            result.clear()
            for p in sort_order_list:
                if p in result_dict:
                    result.append([(p, result_dict[p])])
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


    def check_focusing_used(scene_num = None):
        if scene_num is None:
            scene_num = current_scene
        return (persistent._viewer_focusing and perspective_enabled(scene_num))


    def put_clipboard():
        string = ""
        if (persistent._viewer_hide_window and get_animation_delay() > 0
            and len(scene_keyframes) == 1) or len(scene_keyframes) > 1:
            if renpy.store._window_auto:
                window_mode = "window auto"
            else:
                window_mode = "window"
            string += """
    {} hide""".format(window_mode)
        for channel, times in sound_keyframes.items():
            time = 0
            files = "[\n        " #]"
            sorted_times = sorted(list(times.keys()))
            if sorted_times:
                for t in sorted_times:
                    duration = t - time
                    if duration > 0:
                        files += "'<silence {}>',\n        ".format(duration)
                    fs = times[t]
                    files += fs[1:-1] + ",\n        "

                    file = renpy.python.py_eval(fs, locals=renpy.python.store_dicts["store.audio"])
                    time = t
                    for f in file:
                        time += get_file_duration(f)
                files = files[:-4] + "]\n"
                string += "\n    play {} {}".format(channel, files)
        for s, (scene_tran, scene_start, _) in enumerate(scene_keyframes):
            camera_keyframes = {k:v for k, v in all_keyframes[s].items() if not isinstance(k, tuple)}
            camera_keyframes = set_group_keyframes(camera_keyframes)
            for k, v in camera_keyframes.items():
                if k in any_props:
                    formated_v = []
                    for c in v:
                        if isinstance(c[0], str):
                            formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                        else:
                            formated_v.append(c)
                    camera_keyframes[k] = formated_v
            camera_properties = []
            for p in camera_state_org[s]:
                for gn, ps in props_groups.items():
                    if p in ps:
                        if gn not in camera_properties:
                            camera_properties.append(gn)
                        break
                else:
                    if p not in special_props:
                        camera_properties.append(p)
            if s > 0:
                string += """
    scene"""
                
            if camera_keyframes:
                string += """
    camera:
        subpixel True"""
                if "crop" in camera_keyframes:
                    string += " crop_relative True"
                if persistent._one_line_one_prop:
                    string += "\n        "
                else:
                    string += " "
                #デフォルトと違っても出力しない方が以前の状態の変化に柔軟だが、
                #xposのような元がNoneやmatrixtransformのような元のマトリックスの順番が違うとアニメーションしない
                #rotateは設定されればキーフレームに入り、されてなければ問題ない
                #アニメーションしないなら出力しなくてよいのでここでは不要
                for p, cs in x_and_y_to_xy([(p, camera_keyframes[p]) for p in camera_properties if p in camera_keyframes and len(camera_keyframes[p]) == 1]):
                    string += "{property} {value}".format(property=p, value=cs[0][0])
                    if persistent._one_line_one_prop:
                        string += "\n        "
                    else:
                        string += " "
                sorted_list = put_prop_togetter(camera_keyframes)
                if len(sorted_list):
                    for same_time_set in sorted_list:
                        if len(sorted_list) > 1 or loops[s][xy_to_x(sorted_list[0][0][0])] or "function" in camera_keyframes:
                            add_tab = "    "
                            string += """
        parallel:
            """
                        else:
                            add_tab = ""
                            string += """
        """
                        for p, cs in same_time_set:
                            string += "{property} {value} ".format(property=p, value=cs[0][0])
                        cs = same_time_set[0][1]
                        for i, c in enumerate(cs[1:]):
                            if c[2].startswith("warper_generator"):
                                warper = "warp "+ c[2]
                            else:
                                warper = c[2]
                            string += """
        {tab}{warper} {duration} """.format(tab=add_tab, warper=warper, duration=cs[i+1][1]-cs[i][1])
                            for p2, cs2 in same_time_set:
                                string += "{property} {value} ".format(property=p2, value=cs2[i+1][0])
                                if cs2[i+1][1] in splines[s][xy_to_x(p2)] and splines[s][xy_to_x(p2)][cs2[i+1][1]]:
                                    for knot in splines[s][xy_to_x(p2)][cs2[i+1][1]]:
                                        string += " knot {} ".format(knot)
                        if loops[s][xy_to_x(p)]:
                            string += """
            repeat"""
                if "function" in camera_keyframes:
                    for p, cs in camera_keyframes.items():
                        if len(cs) > 1:
                            string += """
        parallel:
            """
                            break
                    else:
                        string += "\n        "
                    string += "function {} ".format(camera_keyframes["function"][0][0][0])


            for layer in image_state_org[s]:
                state = get_image_state(layer, s)
                for tag, _ in zorder_list[s][layer]:
                    image_keyframes = {k[2]:v for k, v in all_keyframes[s].items() if isinstance(k, tuple) and k[0] == tag and k[1] == layer}
                    image_keyframes = set_group_keyframes(image_keyframes)
                    for k, v in image_keyframes.items():
                        if k in any_props:
                            formated_v = []
                            for c in v:
                                if isinstance(c[0], str):
                                    formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                                else:
                                    formated_v.append(c)
                            image_keyframes[k] = formated_v
                    if check_focusing_used(s) and "blur" in image_keyframes:
                        del image_keyframes["blur"]
                    image_properties = []
                    for p in state[tag]:
                        for gn, ps in props_groups.items():
                            if p in ps:
                                if gn not in image_properties:
                                    image_properties.append(gn)
                                break
                        else:
                            if p not in special_props:
                                image_properties.append(p)
                    if image_keyframes or check_focusing_used(s) or tag in image_state[s][layer]:
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
                            string += "crop_relative True "
                        if persistent._one_line_one_prop:
                            string += "\n        "
                        for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes and len(image_keyframes[p]) == 1], layer, tag):
                                string += "{property} {value}".format(property=p, value=cs[0][0])
                                if persistent._one_line_one_prop:
                                    string += "\n        "
                                else:
                                    string += " "
                        sorted_list = put_prop_togetter(image_keyframes, layer, tag)
                        if "child" in image_keyframes:
                            if len(sorted_list) >= 1 or loops[s][(tag, layer, "child")] or check_focusing_used(s) or "function" in image_keyframes:
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
        {tab}{pause}""".format(tab=add_tab, pause=t-last_time)
                                if i == 0 and (image is not None and transition is not None):
                                    string += """
        {tab}{child}""".format(tab=add_tab, child=null)
                                if image is None:
                                    string += """
        {tab}{child}""".format(tab=add_tab, child=null)
                                else:
                                    string += """
        {tab}'{child}'""".format(tab=add_tab, child=image)
                                if transition is not None:
                                    string += " with {}".format(transition)
                                    t += get_transition_delay(transition)
                                last_time = t
                            if loops[s][(tag,layer,"child")]:
                                string += """
            repeat"""
                        if len(sorted_list):
                            for same_time_set in sorted_list:
                                if len(sorted_list) > 1 or loops[s][(tag, layer, xy_to_x(sorted_list[0][0][0]))] \
                                    or "child" in image_keyframes  or check_focusing_used(s) or "function" in image_keyframes:
                                    add_tab = "    "
                                    string += """
        parallel:
            """
                                else:
                                    add_tab = ""
                                    string += """
        """
                                for p, cs in same_time_set:
                                    string += "{property} {value} ".format(property=p, value=cs[0][0])
                                cs = same_time_set[0][1]
                                for i, c in enumerate(cs[1:]):
                                    if c[2].startswith("warper_generator"):
                                        warper = "warp "+ c[2]
                                    else:
                                        warper = c[2]
                                    string += """
        {tab}{warper} {duration} """.format(tab=add_tab, warper=warper, duration=cs[i+1][1]-cs[i][1])
                                    for p2, cs2 in same_time_set:
                                        string += "{property} {value} ".format(property=p2, value=cs2[i+1][0])
                                        if cs2[i+1][1] in splines[s][(tag, layer, xy_to_x(p2))] and splines[s][(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                            for knot in splines[s][(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                                string += " knot {} ".format(knot)
                                if loops[s][(tag,layer,xy_to_x(p))]:
                                    string += """
            repeat"""
                        if check_focusing_used(s) or "function" in image_keyframes:
                            for p, cs in image_keyframes.items():
                                if len(cs) > 1 or "child" in image_keyframes:
                                    string += """
        parallel:
            """
                                    break
                            else:
                                string += "\n        "
                            if check_focusing_used(s):
                                focusing_cs = {"focusing":[(get_default("focusing"), 0, None)], "dof":[(get_default("dof"), 0, None)]}
                                for p in props_groups["focusing"]:
                                    if p in all_keyframes[s]:
                                        focusing_cs[p] = [(v, t-scene_start, w) for (v, t, w) in all_keyframes[s][p]]
                                if loops[s]["focusing"] or loops[s]["dof"]:
                                    focusing_loop = {}
                                    focusing_loop["focusing_loop"] = loops[s]["focusing"]
                                    focusing_loop["dof_loop"] = loops[s]["dof"]
                                    focusing_func_string = "camera_blur({}, {})".format(focusing_cs, focusing_loop)
                                else:
                                    focusing_func_string = "camera_blur({})".format(focusing_cs)
                                if "function" in image_keyframes:
                                    function_string = image_keyframes["function"][0][0][0]
                                    string += "function mfn({}, {}) ".format(function_string, focusing_func_string)
                                else:
                                    string += "function {} ".format(focusing_func_string)
                            else:
                                string += "function {} ".format(image_keyframes["function"][0][0][0])
            if s != 0:
                string += """
    with {}""".format(scene_tran)
            if len(scene_keyframes) > 1:
                if s < len(scene_keyframes)-1:
                    pause_time = scene_keyframes[s+1][1] - scene_start
                elif (get_scene_delay(s) + scene_start) >= get_animation_delay():
                    pause_time = get_scene_delay(s)
                else:
                    pause_time = get_animation_delay() - scene_start
                pause_time -= get_transition_delay(scene_tran)
                pause_time = round(pause_time + 0.1, 3)
                if pause_time > 0 or s != len(scene_keyframes)-1:
                    string += """
    with Pause({})""".format(pause_time)

        if (persistent._viewer_hide_window and get_animation_delay() > 0) and len(scene_keyframes) == 1:
            string += """
    with Pause({})""".format(round(get_animation_delay()+0.1, 3))
        if (persistent._viewer_hide_window and get_animation_delay() > 0 and persistent._viewer_allow_skip) \
            or len(scene_keyframes) > 1:
            for channel, times in sound_keyframes.items():
                if times:
                    string += "\n    stop {}".format(channel)

            for i in range(-1, -len(scene_keyframes)-1, -1):
                if camera_keyframes_exist(i):
                    break
            last_camera_scene = i
            camera_keyframes = {k:v for k, v in all_keyframes[last_camera_scene].items() if not isinstance(k, tuple)}
            for p in camera_state_org[last_camera_scene]:
                if p not in camera_keyframes:
                    if camera_state_org[last_camera_scene][p] is not None and camera_state_org[last_camera_scene][p] != camera_state_org[0][p]:
                        camera_keyframes[p] = [(camera_state_org[last_camera_scene][p], scene_keyframes[last_camera_scene][1], None)]
            camera_keyframes = set_group_keyframes(camera_keyframes)
            for k, v in camera_keyframes.items():
                if k in any_props:
                    formated_v = []
                    for c in v:
                        if isinstance(c[0], str):
                            formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                        else:
                            formated_v.append(c)
                    camera_keyframes[k] = formated_v
            if [cs for cs in camera_keyframes.values() if len(cs) > 1]:
                string += """
    camera:"""
                for p, cs in camera_keyframes.items():
                    if len(cs) > 1 and loops[last_camera_scene][p]:
                        string += """
        animation"""
                        break
                first = True
                for p, cs in x_and_y_to_xy(sort_props(camera_keyframes), check_loop=True):
                    if p not in special_props:
                        if len(cs) > 1 and not loops[last_camera_scene][xy_to_x(p)]:
                            if first:
                                first = False
                                string += """
        """
                            string += "{property} {value}".format(property=p, value=cs[-1][0])
                            if persistent._one_line_one_prop:
                                string += "\n        "
                            else:
                                string += " "

                for p, cs in sort_props(camera_keyframes):
                    if p not in special_props:
                        if len(cs) > 1 and loops[last_camera_scene][p]:
                            string += """
        parallel:
            {property} {value}""".format(property=p, value=cs[0][0])
                            for i, c in enumerate(cs[1:]):
                                if c[2].startswith("warper_generator"):
                                    warper = "warp "+ c[2]
                                else:
                                    warper = c[2]
                                string += """
            {warper} {duration} {property} {value}""".format(warper=warper, duration=cs[i+1][1]-cs[i][1], property=p, value=c[0])
                                if c[1] in splines[last_camera_scene][p] and splines[last_camera_scene][p][c[1]]:
                                    for knot in splines[last_camera_scene][p][c[1]]:
                                        string += " knot {}".format(knot)
                            string += """
            repeat"""

        #         if "function" in camera_keyframes:
        #             for p, cs in sort_props(camera_keyframes):
        #                 if p not in special_props:
        #                     if len(cs) > 1 and loops[last_camera_scene][p]:
        #                         string += """
        # parallel:
        #     """
        #                         break
        #             else:
        #                 string += """
        # """
        #             string += "{} {}".format("function", camera_keyframes["function"][0][0][0])

            last_scene = len(scene_keyframes)-1
            for layer in image_state_org[last_scene]:
                state = get_image_state(layer, last_scene)
                for tag, _ in zorder_list[last_scene][layer]:
                    image_keyframes = {k[2]:v for k, v in all_keyframes[last_scene].items() if isinstance(k, tuple) and k[0] == tag and k[1] == layer}
                    image_keyframes = set_group_keyframes(image_keyframes)
                    for k, v in image_keyframes.items():
                        if k in any_props:
                            formated_v = []
                            for c in v:
                                if isinstance(c[0], str):
                                    formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                                else:
                                    formated_v.append(c)
                            image_keyframes[k] = formated_v
                    if check_focusing_used(last_scene) and "blur" in image_keyframes:
                        del image_keyframes["blur"]

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
                        string += """:
        pass"""
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
                                string += "{property} {value}".format(property=p, value=cs[-1][0])
                                if persistent._one_line_one_prop:
                                    string += "\n        "
                                else:
                                    string += " "

                    for p, cs in sort_props(image_keyframes):
                        if p not in special_props:
                            if len(cs) > 1 and loops[last_scene][(tag, layer, p)]:
                                string += """
        parallel:
            {property} {value}""".format(property=p, value=cs[0][0])
                                for i, c in enumerate(cs[1:]):
                                    if c[2].startswith("warper_generator"):
                                        warper = "warp "+ c[2]
                                    else:
                                        warper = c[2]
                                    string += """
            {warper} {duration} {property} {value}""".format(warper=warper, duration=cs[i+1][1]-cs[i][1], property=p, value=c[0])
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
            {pause}""".format(pause=t-last_time)
                            if i == 0 and (image is not None and transition is not None):
                                string += """
            {child}""".format(child=null)
                            if image is None:
                                string += """
            {child}""".format(child=null)
                            else:
                                string += """
            '{child}'""".format(child=image)
                            if transition is not None:
                                string += " with {}".format(transition)
                                t += get_transition_delay(transition)
                            last_time = t
                        string += """
            repeat"""

                    if check_focusing_used(last_scene):# or "function" in image_keyframes:
                        # if check_focusing_used(last_scene):
                        focusing_cs = {"focusing":[(get_default("focusing"), 0, None)], "dof":[(get_default("dof"), 0, None)]}
                        if "focusing" in all_keyframes[last_scene]:
                            focusing_cs["focusing"] = all_keyframes[last_scene]["focusing"]
                        if "dof" in all_keyframes[last_scene]:
                            focusing_cs["dof"] = all_keyframes[last_scene]["dof"]
                        if len(focusing_cs["focusing"]) > 1 or len(focusing_cs["dof"]) > 1:
                            for p, cs in sort_props(image_keyframes):
                                if p not in special_props:
                                    if len(cs) > 1 and loops[last_scene][(tag, layer, p)]:
                                        string += """
        parallel:
            {}"""
                                        break
                            else:
                                if "child" in image_keyframes and loops[last_scene][(tag,layer,"child")]:
                                    string += """
        parallel:
            {}"""
                                else:
                                    string += """
        """
                            if not loops[last_scene]["focusing"]:
                                focusing_cs["focusing"] = [focusing_cs["focusing"][-1]]
                            if not loops[last_scene]["dof"]:
                                focusing_cs["dof"] = [focusing_cs["dof"][-1]]
                            if loops[last_scene]["focusing"] or loops[last_scene]["dof"]:
                                focusing_loop = {}
                                focusing_loop["focusing_loop"] = loops[last_scene]["focusing"]
                                focusing_loop["dof_loop"] = loops[last_scene]["dof"]
                                focusing_func_string = "camera_blur({}, {})".format(focusing_cs, focusing_loop)
                            else:
                                focusing_func_string = "camera_blur({}, {})".format(focusing_cs)
                            # if "function" in image_keyframes:
                            #     function_string = image_keyframes["function"][0][0][0]
                            #     string += "{} mfn({}, {}) ".format("function", function_string, focusing_func_string)
                            # else:
                            string += "function {} ".format(focusing_func_string)
                        # else:
                        #     string += "{} {} ".format("function", image_keyframes["function"][0][0][0])

        if (persistent._viewer_hide_window and get_animation_delay() > 0 and len(scene_keyframes) == 1) \
            or len(scene_keyframes) > 1:
            string += """
    {} show""".format(window_mode)
        string = '\n'.join(filter(lambda x: x.strip(), string.split('\n')))
        string = "\n"+ string + "\n\n"

        if string:
            string = string.replace("u'", "'", 999)
            try:
                from pygame import scrap, locals
                scrap.put(locals.SCRAP_TEXT, string.encode("utf-8"))
            except Exception as e:
                message = _("Can't open clip board") + "\n" \
                + traceback.format_exc()
                renpy.notify(message)
            else:
                #syntax hilight error in vim
                renpy.notify("Placed\n{}\n\non clipboard".format(string).replace("{", "{{").replace("[", "[["))  #]"
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
        return renpy.curry(_viewers.transform)(check_points=check_points, loop=loop, subpixel=None, crop_relative=None)

    
    def warper_generator(checkpoints):
        #checkpoints = [(x, y, k), ... (1, 1, k)]
        checkpoints = [(0, 0, None)] + checkpoints

        def f(x, x_0, y_0, x_1, y_1, k):
            if k <= 0:
                return y_1
            elif k == 0.5:
                return ((y_1 - y_0) / (x_1 - x_0)) * (x - x_0) + y_0
            elif k >= 1:
                return 0.
            else:
                s = -k**2 / (1 - 2*k)
                t = (k**2 - 2*k + 1) / (1 - 2*k)
                u = -k**2 * (k - 1)**2 / (2*k - 1)**2
                x = (x - x_0) / (x_1 - x_0)

                y = (u / (x - s) + t) * (y_1 - y_0) + y_0
                return y

        def warper(x):
            if x >= 1:
                return 1.
            elif x <= 0:
                return 0.
            for i, (x_1, y_1, k) in enumerate(checkpoints):
                if x_1 > x:
                    x_0, y_0, _ = checkpoints[i-1]
                    return f(x, x_0, y_0, x_1, y_1, k)
        return warper
