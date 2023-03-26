import pynvim
import pytest
from typing import Generator


@pytest.fixture
def nvim() -> Generator[pynvim.Nvim, None, None]:
    nvim = pynvim.attach("child", argv=['nvim', '--embed'])
    # nvim = pynvim.attach("child", argv=['nvim', '--embed', '-n', '-u', 'NONE'])
    nvim.command("source ~/.config/nvim/init.lua")
    nvim.command("source .nvimrc")
    yield nvim
    nvim.quit()


def test_toggle(nvim: pynvim.Nvim):
    nvim.command("AIAssistantToggle")
    wins = nvim.windows
    input_win = None
    output_win = None
    for win in wins:
        buf = nvim.api.win_get_buf(win)
        buf_name = nvim.api.buf_get_name(buf).split("/")[-1]
        if buf_name == "ai_assistant_input_buf":
            input_win = win
        elif buf_name == "ai_assistant_output_buf":
            output_win = win
    # Are AIAssistant windows open?
    assert input_win != None
    assert output_win != None

    nvim.command("AIAssistantToggle")
    wins = nvim.windows
    input_win = None
    output_win = None
    for win in wins:
        buf = nvim.api.win_get_buf(win)
        buf_name = nvim.api.buf_get_name(buf).split("/")[-1]
        if buf_name == "ai_assistant_input_buf":
            input_win = win
        elif buf_name == "ai_assistant_output_buf":
            output_win = win
    # Are AIAssistant windows close?
    assert input_win == None
    assert output_win == None
    

def test_refresh(nvim: pynvim.Nvim):
    nvim.command("AIAssistantRefresh")
