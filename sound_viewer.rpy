#Sound Viewer
#Open by shift + S
#The files in only game/audio/**/* is shown

screen _sound_selector(default=""):
    default filter_string = default
    key "game_menu" action Return("")
    on "hide" action Stop("music")
    zorder 20
    frame:
        style_group "sound_selecter"
        vbox:
            label _("type filenames(ex: variable or [[variable, variable])") style "sound_selecter_input"
            input value ScreenVariableInputValue("filter_string", default=True, returnable=True) copypaste True style "sound_selecter_input" #changed _tag_input
            $filtered_list = _viewers.filter_sound_name(filter_string)
            viewport:
                mousewheel True
                scrollbars "vertical"
                vbox:
                    for sound_name in filtered_list:
                        $file = renpy.python.py_eval("renpy.store.audio." + sound_name)
                        textbutton sound_name action Return(tuple(sound_name.split())) hovered Play("music", file) unhovered Stop("music")
            textbutton _("clipboard") action [SensitiveIf(filter_string), Function(_viewers.put_clipboard_text, filter_string)] xalign 1.0 idle_background None insensitive_background None
    key "K_TAB" action Function(_viewers.completion, filter_string, filtered_list)

init:
    style sound_selecter_frame:
        background "#0006"
        yfill True
    style sound_selecter_viewport:
        ymaximum 600
    style sound_selecter_input:
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]
    style sound_selecter_button:
        size_group "sound_selecter"
        idle_background None
    style sound_selecter_button_text:
        color "#CCC"
        hover_underline True
        selected_color "#FFF"
        insensitive_color "#888"
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]
        xalign .0

init -2000 python in _viewers:
    def open_sound_viewer():
        if not renpy.config.developer:
            return
        _skipping_org = renpy.store._skipping
        renpy.store._skipping = False
        renpy.invoke_in_new_context(renpy.call_screen, "_sound_selector")
        renpy.store._skipping = _skipping_org

    def filter_sound_name(filter_string):
        filtered_list = []
        if "," in filter_string:
            last_element = filter_string[filter_string.rfind(",")+1:].strip()
        elif "[" in filter_string:  #]"
            last_element = filter_string[1:]
        else:
            last_element = filter_string
        for name in dir(renpy.store.audio):
            if name.startswith(last_element):
                file = renpy.python.py_eval("renpy.store.audio." + name)
                if isinstance(file, str) and renpy.loadable(file):
                    filtered_list.append(name)
        return filtered_list

    def put_clipboard_text(s):
        from pygame import scrap, locals
        scrap.put(locals.SCRAP_TEXT, s)
        renpy.notify("'{}'\nis copied to clipboard".format(s))

    def completion(filter_string, filtered_list):
        if "," in filter_string:
            last_element = filter_string[filter_string.rfind(",")+1:].strip()
        elif "[" in filter_string:  #]"
            last_element = filter_string[1:]
        else:
            last_element = filter_string
        if last_element:
            candidate = []
            for name in dir(renpy.store.audio):
                if name.startswith(last_element):
                    file = renpy.python.py_eval("renpy.store.audio." + name)
                    if isinstance(file, str) and renpy.loadable(file):
                        candidate.append(name)
            if candidate:
                cs = renpy.current_screen()
                cs.scope["filter_string"] += candidate[0][len(last_element):]