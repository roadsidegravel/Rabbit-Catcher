#https://docs.panda3d.org/1.10/python/programming/hardware-support/keyboard-support
# raw- reports the key as if the user has a standard ANSI US qwerty
# and or use get_keyboard_map as explained in the docs

InputMap = {
    #movement
    "up" : False,
    "down" : False,
    "left" : False,
    "right" : False,
    #actions
    "jump" : False,
    "spawn" : False,
    "screenshot": False,
    "menu": False
}

        
def set_default_input(parentSelf):
    parentSelf.inputMap = InputMap
    parentSelf.keyboardMap = base.win.get_keyboard_map()
    parentSelf.accept("raw-w", parentSelf.event_key_change, ["up", True])
    parentSelf.accept("raw-w-up", parentSelf.event_key_change, ["up", False])
    parentSelf.accept("raw-s", parentSelf.event_key_change, ["down", True])
    parentSelf.accept("raw-s-up", parentSelf.event_key_change, ["down", False])
    parentSelf.accept("raw-a", parentSelf.event_key_change, ["left", True])
    parentSelf.accept("raw-a-up", parentSelf.event_key_change, ["left", False])
    parentSelf.accept("raw-d", parentSelf.event_key_change, ["right", True])
    parentSelf.accept("raw-d-up", parentSelf.event_key_change, ["right", False])
    #parentSelf.accept("raw-space", parentSelf.event_key_change, ["spawn", True])
    parentSelf.accept("raw-space-up", parentSelf.event_key_change, ["jump", True])
    #parentSelf.accept("raw-p", parentSelf.event_key_change, ["screenshot",True])
    parentSelf.accept("raw-p-up", parentSelf.event_key_change, ["screenshot",True])
    #parentSelf.accept("raw-escape",parentSelf.event_key_change, ["menu",True])
    parentSelf.accept("raw-escape-up",parentSelf.event_key_change, ["menu",True])