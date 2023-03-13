import pynvim
from pynvim.api.nvim import Nvim
from ai_assistant.request_chatgpt import RequestChatGPT


@pynvim.plugin
class AIAssistant:
    def __init__(self, nvim: Nvim):
       self.nvim = nvim 
       self.api = nvim.api
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
        input_win = self.open_input_win()
        output_win = self.open_output_win()
        self.set_keymap(input_win.handle, output_win.handle)

    @pynvim.function("_aiassistant_close_win", sync=True)
    def close_win(self, *args):
        self.close_input_win()
        self.close_output_win()

    @pynvim.function("_aiassistant_prompt_callback", sync=True)
    def prompt_callback(self, args):
        instruction = args[0]
        res = RequestChatGPT.generate_code(instruction)
        res = res.split("\n")
        self.api.buf_set_lines(self.output_buf, 0, -1, False, res)

    @pynvim.autocmd("BufEnter", pattern="ai_assistant_input_buf", sync=True)
    def on_input_bufenter(self):
        # Change input buffer type to 'prompt' at every BufEnter event.
        if self.input_buf:
            self.api.buf_set_option(self.input_buf, "buftype", "prompt")
            self.nvim.command("call prompt_setprompt({}, '  ')".format(self.input_buf.number))
            self.nvim.command("call prompt_setcallback({}, 'Aiassistant_prompt_callback')".format(self.input_buf.number))

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

    def init_input_buf(self):
        self.input_buf = self.api.create_buf(False, True)
        self.api.buf_set_name(self.input_buf, "ai_assistant_input_buf")

    def set_keymap(self, input_win_number, output_win_number):
        def _set_keymap(self, mode, lhs, rhs):
            km = self.api.buf_set_keymap
            km(self.input_buf, mode, lhs, rhs, {})
            km(self.output_buf, mode, lhs, rhs, {})

        if self.input_win and self.output_win:
            _set_keymap(self, "n", "<C-k>", ":call nvim_set_current_win({})<cr>".format(input_win_number))
            _set_keymap(self, "n", "<C-j>", ":call nvim_set_current_win({})<cr>".format(output_win_number))

    def open_input_win(self):
        editor_width, editor_height = self.get_editor_dimensions()
        win_config = {
            "relative": "editor",
            "width": int(editor_width * 0.6),
            "height": int(1),
            "col": int(editor_width * 0.2),
            "row": int(editor_height * 0.1),
            "border": "rounded",
            "style": "minimal",
            "title": "input",
            "title_pos": "center",
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

    def open_output_win(self):
        editor_width, editor_height = self.get_editor_dimensions()
        win_config = {
            "relative": "editor",
            "width": int(editor_width * 0.6),
            "height": int(editor_height * 0.5),
            "col": int(editor_width * 0.2),
            "row": int(1 + editor_height * 0.1 + 2),
            "border": "rounded",
            "style": "minimal",
            "title": "output",
            "title_pos": "center",
        }
        self.output_win = self.api.open_win(self.output_buf, False, win_config)
        return self.output_win

    def close_output_win(self):
        if self.output_win and self.api.win_is_valid(self.output_win):
            self.api.win_close(self.output_win, True)
            self.output_win = None

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
