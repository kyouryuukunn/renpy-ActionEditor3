init python:

    @renpy.pure
    class ShowAlternateMenu(Action, DictEquality):
        """
         :doc: menu_action

         Show alternate menu screen at the bottom right corner of the cursor.
         That screen can include textbuttons.

         `button_list`
             The list of tuple which has two elements. first is a string used
             as text for textbutton and second is action.
         `menu_width`
             If the x-coordinate of the cursor plus this number is greater than
             :var:`config.scren_witdth`, the menu will be displayed to the left
             of the cursor. default is 300
         `menu_height`
             If the y-coordinate of the cursor plus this number is greater than
             :var:`config.scren_witdth`, the menu will be displayed to the upper
             of the cursor. default is 300
         `style_prefix`
             If not None, this is used for menu screen as style_prefix.

         """
        def __init__(self, button_list, menu_width=300, menu_height=200, style_prefix=None):
            self.button_list = button_list
            self.style_prefix = style_prefix
            self.menu_width = menu_width
            self.menu_height = menu_height

        def predict(self):
            renpy.predict_screen("_alternate_menu", self.button_list, 
                menu_width=self.menu_width, menu_height=self.menu_height, style_prefix=self.style_prefix, _transient=True)

        def __call__(self):

            renpy.show_screen("_alternate_menu", self.button_list, 
                menu_width=self.menu_width, menu_height=self.menu_height, style_prefix=self.style_prefix, _transient=True)
            renpy.restart_interaction()


init -1500:
    screen _alternate_menu(button_list, menu_width=300, menu_height=200, style_prefix=None):
        key ["game_menu", "dismiss"] action Hide("_alternate_menu")
        modal True

        $(x, y) = renpy.get_mouse_pos()

        frame:
            if style_prefix:
                style_prefix style_prefix
            pos (x, y)
            if x + menu_width > config.screen_width:
                xanchor 1.0
            else:
                xanchor 0.0
            if y + menu_height > config.screen_height:
                yanchor 1.0
            else:
                yanchor 0.0
            vbox:
                xfill False
                for text, action in button_list:
                    if not isinstance(action, list):
                        $action = [action]
                    textbutton text action action+[Hide("_alternate_menu")]
