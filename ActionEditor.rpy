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
#最初のキーフレームをキーフレームエデイタで編集削除可能に
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

init -1098 python:
    # Added keymap
    config.underlay.append(renpy.Keymap(
        action_editor = renpy.curry(renpy.invoke_in_new_context)(_viewers.open_action_editor),
        image_viewer = _viewers.open_image_viewer,
        ))


init -1600 python in _viewers:
    from renpy.store import Solid, Fixed, Transform, persistent, Null, Matrix, config, Text
    from renpy import config
init python in _viewers:
    from renpy.store import InvertMatrix, ContrastMatrix, SaturationMatrix, BrightnessMatrix, HueMatrix 

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
        if not config.developer:
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
        renpy.exports.show_layer_at(Transform(**kwargs), camera=True)


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
        elif group_name == "alignaround":
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
        key_list = [(tag, layer, prop) for layer in config.layers for tag, props in get_image_state(layer).items() for prop in props]
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
            if prop not in force_float and (prop in force_wide_range
                or ( (state[prop] is None and isinstance(default, int)) or isinstance(state[prop], int) )):
                if isinstance(get_property(key), float) and prop in force_wide_range:
                    if prop in force_plus:
                        v = float(v)
                    else:
                        v -= float(persistent._wide_range)
                else:
                    if prop not in force_plus:
                        v -= persistent._wide_range
            else:
                if prop in force_plus:
                    v = round(float(v), 2)
                else:
                    v = round(v -persistent._narrow_range, 2)

            set_keyframe(key, v, time=time)
            if knot_number is not None:
                splines[current_scene][key][time][knot_number] = v
            change_time(time)
        return changed


    def convert_to_changed_value(value, force_plus, use_wide_range):
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
                    org = get_default(prop, not isinstance(key, tuple))
                if prop == "child" and ((current_scene == 0 and tag in image_state[current_scene][layer])
                    or (current_scene != 0 and time > scene_keyframes[current_scene][1])):
                    org = (None, None)
                all_keyframes[current_scene][key] = [
                    (org, scene_keyframes[current_scene][1], persistent._viewer_warper),
                    (value, time, persistent._viewer_warper)]
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
            polar_coordinate = False
            for prop in ("xalignaround", "yalignaround", "radius", "angle"):
                if prop in all_keyframes[s]:
                    polar_coordinate = True
                    break
            for prop, d in camera_props:
                if polar_coordinate and prop in ("xpos", "ypos"):
                    continue
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
            for layer in config.layers:
                state = get_image_state(layer, s)
                check_points[layer] = {}
                for tag in state:
                    check_points[layer][tag] = {}
                    polar_coordinate = False
                    for prop in ("xalignaround", "yalignaround", "radius", "angle"):
                        if (tag, layer, prop) in all_keyframes[s]:
                            polar_coordinate = True
                            break
                    for prop, d in transform_props:
                        if polar_coordinate and prop in ("xpos", "ypos"):
                            continue
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
                    if persistent._viewer_focusing and get_value("perspective", t, True, scene_num=s):
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
            renpy.show("action_preview", what=Transform(function=renpy.curry(viewer_transform)(
             camera_check_points=camera_check_points, image_check_points=image_check_points,
             scene_checkpoints=deepcopy(scene_keyframes), zorder_list=zorder_list, loop=loop, spline=spline)))
        else:
            renpy.show("action_preview", what=Transform(function=renpy.curry(viewer_transform)(
             camera_check_points=camera_check_points, image_check_points=image_check_points,
             scene_checkpoints=deepcopy(scene_keyframes), zorder_list=zorder_list, loop=loop, spline=spline, time=current_time)))


    def viewer_transform(tran, st, at, camera_check_points, image_check_points, scene_checkpoints, zorder_list, loop, spline=None, subpixel=True, time=None):
        if time is None:
            time = st
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
                    during_transition_displayable = DuringTransitionDisplayble(transition(old_widget, new_widget), time - checkpoint, 0)
                    child = during_transition_displayable
                break
        else:
            child = Transform(function=renpy.curry(camera_transform)(
             camera_check_points=camera_check_points[0], image_check_points=image_check_points[0],
             scene_checkpoints=scene_checkpoints, zorder_list=zorder_list, loop=loop[0], spline=spline[0],
             subpixel=subpixel, time=time, scene_num=0))
        if not persistent._viewer_legacy_gui:
            if round(float(config.screen_width)/config.screen_height, 2) == 1.78:
                box.add(Transform(zoom=preview_size, xpos=(1 - preview_size)/2)(child))
                box.add(Solid(preview_background_color, xsize=config.screen_width, ysize=(1-preview_size), ypos=preview_size))
                box.add(Solid(preview_background_color, xsize=(1-preview_size)/2, ysize=preview_size, xpos=0.))
                box.add(Solid(preview_background_color, xsize=(1-preview_size)/2, ysize=preview_size, xalign=1.))
                if persistent._viewer_rot:
                    for i in range(1, 3):
                        box.add(Solid("#F00", xsize=preview_size, ysize=1, xpos=(1-preview_size)/2, ypos=preview_size*i/3))
                        box.add(Solid("#F00", xsize=1, ysize=preview_size, xpos=preview_size*i/3+(1-preview_size)/2))
            else:
                box.add(Transform(zoom=preview_size)(child))
                box.add(Solid(preview_background_color, xsize=config.screen_width, ysize=(1-preview_size), ypos=preview_size))
                box.add(Solid(preview_background_color, xsize=(1-preview_size), ysize=preview_size, xalign=1.))
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
                                            result = Matrix.offset(ox, oy, oz)*Matrix.rotate(rx, ry, rz)
                                            setattr(tran, gn, result)
                                        elif gn == "matrixanchor":
                                            mxa, mya = group_cache[gn]["matrixanchorX"], group_cache[gn]["matrixanchorY"]
                                            result = (mxa, mya)
                                            setattr(tran, gn, result)
                                        elif gn ==  "matrixcolor":
                                            i, c, s, b, h = group_cache[gn]["invert"], group_cache[gn]["contrast"], group_cache[gn]["saturate"], group_cache[gn]["bright"], group_cache[gn]["hue"]
                                            result = InvertMatrix(i)*ContrastMatrix(c)*SaturationMatrix(s)*BrightnessMatrix(b)*HueMatrix(h)
                                            setattr(tran, gn, result)
                                        elif gn == "crop":
                                            result = (group_cache[gn]["cropX"], group_cache[gn]["cropY"], group_cache[gn]["cropW"], group_cache[gn]["cropH"])
                                            setattr(tran, gn, result)
                                        elif gn == "alignaround":
                                            result = (group_cache[gn]["xalignaround"], group_cache[gn]["yalignaround"])
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
                                result = Matrix.offset(ox, oy, oz)*Matrix.rotate(rx, ry, rz)
                                setattr(tran, gn, result)
                            elif gn == "matrixanchor":
                                mxa, mya = group_cache[gn]["matrixanchorX"], group_cache[gn]["matrixanchorY"]
                                result = (mxa, mya)
                                setattr(tran, gn, result)
                            elif gn ==  "matrixcolor":
                                i, c, s, b, h = group_cache[gn]["invert"], group_cache[gn]["contrast"], group_cache[gn]["saturate"], group_cache[gn]["bright"], group_cache[gn]["hue"]
                                result = InvertMatrix(i)*ContrastMatrix(c)*SaturationMatrix(s)*BrightnessMatrix(b)*HueMatrix(h)
                                setattr(tran, gn, result)
                            elif gn == "crop":
                                result = (group_cache[gn]["cropX"], group_cache[gn]["cropY"], group_cache[gn]["cropW"], group_cache[gn]["cropH"])
                                setattr(tran, gn, result)
                            elif gn == "alignaround":
                                result = (group_cache[gn]["xalignaround"], group_cache[gn]["yalignaround"])
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
                        tran.set_child(Null())
                        break
                    elif start[0][0] is None:
                        new_widget = FixedTimeDisplayable(renpy.easy.displayable(goal[0][0]), time, at)
                        w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                        old_widget = Null(w, h)
                    elif goal[0][0] is None:
                        old_widget = FixedTimeDisplayable(renpy.easy.displayable(start[0][0]), time, at)
                        w, h = renpy.render(old_widget, 0, 0, 0, 0).get_size()
                        new_widget = Null(w, h)
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
                    child = Null()
                else:
                    fixed_time = time-checkpoint
                    if fixed_time < 0:
                        fixed_time = 0
                    new_widget = FixedTimeDisplayable(renpy.easy.displayable(goal[0][0]), time, at)
                    w, h = renpy.render(new_widget, 0, 0, 0, 0).get_size()
                    old_widget = Null(w, h)
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
                    v = v + persistent._wide_range
                else:
                    v = v + persistent._narrow_range
            if not force_plus or 0 <= v:
                function(v, time=time)
            else:
                renpy.notify(_("Please type plus value"))


    def edit_default_transition():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_input_screen", message="Type transition")
        if v:
            if v == "None":
                v = None
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
                            set_keyframe((added_tag, layer, p), (image_name, persistent._viewer_transition))
                    else:
                        image_state[current_scene][layer][added_tag][p] = getattr(renpy.store.default, p, None)
                change_time(current_time)
                if persistent._viewer_legacy_gui:
                    renpy.show_screen("_action_editor")
                else:
                    renpy.show_screen("_new_action_editor")
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
                set_keyframe((tag, layer, "child"), (string, persistent._viewer_transition), time=time)
                return
        else:
            if new_image and new_image[0] == "None" and org is not None:
                set_keyframe((tag, layer, "child"), (None, persistent._viewer_transition), time=time)
                return
            renpy.notify(_("Please type image name"))
            return


    def toggle_boolean_property(key):
        if isinstance(key, tuple):
            tag, layer, prop = key
            value_org = get_image_state(layer)[tag]["zzoom"]
        else:
            value_org = camera_state_org[key]
        value = get_value(key, scene_keyframes[current_scene][1], True)
        #assume default is False
        if value == value_org or (not value and not value_org):
            set_keyframe(key, not value, time=scene_keyframes[current_scene][1])
        else:
            remove_keyframe(scene_keyframes[current_scene][1], key)
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
        camera_keyframes = {}
        for k, v in all_keyframes[current_scene].items():
            if not isinstance(k, tuple):
                value = get_value(k, current_time)
                if isinstance(value, float):
                    value = round(value, 3)
                camera_keyframes[k] = [(value, 0, None)]
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
            string += "{} {}".format(p, cs[0][0])
            if persistent._one_line_one_prop:
                string += "\n        "
            else:
                string += " "

        string = '\n'.join(filter(lambda x: x.strip(), string.split('\n')))
        string = "\n"+ string + "\n\n"

        try:
            from pygame import scrap, locals
            scrap.put(locals.SCRAP_TEXT, string)
        except:
            renpy.notify(_("Can't open clipboard"))
        else:
            renpy.notify(__('Placed \n"%s"\n on clipboard') % string)


    def put_image_clipboard(tag, layer):
        image_keyframes = {}
        for k, v in all_keyframes[current_scene].items():
            if isinstance(k, tuple) and k[0] == tag and k[1] == layer:
                value = get_value(k, current_time)
                if isinstance(value, float):
                    value = round(value, 3)
                image_keyframes[k[2]] = [(value, 0, None)]
        image_keyframes = set_group_keyframes(image_keyframes)
        if (persistent._viewer_focusing and get_value("perspective", scene_keyframes[current_scene][1], True)) \
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
    default"""
            if persistent._one_line_one_prop:
                string += "\n        "
            else:
                string += " "
        for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes]):
            if string.find(":") < 0:
                string += ":\n        "
            string += "{} {}".format(p, cs[0][0])
            if persistent._one_line_one_prop:
                string += "\n        "
            else:
                string += " "
        if persistent._viewer_focusing and get_value("perspective", scene_keyframes[current_scene][1], True):
            focus = get_value("focusing", current_time, True)
            dof = get_value("dof", current_time, True)
            result = "function camera_blur({'focusing':[(%s, 0, None)], 'dof':[(%s, 0, None)]})" % (focus, dof)
            string += "\n        "
            string += result

        string = '\n'.join(filter(lambda x: x.strip(), string.split('\n')))
        string = "\n"+ string + "\n\n"
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
        i = len(scene_keyframes)
        current_scene = i
        scene_keyframes.insert(current_scene, (persistent._viewer_transition, current_time, None))
        image_state.insert(current_scene, {})
        image_state_org.insert(current_scene, {})
        camera_state_org.insert(current_scene, {})
        zorder_list.insert(current_scene, {})
        all_keyframes.insert(current_scene, {})
        sorted_keyframes.insert(current_scene, [])
        for l in config.layers:
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
        if persistent._viewer_legacy_gui:
            renpy.show_screen("_action_editor")
        elif persistent._open_only_one_page:
            renpy.show_screen("_new_action_editor")
        renpy.restart_interaction()


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
        if persistent._viewer_legacy_gui:
            renpy.show_screen("_action_editor")
        elif persistent._open_only_one_page:
            renpy.show_screen("_new_action_editor")
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
            for i, (v, t, w) in enumerate(cs):
                cs[i] = (v, t - (old - new), w)
                if splines[new_scene_num][k]:
                    for t in splines[new_scene_num][k]:
                        knots = splines[new_scene_num][k].pop(t)
                        splines[new_scene_num][k][t - (old - new)] = knots
        sorted_keyframes[new_scene_num] = [t-(old-new) for t in sorted_keyframes[new_scene_num]]
        
        if persistent._viewer_legacy_gui:
            renpy.show_screen("_action_editor")
        else:
            renpy.show_screen("_new_action_editor")
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
        if persistent._viewer_legacy_gui:
            renpy.show_screen("_action_editor")
        elif persistent._open_only_one_page:
            renpy.show_screen("_new_action_editor")
        change_time(current_time)


    def select_default_warper():
        v = renpy.invoke_in_new_context(renpy.call_screen, "_warper_selecter")
        if v:
            persistent._viewer_warper = v


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
                            or (remove_time == scene_keyframes[current_scene][1]
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
                return False
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
        play(False)
        renpy.restart_interaction()


    def open_action_editor():
        global current_time, current_scene, scene_keyframes, zorder_list
        if not config.developer:
            return
        current_time = 0
        current_scene = 0
        moved_time = 0
        loops = [defaultdict(lambda:False)]
        splines = [defaultdict(lambda:{})]
        clear_keyframes()
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
        zorder_list = [{}]
        for l in config.layers:
            zorder_list[current_scene][l] = renpy.get_zorder_list(l)
        scene_keyframes = [(None, 0, None)]
        action_editor_init()
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
                        elif gn == "alignaround":
                            v = "(%s, %s)"
                            r = [(v%(xa[0], ya[0]), xa[1], xa[2]) for xa, ya in zip(group_cache[gn]["xalignaround"], group_cache[gn]["yalignaround"])]
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
        if persistent._one_line_one_prop:
            result_dict = {k:v for same_time_set in result for (k, v) in same_time_set}
            result.clear()
            for p in sort_ref_list:
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
        subpixel True"""
                if "crop" in camera_keyframes:
                    string += " {} {}".format("crop_relative", True)
                if persistent._one_line_one_prop:
                    string += "\n        "
                else:
                    string += " "
                #デフォルトと違っても出力しない方が以前の状態の変化に柔軟だが、
                #xposのような元がNoneやmatrixtransformのような元のマトリックスの順番が違うとアニメーションしない
                #rotateは設定されればキーフレームに入り、されてなければ問題ない
                #アニメーションしないなら出力しなくてよいのでここでは不要
                for p, cs in x_and_y_to_xy([(p, camera_keyframes[p]) for p in camera_properties if p in camera_keyframes and len(camera_keyframes[p]) == 1]):
                    string += "{} {}".format(p, cs[0][0])
                    if persistent._one_line_one_prop:
                        string += "\n        "
                    else:
                        string += " "
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
                    if (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)) \
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
                    if image_keyframes or (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)) \
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
                        if persistent._one_line_one_prop:
                            string += "\n        "
                        for p, cs in x_and_y_to_xy([(p, image_keyframes[p]) for p in image_properties if p in image_keyframes and len(image_keyframes[p]) == 1], layer, tag):
                                string += "{} {}".format(p, cs[0][0])
                                if persistent._one_line_one_prop:
                                    string += "\n        "
                                else:
                                    string += " "
                        sorted = put_prop_togetter(image_keyframes, layer, tag)
                        if "child" in image_keyframes:
                            if len(sorted) >= 1 or loops[s][(tag, layer, "child")] or (persistent._viewer_focusing \
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
                                or (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)):
                                add_tab = "    "
                            else:
                                add_tab = ""
                            for same_time_set in sorted:
                                if len(sorted) > 1 or loops[s][(tag, layer, xy_to_x(sorted[0][0][0]))] or "child" in image_keyframes \
                                    or (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)):
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
                        if (persistent._viewer_focusing and get_value("perspective", scene_keyframes[s][1], True, s)):
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
                                    focusing_cs[p] = [(v, t-scene_start, w) for (v, t, w) in all_keyframes[s][p]]
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
                if pause_time > 0 or s != len(scene_keyframes)-1:
                    string += """
    with Pause({})""".format(pause_time)

        if (persistent._viewer_hide_window and get_animation_delay() > 0) and len(scene_keyframes) == 1:
            string += """
    with Pause({})""".format(get_animation_delay())
        if (persistent._viewer_hide_window and get_animation_delay() > 0 and persistent._viewer_allow_skip) \
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
                                string += "{} {}".format(p, cs[-1][0])
                                if persistent._one_line_one_prop:
                                    string += "\n        "
                                else:
                                    string += " "
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
                    if (persistent._viewer_focusing and get_value("perspective", scene_keyframes[last_scene][1], True, last_scene)) \
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
                                string += "{} {}".format(p, cs[-1][0])
                                if persistent._one_line_one_prop:
                                    string += "\n        "
                                else:
                                    string += " "

                    if (persistent._viewer_focusing and get_value("perspective", scene_keyframes[last_scene][1], True, last_scene)):
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
