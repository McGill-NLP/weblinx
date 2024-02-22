from dataclasses import dataclass

@dataclass
class Intent:
    SAY = "say"
    CLICK = "click"
    HOVER = "hover"
    TEXT_INPUT = "textinput"
    SUBMIT = "submit"
    CHANGE = "change"
    LOAD = "load"
    SCROLL = "scroll"
    COPY = "copy"
    PASTE = "paste"
    TAB_CREATE = "tabcreate"
    TAB_REMOVE = "tabremove"
    TAB_SWITCH = "tabswitch"
    ACTION = "action"
    UNKNOWN = "<unk>"

    @classmethod
    def from_string(cls, intent):
        intent = intent.lower().strip().replace("_", "")

        mapping = {
            "say": cls.SAY,
            "click": cls.CLICK,
            "hover": cls.HOVER,
            "textinput": cls.TEXT_INPUT,
            "submit": cls.SUBMIT,
            "change": cls.CHANGE,
            "load": cls.LOAD,
            "scroll": cls.SCROLL,
            "copy": cls.COPY,
            "paste": cls.PASTE,
            "tabcreate": cls.TAB_CREATE,
            "tabremove": cls.TAB_REMOVE,
            "tabswitch": cls.TAB_SWITCH,
            "action": cls.ACTION,
        }
        return mapping.get(intent, cls.UNKNOWN)

    @classmethod
    def get_element_intents(cls, as_set=False):
        intents = {
            cls.CLICK,
            cls.HOVER,
            cls.TEXT_INPUT,
            cls.SUBMIT,
            cls.CHANGE,
            cls.SCROLL,
            cls.COPY,
            cls.PASTE,
        }

        if as_set:
            return intents
        else:
            return list(intents)

    @classmethod
    def get_text_intents(cls, as_set=False):
        intents = {cls.SAY, cls.TEXT_INPUT, cls.COPY, cls.PASTE, cls.LOAD, cls.CHANGE}

        if as_set:
            return intents

        else:
            return list(intents)

    @classmethod
    def get_tab_intents(cls, as_set=False):
        intents = {cls.TAB_CREATE, cls.TAB_REMOVE, cls.TAB_SWITCH}

        if as_set:
            return intents
        else:
            return list(intents)

    @classmethod
    def get_eval_intents(cls, as_set=False):
        intents = {
            cls.CHANGE,
            cls.CLICK,
            cls.TEXT_INPUT,
            cls.SAY,
            cls.LOAD,
            cls.SUBMIT,
            cls.SCROLL,
            cls.ACTION,
        }

        if as_set:
            return intents
        else:
            return list(intents)

