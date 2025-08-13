import pygame as pg


class FontManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        pg.font.init()
        self._fonts = {}
        self._initialized = True

    def load_font(self, name, size, font_path=None):
        if (name, size) not in self._fonts:
            if font_path:
                font = pg.font.Font(font_path, size)
            else:
                font = pg.font.SysFont(name, size)
            self._fonts[(name, size)] = font
        return self._fonts[(name, size)]

    def get_font(self, name, size):
        return self._fonts.get((name, size))

    def unload_font(self, name, size):
        if (name, size) in self._fonts:
            del self._fonts[(name, size)]

    def unload_all_fonts(self):
        self._fonts = {}
