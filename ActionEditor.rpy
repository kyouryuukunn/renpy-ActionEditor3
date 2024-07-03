
#既知の問題
#cameraではset_childを使用していないのでat節の再現ができない

#課題
#childのみならばparallelなくてよい
#動画およびat節で指定されたアニメーションtransformと同期できない(要本体の最適化)
#vpunch等Move transtion, ATLtranstionが動作しない
#ATLtransitionのdelayを所得できない

#極座標表示対応
#ATLではaroundはradius, angle変更時に参照されて始めて効果を持ち、単独で動かしても反映されない
#aroundの動作をEditorで再現するには、同時刻にradiusかangleが明示的に操作されているかチェックしなければいけない
#時間ベースで考えるとループが面倒

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

    def check_version(version_date):
        if renpy.version_tuple[3] >= version_date:
            return True
        else:
            return False

init python in _viewers:
    from renpy.store import RotateMatrix, OffsetMatrix, ScaleMatrix, _MultiplyMatrix
    from renpy.store import InvertMatrix, ContrastMatrix, SaturationMatrix, BrightnessMatrix, HueMatrix 

    def action_editor_version():
        return "231223_1"

    def check_new_position_type(v):
        if not check_version(24010100):
            return False
        elif isinstance(v, renpy.atl.position):
            return True
        else:
            return False

    if check_version(23032500):
        euler_slerp = renpy.display.quaternion.euler_slerp
    elif check_version(23030700):
        euler_slerp = renpy.display.accelerator.quaternion
    else:
        euler_slerp = None

    def get_layers():
        r = []
        for l in config.layers:
            if l not in not_included_layer:
                r.append(l)
        return r

    #z -> y -> x order roate
    def rotate_matrix2(_, x, y, z):
        from math import sin, cos, pi

        sinx = sin(pi*x/180)
        cosx = cos(pi*x/180)
        siny = sin(pi*y/180)
        cosy = cos(pi*y/180)
        sinz = sin(pi*z/180)
        cosz = cos(pi*z/180)

        rv = Matrix(None)

        rv.xdx = cosy*cosz
        rv.xdy = -cosy*sinz
        rv.xdz = siny

        rv.ydx = cosx*sinz + sinx*siny*cosz
        rv.ydy = cosx*cosz - sinx*siny*sinz
        rv.ydz = -sinx*cosy

        rv.zdx = sinx*sinz - cosx*siny*cosz
        rv.zdy = sinx*cosz + cosx*siny*sinz
        rv.zdz = cosx*cosy

        rv.wdw = 1

        return rv

    #Rzyx(a, b, c)をRxyz(x, y, z)に変換
    def zyx_to_xyz(a, b, c):
        from math import sin, cos, pi, sqrt, acos, asin

        sina = sin(pi*a/180)
        cosa = cos(pi*a/180)
        sinb = sin(pi*b/180)
        cosb = cos(pi*b/180)
        sinc = sin(pi*c/180)
        cosc = cos(pi*c/180)

        siny = min(1, max(-sina * sinc + cosa * sinb * cosc, -1))
        cosy = sqrt(1 - siny**2)
        if cosy != 0:
            cosx = min(1, max(cosa * cosb / cosy, -1))
            cosz = min(1, max(cosb * cosc / cosy, -1))
        else:
            cosx = 1
            cosz = 1

        x = acos(cosx) * 180 /pi
        y = asin(siny) * 180 /pi
        z = acos(cosz) * 180 /pi

        #assume cosy > 0
        if sina * cosc + cosa * sinb * sinc < 0:
            x = 360 - x

        if cosa * sinc + sina * sinb * cosc < 0:
            z = 360 - z

        return (x, y, z)

    class RotateMatrix2(renpy.store.TransformMatrix):
        nargs = 3
        function = rotate_matrix2


init -1598 python in _viewers:
    from copy import deepcopy
    from math import sqrt
    from collections import defaultdict
    from renpy.display.image import images
    from traceback import format_exc
    debug = False

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
            self.fixed_st = st
            self.fixed_at = at
        

        #単純にst, atを上書きしただけでは動作しない accelerator.pyx等とatl.pyを確認する
        #https://lemmasoft.renai.us/forums/viewtopic.php?f=8&t=66013&p=557882#p557882
        #renpy.display.render.redraw, kill_cache効果なし
        #st, atの値を固定にしても0sからの状態からスタートするので最初からst, atを見ていない
        #cacheの問題ではない
        #renderは内部的に増す分で作業しているようで、0から始めないと動作しない
        def render(self, width, height, st, at):

            self.d.render(width, height, 0, 0)
            return self.d.render(width, height, self.fixed_st, self.fixed_at)


    class RenderToDisplayable(renpy.Displayable):


        def __init__(self, render, **properties):
            super(RenderToDisplayable, self).__init__(**properties)

            self.render = render
        

        def render(self, width, height, st, at):
            #st, at is 0 allways?
            return self.render


    def action_editor_init():
        global image_state, image_state_org, camera_state_org, movie_cache, third_view_child
        from renpy.display.core import absolute

        sle = renpy.game.context().scene_lists
        # layer->tag->property->value
        image_state_org = []
        image_state = []
        camera_state_org = []
        image_state_org.append({})
        image_state.append({})
        camera_state_org.append({})
        movie_cache = {}
        third_view_child = {}


        for layer in get_layers():
            d = sle.camera_transform[layer]

            # child = getattr(d, "child", None)
            # child = getattr(child, "child", None)
            # if child is not None:
            #     renpy.store._viewers.at_clauses_flag = True

            child = getattr(d, "child", None)
            at_list = []
            while child is not None and type(child) is not renpy.display.layout.MultiBox:
                trans = get_transform_name(child)
                if trans is not None:
                    at_list.append(trans)
                child = getattr(child, "child", None)
            at_list.reverse()
            camera_state_org[current_scene][layer] = {}
            camera_state_org[current_scene][layer]["at_list"] = at_list

            #cameraはget_placementを使用すると座標が所得できない
            # if d is not None:
            #     pos = renpy.get_placement(d)
            pos = d
            state = getattr(d, "state", None)
            for p in {"xpos", "ypos", "xanchor", "yanchor"}:
                v = getattr(pos, p, None)
                if check_new_position_type(v):
                    if v.absolute == 0:
                        v = float(v.relative)
                    elif v.relative == 0:
                        v = int(v.absolute)
                    camera_state_org[current_scene][layer][p] = v
                else:
                    if isinstance(v, absolute):
                        v = round(v)
                    camera_state_org[current_scene][layer][p] = v
            for p in {"xoffset", "yoffset"}:
                camera_state_org[current_scene][layer][p] = getattr(pos, p, None)
            for p in camera_props:
                if p not in camera_state_org[current_scene][layer]:
                    if p in ("matrixtransform", "matrixcolor"):
                        for prop, v in load_matrix(p, getattr(state, p, None)):
                            if is_force_float(p) and isinstance(v, int):
                                v = float(v)
                            camera_state_org[current_scene][layer][prop] = v
                    else:
                        v = getattr(state, p, None)
                        if isinstance(v, absolute):
                            v = round(v)
                        if is_force_float(p) and isinstance(v, int):
                            v = float(v)
                        camera_state_org[current_scene][layer][p] = v
            for gn, ps in props_groups.items():
                for p in camera_props:
                    if p in ps:
                        pvs = getattr(state, gn, None)
                        if pvs is not None:
                            for gp, v in zip(ps, pvs):
                                if is_force_float(gp) and isinstance(v, int):
                                    v = float(v)
                                camera_state_org[current_scene][layer][gp] = v
                        break

        for layer in get_layers():
            image_state_org[current_scene][layer] = {}
            image_state[current_scene][layer] = {}
            for image in sle.layers[layer]:

                if not image[0]:
                    continue
                if isinstance(d, renpy.display.screen.ScreenDisplayable):
                    continue

                tag = image[0]
                d = sle.get_displayable_by_tag(layer, tag)
                image_name_tuple = getattr(d, "name", None)
                child = d
                while image_name_tuple is None:
                    if child is None:
                        break
                    child = getattr(child, "child", None)
                    image_name_tuple = getattr(child, "name", None)
                child = d
                while image_name_tuple is None:
                    if child is None:
                        break
                    child = getattr(child, "raw_child", None)
                    image_name_tuple = getattr(child, "name", None)
                if image_name_tuple is None:
                    continue

                name = " ".join(image.name)
                try:
                    image_name = " ".join(image_name_tuple)
                except:
                    if debug:
                        raise Exception(image_name_tuple, layer, tag)
                    continue
                image_state_org[current_scene][layer][tag] = {}

                child = getattr(d, "child", None)
                at_list = []
                while child is not None:
                    trans = get_transform_name(child)
                    if trans is not None:
                        at_list.append(trans)
                    child = getattr(child, "child", None)
                at_list.reverse()
                image_state_org[current_scene][layer][tag]["at_list"] = at_list

                pos = renpy.get_placement(d)
                state = getattr(d, "state", None)
                for p in {"xpos", "ypos", "xanchor", "yanchor", "xoffset", "yoffset"}:
                    v = getattr(pos, p, None)
                    if check_new_position_type(v):
                        if v.absolute == 0:
                            v = float(v.relative)
                        elif v.relative == 0:
                            v = int(v.absolute)
                        image_state_org[current_scene][layer][tag][p] = v
                    else:
                        if isinstance(v, absolute):
                            v = round(v)
                        image_state_org[current_scene][layer][tag][p] = v
                for p in {"xoffset", "yoffset"}:
                    image_state_org[current_scene][layer][tag][p] = getattr(pos, p, None)
                for p in transform_props:
                    if p not in image_state_org[current_scene][layer][tag]:
                        if p == "child":
                            image_state_org[current_scene][layer][tag][p] = (image_name, None)
                        elif p in ("matrixtransform", "matrixcolor"):
                            for prop, v in load_matrix(p, getattr(state, p, None)):
                                if is_force_float(prop) and isinstance(v, int):
                                    v = float(v)
                                image_state_org[current_scene][layer][tag][prop] = v
                        else:
                            v = getattr(state, p, None)
                            if isinstance(v, absolute):
                                v = round(v)
                            if is_force_float(p) and isinstance(v, int):
                                v = float(v)
                            image_state_org[current_scene][layer][tag][p] = v
                for gn, ps in props_groups.items():
                    for p in transform_props:
                        if p in ps:
                            pvs = getattr(state, gn, None)
                            if pvs is not None:
                                for gp, v in zip(ps, pvs):
                                    if is_force_float(gp) and isinstance(v, int):
                                        v = float(v)
                                    image_state_org[current_scene][layer][tag][gp] = v
                            break

        # init camera, layer and images
        for layer in get_layers():
            renpy.scene(layer)
            sle.set_layer_at_list(layer, [], camera=True)
            sle.set_layer_at_list(layer, [])


    def get_transform_name(obj):
        atl = getattr(obj, "atl", None)
        if atl is None:
            return None

        for name, _, _ in renpy.dump.transforms:
            transform = getattr(renpy.store, name, None)
            if transform is not None:
                #定義場所が同じなら同じと判定
                #リロードで再定義されるのでisでは判定できない
                if transform.atl.loc == atl.loc:
                    return (name, obj.context.context)
        else:
            return None


    def apply_at_list(child, at_list):
        if not at_list:
            return child
        for name, kwargs in at_list:
            child = getattr(renpy.store, name)(child=child, **kwargs)
        #この方法では位置プロパティーは継承できない
        return child


    def get_at_list_props(at_list, prop, st, at):
        if not at_list:
            return None
        at_list_d = []
        for name, kwargs in at_list:
            at_list_d.append(getattr(renpy.store, name)(**kwargs))

        # rv = None
        # for i in at_list_d:
        #     v = getattr(i, prop, None)
        #     if v is not None:
        #         rv = v

        rv = at_list_d[0]()
        for i in at_list_d[1:]:
            rv = i(rv)
        rv = getattr(renpy.get_placement(rv), prop, None)

        return rv


    # def expand_at_list(at_list):
    #     rv = ""
    #     for name, kwargs in at_list:
    #         if kwargs:
    #             para = ""
    #             for k, v in kwargs.items():
    #                 para += "{}={}, ".format(k, v)
    #             else:
    #                 para = para[:-2]
    #             rv += "{}({}), ".format(name, para)
    #         else:
    #             rv += "{}, ".format(name)
    #     else:
    #         rv = rv[:-2]
    #     return rv


    def check_props_group(key, scene_num=None):
        tag, layer, prop = key
        #tag = (None, "layer") express camera
        if prop.count("_") == 3 and prop.split("_")[0] in ("matrixtransform", "matrixcolor"):
            if scene_num is None:
                scene_num = current_scene
            if tag is None:
                state = camera_state_org[scene_num][layer]
            else:
                state = get_image_state(layer, scene_num)[tag]
            gn = prop.split("_")[0]

            matrixargs = []
            for p in state:
                if p.count("_") == 3:
                    sign, _, _, _ = p.split("_")
                    if sign == gn:
                        matrixargs.append(p)
            matrixargs.sort()
            return gn, matrixargs

        for gn, ps in props_groups.items():
            if prop in ps:
                return gn, ps
        else:
            return None


    def load_matrix(matrix, value):
        if matrix == "matrixtransform":
            if value is None:
                return default_matrixtransform
            else:
                rv = []
                for i, (type, args) in enumerate(get_matrix_info(value)):
                    if isinstance(type, ScaleMatrix):
                        for j, x in enumerate(("X", "Y", "Z")):
                            rv.append(("matrixtransform_{}_{}_{}{}".format(i+1, j+1, "scale", x), args[j]))
                    elif isinstance(type, OffsetMatrix):
                        for j, x in enumerate(("X", "Y", "Z")):
                            rv.append(("matrixtransform_{}_{}_{}{}".format(i+1, j+1, "offset", x), args[j]))
                    elif isinstance(type, RotateMatrix):
                        for j, x in enumerate(("X", "Y", "Z")):
                            rv.append(("matrixtransform_{}_{}_{}{}".format(i+1, j+1, "rotate", x), args[j]))
                    # else:
                    #     renpy.notify(_("ActionEditor doesn't support ") + str(type))
                return rv
        else:
            if value is None:
                return default_matrixcolor
            else:
                rv = []
                for i, (type, args) in enumerate(get_matrix_info(value)):
                    if isinstance(type, InvertMatrix):
                        rv.append(("matrixcolor_{}_{}_{}".format(i+1, 1, "invert"), args))
                    elif isinstance(type, ContrastMatrix):
                        rv.append(("matrixcolor_{}_{}_{}".format(i+1, 1, "contrast"), args))
                    elif isinstance(type, SaturationMatrix):
                        rv.append(("matrixcolor_{}_{}_{}".format(i+1, 1, "saturate"), args))
                    elif isinstance(type, BrightnessMatrix):
                        rv.append(("matrixcolor_{}_{}_{}".format(i+1, 1, "bright"), args))
                    elif isinstance(type, HueMatrix):
                        rv.append(("matrixcolor_{}_{}_{}".format(i+1, 1, "hue"), args))
                    # else:
                    #     renpy.notify(_("ActionEditor doesn't support ") + str(type))
                return rv


    def get_matrix_info(matrix):
        matrix_info = []
        def _get_matrix_info(origin):
            if isinstance(origin, _MultiplyMatrix):
                args = getattr(origin.right, "args", None)
                if args is None:
                    args = getattr(origin.right, "value", None)
                if args is None:
                    args = getattr(origin.right, "color")
                matrix_info.append((origin.right, args))
                _get_matrix_info(origin.left)
            else:
                args = getattr(origin, "args", None)
                if args is None:
                    args = getattr(origin, "value", None)
                if args is None:
                    args = getattr(origin, "color")
                matrix_info.append((origin, args))

        origin = getattr(matrix, "origin", False)
        if not origin:
            return matrix_info
        else:
            _get_matrix_info(origin)
            matrix_info.reverse()
        return matrix_info

    def is_force_float(prop):
        if prop.count("_") == 3:
            sign, _, _, prop2 = prop.split("_")
            if sign in ("matrixtransform", "matrixcolor"):
                prop = prop2
        return prop in force_float


    def is_force_plus(prop):
        if prop is None:
            return False
        if prop.count("_") == 3:
            sign, _, _, prop2 = prop.split("_")
            if sign in ("matrixtransform", "matrixcolor"):
                prop = prop2
        return prop in force_plus


    def is_wide_range(key, scene_num=None):
        if scene_num is None:
            scene_num = current_scene
        tag, layer, prop = key
        if prop.count("_") == 3:
            sign, _, _, prop2 = prop.split("_")
            if sign in ("matrixtransform", "matrixcolor"):
                if prop2 in force_wide_range:
                    return True
                if prop2 in force_narrow_range:
                    return False
        if prop in force_wide_range:
            return True
        if prop in force_narrow_range:
            return False
        if key in all_keyframes[current_scene]:
            v = all_keyframes[current_scene][key][-1][0]
        else:
            if tag is None:
                state = camera_state_org[current_scene][layer]
            else:
                state = get_image_state(layer)[tag]
            if state[prop] is not None:
                v = state[prop]
            else:
                v = get_default(prop)
        if isinstance(v, int) or (check_new_position_type(v) and v.relative == 0):
            return True
        elif isinstance(v, float) or (check_new_position_type(v) and v.absolute == 0):
            return False
        else:
            return False


    def reset(key_list, time=None):
        if time is None:
            time = current_time
        if time < scene_keyframes[current_scene][1]:
            renpy.notify(_("can't change values before the start tiem of the current scene"))
            return
        if not isinstance(key_list, list):
            key_list = [key_list]
        for key in key_list:
            tag, layer, prop = key
            if tag is None:
                state = camera_state_org[current_scene][layer]
            else:
                state = get_image_state(layer)[tag]
            v = state[prop]
            if v is None:
                v = get_default(prop)
            #もともとNoneでNoneとデフォルトで結果が違うPropertyはリセット時にずれるが、デフォルの値で入力すると考えてキーフレーム設定した方が自然
            set_keyframe(key, v, time=time)
        change_time(time)


    def image_reset():
        key_list = [(tag, layer, prop) for layer in get_layers() for tag, props in get_image_state(layer).items() for prop in props]
        reset(key_list)


    def camera_reset():
        key_list = [(None, layer, prop) for layer in get_layers() for prop in camera_state_org[current_scene][layer].keys()]
        reset(key_list)


    def generate_changed(key):
        tag, layer, prop = key
        if tag is None:
            state = camera_state_org[current_scene][layer]
        else:
            state = get_image_state(layer)[tag]
        def changed(v, time=None, knot_number=None):
            if not exclusive_check(key):
                return
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
                elif isinstance(get_value(key, default=True), int):
                    if not is_force_plus(prop):
                        v -= persistent._wide_range
                    elif v < 0:
                        v = 0
                    v = int(v)
                elif check_new_position_type(get_value(key, default=True)):
                    if not is_force_plus(prop):
                        v = renpy.atl.position.from_any(v) - renpy.atl.position.from_any(persistent._wide_range)
                    # elif v < 0:
                    #     v = 0
            else:
                if isinstance(get_value(key, default=True), float):
                    if not is_force_plus(prop):
                        v -= persistent._narrow_range
                    elif v < 0:
                        v = 0
                    v = round(float(v), 2)
                elif isinstance(get_value(key, default=True), int):
                    if not is_force_plus(prop):
                        v -= persistent._narrow_range
                    elif v < 0:
                        v = 0
                    v = int(v)
                elif check_new_position_type(get_value(key, default=True)):
                    if not is_force_plus(prop):
                        v = renpy.atl.position.from_any(v) - renpy.atl.position.from_any(persistent._narrow_range)
                    # elif v < 0:
                    #     v = 0

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
                update_gn_spline(key, time)
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
            if check_new_position_type(value):
                return value + renpy.atl.position(range)
            else:
                return value + range


    def set_keyframe(key, value, recursion=False, time=None):
        tag, layer, prop = key
        if tag is None:
            state = camera_state_org[current_scene][layer]
        else:
            state = get_image_state(layer)[tag]
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
        
        if not recursion:
            check_result = check_props_group(key)
            if check_result is not None:
                gn, ps = check_result
                if gn != "focusing":
                    ps_set = set(ps)
                    ps_set.remove(prop)
                    for p in ps_set:
                        key2 = (tag, layer, p)
                        set_keyframe(key2, get_value(key2, default=True), True, time=time)
        if not recursion:
            for s in range(current_scene+1, len(scene_keyframes)):
                for layer in get_layers():
                    for i in range(s, -1, -1):
                        if camera_keyframes_exist(i, layer):
                            break
                    for p in camera_state_org[i][layer]:
                        if p in camera_state_org[s][layer]:
                            middle_value = get_value((None, layer, p), scene_keyframes[s][1], False, i)
                            if isinstance(middle_value, float):
                                camera_state_org[s][layer][p] = round(middle_value, 2)
                            else:
                                camera_state_org[s][layer][p] = middle_value


    def generate_matrix_strings(args, matrix, ps, side_view=False):
        rv = ""
        if matrix == "matrixtransform":
            for i in range(0, len(ps), 3):
                _, _, _, prop = ps[i].split("_")
                if prop.startswith("offset"):
                    rv += "OffsetMatrix({}, {}, {})*"
                elif prop.startswith("rotate"):
                    if side_view:
                        rv += "_viewers.RotateMatrix2({}, {}, {})*"
                    else:
                        rv += "RotateMatrix({}, {}, {})*"
                elif prop.startswith("scale"):
                    rv += "ScaleMatrix({}, {}, {})*"
            rv = rv[:-1].format(*args)
        else:
            for p in ps:
                _, _, _, prop = p.split("_")
                if prop == "invert":
                    rv += "InvertMatrix({})*"
                elif prop == "contrast":
                    rv += "ContrastMatrix({})*"
                elif prop == "saturate":
                    rv += "SaturationMatrix({})*"
                elif prop == "bright":
                    rv += "BrightnessMatrix({})*"
                elif prop == "hue":
                    rv += "HueMatrix({})*"
            rv = rv[:-1].format(*args)
        return rv


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

        for layer in get_layers():
            camera_check_points = []
            viewer_check_points = []
            loop = []
            spline = []
            for s, (_, t, _) in enumerate(scene_keyframes):
                check_points = {}
                vcheck_points = {}
                camera_is_used = False
                props_use_default = []
                check_points = {}
                vcheck_points = {}
                at_list = camera_state_org[0][layer].get("at_list")
                check_points["at_list"] = [(at_list, 0, None)]

                for prop in camera_state_org[s][layer]:
                    if prop in ("xpos", "ypos"):
                        for p in ("xaround", "yaround", "radius", "angle"):
                            if (None, layer, p) in all_keyframes[s]:
                                skip = True
                                break
                        else:
                            skip = False
                        if skip:
                            continue
                    if prop in ("xaround", "yaround", "radius", "angle"):
                        for p in ("xpos", "ypos"):
                            if (None, layer, p) in all_keyframes[s]:
                                skip = True
                                break
                        else:
                            for p in ("xaround", "yaround", "radius", "angle"):
                                if (None, layer, p) in all_keyframes[s]:
                                    skip = False
                                    break
                            else:
                                skip = True
                        if skip:
                            continue

                    if (None, layer, prop) in all_keyframes[s]:
                        check_points[prop] = all_keyframes[s][(None, layer, prop)]
                        camera_is_used = True
                    else:
                        if camera_state_org[s][layer][prop] is not None:
                            check_points[prop] = [(get_value((None, layer, prop), default=False, scene_num=s), t, None)]
                        elif prop not in not_used_by_default:
                            check_points[prop] = [(get_value((None, layer, prop), default=True, scene_num=s), t, None)]
                            props_use_default.append(prop)

                check_points["props_use_default"] = [(props_use_default, t, None)]
                #focusing以外のグループプロパティーはここで纏める
                included_gp = {}
                for p in check_points:
                    check_result = check_props_group((None, layer, p), s)
                    if check_result is not None:
                        gn, ps = check_result
                        if gn != "focusing" and gn not in included_gp:
                            args = []
                            for prop in ps:
                                args.append(check_points[prop])
                            group_cs = []
                            for cs in zip(*args):
                                v = tuple(c[0] for c in cs)
                                if gn in ("matrixtransform", "matrixcolor"):
                                    v = generate_matrix_strings(v, gn, ps)
                                    v = renpy.python.py_eval(v)
                                group_cs.append((v, cs[0][1], cs[0][2]))
                            included_gp[gn] = (ps, group_cs)

                            #viewer上ではmatrixtransformは符号と順番が反転する。回転順も反転するためz-y-x順の回転行列がないと対応不可
                            if gn == "matrixtransform" and persistent._viewer_sideview:
                                viewer_group_cs = []
                                #ScaleMatrixのみ逆数をとる
                                scale_ps = []
                                for i, prop in enumerate(ps):
                                    _, _, _, p_name = prop.split("_")
                                    if p_name.startswith("scale"):
                                        scale_ps.append(i)
                                for cs in zip(*args):
                                    org_v = tuple(c[0] for c in cs)
                                    viewer_v = []
                                    for i, e in enumerate(org_v):
                                        if i in scale_ps:
                                            if e == 0:
                                                viewer_v.append(1000.) #inf
                                            else:
                                                viewer_v.append(1.0/e)
                                        else:
                                            viewer_v.append(-e)
                                    #matrixの順番を反転 marixの引数が3個単位と前提
                                    viewer_ps = []
                                    rviewer_v = []
                                    start_index = range(0, len(ps), 3)
                                    start_index.reverse()
                                    for i in start_index:
                                        viewer_ps.extend((ps[i], ps[i+1], ps[i+2]))
                                        rviewer_v.extend((viewer_v[i], viewer_v[i+1], viewer_v[i+2]))

                                    viewer_v = generate_matrix_strings(tuple(rviewer_v), gn, viewer_ps, True)
                                    viewer_v = renpy.python.py_eval(viewer_v)
                                    viewer_group_cs.append((viewer_v, cs[0][1], cs[0][2]))
                                vcheck_points[gn] = viewer_group_cs

                for gn, (ps, group_cs) in included_gp.items():
                    for prop in ps:
                        del check_points[prop]
                    check_points[gn] = group_cs

                #around has effect only when radius or angle exis at sametime
                if "around" in check_points:
                    if (None, layer, "radius") not in all_keyframes[s] and (None, layer, "angle") not in all_keyframes[s]:
                        check_points["around"] = [((camera_state_org[s][layer]["xaround"], camera_state_org[s][layer]["yaround"]), 0, None)]

                #viewerで使用するプロパティー(functionはblur等が含まれる可能性がある)
                #These properties are shown in side viewer(function property has danger of including blur)
                if persistent._viewer_sideview:
                    for p in ("xpos", "xanchor", "xoffset", "ypos", "yanchor", "yoffset", "around", "radius", "angle", "zpos", "rotate", "xrotate", "yrotate", "zrotate", "orientation", "point_to"):
                        if p in check_points:
                            vcheck_points[p] = check_points[p]
                    vcheck_points["props_use_default"] = check_points["props_use_default"]
                    vcheck_points["at_list"] = check_points["at_list"]

                if not camera_is_used and s > 0:
                    loop.append(loop[s-1])
                    spline.append(spline[s-1])
                    camera_check_points.append(camera_check_points[s-1])
                    viewer_check_points.append(viewer_check_points[s-1])
                else:
                    loop.append({key: loops[s][key] for key in loops[s] if key[0] is None and key[1] == layer})
                    spline.append({key: splines[s][key] for key in splines[s] if key[0] is None and key[1] == layer})
                    camera_check_points.append(check_points)
                    viewer_check_points.append(vcheck_points)

            image_check_points = []
            for s, (_, t, _) in enumerate(scene_keyframes):
                check_points = {}
                state = get_image_state(layer, s)
                for tag in state:
                    check_points[tag] = {}
                    props_use_default = []
                    at_list = state[tag].get("at_list")
                    check_points[tag]["at_list"] = [(at_list, t, None)]
                    for prop in state[tag]:
                        if prop in ("xpos", "ypos"):
                            for p in ("xaround", "yaround", "radius", "angle"):
                                if (tag, layer, p) in all_keyframes[s]:
                                    skip = True
                                    break
                            else:
                                skip = False
                            if skip:
                                continue
                        if prop in ("xaround", "yaround", "radius", "angle"):
                            for p in ("xpos", "ypos"):
                                if (tag, layer, p) in all_keyframes[s]:
                                    skip = True
                                    break
                            else:
                                for p in ("xaround", "yaround", "radius", "angle"):
                                    if (tag, layer, p) in all_keyframes[s]:
                                        skip = False
                                        break
                                else:
                                    skip = True
                            if skip:
                                continue

                        if (tag, layer, prop) in all_keyframes[s]:
                            check_points[tag][prop] = all_keyframes[s][(tag, layer, prop)]
                        elif prop in props_groups["focusing"] and prop in camera_check_points[s]:
                            check_points[tag][prop] = camera_check_points[s][prop]
                        else:
                            if state[tag][prop] is not None:
                                check_points[tag][prop] = [(get_value((tag, layer, prop), default=False, scene_num=s), t, None)]
                            elif prop not in not_used_by_default:
                                check_points[tag][prop] = [(get_value((tag, layer, prop), default=True, scene_num=s), t, None)]
                                props_use_default.append(prop)

                    check_points[tag]["props_use_default"] = [(props_use_default, t, None)]
                    #focusing以外のグループプロパティーはここで纏める
                    included_gp = {}
                    for p in check_points[tag]:
                        check_result = check_props_group((tag, layer, p), s)
                        if check_result is not None:
                            gn, ps = check_result
                            if gn != "focusing":
                                args = []
                                for prop in ps:
                                    args.append(check_points[tag][prop])
                                group_cs = []
                                for cs in zip(*args):
                                    v = tuple(c[0] for c in cs)
                                    if gn in ("matrixtransform", "matrixcolor"):
                                        v = generate_matrix_strings(v, gn, ps)
                                        v = renpy.python.py_eval(v)
                                    group_cs.append((v, cs[0][1], cs[0][2]))
                                included_gp[gn] = (ps, group_cs)
                    for gn, (ps, group_cs) in included_gp.items():
                        for prop in ps:
                            del check_points[tag][prop]
                        check_points[tag][gn] = group_cs

                    # around has effect only when radius or angle exis at sametime
                    if "around" in check_points[tag]:
                        if (tag, layer, "radius") not in all_keyframes[s] and (tag, layer, "angle") not in all_keyframes[s]:
                            check_points[tag]["around"] = [(((state[tag]["xaround"], state[tag]["yaround"])), 0, None)]
                            print(check_points[tag]["around"])

                    if persistent._viewer_focusing and perspective_enabled(layer, s, time=t):
                        if "blur" in check_points[tag]:
                            del check_points[tag]["blur"]
                    else:
                        for p in ("focusing", "dof"):
                            if p in check_points[tag]:
                                del check_points[tag][p]

                    # if "around" in check_points:
                    #     if "radius" not in all_keyframes[s][(tag, layer, "radius")] or "angle" not in all_keyframes[s][(tag, layer, "angle")]:
                    #         del check_points["around"]

                image_check_points.append(check_points)

                for css in camera_check_points:
                    for p in props_groups["focusing"]:
                        if p in css:
                            del css[p]
            if play:
                renpy.show("action_preview_"+layer, what=Transform(function=renpy.curry(viewer_transform)(
                 camera_check_points=camera_check_points, image_check_points=image_check_points, scene_checkpoints=deepcopy(scene_keyframes),
                 viewer_check_points=viewer_check_points, zorder_list=zorder_list, loop=loop, spline=spline, start_time=0., end_time=get_animation_delay(), layer=layer)))
            else:
                renpy.show("action_preview_"+layer, what=Transform(function=renpy.curry(viewer_transform)(
                 camera_check_points=camera_check_points, image_check_points=image_check_points, scene_checkpoints=deepcopy(scene_keyframes),
                 viewer_check_points=viewer_check_points, zorder_list=zorder_list, loop=loop, spline=spline, time=current_time, layer=layer)))


    def viewer_transform(tran, st, at, camera_check_points, image_check_points, scene_checkpoints, viewer_check_points,
                         zorder_list, loop, spline=None, subpixel=True, time=None, start_time=None, end_time=None, layer=None):
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
                    #シーン変移後
                    child = FixedTimeDisplayable(Transform(function=renpy.curry(
                     camera_transform)(camera_check_points=camera_check_points[i], image_check_points=image_check_points[i],
                     scene_checkpoints=scene_checkpoints, viewer_check_points=viewer_check_points[i],
                     zorder_list=zorder_list, loop=loop[i], spline=spline[i], subpixel=subpixel, time=time, scene_num=i, layer=layer)), time, at)
                else:
                    #シーン変移中
                    old_widget = FixedTimeDisplayable(Transform(function=renpy.curry(
                     camera_transform)(camera_check_points=camera_check_points[i-1], image_check_points=image_check_points[i-1],
                     scene_checkpoints=scene_checkpoints, viewer_check_points=viewer_check_points[i-1],
                     zorder_list=zorder_list, loop=loop[i-1], spline=spline[i-1], subpixel=subpixel, time=time, scene_num=i-1, layer=layer)), time, at)
                    new_widget = FixedTimeDisplayable(Transform(function=renpy.curry(
                     camera_transform)(camera_check_points=camera_check_points[i], image_check_points=image_check_points[i],
                     scene_checkpoints=scene_checkpoints, viewer_check_points=viewer_check_points[i],
                     zorder_list=zorder_list, loop=loop[i], spline=spline[i], subpixel=subpixel, time=time, scene_num=i, layer=layer)), time, at)
                    transition = renpy.python.py_eval("renpy.store."+goal[0])
                    during_transition_displayable = DuringTransitionDisplayble(transition, old_widget, new_widget, time - checkpoint, 0)
                    child = during_transition_displayable

                break
        else:
            #スタートシーン
            child = Transform(function=renpy.curry(camera_transform)(
             camera_check_points=camera_check_points[-len(scene_checkpoints)], image_check_points=image_check_points[-len(scene_checkpoints)],
             scene_checkpoints=scene_checkpoints, viewer_check_points=viewer_check_points[-len(scene_checkpoints)], 
             zorder_list=zorder_list, loop=loop[-len(scene_checkpoints)], spline=spline[-len(scene_checkpoints)], subpixel=subpixel, time=time, scene_num=-len(scene_checkpoints), layer=layer))
        if not persistent._viewer_legacy_gui:
            if aspect_16_9:
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


    def add_thick(child):
        w, h = renpy.render(child, 0, 0, 0, 0).get_size()
        w = int(w)
        h = int(h)
        bold=50

        rv = renpy.display.layout.MultiBox(layout='fixed', xsize=w, ysize=h)
        rv.add(Transform(matrixtransform=Matrix.rotate( 90,  0, 0), matrixanchor=(.5, 1.))(Solid("#FFF" , xpos=0     , ypos=-bold , xsize=w    , ysize=bold)    ))
        rv.add(Transform(matrixtransform=Matrix.rotate(-90,  0, 0), matrixanchor=(.5, 0.))(Solid("#FFF" , xpos=0     , ypos=h     , xsize=w    , ysize=bold)    ))
        rv.add(Transform(matrixtransform=Matrix.rotate( 0, -90, 0), matrixanchor=(1., .5))(Solid("#FFF" , xpos=-bold , ypos=-bold , xsize=bold , ysize=h+2*bold)))
        rv.add(Transform(matrixtransform=Matrix.rotate( 0,  90, 0), matrixanchor=(0., .5))(Solid("#FFF" , xpos=w     , ypos=-bold , xsize=bold , ysize=h+2*bold)))
        rv.add(child)

        return rv



    def define_camera_model(z11):
        from math import atan2, degrees

        camera_model = renpy.display.layout.MultiBox(layout='fixed')
        inf = 10000000
        bold = 50

        d1 = degrees(atan2(config.screen_height, config.screen_width))
        d2 = (90 - d1)*2
        d3 = degrees(atan2(z11, sqrt(config.screen_height**2 + config.screen_width**2)/2))
        camera_model.add(Transform(yanchor=.5, matrixanchor=(0, 0.5), matrixtransform=Matrix.rotate(0, d3, d1))(Solid("#F00", xsize=inf, ysize=bold)))
        camera_model.add(Transform(yanchor=.5, matrixanchor=(0, 0.5), matrixtransform=Matrix.rotate(0, d3, d1+d2))(Solid("#0F0", xsize=inf, ysize=bold)))
        camera_model.add(Transform(yanchor=.5, matrixanchor=(0, 0.5), matrixtransform=Matrix.rotate(0, d3, 3*d1+d2))(Solid("#0FF", xsize=inf, ysize=bold)))
        camera_model.add(Transform(yanchor=.5, matrixanchor=(0, 0.5), matrixtransform=Matrix.rotate(0, d3, 3*d1+2*d2))(Solid("#939", xsize=inf, ysize=bold)))

        width = renpy.config.screen_width
        height = renpy.config.screen_height
        return Transform(align=(.5, .5), matrixtransform=Matrix.offset(width/2, height/2, z11))(camera_model)

    def camera_transform(tran, st, at, camera_check_points, image_check_points, scene_checkpoints, viewer_check_points, zorder_list, loop, spline=None, subpixel=True, time=None, scene_num=0, layer=None):
        global third_view_child

        image_box = renpy.display.layout.MultiBox(layout='fixed')
        sideview_image_box = renpy.display.layout.MultiBox(layout='fixed')
        for tag, zorder in zorder_list[scene_num][layer]:
            if tag in image_check_points:
                image_loop = {key[2]+"_loop": loops[scene_num][key] for key in loops[scene_num] if key[0] == tag and key[1] == layer}
                image_spline = {key[2]+"_spline": splines[scene_num][key] for key in splines[scene_num] if key[0] == tag and key[1] == layer}
                for p in props_groups["focusing"]:
                    image_loop[p+"_loop"] = loops[scene_num][(None, layer, p)]
                    image_spline[p+"_spline"] = splines[scene_num][(None, layer, p)]
                image_box.add(Transform(function=renpy.curry(transform)(
                 check_points=image_check_points[tag],
                 loop=image_loop, spline=image_spline,
                 subpixel=subpixel, time=time, scene_num=scene_num, scene_checkpoints=scene_checkpoints, layer=layer)))

                if persistent._viewer_sideview and len(scene_keyframes)+scene_num == current_scene and perspective_enabled(layer, scene_num) and not persistent._viewer_legacy_gui:
                    sideview_image_box.add(Transform(function=renpy.curry(transform)(
                     check_points=image_check_points[tag], loop=image_loop, spline=image_spline, subpixel=subpixel,
                     time=time, scene_num=scene_num, scene_checkpoints=scene_checkpoints, side_view=True, layer=layer)))

        camera_loop = {key[2]+"_loop": loop[key] for key in loop if key[1] == layer}
        camera_spline = {key[2]+"_spline": spline[key] for key in spline if key[1] == layer}
        if persistent._viewer_sideview and len(scene_keyframes)+scene_num == current_scene and perspective_enabled(layer, scene_num) and not persistent._viewer_legacy_gui:
            third_view_child[layer] = []
            sideview_box = renpy.display.layout.MultiBox(layout='fixed')
            sideview_box.add(sideview_image_box)

            perspective = camera_check_points["perspective"][0][0]
            if perspective is True:
                perspective = config.perspective

            if isinstance(perspective, (int, float)):
                z11 = perspective
            else:
                z11 = perspective[1]

            camera_model = define_camera_model(z11)

            camera_model = Transform(function=renpy.curry(transform)(
                        check_points=viewer_check_points, loop=camera_loop, spline=camera_spline, subpixel=subpixel, time=time, 
                        scene_num=scene_num, scene_checkpoints=scene_checkpoints, camera=True, side_view=True, layer=layer))(camera_model)

            sideview_box.add(camera_model)

            inf = 1000000
            for i, r in enumerate(((-90, 0, 0), (0, -90, 0), (0, 0, 0))):
                sd = Transform(perspective=(0, inf, inf*10), matrixtransform=Matrix.scale(0.2, 0.2, 1.0)*Matrix.rotate(*r))(sideview_box)
                sd = renpy.store.AlphaMask(sd, Solid("#000"))

                if aspect_16_9:
                    sd = Transform(zoom=(1 - preview_size)/2, ypos=i*preview_size/3)(sd)
                else:
                    sd = Transform(zoom=(1 - preview_size)/2, xpos=preview_size, ypos=i*preview_size/3)(sd)
                third_view_child[layer].append(sd)

        camera_box = renpy.display.layout.MultiBox(layout='fixed')
        #camera position doesn't have effect whithout box
        camera_box.add(Transform(function=renpy.curry(transform)(
         check_points=camera_check_points, loop=camera_loop, spline=camera_spline,
         subpixel=subpixel, time=time, camera=True, scene_num=scene_num, scene_checkpoints=scene_checkpoints, layer=layer))(image_box))
        tran.set_child(camera_box)
        return 0


    def transform(tran, st, at, check_points, loop, spline=None, subpixel=True, crop_relative=True, time=None, camera=False, scene_num=None, scene_checkpoints=None, side_view=False, layer=None):
        # check_points = { prop: [ (value, time, warper).. ] }
        if subpixel is not None:
            tran.subpixel = subpixel
        if crop_relative is not None:
            tran.crop_relative = crop_relative
        if time is None:
            time = st
        group_cache = {}
        sle = renpy.game.context().scene_lists
        if in_editor and camera and not side_view:
            tran.perspective = get_value((None, layer, "perspective"), scene_keyframes[scene_num][1], True)

        #around should be before radius and angle
        items = list(check_points.items())
        for i, (p, cs) in enumerate(items):
            if p == "around":
                for_around_time = max(check_points["radius"][-1][1],  check_points["angle"][-1][1])
                break
        items = [items[i]] + items[:i] + items[i+1:]

        for p, cs in items:

            if not cs: #恐らく不要
                break

            scene_start = cs[0][1]
            looped_time = time
            if p+"_loop" in loop and loop[p+"_loop"] and cs[-1][1]:
                if (time - scene_start) % (cs[-1][1] - scene_start) != 0:
                    looped_time = (time - scene_start) % (cs[-1][1] - scene_start) + scene_start

            if p == "around":
                if not loop.get("angle_loop", None) and not loop.get("radius_loop", None):
                    if time > for_around_time:
                        looped_time = for_around_time

            for i in range(1, len(cs)):
                checkpoint = cs[i][1]
                pre_checkpoint = cs[i-1][1]
                if looped_time >= scene_start and looped_time < checkpoint:
                    start = cs[i-1]
                    goal = cs[i]
                    if p not in ("child", "function", "at_list", "props_use_default"):

                        if checkpoint != pre_checkpoint:
                            if goal[2].startswith("warper_generator"):
                                warper = renpy.python.py_eval(goal[2])
                            else:
                                warper = renpy.atl.warpers[goal[2]]
                            complete = warper((looped_time - pre_checkpoint) / (checkpoint - pre_checkpoint))
                        else:
                            complete = 1.

                        knots = []
                        if spline is not None and p+"_spline" in spline and checkpoint in spline[p+"_spline"]:
                            knots = spline[p+"_spline"][checkpoint]
                            if knots:
                                knots = [start[0]] + knots + [goal[0]]

                        if knots:
                            v = renpy.atl.interpolate_spline(complete, knots)
                        elif p not in props_groups["focusing"]:
                            old = start[0]
                            new = goal[0]
                            if p == "orientation":
                                if old is None:
                                    old = (0.0, 0.0, 0.0)
                                if new is not None:
                                    v = euler_slerp(complete, old, new)
                                elif complete >= 1:
                                    v = None
                                else:
                                    v = old
                            else:
                                if p in ("matrixtransform", "matrixcolor"):
                                    old = start[0](None, 1.0)
                                    old.origin = start[0]
                                v = renpy.atl.interpolate(complete, old, new, renpy.atl.PROPERTIES[p])
                        if p in props_groups["focusing"]:
                            if not side_view:
                                group_cache[p] = complete * (goal[0] - start[0]) + start[0]
                                if len(group_cache) == len(props_groups["focusing"]):
                                    focusing = group_cache["focusing"]
                                    dof = group_cache["dof"]
                                    image_zpos = 0
                                    if tran.zpos:
                                        image_zpos = tran.zpos
                                    if tran.matrixtransform:
                                        image_zpos += tran.matrixtransform.zdw
                                    camera_zpos = 0
                                    if in_editor:
                                        camera_zpos = get_value((None, layer, "zpos"), default=True, scene_num=scene_num)
                                    else:
                                        if layer in sle.camera_transform:
                                            props = sle.camera_transform[layer]
                                            if props.zpos:
                                                camera_zpos = props.zpos
                                    result = camera_blur_amount(image_zpos, camera_zpos, dof, focusing)
                                    setattr(tran, "blur", result)
                        else:
                            setattr(tran, p, v)
                    break
            else:
                if looped_time < scene_start:
                    fixed_index = 0
                else:
                    fixed_index = -1
                if p in props_groups["focusing"]:
                    if not side_view:
                        group_cache[p] = cs[fixed_index][0]
                        if len(group_cache) == len(props_groups["focusing"]):
                            focusing = group_cache["focusing"]
                            dof = group_cache["dof"]
                            image_zpos = 0
                            if tran.zpos:
                                image_zpos = tran.zpos
                            if tran.matrixtransform:
                                image_zpos += tran.matrixtransform.zdw
                            camera_zpos = 0
                            if in_editor:
                                camera_zpos = get_value((None, layer, "zpos"), default=True, scene_num=scene_num)
                            else:
                                if layer in sle.camera_transform:
                                    props = sle.camera_transform[layer]
                                    if props.zpos:
                                        camera_zpos = props.zpos
                            result = camera_blur_amount(image_zpos, camera_zpos, dof, focusing)
                            setattr(tran, "blur", result)
                else:
                    if p not in ("child", "function", "at_list", "props_use_default"):
                        v = cs[fixed_index][0]
                        #inherit position properties from 'at clauses' if not given.
                        if p in check_points["props_use_default"][0][0] and p in {"xpos", "ypos", "xanchor", "yanchor", "xoffset", "yoffset"}:
                            at_v = get_at_list_props(check_points["at_list"][0][0], p, time, at)
                            if at_v is not None:
                                v = at_v
                        if p in ("matrixtransform", "matrixcolor"):
                            v = v(1.0, None)
                        setattr(tran, p, v)

        if "child" in check_points and check_points["child"]:
            at_list = check_points["at_list"][0][0]
            cs = check_points["child"]

            scene_start = cs[0][1]
            looped_time = time
            if "child_loop" in loop and loop["child_loop"] and cs[-1][1]:
                if (time - scene_start) % (cs[-1][1] - scene_start) != 0:
                    looped_time = (time - scene_start) % (cs[-1][1] - scene_start) + scene_start

            for i in range(-1, -len(cs), -1):
                checkpoint = cs[i][1]
                pre_checkpoint = cs[i-1][1]
                if looped_time >= scene_start and looped_time >= checkpoint:
                    start = cs[i-1]
                    goal = cs[i]
                    if start[0][0] is None and goal[0][0] is None:
                        tran.set_child(Null())
                        break
                    elif start[0][0] is None:
                        new_widget = get_widget(goal[0][0], looped_time, at, at_list)
                        w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                        old_widget = Null(w, h)
                    elif goal[0][0] is None:
                        old_widget = get_widget(start[0][0], looped_time, at, at_list)
                        w, h = renpy.render(old_widget, 0, 0, 0, 0).get_size()
                        new_widget = Null(w, h)
                    else:
                        old_widget = get_widget(start[0][0], looped_time, at, at_list)
                        new_widget = get_widget(goal[0][0], looped_time, at, at_list)
                    if looped_time - checkpoint >= get_transition_delay(goal[0][1]):
                        child = new_widget
                    else:
                        transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                        during_transition_displayable = DuringTransitionDisplayble(transition, old_widget, new_widget, looped_time-checkpoint, 0)
                        child = during_transition_displayable
                        if side_view:
                            child = add_thick(child)
                    tran.set_child(child)
                    break
            else:
                start = ((None, None), 0, None)
                goal = cs[0]
                checkpoint = goal[1]
                if goal[0][0] is None:
                    child = Null()
                else:
                    fixed_time = looped_time-checkpoint
                    if fixed_time < 0:
                        fixed_time = 0
                    new_widget = get_widget(goal[0][0], looped_time, at, at_list)
                    w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                    old_widget = Null(w, h)
                    if fixed_time >= get_transition_delay(goal[0][1]):
                        child = new_widget
                    else:
                        transition = renpy.python.py_eval("renpy.store."+goal[0][1])
                        child = DuringTransitionDisplayble(transition, old_widget, new_widget, fixed_time, 0)
                if side_view:
                    child = add_thick(child)
                tran.set_child(child)

        if "function" in check_points and check_points["function"]:
            f = check_points["function"][0][0][1]
            if f is not None:
                f(tran, time, at)

        if in_editor:
            point_to = getattr(tran, "point_to", None)
            perspective = get_value((None, layer, "perspective"), scene_keyframes[scene_num][1], True)
            if perspective and (check_version(23032300) and isinstance(point_to, renpy.display.transform.Camera) or (side_view and camera)):
                if perspective is True:
                    perspective = renpy.config.perspective

                elif isinstance(perspective, (int, float)):
                    perspective = (renpy.config.perspective[0], perspective, renpy.config.perspective[2])

                if perspective:
                    z11 = perspective[1]

                    width = renpy.config.screen_width
                    height = renpy.config.screen_height

                    placement = (get_value((None, layer, "xpos"), default=True, scene_num=scene_num), get_value((None, layer, "ypos"), default=True, scene_num=scene_num), get_value((None, layer, "xanchor"), default=True, scene_num=scene_num), get_value((None, layer, "yanchor"), default=True, scene_num=scene_num), get_value((None, layer, "xoffset"), default=True, scene_num=scene_num), get_value((None, layer, "yoffset"), default=True, scene_num=scene_num), True)
                    xplacement, yplacement = renpy.display.core.place(width, height, width, height, placement)
                    zpos = get_value((None, layer, "zpos"), default=True, scene_num=scene_num)

                    # direct displayable toward camera
                    if point_to is not None and isinstance(point_to, renpy.display.transform.Camera):
                        point_to = (xplacement + width / 2, yplacement + height / 2, zpos + z11)
                        setattr(tran, "point_to", point_to)
                    elif side_view and camera:
                        mrotation = None
                        xrotate = getattr(tran, "xrotate", None)
                        yrotate = getattr(tran, "yrotate", None)
                        zrotate = getattr(tran, "zrotate", None)
                        if (xrotate is not None) or (yrotate is not None) or (zrotate is not None):
                            xrotate, yrotate, zrotate = zyx_to_xyz(xrotate, yrotate, zrotate)
                            mrotation = Matrix.rotate(xrotate, yrotate, zrotate)
                            setattr(tran, "xrotate", None)
                            setattr(tran, "yrotate", None)
                            setattr(tran, "zrotate", None)

                        morientation = None
                        orientation = getattr(tran, "orientation", None)
                        if orientation is not None:
                            orientation = zyx_to_xyz(*orientation)
                            morientation = Matrix.rotate(*orientation)
                            setattr(tran, "orientation", None)

                        mpoint_to = None
                        poi = getattr(tran, "point_to", None)
                        if poi is not None:
                            from math import sin, cos, asin, atan, degrees, pi, sqrt
                            start_pos = (xplacement + width / 2, yplacement + height / 2, zpos + z11)
                            a, b, c = ( float(e - s) for s, e in zip(start_pos, poi) )

                            #cameras is rotated in z, y, x order.
                            #It is because rotating stage in x, y, z order means rotating a camera in z, y, x order.
                            #rotating around z axis isn't rotating around the center of the screen when rotating camera in x, y, z order.
                            v_len = sqrt(a**2 + b**2 + c**2) # math.hypot is better in py3.8+
                            if v_len == 0:
                                xpoi = ypoi = zpoi = 0
                            else:
                                a /= v_len
                                b /= v_len
                                c /= v_len

                                sin_ypoi = min(1., max(-a, -1.))
                                ypoi = asin(sin_ypoi)
                                if c == 0:
                                    if abs(a) == 1:
                                        xpoi = 0
                                    else:
                                        sin_xpoi = min(1., max(b / cos(ypoi), -1.))
                                        xpoi = asin(sin_xpoi)
                                else:
                                    xpoi = atan(-b/c)

                                if c > 0:
                                    ypoi = pi - ypoi

                                if xpoi != 0.0 and ypoi != 0.0:
                                    if xpoi == pi / 2 or xpoi == - pi / 2:
                                        if -sin(xpoi) * sin(ypoi) > 0.0:
                                            zpoi = pi / 2
                                        else:
                                            zpoi = - pi / 2
                                    else:
                                        zpoi = atan(-(sin(xpoi) * sin(ypoi)) / cos(xpoi))
                                else:
                                    zpoi = 0

                                xpoi = degrees(xpoi)
                                ypoi = degrees(ypoi)
                                zpoi = degrees(zpoi)

                            xpoi, ypoi, zpoi = zyx_to_xyz(xpoi, ypoi, zpoi)
                            mpoint_to = Matrix.rotate(xpoi, ypoi, zpoi)
                            setattr(tran, "point_to", None)

                        m = Matrix.identity()

                        mt = getattr(tran, "matrixtransform", None)
                        if mt is not None:
                            matrixanchor = getattr(tran, "matrixanchor", None)
                            if matrixanchor is None:
                                manchorx = width / 2.0
                                manchory = height / 2.0
                            else:
                                manchorx, manchory = matrixanchor
                                if type(manchorx) is float:
                                    manchorx *= width
                                if type(manchory) is float:
                                    manchory *= height

                            m = Matrix.offset(-manchorx, -manchory, 0.0) * m
                            m = mt * m
                            m = Matrix.offset(manchorx, manchory, 0.0) * m
                        setattr(tran, "matrixanchor", (0, 0))

                        rotate = getattr(tran, "rotate", None)
                        if rotate is not None:
                            setattr(tran, "rotate", None)
                            m = Matrix.offset(-width / 2, -height / 2, 0) * m
                            m = Matrix.rotate(0, 0, rotate) * m
                            m = Matrix.offset(width / 2, height / 2, 0) * m

                        if mrotation is not None or morientation is not None or mpoint_to is not None:
                            #original code width /2
                            m = Matrix.offset(-width / 2, -height / 2, -z11) * m

                            if mrotation is not None:
                                m = mrotation * m

                            if morientation is not None:
                                m = morientation * m

                            if mpoint_to is not None:
                                m = mpoint_to * m

                            #original code width /2
                            m = Matrix.offset(width / 2, height / 2, z11) * m

                        if xplacement:
                            setattr(tran, "xpos", 0)
                            setattr(tran, "xanchor", 0)
                            setattr(tran, "xoffset", 0)
                        if yplacement:
                            setattr(tran, "ypos", 0)
                            setattr(tran, "yanchor", 0)
                            setattr(tran, "yoffset", 0)
                        if zpos:
                            setattr(tran, "zpos", 0)
                        m = Matrix.offset(xplacement, yplacement, zpos) * m

                        setattr(tran, "matrixtransform", m)

        return 0


    def get_widget(name, time, at, at_list):
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

            prefix = "<from {} to {}>".format(time, time+0.1)
            if mask_file_name:
                mask_prefix = "<from {} to {}>".format(time, time+0.1)

            play = prefix + file_name
            if mask_file_name:
                mask = mask_prefix + mask_file_name
            else:
                mask = None

            # if True:
                #movie isn't updated with this cache.
                # if name_tuple in movie_cache:
                #     d = movie_cache[name_tuple]
                # else:
                #     d = deepcopy(d_org)
                #     movie_cache[name_tuple] = d
            #this isn't shown correctly if movie is longer than 2 or 3 sec.
            d = deepcopy(d_org)

            d._play = play
            d.mask = mask
            d.loop = True
            # else:
            #     pass
                #heavy and both isn't shown
                # d = Movie(play=play, mask=mask, loop=True)
                # d = FixedTimeDisplayable(Movie(play=play, mask=mask, loop=True), time, at)

            widget = d
            # raise Exception((d._play, d.mask))
        # elif name_tuple in images:
            # child = images[name_tuple]
            # child = apply_at_list(child, at_list)
            # widget = FixedTimeDisplayable(child, time, at)
        else:
            #easy displayableではすべてImageReference objectになるがなにか問題あるか?
            child = renpy.easy.displayable(name)
            child = apply_at_list(child, at_list)
            widget = FixedTimeDisplayable(child, time, at)

        return widget


    def exclusive_check(key, scene_num=None):
        #check exclusive properties
        if scene_num is None:
            scene_num = current_scene
        tag, layer, prop = key
        if tag is None:
            state = camera_state_org[scene_num][layer]
        else:
            state = get_image_state(layer, scene_num)

        for set1, set2 in exclusive:
            if prop in set1 or prop in set2:
                if prop in set1:
                    one_set = set1
                    other_set = set2
                else:
                    one_set = set2
                    other_set = set1
                # for p in one_set:
                #     key2 = (tag, layer, p)
                #     if key2 in all_keyframes[scene_num]:
                #         return True
                #     # if key2 in state and (state[key2] is not None and state[key2] != get_default(p)):
                #     #     return True
                for p in other_set:
                    key2 = (tag, layer, p)
                    if key2 in all_keyframes[scene_num]:
                        return False
                    # if key2 in state and (state[key2] is not None and state[key2] != get_default(p)):
                    #     return False
                else:
                    # if prop in set1:
                    #     return True
                    # else:
                    #     return False
                    return True
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
                + format_exc()
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
                    + format_exc()
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
                    + format_exc()
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
                image_state[current_scene][layer][added_tag]["at_list"] = [("default", {})]
                zorder_list[current_scene][layer].append((added_tag, 0))
                for p in transform_props:
                    if p == "child":
                        image_state[current_scene][layer][added_tag][p] = (image_name, None)
                        if current_scene == 0 or current_time > scene_keyframes[current_scene][1]:
                            set_keyframe((added_tag, layer, p), (image_name, persistent._viewer_transition))
                    elif p in ("matrixtransform", "matrixcolor"):
                        for prop, v in load_matrix(p, None):
                            image_state[current_scene][layer][added_tag][prop] = v
                    else:
                        image_state[current_scene][layer][added_tag][p] = None
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
                    + format_exc()
                    renpy.notify(message)
                    return
                set_keyframe(key, (value, f), time=scene_keyframes[current_scene][1])
                change_time(current_time)


    def edit_any(key, time=None):
        if time is None:
            time = current_time
        prop = key[2]
        value = get_value(key, time)
        if prop in menu_props:
            global _return
            _return = value
            renpy.invoke_in_new_context(renpy.call_screen, "_value_menu", prop=prop, default=value)
            value = _return
        else:
            if isinstance(value, str):
                value = "'" + value + "'"
            value = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", default=value)
            if value:
                try:
                    value = renpy.python.py_eval(value)
                    if prop in check_any_props and not check_any_props[prop](value):
                        renpy.notify(_("{} is an invalid data".format(value)))
                        return
                except Exception as e:
                    message = _("Please type a valid data") + "\n" \
                    + format_exc()
                    renpy.notify(message)
                    return
            else:
                return
        set_keyframe(key, value, time=time)
        change_time(current_time)


    def toggle_boolean_property(key):
        tag, layer, prop = key
        if tag is None:
            value_org = camera_state_org[current_scene][layer][key]
        else:
            value_org = get_image_state(layer)[tag][prop]
        value = get_value(key, scene_keyframes[current_scene][1], True)
        #assume default is False
        if value == value_org or (not value and not value_org):
            set_keyframe(key, not value, time=scene_keyframes[current_scene][1])
        else:
            remove_keyframe(scene_keyframes[current_scene][1], key)
        change_time(current_time)


    def perspective_enabled(layer, scene_num=None, time=None):
        if scene_num is None:
            scene_num = current_scene
        if time is None:
            time = scene_keyframes[scene_num][1]
        v = get_value((None, layer, "perspective"), scene_keyframes[scene_num][1], True, scene_num)
        return v or (v is not False and v == 0)


    def remove_image(layer, tag):
        def remove_keyframes(tag, layer):
            k_list = []
            for k in (k for k in all_keyframes[current_scene] if k[0] is not None and k[0] == tag and k[1] == layer):
                k_list.append(k)
            for k in k_list:
                del all_keyframes[current_scene][k]

        renpy.hide(tag, layer)
        del image_state[current_scene][layer][tag]
        remove_keyframes(tag, layer)
        zorder_list[current_scene][layer] = [(ztag, z) for (ztag, z) in zorder_list[current_scene][layer] if ztag != tag]


    def get_default(prop):
        if prop.count("_") == 3:
            _, _, _, prop = prop.split("_")
        return property_default_value[prop]


    def get_value(key, time=None, default=False, scene_num=None):
        if scene_num is None:
            scene_num = current_scene

        tag, layer, prop = key
        if tag is not None and prop in props_groups["focusing"]:
            key = (None, layer, prop)
        if tag is None:
            state = camera_state_org[scene_num][layer]
        else:
            state = get_image_state(layer, scene_num)[tag]
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

        scene_start = cs[0][1]
        looped_time = time
        if loops[scene_num][key] and cs[-1][1]:
            if (time - scene_start) % (cs[-1][1] - scene_start) != 0:
                looped_time = (time - scene_start) % (cs[-1][1] - scene_start) + scene_start

        # if consider_around and prop in ("xaround", "yaround"):
        #     if not loops[scene_num].get((tag, layer, "angle"), None) and not loops[scene_num].get((tag, layer, "radius"), None):
        #         if (tag, layer, "angle") in all_keyframes[scene_num]:
        #             a = all_keyframes[scene_num][(tag, layer, "angle")][-1][1]
        #         else:
        #             a = 0
        #         if (tag, layer, "radius") in all_keyframes[scene_num]:
        #             b = all_keyframes[scene_num][(tag, layer, "radius")][-1][1]
        #         else:
        #             b = 0
        #         for_around_time = max(a, b)
        #         if time > for_around_time:
        #             looped_time = for_around_time

        for i in range(1, len(cs)):
            checkpoint = cs[i][1]
            pre_checkpoint = cs[i-1][1]
            if looped_time >= scene_start and looped_time < checkpoint:
                start = cs[i-1]
                goal = cs[i]

                if checkpoint != pre_checkpoint:
                    if goal[2].startswith("warper_generator"):
                        warper = renpy.python.py_eval(goal[2])
                    else:
                        warper = renpy.atl.warpers[goal[2]]
                    complete = warper((looped_time - pre_checkpoint) / (checkpoint - pre_checkpoint))
                else:
                    complete = 1.

                if goal[0] is not None or prop in boolean_props | any_props:
                    check_result = check_props_group(key, scene_num)
                    if check_result:
                        gn, ps = check_result

                    if check_result and gn not in ("focusing", "matrixtransform", "matrixcolor"):
                        old = []
                        new = []
                        default_value = get_default(prop)
                        for p in ps:
                            key2 = (key[0], key[1], p)
                            old.append(all_keyframes[scene_num][key2][i-1][0])
                            new.append(all_keyframes[scene_num][key2][i][0])

                        old = tuple(old)
                        new = tuple(new)

                        knots = []
                        if checkpoint in splines[scene_num][gn]:
                            knots = splines[scene_num][gn][checkpoint]
                            if knots:
                                knots = [old] + knots + [new]

                    else:
                        default_value = get_default(prop)
                        if start[0] is None:
                            old = default_value
                        else:
                            old = start[0]
                        new = goal[0]

                        knots = []
                        if checkpoint in splines[scene_num][key]:
                            knots = splines[scene_num][key][checkpoint]
                            if knots:
                                knots = [old] + knots + [new]

                    if knots:
                        v = renpy.atl.interpolate_spline(complete, knots)
                    elif check_result and gn in ("focusing", "matrixtransform", "matrixcolor"):
                        v = complete*(new-old)+old
                    elif check_result:
                        if gn == "orientation":
                            new = new

                            if old is None:
                                old = (0.0, 0.0, 0.0)
                            if new is not None:
                                v = euler_slerp(complete, old, new)
                            elif complete >= 1:
                                v = None
                            else:
                                v = old
                        else:
                            v = renpy.atl.interpolate(complete, old, new, renpy.atl.PROPERTIES[gn])
                    else:
                        if prop == "orientation":
                            new = new

                            if old is None:
                                old = (0.0, 0.0, 0.0)
                            if new is not None:
                                v = euler_slerp(complete, old, new)
                            elif complete >= 1:
                                v = None
                            else:
                                v = old
                        else:
                            v = renpy.atl.interpolate(complete, old, new, renpy.atl.PROPERTIES[prop])

                    if check_result and gn not in ("focusing", "matrixtransform", "matrixcolor"):
                        index = ps.index(prop)
                        v = v[index]

                    if isinstance(new, int):
                        if check_new_position_type(v):
                            v = int(v.absolute)
                        elif isinstance(new, float):
                            v = int(v)
                    elif isinstance(new, float):
                        if check_new_position_type(v):
                            v = float(v.relative)
                        elif isinstance(new, int):
                            v = float(v)
                    return v
                break
        else:
            if looped_time >= scene_start:
                return cs[-1][0]
            else:
                return cs[0][0]


    def put_camera_clipboard(layer):
        camera_keyframes = {}
        for key in all_keyframes[current_scene]:
            tag, _, prop = key
            if tag is None and prop != "function":
                value = get_value(key, current_time)
                if isinstance(value, float):
                    value = round(value, 3)
                elif prop in any_props and isinstance(value, str):
                    value = "'" + value + "'"
                camera_keyframes[prop] = [(value, 0, None)]
        camera_keyframes = set_group_keyframes(camera_keyframes, (None, layer, None))
        camera_properties = []
        for p in camera_state_org[current_scene][layer]:
            check_result = check_props_group((None, layer, p))
            if check_result is not None:
                gn, ps = check_result
                if gn not in camera_properties:
                    camera_properties.append(gn)
            else:
                if p not in special_props:
                    camera_properties.append(p)

        string = """
camera"""
        if layer != "master":
            string += " {layer}".format(layer=layer)
        for p, cs in x_and_y_to_xy([(p, camera_keyframes[p]) for p in camera_properties if p in camera_keyframes], layer):
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
            + format_exc()
            renpy.notify(message)
        else:
            renpy.notify(__('Placed \n"%s"\n on clipboard') % string)


    def put_image_clipboard(tag, layer):
        image_keyframes = {}
        for k in all_keyframes[current_scene]:
            if k[0] is not None and k[0] == tag and k[1] == layer and k[2] != "function":
                value = get_value(k, current_time)
                if isinstance(value, float):
                    value = round(value, 3)
                elif k[2] in any_props and isinstance(value, str):
                    value = "'" + value + "'"
                image_keyframes[k[2]] = [(value, 0, None)]
        image_keyframes = set_group_keyframes(image_keyframes, (tag, layer, None))
        if check_focusing_used(layer) and "blur" in image_keyframes:
            del image_keyframes["blur"]
        image_properties = []
        for p in get_image_state(layer)[tag]:
            check_result = check_props_group((tag, layer, p))
            if check_result is not None:
                gn, ps = check_result
                if gn not in image_properties:
                    image_properties.append(gn)
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
        for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes], layer):
            if string.find(":") < 0:
                string += ":\n        "
            string += "{property} {value}".format(property=p, value=cs[0][0])
            if persistent._one_line_one_prop:
                string += "\n        "
            else:
                string += " "
        if check_focusing_used(layer):
            focus = get_value((None, layer, "focusing"), current_time, True)
            dof = get_value((None, layer, "dof"), current_time, True)
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
            + format_exc()
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
            + format_exc()
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
                + format_exc()
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
                + format_exc()
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
                + format_exc()
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
                + format_exc()
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
        for l in get_layers():
            image_state[current_scene][l] = {}
            image_state_org[current_scene][l] = {}
            camera_state_org[current_scene][l] = {}
            zorder_list[current_scene][l] = []

        loops.insert(current_scene, defaultdict(_False))
        splines.insert(current_scene, defaultdict(dict))
        for layer in get_layers():
            for i in range(current_scene-1, -1, -1):
                if camera_keyframes_exist(i, layer):
                    break
            for p in camera_state_org[i][layer]:
                middle_value = get_value((None, layer, p), scene_keyframes[current_scene][1], False, i)
                if isinstance(middle_value, float):
                    camera_state_org[current_scene][layer][p] = round(middle_value, 2)
                else:
                    camera_state_org[current_scene][layer][p] = middle_value
        # if persistent._viewer_legacy_gui:
        #     renpy.show_screen("_action_editor")
        # elif persistent._open_only_one_page:
        #     renpy.show_screen("_new_action_editor")
        renpy.restart_interaction()


    def camera_keyframes_exist(scene_num, layer):
        for p in camera_state_org[scene_num][layer]:
            if (None, layer, p) in all_keyframes[scene_num]:
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
            for layer in get_layers():
                for i in range(s, -1, -1):
                    if camera_keyframes_exist(i, layer):
                        break
                for p in camera_state_org[i][layer]:
                    middle_value = get_value((None, layer, p), scene_keyframes[s][1], False, i)
                    if isinstance(middle_value, float):
                        camera_state_org[s][layer][p] = round(middle_value, 2)
                    else:
                        camera_state_org[s][layer][p] = middle_value
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
            for layer in get_layers():
                for i in range(s, -1, -1):
                    if camera_keyframes_exist(i, layer):
                        break
                for p in camera_state_org[i][layer]:
                    middle_value = get_value((None, layer, p), scene_keyframes[s][1], False, i)
                    if isinstance(middle_value, float):
                        camera_state_org[s][layer][p] = round(middle_value, 2)
                    else:
                        camera_state_org[s][layer][p] = middle_value
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
                + format_exc()
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
                    + format_exc()
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
                    evaled = renpy.python.py_eval(f.strip(), locals=renpy.python.store_dicts["store.audio"])
                    if not renpy.loadable(evaled):
                        raise
        except Exception as e:
            message = _("Please Input filenames") + "\n" \
            + format_exc()
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


    def update_gn_spline(key, time, scene_num=None):
        if scene_num is None:
            scene_num = current_scene
        tag, layer, prop = key

        check_result = check_props_group(key, scene_num)
        if check_result:
            gn, ps = check_result

            pre_knots = []
            for p in ps:
                key2 = (tag, layer, p)
                gn_key = (tag, layer, gn)
                pre_knots.append(splines[scene_num][key2][time])
            knots = []
            for knot in zip(*pre_knots):
                knots.append(tuple(knot))
            splines[scene_num][gn_key][time] = knots


    def add_knot(key, time, default, knot_number=None, recursion=False):

        if not recursion:
            tag, layer, prop = key

            check_result = check_props_group(key, current_scene)
            if check_result:
                gn, ps = check_result
                for p in ps:
                    if p != prop:
                        key2 = (tag, layer, p)
                        cs = all_keyframes[current_scene][key2]
                        for i, (v, t, w) in enumerate(cs):
                            if t == time:
                                d2 = cs[i-1][0]
                                add_knot(key2, time, d2, knot_number, recursion=True)

        if time in splines[current_scene][key]:
            if knot_number is not None:
                splines[current_scene][key][time].insert(knot_number, default)
            else:
                splines[current_scene][key][time].append(default)
        else:
            splines[current_scene][key][time] = [default]

        if not recursion:
            update_gn_spline(key, time)


    def remove_knot(key, time, i, recursion=False):

        if not recursion:
            tag, layer, prop = key

            check_result = check_props_group(key, current_scene)
            if check_result:
                gn, ps = check_result
                for p in ps + [gn]:
                    if p != prop:
                        key2 = (tag, layer, p)
                        remove_knot(key2, time, i, recursion=True)

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


    def _False():
        return False


    def open_action_editor():
        global current_time, current_scene, scene_keyframes, zorder_list, sound_keyframes, all_keyframes, playing, in_editor, loops, splines

        if not config.developer:
            return
        playing = False
        current_time = 0.0 #current_time is always float
        current_scene = 0
        moved_time = 0
        loops = [defaultdict(_False)]
        splines = [defaultdict(dict)]
        sound_keyframes = {}
        all_keyframes = [{}]
        zorder_list = [{}]
        for l in get_layers():
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
        if persistent._viewer_sideview is None:
            persistent._viewer_sideview = default_sideview
        for c in persistent._viewer_channel_list:
            sound_keyframes[c] = {}
        for c in renpy.audio.audio.channels:
            renpy.music.stop(c)
        renpy.store._viewers.at_clauses_flag = False
        action_editor_init()
        in_editor = True
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
                prop = key[2]
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
            prop = key[2]
            for (v, t, w) in cs:
                if prop == "child":
                    delay = get_transition_delay(v[1])
                    t += delay
                if t > animation_time:
                    animation_time = t
        return animation_time - scene_start


    def set_group_keyframes(keyframes, key, scene_num=None):
        tag, layer, _ = key
        result = keyframes.copy()

        #focusing以外のグループプロパティーはここで纏める
        included_gp = {}
        for p in result:
            check_result = check_props_group((tag, layer, p), scene_num)
            if check_result is not None:
                gn, ps = check_result
                if gn != "focusing":
                    args = []
                    for prop in ps:
                        args.append(result[prop])
                    group_cs = []
                    for cs in zip(*args):
                        v = tuple(c[0] for c in cs)
                        if gn in ("matrixtransform", "matrixcolor"):
                            v = generate_matrix_strings(v, gn, ps)
                        group_cs.append((v, cs[0][1], cs[0][2]))
                    included_gp[gn] = (ps, group_cs)
        for gn, (ps, group_cs) in included_gp.items():
            for prop  in ps:
                del result[prop]
            result[gn] = group_cs

        for prop in ("focusing", "dof"):
            if prop in result:
                del result[prop]
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
                key = (tag, layer, p)
            for (p2, cs2) in sorted_list[i+1:]:
                if p2 not in already_added and len(cs) == len(cs2):
                    key2 = (tag, layer, p2)
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


    def x_and_y_to_xy(keyframe_list, layer, tag=None, check_spline=False, check_loop=False):
        for xy, (x, y) in xygroup.items():
            if x in [p for p, cs in keyframe_list] and y in [p for p, cs in keyframe_list]:
                xkey = (tag, layer, x)
                ykey = (tag, layer, y)
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


    def check_focusing_used(layer, scene_num = None):
        if scene_num is None:
            scene_num = current_scene
        return (persistent._viewer_focusing and perspective_enabled(layer, scene_num))


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
            for layer in get_layers():
                if s > 0:
                    string += """
    scene"""
                    if layer != "master":
                        string += " onlayer {}".format(layer)
            for layer in get_layers():
                camera_keyframes = {k[2]:v for k, v in all_keyframes[s].items() if k[0] is None and k[1] == layer}
                camera_keyframes = set_group_keyframes(camera_keyframes, (None, "master", None), s)
                for p, v in camera_keyframes.items():
                    if p in any_props:
                        formated_v = []
                        for c in v:
                            if isinstance(c[0], str):
                                formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                            else:
                                formated_v.append(c)
                        camera_keyframes[p] = formated_v
                camera_properties = []
                for p in camera_state_org[s][layer]:
                    check_result = check_props_group((None, layer, p), s)
                    if check_result is not None:
                        gn, ps = check_result
                        if gn not in camera_properties:
                            camera_properties.append(gn)
                    else:
                        if p not in special_props:
                            camera_properties.append(p)
                if camera_keyframes:
                    string += """
    camera"""
                    if layer == "master":
                        string += ":"
                    else:
                        string += " {layer}:".format(layer=layer)
                    string += """
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
                    for p, cs in x_and_y_to_xy([(p, camera_keyframes[p]) for p in camera_properties if p in camera_keyframes and len(camera_keyframes[p]) == 1], layer):
                        string += "{property} {value}".format(property=p, value=cs[0][0])
                        if persistent._one_line_one_prop:
                            string += "\n        "
                        else:
                            string += " "
                    sorted_list = put_prop_togetter(camera_keyframes, layer=layer)
                    if len(sorted_list):
                        for same_time_set in sorted_list:
                            if len(sorted_list) > 1 or loops[s][(None, layer, xy_to_x(sorted_list[0][0][0]))] or "function" in camera_keyframes:
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
        {tab}{warper} {duration:.2f} """.format(tab=add_tab, warper=warper, duration=cs[i+1][1]-cs[i][1])
                                for p2, cs2 in same_time_set:
                                    string += "{property} {value} ".format(property=p2, value=cs2[i+1][0])
                                    if cs2[i+1][1] in splines[s][(None, layer, xy_to_x(p2))] and splines[s][(None, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                        for knot in splines[s][(None, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                            string += " knot {} ".format(knot)
                            if loops[s][(None, layer, xy_to_x(p))]:
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
                    if tag not in state:
                        continue
                    image_keyframes = {k[2]:v for k, v in all_keyframes[s].items() if k[0] is not None and k[0] == tag and k[1] == layer}
                    image_keyframes = set_group_keyframes(image_keyframes, (tag, layer, None), s)
                    for k, v in image_keyframes.items():
                        if k in any_props:
                            formated_v = []
                            for c in v:
                                if isinstance(c[0], str):
                                    formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                                else:
                                    formated_v.append(c)
                            image_keyframes[k] = formated_v
                    if check_focusing_used(layer, s) and "blur" in image_keyframes:
                        del image_keyframes["blur"]
                    image_properties = []
                    for p in state[tag]:
                        check_result = check_props_group((tag, layer, p), s)
                        if check_result is not None:
                            gn, ps = check_result
                            if gn not in image_properties:
                                image_properties.append(gn)
                        else:
                            if p not in special_props:
                                image_properties.append(p)
                    if image_keyframes or check_focusing_used(layer, s) or tag in image_state[s][layer]:
                        image_name = state[tag]["child"][0]
                        if "child" in image_keyframes:
                            last_child = image_keyframes["child"][-1][0][0]
                            if last_child is not None:
                                last_tag = last_child.split()[0]
                                if last_tag == image_name.split()[0]:
                                    image_name = last_child
                        string += """
    show {}""".format(image_name)
                        #at defaultではATLブロックに配置したdisplayableに機能しない
                        # if tag in image_state[s][layer]:
                        #     string += " at default"
                        if image_name.split()[0] != tag:
                            string += " as {}".format(tag)
                        if layer != "master":
                            string += " onlayer {}".format(layer)
                        string += """:
        """
                        if tag in image_state[s][layer]:
                            string += "default\n        "
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
                            if len(sorted_list) >= 1 or loops[s][(tag, layer, "child")] or check_focusing_used(layer, s) or "function" in image_keyframes:
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
        {tab}{pause:.2f}""".format(tab=add_tab, pause=t-last_time)
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
                                    or "child" in image_keyframes  or check_focusing_used(layer, s) or "function" in image_keyframes:
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
        {tab}{warper} {duration:.2f} """.format(tab=add_tab, warper=warper, duration=cs[i+1][1]-cs[i][1])
                                    for p2, cs2 in same_time_set:
                                        string += "{property} {value} ".format(property=p2, value=cs2[i+1][0])
                                        if cs2[i+1][1] in splines[s][(tag, layer, xy_to_x(p2))] and splines[s][(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                            for knot in splines[s][(tag, layer, xy_to_x(p2))][cs2[i+1][1]]:
                                                string += " knot {} ".format(knot)
                                if loops[s][(tag,layer,xy_to_x(p))]:
                                    string += """
            repeat"""
                        if check_focusing_used(layer, s) or "function" in image_keyframes:
                            for p, cs in image_keyframes.items():
                                if len(cs) > 1 or "child" in image_keyframes:
                                    string += """
        parallel:
            """
                                    break
                            else:
                                string += "\n        "
                            if check_focusing_used(layer, s):
                                focusing_cs = {"focusing":[(get_default("focusing"), 0, None)], "dof":[(get_default("dof"), 0, None)]}
                                for p in props_groups["focusing"]:
                                    if (None, layer, p) in all_keyframes[s]:
                                        focusing_cs[p] = [(v, t-scene_start, w) for (v, t, w) in all_keyframes[s][(None, layer, p)]]
                                if loops[s][(None, layer, "focusing")] or loops[s][(None, layer, "dof")]:
                                    focusing_loop = {}
                                    focusing_loop["focusing_loop"] = loops[s][(None, layer, "focusing")]
                                    focusing_loop["dof_loop"] = loops[s][(None, layer, "dof")]
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
                pause_time = pause_time + 0.1 #add margin
                if pause_time > 0 or s != len(scene_keyframes)-1:
                    string += """
    with Pause({:.2f})""".format(pause_time)

        if (persistent._viewer_hide_window and get_animation_delay() > 0) and len(scene_keyframes) == 1:
            string += """
    with Pause({:.2f})""".format(get_animation_delay()+0.1)
        if (persistent._viewer_hide_window and get_animation_delay() > 0 and persistent._viewer_allow_skip) \
            or len(scene_keyframes) > 1:
            for channel, times in sound_keyframes.items():
                if times:
                    string += "\n    stop {}".format(channel)

            for layer in get_layers():
                for i in range(-1, -len(scene_keyframes)-1, -1):
                    if camera_keyframes_exist(i, layer):
                        break
                last_camera_scene = i
                camera_keyframes = {k[2]:v for k, v in all_keyframes[last_camera_scene].items() if k[0] is None and k[1] == layer}
                for p in camera_state_org[last_camera_scene][layer]:
                    if p not in camera_keyframes:
                        if camera_state_org[last_camera_scene][layer][p] is not None and camera_state_org[last_camera_scene][layer][p] != camera_state_org[0][layer][p]:
                            camera_keyframes[p] = [(camera_state_org[last_camera_scene][layer][p], scene_keyframes[last_camera_scene][1], None)]
                camera_keyframes = set_group_keyframes(camera_keyframes, (None, layer, None), last_camera_scene)
                for p, v in camera_keyframes.items():
                    if p in any_props:
                        formated_v = []
                        for c in v:
                            if isinstance(c[0], str):
                                formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                            else:
                                formated_v.append(c)
                        camera_keyframes[p] = formated_v
                if [cs for cs in camera_keyframes.values() if len(cs) > 1]:
                    string += """
    camera"""
                    if layer == "master":
                        string += ":"
                    else:
                        string += " {}:".format(layer)
                    for p, cs in camera_keyframes.items():
                        if len(cs) > 1 and loops[last_camera_scene][(None, layer, p)]:
                            string += """
        animation"""
                            break
                    first = True
                    for p, cs in x_and_y_to_xy(sort_props(camera_keyframes), layer, check_loop=True):
                        if p not in special_props:
                            if len(cs) > 1 and not loops[last_camera_scene][(None, layer, xy_to_x(p))]:
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
                            if len(cs) > 1 and loops[last_camera_scene][(None, layer, p)]:
                                string += """
        parallel:
            {property} {value}""".format(property=p, value=cs[0][0])
                                for i, c in enumerate(cs[1:]):
                                    if c[2].startswith("warper_generator"):
                                        warper = "warp "+ c[2]
                                    else:
                                        warper = c[2]
                                    string += """
            {warper} {duration:.2f} {property} {value}""".format(warper=warper, duration=cs[i+1][1]-cs[i][1], property=p, value=c[0])
                                    if c[1] in splines[last_camera_scene][(None, layer, p)] and splines[last_camera_scene][(None, layer, p)][c[1]]:
                                        for knot in splines[last_camera_scene][(None, layer, p)][c[1]]:
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
                    if tag not in state:
                        continue
                    image_keyframes = {k[2]:v for k, v in all_keyframes[last_scene].items() if k[0] is not None and k[0] == tag and k[1] == layer}
                    image_keyframes = set_group_keyframes(image_keyframes, (tag, layer, None), last_scene)
                    for k, v in image_keyframes.items():
                        if k in any_props:
                            formated_v = []
                            for c in v:
                                if isinstance(c[0], str):
                                    formated_v.append(("'" + c[0] + "'", c[1], c[2]))
                                else:
                                    formated_v.append(c)
                            image_keyframes[k] = formated_v
                    if check_focusing_used(layer, last_scene) and "blur" in image_keyframes:
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
            {warper} {duration:.2f} {property} {value}""".format(warper=warper, duration=cs[i+1][1]-cs[i][1], property=p, value=c[0])
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
            {pause:.2f}""".format(pause=t-last_time)
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

                    if check_focusing_used(layer, last_scene):# or "function" in image_keyframes:
                        # if check_focusing_used(last_scene):
                        focusing_cs = {"focusing":[(get_default("focusing"), 0, None)], "dof":[(get_default("dof"), 0, None)]}
                        if (None, layer, "focusing") in all_keyframes[last_scene]:
                            focusing_cs["focusing"] = all_keyframes[last_scene][(None, layer, "focusing")]
                        if (None, layer, "dof") in all_keyframes[last_scene]:
                            focusing_cs["dof"] = all_keyframes[last_scene][(None, layer, "dof")]
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
                            if not loops[last_scene][(None, layer, "focusing")]:
                                focusing_cs["focusing"] = [focusing_cs["focusing"][-1]]
                            if not loops[last_scene]["dof"]:
                                focusing_cs["dof"] = [focusing_cs["dof"][-1]]
                            if loops[last_scene][(None, layer, "focusing")] or loops[last_scene][(None, layer, "dof")]:
                                focusing_loop = {}
                                focusing_loop["focusing_loop"] = loops[last_scene][(None, layer, "focusing")]
                                focusing_loop["dof_loop"] = loops[last_scene][(None, layer, "dof")]
                                focusing_func_string = "camera_blur({}, {})".format(focusing_cs, focusing_loop)
                            else:
                                focusing_func_string = "camera_blur({})".format(focusing_cs)
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
                + format_exc()
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
