import asyncio


class AIAssistantOutput:
    def __init__(self, nvim, width_ratio, height_ratio):
        self.nvim = nvim
        self.api = nvim.api
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.buf = self.create_buf()
        self.window = None
        self.history = []
        self.token = 0

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
        row = int((editor_height - height) / 2)
        config = {
            "relative": "editor",
            "width": width,
            "height": height,
            "col": col,
            "row": row,
            "border": "rounded",
            "style": "minimal",
            "zindex": 50,
            "title": "Chat History",
            "title_pos": "center",
        }
        return config

    def create_buf(self):
        buf = self.api.create_buf(False, True)
        self.api.buf_set_name(buf, "ai_assistant_output_buf")
        return buf

    def open(self):
        config = self.get_win_config()
        self.window = self.api.open_win(self.buf, False, config)
        return self.window

    def close(self):
        if self.is_open():
            self.api.win_close(self.window, True)
        self.window = None

    def is_open(self):
        return self.window and self.api.win_is_valid(self.window)

    def show(self):
        self.show_history()

    def get_history(self):
        return self.history

    def add_history(self, message):
        self.history.append(message)

    def show_history(self):
        lines = []
        for message in self.history:
            role = message["role"]
            content = message["content"]
            if role == "system":
                lines.append("  AI")
            elif role == "user":
                lines.append("  user")
            for line in content.split("\n"):
                lines.append(line)
            lines.append("")
        self.set_lines(lines)
        if self.window and self.is_open():
            # self.nvim.command("call win_execute({}, 'normal G')".format(self.window.handle))
            self.nvim.api.win_set_cursor(self.window.handle, (len(self.window.buffer), 0))

    def set_lines(self, lines):
        self.buf[:] = lines

    def set_token(self, token):
        self.token = token

    def get_cost(self):
        cost = 0.002 * 0.001 * self.token
        return cost

    def refresh(self):
        self.history = []
        self.show()
