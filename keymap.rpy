init 1100 python:
    config.locked = False
    if _viewers.check_version(23060707):
        config.keymap["action_editor"] = ['shift_K_p']
        config.keymap["image_viewer"] =  ['shift_K_u']
        config.keymap["sound_viewer"] =  ['shift_K_s']
    else:
        config.keymap["action_editor"] = ['P']
        config.keymap["image_viewer"] =  ['U']
        config.keymap["sound_viewer"] =  ['S']
    config.locked = True
