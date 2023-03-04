import pynvim
from typing import List, Dict


@pynvim.plugin
class AIAssistant:
    def __init__(self, nvim):
       self.nvim = nvim 

    @pynvim.function("requestChatGPT")
    def requestChatGPT(self, model: str, message: List[Dict]):
        """TODO: Docstring for requestChatGPT.

        :model: TODO
        :message: TODO
        :returns: TODO

        """
        pass

    @pynvim.command("OpenCreateCodeBuf")
    def open_create_code_buf(self):
        """TODO: Docstring for open_create_code_buf.

        :returns: TODO

        """
        pass

    @pynvim.command("CloseCreateCodeBuf")
    def close_create_code_buf(self):
        """TODO: Docstring for close_create_code_buf.

        :returns: TODO

        """
        pass

    @pynvim.command("CreateCode")
    def create_code(self):
        """TODO: Docstring for create_code.

        :returns: TODO

        """
        pass
