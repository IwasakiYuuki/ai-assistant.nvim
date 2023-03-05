import pynvim
from pynvim.api.nvim import Nvim
from typing import List, Dict

from ai_assistant.request_chatgpt import RequestChatGPT


@pynvim.plugin
class AIAssistant:
    def __init__(self, nvim: Nvim):
       self.nvim = nvim 
       self.input_buf = None
       self.input_win = None
       self.output_buf = None
       self.output_win = None

    @pynvim.command("AIAssistantToggle")
    def toggle_aiassistant(self):
        if self.input_win and self.output_win:
            self.close_input_win()
            self.close_output_win()
        else:
            if not self.input_win:
                self.open_input_win()
            if not self.output_win:
                self.open_output_win()

    def open_input_win(self):
        self.nvim.command("vsplit")
        self.input_win = self.nvim.api.get_current_win()
        if not self.input_buf:
            self.input_buf = self.nvim.api.create_buf(False, False)
            self.nvim.api.buf_set_option(self.input_buf, "readonly", False)
        self.nvim.api.win_set_buf(self.input_win, self.input_buf)

    def close_input_win(self):
        self.nvim.api.win_close(self.input_win, True)
        self.input_win = None

    def open_output_win(self):
        self.nvim.command("split")
        self.output_win = self.nvim.api.get_current_win()
        if not self.output_buf:
            self.output_buf = self.nvim.api.create_buf(False, False)
            self.nvim.api.buf_set_option(self.output_buf, "readonly", False)
        self.nvim.api.win_set_buf(self.output_win, self.output_buf)

    def close_output_win(self):
        self.nvim.api.win_close(self.output_win, True)
        self.output_win = None

    @pynvim.command("AIAssistantCodeCompletion")
    def code_completion(self):
        if not (self.input_win and self.output_win):
            self.toggle_aiassistant()        

        instruction = self.nvim.api.buf_get_lines(self.input_buf, 0, -1, False)
        instruction = "\n".join(instruction)
        res = RequestChatGPT.generate_code(instruction)
        res = res.split("\n")
        self.nvim.api.buf_set_lines(self.output_buf, 0, -1, False, res)
