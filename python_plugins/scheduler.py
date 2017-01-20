import vim
import threading
import os
import signal
import time
import subprocess
import random
import string
import re


class ScriptProcess(threading.Thread):
    def __init__(self, uid, args, message_queue, commandwindow):
        threading.Thread.__init__(self)
        self.uid = uid
        self.args = args
        self.message_queue = message_queue
        self.process_queue = None
        self.process = None
        self.stop_var = False
        self.lock = threading.Lock()

        self.commandwindow = commandwindow
        self.defaultbuffer = "log.output"

    def run(self):
        if self.process_queue is None:
            self.message_queue.push_message(defaultbuffer, self.uid + " - ERROR!")
            self.stop()
     
        arguments = self.args.split(' ')

        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, shell=False)
        
        while True:
            self.lock.acquire()
            if self.stop_var:
                self.lock.release()
                break
            self.lock.release()
            nextline = self.process.stdout.readline()
            
            if nextline == '' and self.process.poll() is not None:
                break
            if nextline:
                self.message_queue.push_message(self.defaultbuffer, nextline)

            #if self.process.poll() is not None:
            #    self.message_queue.push_message(self.defaultbuffer, self.uid + "\n" + self.process.stdout.readline())
            #    break

            #self.message_queue.push_message(self.defaultbuffer, readline + "\n")
            #time.sleep(1)
                
        self.process_queue.remove_process_from_queue(self.uid)

    def stop(self):
        if self.process is not None and self.process.poll() is None:
            #self.commandwindow.command("echo \"Killing the subprocess\"")
            print("Killing the subprocess")
            self.process.terminate()
            #os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        self.lock.acquire()
        self.stop_var = True
        self.lock.release()

class ProcessQueue():
    def __init__(self, commandwindow):
        self.name = "Processes"
        self.pqueue = []
        self.lock = threading.Lock()
        self.commandwindow = commandwindow
    
    def get_queue(self):
        queue_str = "Current queue:\n"
        for i in self.pqueue:
            queue_str = queue_str + i.uid + "\n"
        return queue_str

    def push_process_to_queue(self, process):
        self.lock.acquire()
        self.pqueue.append(process)
        self.lock.release()

    def kill_process(self, uid):
        self.lock.acquire()
        for p in range(len(self.pqueue)):
            if self.pqueue[p].uid == uid:
                self.pqueue[p].stop()
                del self.pqueue[p]
        self.lock.release()

    def remove_process_from_queue(self, process_uid): 
        self.lock.acquire()

        for p in range(len(self.pqueue)):
            if self.pqueue[p].uid == process_uid:
                del self.pqueue[p]
                break

        self.lock.release()
    def clear_queue(self):
        self.lock.acquire()
        for i in range(len(self.pqueue)):
            self.pqueue[i].stop()
        self.lock.release()

    def generate_random_id(self):
        unique_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.lock.acquire()
        for p in range(len(self.pqueue)):
            if self.pqueue[p].uid == unique_id:
                self.lock.release()
                unique_id = self.generate_random_id()
                self.lock.acquire()
                break
        self.lock.release()
        return unique_id

class MessageQueue():
    def __init__(self, commandwindow, autoupdate):
        self.message_queue = []
        self.lock = threading.Lock()
        self.commandwindow = commandwindow
        self.autoupdate = autoupdate
        #self.message_queue = queue.Queue()
    
    def push_message(self, buffername, message):
        self.lock.acquire()
        if (self.autoupdate):
            self.commandwindow.appendtobuffer(buffername, message)
        else:
            self.message_queue.append(buffername + ";%;" + message)
        #vim.command("echo \"Appended\"")
        self.lock.release()
        #self.message_queue.put(message)
    
    def get_message(self):
        if len(self.message_queue) == 0:
            return ""
        else:
            item = self.message_queue[0]
            del self.message_queue[0]
            return item

class WindowUpdater():
    def __init__(self):
        self.lock = threading.Lock()

    def command(self, command):
        self.lock.acquire()
        vim.command(command)
        self.lock.release()
        
    def appendtobuffer(self, buffername, message):
        self.lock.acquire()
        buffers = vim.buffers
        found_buffer = ""
        for b in buffers:
            if (re.match(".*?"+re.escape(buffername), b.name)):
                #message_rows = message.split('\n')
                found_buffer = b.name
                b.append(message)
                #for m in message_rows:
                #    b.append(m)
                break
            #else:
            #    vim.command("echo \"Buffername " + b.name + "\"")
        
        self.lock.release()

class Scheduler():
    def __init__(self):
        self.autoupdate = True
        self.commandwindow = WindowUpdater()
        self.processes = ProcessQueue(self.commandwindow)
        self.messages = MessageQueue(self.commandwindow, self.autoupdate)

        #self.commandwindow.command('botright vnew log.output')

    def __del__(self):
        #self.commandwindow.command("echom \"Stopping the program\"")
        print("Stopping the program")
        self.stop()

    def stop(self):
        #self.commandwindow.command("echo \"Terminating all remaining threads..\"")
        print("Terminating all reamining threads...")  
        self.processes.clear_queue()

    def kill_process(self, args):
        self.processes.kill_process(args)

    def get_process_queue(self):
        message = "echo \"" + self.processes.get_queue() + "\""
        #message = "echo \"" + "\"something\""
        #self.commandwindow.command(message)
        print(Self.processes.get_queue())

    def start_new_process(self, args):
         process = ScriptProcess(self.processes.generate_random_id(), args, self.messages, self.commandwindow)
         process.process_queue = self.processes
         self.processes.push_process_to_queue(process)
         process.start()
         #self.commandwindow.command("echo \"Done\"")

    def check_messages(self):
        #self.commandwindow.command("echo \"Number of messages " + str(len(self.messages.message_queue)) + "\"")
        print("Number of messages " + str(len(self.messages.message_queue)))
        message = self.messages.get_message()
        if message is not None and message != '':
            buff_and_message = message.split(';%;')
            self.commandwindow.appendtobuffer(buff_and_message[0], buff_and_message[1])
            #self.commandwindow.command("echo \"" + message + "\"\n")

    def create_new_buffer(self, args):
        self.commandwindow.command("botright vnew log.output")
        b = vim.current.buffer
        b.append(args)
        #vim.command("echo \"" + b.name + "\"")
         
