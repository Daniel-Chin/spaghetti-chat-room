'''
user_list is a safe of list of safes of users. 
'''
print('Loading...')
import sys
from socket import socket
from myhttp import *
from queue import Empty
from time import sleep, time
from mythread import Safe
from console import console
IP = '10.209.0.218'
MAX_HEARTDEAD = 1

class User:
    def __init__(self, name):
        self.name = name
        self.last_heartbeat = time()
        self.msgs = []
        self.last_peek = ''
    
    def heartbeat(self):
        self.last_heartbeat = time()
    
    def isDead(self):
        return time() - self.last_heartbeat > MAX_HEARTDEAD
    
    def getUpdate(self):
        if self.msgs:
            msgs = self.msgs
            self.msgs = []
            return ('msgs', msgs)
        peek = server.peek_board.get()
        if peek != self.last_peek:
            self.last_peek = peek
            return ('peek', peek)
        return None
    
    def newLastPeek(self, peek):
        self.last_peek = peek
    
    def append(self, msg):
        self.msgs.append(msg)

class MyOneServer(OneServer):
    request_filter = ['pull']
    
    def handle(self, request):
        if request.target[:2] in ('/', '/?'):
            self.respond(page())
            log(self, 'page.html sent. ')
            return
        if request.target not in ('/pull', '/push', '/leak'):
            log(self, 'unidentified request:', request)
            self.respond(b'', do_log=False)
            return
        if len(request.body) < 12:
            log(self, 'Illegal username. ', request)
            self.respond(b'')
            return
        user_name = request.body[:12]
        assert len(user_name) == 12
        user_list_copy = server.user_list.call(dict.copy)
        try:
            userSafe = user_list_copy[user_name]
        except KeyError:
            log(self, 'Hello,', user_name)
            userSafe = Safe(User(user_name))
            with server.user_list:
                server.user_list.value[user_name] = userSafe 
            for userSafe_to_hello in user_list_copy.values():
                userSafe_to_hello.call(User.append, 
                                       user_name + ' entered the chat. ')
        userSafe.call(User.heartbeat)
        if request.target == '/pull':
            for i in range(6):
                update = userSafe.call(User.getUpdate)
                if update is None:
                    sleep(.05)
                    userSafe.call(User.heartbeat)
                else:
                    if update[0] == 'msgs':
                        self.respond(('MSG__' + '<br>'.join(update[1])).encode())
                        server.peek_board.set('')
                    else:
                        self.respond(('PEEK_' + update[1]).encode())
                    break
            else:
                self.respond(('QUIET' + server.getStrUserList()).encode(), 
                             do_log = False)
        if request.target == '/push':
            msg = request.body[12:]
            if msg != '':
                user_list_copy = server.user_list.call(dict.copy).values()
                for userSafe_to_msg in user_list_copy:
                    userSafe_to_msg.call(User.append, 
                                           user_name + ': ' + msg)
            self.respond(b'', do_log=False)
        elif request.target == '/leak':
            msg = request.body[12:]
            str_peek = user_name + ': ' + msg
            server.user_list.call(dict.copy)[user_name].call(
                User.newLastPeek, str_peek)
            server.peek_board.set(str_peek)
            self.respond(b'', do_log=False)

class MyServer(Server):
    def __init__(self, my_OneServer = OneServer, port = 80, listen = 1):
        Server.__init__(self, my_OneServer, port, listen)
        self.user_list = Safe({})
        self.peek_board = Safe('')
    
    def getStrUserList(self):
        names = []
        for name in self.user_list.call(dict.copy).keys():
            names.append(name.strip('_'))
        return '; '.join(names)
    
    def interval(self):
        user_list_copy = self.user_list.call(dict.copy).items()
        for user_name, userSafe in user_list_copy:
            if userSafe.call(User.isDead):
                log('Goodbye,', user_name)
                self.user_list.call(dict.pop, user_name)
                for _, userSafe_to_bye in user_list_copy:
                    userSafe_to_bye.call(User.append, user_name + 
                                         ' left the chat. ')

def page():
    with open('page.html', 'rb') as f:
        html = f.read()
    with open('js.js', 'rb') as f:
        return html + f.read()

def close():
    server.close()

def start():
    global server
    server = MyServer(MyOneServer)
    server.start()

def restart():
    server.close()
    start()

start()
console(globals())
server.close()
sleep(1)
print('done')
sys.exit(0)
