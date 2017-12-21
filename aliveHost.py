import botogram
from datetime import datetime
import json
import re
import time
import threading
import requests
import sys
import subprocess
import socket
bot  = botogram.create('441586309:AAGfrlV7RniRRSrn9rUlSkriqvvEajXBVt4')
status={0: 'Alive',1 : 'Dead', 2:"No connection to internet"}
ports={22:'ssh',80:'http',443:'https',23:'telnet',21:'ftp',25:'smtp',110:'pop3',143:'impap'}
userLock=threading.Lock()



class Host:
    def __init__(self,ip,nickname,state=1):
        self.ip = ip
        self.state = state
        self.nickname=nickname
        self.old_state = state
        self.thread_active=True
        self.thread=threading.Thread(target=self.check,)

    def start_thread(self):
        self.thread.start()

    def stop_thread(self):
        self.thread_active = False


    def check(self):        
        while self.thread_active:            
            self.state = subprocess.call(['ping','-c 2','-i 0.2',self.ip],stdout=subprocess.PIPE)
            if self.old_state != self.state:
                toggle = self.nickname + ' ' + self.ip + ' ' + status[self.state]
                print (toggle)
                with lock_log:
                    with open('aliveHost.log','a') as f:
                        f.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+' host '+self.nickname+' '+self.ip+' is now '+status[self.state]+'\n')                
                with userLock:
                    with open('.chatidlist.txt','r') as user_list:
                        for i in user_list.readlines():
                            requests.get("https://api.telegram.org/bot441586309:AAGfrlV7RniRRSrn9rUlSkriqvvEajXBVt4/sendmessage?chat_id={}&text={}".format(i,toggle))
            else:
                pass
            self.old_state=self.state

def checkport(port,ip,chat):
    global ports
    client = socket.socket()
    client.settimeout(50)
    try:
        client.connect((ip,int(port)))
        client.send(bytes('qwerty', 'utf-8'))
        response=client.recv(1024)
        chat.send('Port {}/{} is open'.format(str(port),ports[port]))
    except socket.timeout:
        pass
    except ConnectionRefusedError:
        pass


@bot.command('start')
def startbot_command(chat, message, args):
    users=list()
    with userLock:
        with open('.chatidlist.txt','r') as u:
            for i in u.readlines():
                user = i.strip('\n')
                users.append(user)
        with open('.chatidlist.txt','a') as u:
            for i in users:
                if i == str(chat.id):
                    chat.send('User already in list')
                    break
            else:    
                u.write(str(chat.id)+'\n')                        
                chat.send('User added, chat id: '+str(chat.id))
                print (str(chat.id)+" added")

@bot.command('stop')
def stop_command(chat,message,args):
    tmp_list=list()
    with userLock:
        with open('.chatidlist.txt','r') as user_list:
            for i in user_list:
                if i.strip('\n') == str(chat.id):
                    chat.send('Id removed')
                    print (i.strip('\n')+' removed')
                else:
                    tmp_list.append(i.strip('\n'))
        with open('.chatidlist.txt','w') as user_list:
            for i in tmp_list:
                user_list.write(i+'\n')



@bot.command('scan')
def scanhost_command(chat, message, args):
    global ports
    port_checking=list()
    chat.send('Scanning...')
    for i in ports.keys():
        t=threading.Thread(target=checkport,args=(i,str(args[0]),chat))
        port_checking.append(t)
    for i in port_checking:
        i.start()
    for i in port_checking:
        i.join()
    chat.send('Other main ports are closed')


status={0: 'Alive',1 : 'Dead', 2:"No connection to internet"}

lock_log = threading.Lock()
with lock_log:
    with open('aliveHost.log','w') as f:
        f.write('Start log\n')
host_list=list()
with open('.chatidlist.txt','w') as f:
    f.write('')
with open('hosts.json','r') as j:   #Elaborate JSON file
    json_obj=json.load(j)

for i in json_obj["hosts"].keys():
    host_list.append(Host(json_obj["hosts"][i],i))  #Initialize the list of host

for h in host_list:
    h.start_thread()
    print ('Thread for host ' + h.nickname + ' start.')
bot.run()                                               #Bisogna per forza ctrl+c per arrestare bot e programma
#   while sys.stdin.read(1)=='':
#       pass
for h in host_list:
    h.stop_thread()
with lock_log:
    with open('aliveHost.log','a') as f:
        f.write('Log end\n')

