import pynvim
from pynvim.api.nvim import Nvim
from ai_assistant.request_chatgpt import RequestChatGPT
from .input import AIAssistantInput
from .output import AIAssistantOutput


@pynvim.plugin
class AIAssistant:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim 
        self.api = nvim.api
        self.input = AIAssistantInput(nvim, self.width_ratio, self.height_ratio)
        self.output = AIAssistantOutput(nvim, self.width_ratio, self.height_ratio)

    @property
    def width_ratio(self) -> float:
        return 0.6

    @property
    def height_ratio(self) -> float:
        return 0.6

    @pynvim.command("AIAssistantToggle")
    def toggle(self):
        if self.is_open():
            self.close()
        else:
            self.open()

    def open(self):
        self.input.open()
        self.output.open()
        self.set_keymap()

    def set_keymap(self):
        def _set_keymap(self, mode, lhs, rhs):
            km = self.api.buf_set_keymap
            km(self.input.buf, mode, lhs, rhs, {"silent": True})
            km(self.output.buf, mode, lhs, rhs, {"silent": True})

        if self.input.window and self.output.window:
            _set_keymap(self, "n", "<C-i>", ":call nvim_set_current_win({})<cr>".format(self.input.window.handle))
            _set_keymap(self, "n", "<C-o>", ":call nvim_set_current_win({})<cr>".format(self.output.window.handle))

    def close(self):
        self.input.close()
        self.output.close()

    def is_open(self):
        is_open = True
        is_open = is_open and self.input.is_open()
        is_open = is_open and self.output.is_open()
        return is_open

    @pynvim.autocmd("BufEnter", pattern="ai_assistant_input_buf", sync=True)
    def on_input_bufenter(self):
        self.input.set_prompt()

    @pynvim.autocmd("WinLeave", pattern="ai_assistant_input_buf,ai_assistant_output_buf")
    def on_input_output_winleave(self):
        buf_name = self.nvim.eval("@%")
        entering_another = buf_name not in ("ai_assistant_input_buf", "ai_assistant_output_buf")
        closing = not self.is_open()
        if entering_another or closing:
            self.close()
            self.input.unset_prompt()

    @pynvim.function("_aiassistant_chat_completion")
    def chat_completion(self, args):
        input_content = args[0]
        current_input_message = {"role": "user", "content": input_content}
        messages = self.output.get_history() + [current_input_message]
        output_content, total_token = RequestChatGPT.chat_completions("gpt-3.5-turbo", messages, timeout=30)
        current_output_message = {"role": "system", "content": output_content}
        self.output.add_history(current_input_message)
        self.output.add_history(current_output_message)
        self.output.add_total_token(total_token)
        self.output.show()
