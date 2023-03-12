function! Aiassistant_open_win() abort
  call _aiassistant_open_win()
endfunction

function! Aiassistant_close_win() abort
  call _aiassistant_close_win()
endfunction

function! Aiassistant_prompt_callback(msg) abort
  call _aiassistant_prompt_callback(a:msg)
endfunction

command! AIAssistantOpenWin call Aiassistant_open_win()
command! AIAssistantCloseWin call Aiassistant_close_win()
