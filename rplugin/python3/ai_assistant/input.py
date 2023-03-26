from pynvim.api.buffer import Buffer


class AIAssistantInput:
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

    def get_win_config(self):
        editor_width, editor_height = self._get_editor_dimensions()
        width = int(editor_width * self.width_ratio)
        height = int(editor_height * self.height_ratio) - 4
        col = int((editor_width - width) / 2)
        row = int((editor_height - height) / 2) + height + 2
        config = {
            "relative": "editor",
            "width": width,
            "height": 1,
            "col": col,
            "row": row,
            "border": "rounded",
            "style": "minimal",
        }
        return config

    def create_buf(self) -> Buffer:
        buf = self.api.create_buf(False, True)
        self.api.buf_set_name(buf, "ai_assistant_input_buf")
        return buf

    def open(self):
        config = self.get_win_config()
        self.window = self.api.open_win(self.buf, True, config)
        return self.window

    def close(self):
        if self.is_open():
            self.api.win_close(self.window, True)
        self.window = None

    def is_open(self):
        return self.window and self.api.win_is_valid(self.window)

    def set_prompt(self):
        self.api.buf_set_option(self.buf, "buftype", "prompt")
        self.nvim.command("call prompt_setprompt({}, '  ')".format(self.buf.number))
        self.nvim.command("call prompt_setcallback({}, 'Aiassistant_start_chat_completion')".format(self.buf.number))

    def unset_prompt(self):
        self.api.buf_set_option(self.buf, "buftype", "nofile")
