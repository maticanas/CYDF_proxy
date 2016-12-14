# -*- coding: utf-8 -*-
import socket
import select
import time
import sys
import urlparse
import re
import os
from http_parser.http import HttpStream
from http_parser.reader import SocketReader


#Client, Target
C_HOST = '127.0.0.1' 
C_PORT = 7082
T_HOST = ''
T_PORT = 80
BUFFSIZE = 1024
tstr = "hacking"
cstr = "aaaaaaaaaaaa"

def change_to_deflate(data):
    accept_idx = data.find("Accept-Encoding:")
    if(accept_idx == -1):
        return data
    start_idx = data.find(":", accept_idx) + 1
    end_idx = data.find("\r\n", start_idx)
    num_space = (end_idx - start_idx - 1)
    deflate_str = " deflate"
    deflate_str += " "*(num_space - len(deflate_str))
    cdata = data[:start_idx]
    cdata += deflate_str
    cdata += data[end_idx:]
    print("==============reqeust Accept-Encoding changed to deflate ================")
    print cdata
    
    return cdata

def change(odata):

    num = odata.count(tstr)
    diff = (len(cstr) - len(tstr))*num
    #print diff
    CL = "Content-Length:"
    if(odata.find(CL)==-1):
        return odata
    CLs = odata.find(CL) + len(CL) + 1
    CLe = odata.find("\r\n", CLs)
    CLstr = odata[CLs:CLe]
    print CLstr
    CLstrlen = len(CLstr)
    length = int(CLstr)
    length += diff
    CLstr_after = str(length)
    CLstr_afterlen = len(CLstr_after)
    
    mdata = odata[:CLs] + odata[CLs:CLe].replace(CLstr, CLstr_after) + odata[CLe:]

    
    cdata = mdata.replace(tstr, cstr)
    print "original data=====================\n", odata
    #print "mdata = \n", mdata
    print "changed data======================\n",cdata
    return cdata


def GetURL(data):
    URL = ''
    PORT = 0
    if(data.find(":443")!=-1):
        PORT = 443
    else:
        PORT = 80
    if(data.find("GET")!=-1):
        URLs = data.find("http://")
        URLe = data.find("/", URLs+7)
        URL = data[URLs+7:URLe]
        #print URL
        return (URL, PORT)

        
    if(data.find("CONNECT")!=-1):
        conns = data.find("CONNECT")
        URLs = data.find(" ", conns) + 1
        URLe = data.find(":")
        URL = data[URLs:URLe]
        #print URL
        return (URL, PORT)

    if(data.find("Host")!=-1):
        conns = data.find("Host:")
        URLs = data.find(" ", conns) + 1
        URLe = data.find("\r\rn")
        URL = data[URLs:URLe]
        #print URL
        return (URL, PORT)
        
    return (URL, PORT)
    

def parse_and_send(data, conn):
    #if(data.find("GET") == -1):
    #    return -1
    #print "sending data :", data

    #socket going to target
    ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts.settimeout(10)
    ts.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        T_HOST, T_PORT = GetURL(data)
        print "Host and port : \n", T_HOST, T_PORT
        if(T_HOST == ""):
            return -1
        try:
            ts.connect((T_HOST, T_PORT))
        except:
            ts.shutdown(1)
            ts.close()
            return -1
        print "connected to ", T_HOST
        f_data = change_to_deflate(data)
        ts.send(f_data)
        print("request sent to target\n")
        recv_data = ''
        try:
            while True:
                rcdata = ts.recv(1024)
                if not rcdata:
                    break
                recv_data += rcdata
        except:
            print("cannot get data\n")
            ts.shutdown(1)
            ts.close()
            return -1

        print("got data from target")
        #print "received data:", recv_data
        #print "repr", repr(recv_data)
        #print "str", str(recv_data)
        print "data change"
        changed_data = change(recv_data)
        print "send to client"
        conn.send(changed_data)
        
        ts.shutdown(1)
    except (KeyboardInterrupt, SystemExit):
        ts.close()
    ts.close()

    return 1
    
    
#socket from client
cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cs.bind((C_HOST, C_PORT))
cs.listen(100000)
cs.settimeout(10)
cs.setblocking(1)

while True:
    print("trying connection")
    try:
        conn, addr = cs.accept()
    except (KeyboardInterrupt, SystemExit):
        continue
    try:
        print 'Connected from : ', addr
        while True:
            #print("trying to get conn data")
            conn.setblocking(1)
            try:
                data = conn.recv(BUFFSIZE)
            except socket.error as error:
                if error.errno == 10054:
                    conn.shutdown(1)
                    break
            if not data:
                conn.shutdown(1)
                break
            print("data = \n"), data
            res = parse_and_send(data, conn)
            if(res==-1):
                continue
        conn.close()
        print "connection closed from addr : ", addr
        print "\n\n\n"
    except (KeyboardInterrupt, SystemExit):
        conn.close()
        cs.close()
        
cs.close()

