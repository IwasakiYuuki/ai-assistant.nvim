import pynvim
from pynvim.api.nvim import Nvim
from ai_assistant.request_chatgpt import RequestChatGPT


@pynvim.plugin
class AIAssistant:
    def __init__(self, nvim: Nvim):
       self.nvim = nvim 
       self.api = nvim.api
       self.input_buf = None
       self.input_win = None
       self.output_buf = None
       self.output_win = None

    @pynvim.command("AIAssistantToggle")
    def toggle_aiassistant(self):
        if self._is_wins_open():
            self.close_win()
        else:
            self.open_win()

    @pynvim.function("_aiassistant_open_win", sync=True)
    def open_win(self, *args):
        self.open_input_win()
        self.open_output_win()

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

    def init_input_buf(self):
        if not self.input_buf:
            self.input_buf = self.api.create_buf(False, True)
            self.api.buf_set_name(self.input_buf, "ai_assistant_input_buf")

    @pynvim.autocmd("BufEnter", pattern="ai_assistant_input_buf", sync=True)
    def change_input_buf_prompt(self):
        if self.input_buf:
            self.api.buf_set_option(self.input_buf, "buftype", "prompt")
            self.nvim.command("call prompt_setprompt({}, '  ')".format(self.input_buf.number))
            self.nvim.command("call prompt_setcallback({}, 'Aiassistant_prompt_callback')".format(self.input_buf.number))

    @pynvim.autocmd("WinLeave", pattern="ai_assistant_input_buf", sync=True)
    def change_input_buf_nofile(self):
        if self.input_buf:
            self.api.buf_set_option(self.input_buf, "buftype", "nofile")

    def init_output_buf(self):
        if not self.output_buf:
            self.output_buf = self.api.create_buf(False, True)
            self.api.buf_set_name(self.output_buf, "ai_assistant_output_buf")

    def open_input_win(self):
        self.init_input_buf()
        editor_width, editor_height = self.get_editor_dimensions()
        win_config = {
            "relative": "editor",
            "width": int(editor_width * 0.6),
            "height": int(editor_height * 0.2),
            "col": int(editor_width * 0.2),
            "row": int(editor_height * 0.1),
            "border": "rounded",
            "style": "minimal",
            "title": "input",
            "title_pos": "center",
        }
        self.input_win = self.api.open_win(self.input_buf, True, win_config)

    def close_input_win(self):
        if self.input_win and self.api.win_is_valid(self.input_win):
            self.api.win_close(self.input_win, True)
            self.input_win = None

    def open_output_win(self):
        self.init_output_buf()
        editor_width, editor_height = self.get_editor_dimensions()
        win_config = {
            "relative": "editor",
            "width": int(editor_width * 0.6),
            "height": int(editor_height * 0.5),
            "col": int(editor_width * 0.2),
            "row": int(editor_height * 0.3 + 2),
            "border": "rounded",
            "style": "minimal",
            "title": "output",
            "title_pos": "center",
        }
        self.output_win = self.api.open_win(self.output_buf, False, win_config)

    def close_output_win(self):
        if self.output_win and self.api.win_is_valid(self.output_win):
            self.api.win_close(self.output_win, True)
            self.output_win = None

    @pynvim.autocmd("BufEnter", pattern="ai_assistant_input_buf,ai_assistant_output_buf")
    def set_keymap(self):
        pass

    @pynvim.autocmd("WinLeave", pattern="ai_assistant_input_buf,ai_assistant_output_buf", sync=True)
    def on_aiassistant_buf_winleave(self):
        self.close_win()

    def get_editor_dimensions(self):
        windows = self.api.list_wins()
        width = 0
        height = 0
        for window in windows:
            config = self.api.win_get_config(window)
            if config["relative"] == "":
                width += window.width
                height += window.height

        return [width, height]

    def _is_wins_open(self):
        input_win = self.api.win_is_valid(self.input_win) if self.input_win else False
        output_win = self.api.win_is_valid(self.output_win) if self.output_win else False
        return input_win and output_win

    @pynvim.command("AIAssistantCodeCompletion")
    def code_completion(self):
        if not (self.input_win and self.output_win):
            self.toggle_aiassistant()

        instruction = self.api.buf_get_lines(self.input_buf, 0, -1, False)
        instruction = "\n".join(instruction)
        res = RequestChatGPT.generate_code(instruction)
        res = res.split("\n")
        self.api.buf_set_lines(self.output_buf, 0, -1, False, res)
