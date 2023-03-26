function! Aiassistant_start_chat_completion(msg) abort
  call _aiassistant_start_chat_completion(a:msg)
endfunction

function! Aiassistant_chat_update() abort
  call _aiassistant_chat_update()
endfunction

autocmd User AIAssistantChatUpdate :call Aiassistant_chat_update()
