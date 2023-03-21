from pynvim.api.buffer import Buffer
from abc import ABC, abstractmethod


class AIAssistantBase(ABC):
    def __init__(self, nvim, width_ratio, height_ratio):
        self.nvim = nvim
        self.api = nvim.api
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.buf = self.create_buf()
        self.window = None

    def _get_editor_dimensions(self):
        width = self.nvim.eval("&columns")
        height = self.nvim.eval("&lines")
        if not (isinstance(width, int) and isinstance(height, int)):
            raise TypeError(
                    "&columns, &lines were not expected type (int), got {} (&columns) , {} (&lines)"
                    .format(type(width), type(height))
                    )

        return width, height

    @abstractmethod
    def get_win_config(self) -> dict:
        ...

    @abstractmethod
    def create_buf(self) -> Buffer:
        ...

    @property
    @abstractmethod
    def entering(self) -> bool:
        ...
    
    def open(self):
        config = self.get_win_config()
        self.window = self.api.open_win(self.buf, self.entering, config)
        return self.window

    def close(self):
        if self.is_open():
            self.api.win_close(self.window, True)
        self.window = None

    def is_open(self):
        return self.window and self.api.win_is_valid(self.window)
