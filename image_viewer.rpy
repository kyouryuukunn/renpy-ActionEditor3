#画像ビューワー
#Shift+U: Open Image Viewer
#2016 1/22 v6.99

screen _image_selecter(default=""):
    default filter_string = default
    default filter_string_cache = default
    key "game_menu" action Return("")
    zorder 20
    frame:
        background "#0006"
        xmaximum 400
        yfill True
        vbox:
            label _("Type a image name") style "image_selecter_input"
            input value ScreenVariableInputValue("filter_string", default=True, returnable=True) copypaste True style "image_selecter_input" #changed _tag_input
            $filtered_list = _viewers.filter_image_name(filter_string)
            viewport:
                mousewheel True
                ymaximum 600
                scrollbars "vertical"
                vbox:
                    style_group "image_selecter"
                    for image_name in filtered_list:
                        textbutton image_name action Return(tuple(image_name.split())) hovered _viewers.ShowImage(tuple(image_name.split())) unhovered Function(renpy.hide, "preview", layer="screens")
            textbutton _("clipboard") action [SensitiveIf(filter_string), Function(_viewers.put_clipboard_text, filter_string)] xalign 1.0 idle_background None insensitive_background None
    if filter_string_cache != filter_string:
        if len(filtered_list) == 1:
            if "preview" not in renpy.get_showing_tags("screens"):
                $filter_string_cache = filter_string
                $_viewers.ShowImage(tuple(filtered_list[0].split()))()
        elif "preview" in renpy.get_showing_tags("screens"):
            $filter_string_cache = filter_string
            $_viewers._image_viewer_hide()
    key "K_TAB" action Function(_viewers.completion, filter_string, filtered_list)

init:
    style image_selecter_input:
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]
    style image_selecter_button:
        size_group "image_selecter"
        idle_background None
    style image_selecter_button_text:
        xalign .0
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]

init -2000 python in _viewers:
    def open_image_viewer():
        if not renpy.config.developer:
            return
        renpy.invoke_in_new_context(renpy.call_screen, "_image_selecter")

    def filter_image_name(filter_string):
        filtered_list = []
        filter_elements = filter_string.split()
        if filter_elements:
            for name in renpy.display.image.images:
                if name[0].startswith(filter_elements[0]):
                    if len(filter_elements) == 1:
                        filtered_list.append(" ".join(name))
                    else:
                        for e in filter_elements[1:]:
                            if e in name:
                                continue
                            else:
                                for e2 in name[1:]:
                                    if e2.startswith(e):
                                        break
                                else:
                                    break
                                continue
                        else:
                            filtered_list.append(" ".join(name))
        else:
            filtered_list = [name[0] for name in renpy.display.image.images]
        return filtered_list

    def put_clipboard_text(s):
        from pygame import scrap, locals
        scrap.put(locals.SCRAP_TEXT, s)
        renpy.notify("'{}'\nis copied to clipboard".format(s))

    def completion(filter_string, filtered_list):
        if filter_string and filter_string[-1] != " ":
            completed_string = filter_string.split()[-1]
            candidate = []
            if len(filter_string.split()) == 1:
                for es in filtered_list:
                    candidate.append(es.split()[0])
            else:
                for es in filtered_list:
                    for e in es.split()[1:]:
                        if e.startswith(completed_string):
                            candidate.append(e)
            cs = renpy.current_screen()
            cs.scope["filter_string"] += candidate[0][len(completed_string):] + " "

    def _image_viewer_hide():
        renpy.hide("preview", layer="screens")
        renpy.restart_interaction()

init -1 python in _viewers:
    @renpy.pure
    class ShowImage(renpy.store.Action, renpy.store.DictEquality):
        def __init__(self, image_name_tuple):
            string=""
            for e in image_name_tuple:
                string += e + " "
            self.string = string.strip()
            self.check = None

        def __call__(self):
            if self.check is None:
                for n in renpy.display.image.images:
                    if set(n) == set(self.string.split()) and n[0] == self.string.split()[0]:
                        self.string=""
                        for e in n:
                            self.string += e + " "
                        self.string = self.string.strip()
                        try:
                            for fn in renpy.display.image.images[n].predict_files():
                                if not renpy.loader.loadable(fn):
                                    self.check = False
                                    break
                            else:
                                self.check = True
                        except:
                            self.check = True #text displayable
            try:
                if self.check:
                    renpy.show(self.string, at_list=[renpy.store.truecenter], layer="screens", tag="preview")
                else:
                    renpy.show("preview", what=renpy.text.text.Text("No files", color="#F00"), at_list=[renpy.store.truecenter], layer="screens")
            except:
                renpy.show("preview", what=renpy.text.text.Text("No files", color="#F00"), at_list=[renpy.store.truecenter], layer="screens")
            renpy.restart_interaction()
