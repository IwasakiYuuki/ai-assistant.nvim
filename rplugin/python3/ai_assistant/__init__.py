import pynvim
from pynvim.api.nvim import Nvim
from ai_assistant.request_chatgpt import RequestChatGPT


@pynvim.plugin
class AIAssistant:
    def __init__(self, nvim: Nvim):
       self.nvim = nvim 
       self.api = nvim.api
       self.message_history = []
       self.output_win = None
       self.init_input_buf()
       self.init_output_buf()
       self.input_win = None
       self.output_win = None

    @pynvim.command("AIAssistantToggle")
    def toggle_aiassistant(self):
        if self._is_wins_open():
            self.close_win()
        else:
            self.open_win()

    @pynvim.function("_aiassistant_open_win", sync=True)
    def open_win(self, *args):
        _ = args
        input_win = self.open_input_win()
        output_win = self.open_output_win()
        self.set_keymap(input_win.handle, output_win.handle)

    @pynvim.function("_aiassistant_close_win", sync=True)
    def close_win(self, *args):
        _ = args
        self.close_input_win()
        self.close_output_win()

    @pynvim.function("_aiassistant_chat_completion")
    def chat_completion(self, args):
        input_content = args[0]
        current_input_message = {"role": "user", "content": input_content}
        messages = self.message_history + [current_input_message]
        output_content = RequestChatGPT.chat_completions("gpt-3.5-turbo", messages, timeout=30)
        current_output_message = {"role": "system", "content": output_content}
        self.message_history.append(current_input_message)
        self.message_history.append(current_output_message)
        self.set_history()
        if self.output_win and self._is_wins_open():
            self.nvim.command("echomsg('{}')".format(self.output_win.handle))
            self.nvim.command("call win_execute({}, 'normal G')".format(self.output_win.handle))

    @pynvim.autocmd("BufEnter", pattern="ai_assistant_input_buf", sync=True)
    def on_input_bufenter(self):
        # Change input buffer type to 'prompt' at every BufEnter event.
        if self.input_buf:
            self.api.buf_set_option(self.input_buf, "buftype", "prompt")
            self.nvim.command("call prompt_setprompt({}, '  ')".format(self.input_buf.number))
            self.nvim.command("call prompt_setcallback({}, 'Aiassistant_chat_completion')".format(self.input_buf.number))

    @pynvim.autocmd("WinLeave", pattern="ai_assistant_input_buf,ai_assistant_output_buf")
    def on_input_output_winleave(self):
        buf_name = self.nvim.eval("@%")
        self.nvim.command("echomsg '{}'".format(buf_name))
        entering_another = buf_name not in ("ai_assistant_input_buf", "ai_assistant_output_buf")
        closing = not self._is_wins_open()
        # When you move to another window (not plugin's windows) or
        # any of the plugin's windows are closed
        if entering_another or closing:
            self.close_win()
            # Change input buffer type to 'nofile'.
            # Without this setting, get a warning "save prompt buffer changes" when vim leaving.
            self.api.buf_set_option(self.input_buf, "buftype", "nofile")

    @property
    def width_ratio(self) -> float:
        return 0.6

    @property
    def height_ratio(self) -> float:
        return 0.6

    def init_input_buf(self):
        self.input_buf = self.api.create_buf(False, True)
        self.api.buf_set_name(self.input_buf, "ai_assistant_input_buf")

    def set_keymap(self, input_win_number, output_win_number):
        def _set_keymap(self, mode, lhs, rhs):
            km = self.api.buf_set_keymap
            km(self.input_buf, mode, lhs, rhs, {})
            km(self.output_buf, mode, lhs, rhs, {})

        if self.input_win and self.output_win:
            _set_keymap(self, "n", "<C-i>", ":call nvim_set_current_win({})<cr>".format(input_win_number))
            _set_keymap(self, "n", "<C-o>", ":call nvim_set_current_win({})<cr>".format(output_win_number))

    def open_input_win(self):
        editor_width, editor_height = self.get_editor_dimensions()
        width, height = int(editor_width * self.width_ratio), 1
        output_height = int(editor_height * self.height_ratio)
        col = int((editor_width - width) / 2)
        row = editor_height - (int((editor_height - output_height) / 2) + height - 1)
        win_config = {
            "relative": "editor",
            "width": int(width),
            "height": int(height),
            "col": int(col),
            "row": int(row),
            "border": "rounded",
            "style": "minimal",
        }
        self.input_win = self.api.open_win(self.input_buf, True, win_config)
        return self.input_win

    def close_input_win(self):
        if self.input_win and self.api.win_is_valid(self.input_win):
            self.api.win_close(self.input_win, True)
            self.input_win = None

    def init_output_buf(self):
        self.output_buf = self.api.create_buf(False, True)
        self.api.buf_set_name(self.output_buf, "ai_assistant_output_buf")
        self.api.buf_set_option(self.output_buf, "modifiable", False)

    def open_output_win(self):
        editor_width, editor_height = self.get_editor_dimensions()
        width, height = int(editor_width * self.width_ratio), int(editor_height * self.height_ratio)
        col = int((editor_width - width) / 2)
        row = int((editor_height - height) / 2)
        win_config = {
            "relative": "editor",
            "width": width,
            "height": height - 2,
            "col": col,
            "row": row,
            "border": "rounded",
            "style": "minimal",
            "title": "AI Assistant",
            "title_pos": "center",
        }
        self.output_win = self.api.open_win(self.output_buf, False, win_config)
        return self.output_win

    def close_output_win(self):
        if self.output_win and self.api.win_is_valid(self.output_win):
            self.api.win_close(self.output_win, True)
            self.output_win = None

    def set_history(self):
        # To avoid accidentally changing the output of chatGPT,
        # basically "modifiable" is setted off.
        self.api.buf_set_option(self.output_buf, "modifiable", True)
        lines = []
        for message in self.message_history:
            role = message["role"]
            content = message["content"]
            if role == "system":
                lines.append("  AI")
            elif role == "user":
                lines.append("  user")
            for line in content.split("\n"):
                lines.append(line)
            lines.append("")

        self.api.buf_set_lines(self.output_buf, 0, -1, False, lines)
        self.api.buf_set_option(self.output_buf, "modifiable", False)

    def get_editor_dimensions(self):
        width = self.nvim.eval("&columns")
        height = self.nvim.eval("&lines")
        if not (isinstance(width, int) and isinstance(height, int)):
            raise TypeError(
                "&columns, &lines were not expected type (int), got {} (&columns) , {} (&lines)"
                .format(type(width), type(height))
            )

        return [width, height]

    def _is_wins_open(self):
        input_win = self.api.win_is_valid(self.input_win) if self.input_win else False
        output_win = self.api.win_is_valid(self.output_win) if self.output_win else False
        return input_win and output_win
