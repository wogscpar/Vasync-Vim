autocmd FileType python call InitPython() 

pyfile $HOME/.vim/ftplugin/python_plugins/scheduler.py

" Actual vim scripts

function! ErrorMessage(message)
	echohl Error | echomsg a:message | echohl None
endfunction

function! Message(message)
	echomsg a:message
endfunction


function! ScriptAsync(command, ...)
	let l:command = a:command
	if empty(l:command)
		call ErrorMessage("Command was empty...")
	else
		"call Message(l:command)
python <<endpython
sched.start_new_process(vim.eval("l:command"))
endpython
	endif
endfunction

function! CheckProcessMessages()
	python sched.check_messages()
endfunction

function! Processes()
	python sched.get_process_queue()
endfunction

function! KillProcess(command, ...)
	let l:command = a:command
	if empty(l:command)
		call ErrorMessage("Invalid use! :RScriptProcessesKill <ProcessID>")
	else
		call Message(l:command)
python <<endpython
sched.kill_process(vim.eval("l:command"))
endpython
	endif
endfunction

" A test function for running python code


function! ASyncPythonCode()
python << endpython
import vim
vim.current.buffer.append("Last line!")
endpython
endfunction


function MapPython()
	nnoremap <silent> <F9> :exec '!python' shellescape(@%, 1)<cr>
	command! -nargs=* RScript call ScriptAsync(<q-args>)
	command! RScriptProcesses call Processes()
	command! -nargs=* RScriptProcessesKill call KillProcess(<q-args>) 
	command! RScriptMessages call CheckProcessMessages()

	nnoremap <space> za
	nnoremap . :RScriptMessages <cr>
	map <leader>g :YcmCompleter GoToDefinitionElseDeclaration<CR>
endfunction

function ConfigurePython()
	set foldmethod=indent
	set foldlevel=99

	au BufNewFile,BufRead *.py
		\ set tabstop=4
		\ set softtabstop=4
		\ set shiftwidth=4
		\ set textwidth=79
		\ set expandtab
		\ set autoindent
		\ set fileformat=unix
	
	au BufRead,BufNewFile *.py,*.pyw,*.c,*.h match BadWhitespace /\s\+$/

	set encoding=utf8

	let g:ycm_autoclose_preview_window_after_completion=1
	let python_highlight_all=1
	syntax on	

	set nu
endfunction

function InitPython()
	call ConfigurePython()
	call MapPython()
endfunction

autocmd VimLeavePre * python sched.stop()
python sched = Scheduler()
