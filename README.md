# ai-assistant.nvim
This is a Neovim plugin that allows ChatGPT to be used from within the editor.
<div style="text-align: center">
  <img src="https://github.com/IwasakiYuuki/ai-assistant.nvim/blob/develop/demo.gif" width="700">
</div>


# Features
- Receive and display ChatGPT's responses in a dedicated chat history buffer.
- Chat history buffer allows you to review past conversations.
- Asynchronous communication with ChatGPT, not blocking your editing experience.


# Requirements
- Neovim nightly
- [rcarriga/nvim-notify](https://github.com/rcarriga/nvim-notify)
- Setting environment `OPENAI_API_KEY` using OpenAI API


# Install
## lazy.nvim
```lua
{
  "rcarriga/nvim-notify",
},
{
  "IwasakiYuuki/ai-assistant.nvim",
  dependencies = { "rcarriga/nvim-notify" },
}
```


# Config
## Call plugin command
Press `<leader>c`, open / close a window to interact with ChatGPT.
```lua
vim.keymap.set('n', '<leader>c', "<cmd>AIAssistantToggle<cr>")
```


## Local Keymap (avaliable in this plugin's windows)
- (normal/insert) Move into chat history: Ctrl-o
- (normal/insert) Move into prompt: Ctrl-i
- (normal/insert) Refresh chat history: Ctrl-r
- (insert) Abort request: Ctrl-c


# Usage
### 1. Open the chat interface
Press `<leader>c` or running the `:AIAssistantToggle` command.

<img src="https://github.com/IwasakiYuuki/ai-assistant.nvim/blob/develop/img/usage_1.png" width="700">

### 2. Send a message
Input your message to ChatGPT via input prompt, and press enter to send request.

<img src="https://github.com/IwasakiYuuki/ai-assistant.nvim/blob/develop/img/usage_2.png" width="700">

### 3. Check response
ChatGPT's response will appear in the chat history window.

<img src="https://github.com/IwasakiYuuki/ai-assistant.nvim/blob/develop/img/usage_3.png" width="700">

### 4. Copy response
Move into chat history window by pressing `Ctrl-o`, copy the ChatGPT's response.

<img src="https://github.com/IwasakiYuuki/ai-assistant.nvim/blob/develop/img/usage_4.png" width="700">

# License
This project is licensed under the MIT License. See the LICENSE file for more details.
