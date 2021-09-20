#Shift+U: Open Image Viewer
#2016 1/22 v6.99

# screen _image_tag_input(default, string=""):
#     key "game_menu" action Return("")
#     on "show" action Show("_image_selecter", default=default)
#     for e in default:
#         $string += e + " "
#     vbox:
#         button:
#             id "tag_input"
#             action NullAction()
#             add Input(default=string, changed=_tag_input, button=renpy.get_widget("_image_tag_input","tag_input"))
#
# init python:
#     def _tag_input(input):
#         if len(input) and input[-1] == " ":
#             renpy.show_screen("_image_selecter", default=tuple(input.split()))
#             renpy.restart_interaction()

screen _image_selecter(default, string=""):
    key "game_menu" action Return("")
    zorder 20
    for e in default:
        $string += e + " "
    $default_set = set(default)
    frame:
        background "#0006"
        xalign 1.
        has vbox
        label _("Type a image name") style "image_selecter_input"
        # input value ScreenVariableInputValue("string")  #自動絞り込み 謎バグにより使用不可
        input default string style "image_selecter_input" #changed _tag_input
        if default:
            $s = set()
            for name in renpy.display.image.images:
                $name_set = set(name)
                if default_set < name_set:
                    $s.update(name_set-default_set)
                elif default_set == name_set:
                    $s.update(default_set)
        else:
            $s = {name[0] for name in renpy.display.image.images}
        viewport:
            mousewheel True
            xmaximum 400
            # ymaximum 300
            # edgescroll (100, 100)
            scrollbars "both"
            vbox:
                style_group "image_selecter"
                for tag in tuple(s):
                    textbutton tag action Return(default + (tag, )) hovered ShowImage(default, tag) unhovered Function(renpy.hide, "preview", layer="screens")
            # $s=tuple(s)
            # for x in range(0, len(s), 4):
            #     if x+5 < len(s):
            #         hbox:
            #             for tag in s[x:x+4]:
            #                 textbutton tag action Return(default + (tag, )) hovered _viewers.ShowImage(default, tag) unhovered Function(renpy.hide, "preview", layer="screens")
            #     else:
            #         hbox:
            #             for tag in s[x:]:
            #                 textbutton tag action Return(default + (tag, )) hovered _viewers.ShowImage(default, tag) unhovered Function(renpy.hide, "preview", layer="screens")
init:
    style image_selecter_input:
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]
    style image_selecter_button:
        size_group "image_selecter"
        idle_background None
    style image_selecter_button_text:
        xalign .0
        outlines [ (absolute(1), "#000", absolute(0), absolute(0)) ]
init -2000 python:
    def _open_image_viewer():
        if not renpy.config.developer:
            return
        default = ()
        while True:
            name = renpy.invoke_in_new_context(renpy.call_screen, "_image_selecter", default=default)
            if isinstance(name, tuple): #press button
                default = tuple(name)
            elif name: #from input text
                default = tuple(name.split())
            else:
                renpy.notify(_("Please type image name"))
                return

init -1 python:
    @renpy.pure
    class ShowImage(renpy.store.Action, renpy.store.DictEquality):
        def __init__(self, default, tag):
            self.string=""
            for e in default:
                self.string += e + " "
            self.string += tag
            self.check = None

        def __call__(self):
            if self.check is None:
                for n in renpy.display.image.images:
                    if set(n) == set(self.string.split()):
                        self.string=""
                        for e in n:
                            self.string += e + " "
                        try:
                            for fn in renpy.display.image.images[n].predict_files():
                                if not renpy.loader.loadable(fn):
                                    self.check = False
                                    break
                            else:
                                self.check = True
                        except:
                            self.check = True #text displayable
            if self.check:
                renpy.show(self.string, at_list=[renpy.store.truecenter], layer="screens", tag="preview")
            else:
                renpy.show("preview", what=renpy.text.text.Text("No files", color="#F00"), at_list=[renpy.store.truecenter], layer="screens")
            renpy.restart_interaction()

        # def get_sensitive(self):
        #     for n in renpy.display.image.images:
        #         if set(n) == set(self.string.split()):
        #             return True
        #     else:
        #         return False

# init python:
#     @renpy.pure
#     class _ImageInputValue(ScreenVariableInputValue, FieldEquality):
#
#         def __init__(self, variable, default=True):
#             super(_ImageInputValue, self).__init__(variable, default, returnable=True)
#
#         def set_text(self, s):
#             if s and s[-1] == " ":
#                 for n in renpy.display.image.images:
#                     if set(n) == set(name.split()):
#                         self.state[layer][name] = {}
#                         renpy.show(name, layer=layer)
#                         for p, d in self.props:
#                             self.state[layer][name][p] = self.get_property(layer, name.split()[0], p, False)
#                         all_keyframes[(name, layer, "xpos")] = [(self.state[layer][name]["xpos"], 0, None)]
#                         remove_list = [n_org for n_org in self.state_org[layer] if n_org.split()[0] == n[0]]
#                         for n_org in remove_list:
#                             del self.state_org[layer][n_org]
#                             transform_viewer.remove_keyframes(n_org, layer)
#                         sort_keyframes()
#                         renpy.show_screen("_action_editor", tab="images", layer=layer, name=name)
#                         return
#                 default = tuple(s.split())
#                 renpy.show_screen("_image_selecter", default=default)
#             super(_ImageInputValue, self).set_text(s)
#
