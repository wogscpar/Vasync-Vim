# README #
### What is this repository for? ###

This is a simple implementation for runnning background tasks in vim.

### How do I get set up? ###
Setup:
1. Download the repository.

2. Create a .vim/ftplugin directory in your home directory if non exists.

3. Place the my_python.vim file directly in the ftplugin directory.

4. Create a .vim/ftplugin/python directory.

5. Place the scheduler.py in the .vim/ftplugin/python

6. Add source ~/.vim/frplugin/my_python.vim to your .vimrc

7. Done!

### How to use ###
Run a command such as 'python some_script.py test.txt' with:

:RScript "python some_script.py test.txt"

To check if any background task is finished:

:RScriptMessages

To check which processes that are running:

:RScriptProcesses

To kill a process:

:RScriptProcessesKill "ProcessID"

### Who do I talk to? ###

Owner: Oscar Svensson

Email: wgcp92@gmail.com
