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
C_PORT = 7025
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
    print("==============changed to deflate ================")
    print cdata
    
    return cdata

def change(odata):

    num = odata.count(tstr)
    diff = (len(cstr) - len(tstr))*num
    CL = "Content-Length:"
    CLs = odata.find(CL) + len(CL) + 1
    CLe = odata.find("\r\n", CLs)
    CLstr = odata[CLs:CLe]
    print CLstr
    CLstrlen = len(CLstr)
    length = int(CLstrlen)
    length += diff
    CLstr_after = str(length)
    CLstr_afterlen = len(CLstr_after)
    
    mdata = odata[:CLs] + odata[CLs:CLe].replace(CLstr, CLstr_after) + odata[CLe:]

    
    cdata = mdata.replace(tstr, cstr)
    print odata
    print "mdata = \n", mdata
    print cdata
    """
    print "repr==========="
    print repr(odata)
    loc = odata.find(tstr)
    #odata[loc:loc+len(tstr)] = cstr
    print "index = ", loc
    f = open("./gilgil.txt", 'w')
    f.write(odata)
    f.close()
    print("\n\n\n\n")
    print repr(odata)
    """
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
        print URL
        return (URL, PORT)

        
    if(data.find("CONNECT")!=-1):
        conns = data.find("CONNECT")
        URLs = data.find(" ", conns) + 1
        URLe = data.find(":")
        URL = data[URLs:URLe]
        print URL
        return (URL, PORT)
        
    return (URL, PORT)
    

def parse_and_send(data, conn):
    #if(data.find("GET") == -1):
    #    return -1
    #print "sending data :", data

    #socket going to target
    ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts.settimeout(1000)
    ts.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        T_HOST, T_PORT = GetURL(data)
        print T_HOST
        print T_PORT
        ts.connect((T_HOST, T_PORT))
        f_data = change_to_deflate(data)
        ts.send(f_data)
        recv_data = ''
        while True:
            rcdata = ts.recv(1024)
            if not rcdata:
                break
            recv_data += rcdata
        #print "received data:", recv_data
        #print "repr", repr(recv_data)
        #print "str", str(recv_data)
        print "now send to client"
        changed_data = change(recv_data)
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
    print("trying connection\n")
    try:
        conn, addr = cs.accept()
    except (KeyboardInterrupt, SystemExit):
        continue
    try:
        print 'Connected from : ', addr
        while True:
            #print("trying to get conn data")
            conn.setblocking(1)
            data = conn.recv(BUFFSIZE)
            if not data:
                conn.shutdown(1)
                break
            print("data = \n"), data
            res = parse_and_send(data, conn)
            if(res==-1):
                continue
        conn.close()
    except (KeyboardInterrupt, SystemExit):
        conn.close()
        cs.close()
        
cs.close()



"""
GET http://www.naver.com/ HTTP/1.1

Accept: text/html, application/xhtml+xml, image/jxr, */*

Accept-Language: ko-KR

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko

Accept-Encoding: gzip, deflate

Host: www.naver.com

Proxy-Connection: Keep-Alive

Cookie: NM_THEMECAST_NEW=tcc_lif%2Ctcc_fod; npic=mP7WswFNghnl3UZdeO33LPFoc49c1cqkV4XmoJnv6Q1srsxbSOtOARxFq1BPNsydCA==; NNB=6I3CCIVYVHPVM; nx_ssl=2


Connected from :  ('127.0.0.1', 11371)
CONNECT www.google.co.kr:443 HTTP/1.1

Host: www.google.co.kr:443

Proxy-Connection: keep-alive

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36




Connected from :  ('127.0.0.1', 11372)
CONNECT www.google.co.kr:443 HTTP/1.1

Host: www.google.co.kr:443

Proxy-Connection: keep-alive

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36




Connected from :  ('127.0.0.1', 11373)
CONNECT www.google.co.kr:443 HTTP/1.1

Host: www.google.co.kr:443

Proxy-Connection: keep-alive

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36




Connected from :  ('127.0.0.1', 11374)
CONNECT www.google.co.kr:443 HTTP/1.1

Host: www.google.co.kr:443

Proxy-Connection: keep-alive

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36




Connected from :  ('127.0.0.1', 11375)
CONNECT www.google.co.kr:443 HTTP/1.1

Host: www.google.co.kr:443

Proxy-Connection: keep-alive

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36




Connected from :  ('127.0.0.1', 11376)
CONNECT www.google.co.kr:443 HTTP/1.1

Host: www.google.co.kr:443

Proxy-Connection: keep-alive

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36




Connected from :  ('127.0.0.1', 11378)
Connected from :  ('127.0.0.1', 11379)
Connected from :  ('127.0.0.1', 11380)
Connected from :  ('127.0.0.1', 11381)
Connected from :  ('127.0.0.1', 11382)
Connected from :  ('127.0.0.1', 11458)



"""



"""
Connected from :  ('127.0.0.1', 11128)
sending data : GET http://www.naver.com/ HTTP/1.1

Accept: text/html, application/xhtml+xml, image/jxr, */*

Accept-Language: ko-KR

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko

Accept-Encoding: gzip, deflate

Host: www.naver.com

Proxy-Connection: Keep-Alive

Cookie: NM_THEMECAST_NEW=tcc_lif%2Ctcc_fod; nrefreshx=0; npic=mP7WswFNghnl3UZdeO33LPFoc49c1cqkV4XmoJnv6Q1srsxbSOtOARxFq1BPNsydCA==; NNB=6I3CCIVYVHPVM; nx_ssl=2; nid_iplevel=1; page_uid=fiGZjsoiqyRssKcy32VsssssssN-150613




www.naver.com
received data: HTTP/1.1 200 OK

Server: nginx

Date: Tue, 13 Dec 2016 05:18:06 GMT

Content-Type: text/html; charset=UTF-8

Transfer-Encoding: chunked

Connection: close

Cache-Control: no-cache, no-store, must-revalidate

Pragma: no-cache

P3P: CP="CAO DSP CURa ADMa TAIa PSAa OUR LAW STP PHY ONL UNI PUR FIN COM NAV INT DEM STA PRE"

Content-Encoding: gzip

X-Frame-Options: SAMEORIGIN



53fe

ﾋ
"""

#===============================================================================

"""
Connected from :  ('127.0.0.1', 8390)
sending data : GET http://www.naver.com/ HTTP/1.1

Accept: text/html, application/xhtml+xml, image/jxr, */*

Accept-Language: ko-KR

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko

Accept-Encoding: gzip, deflate

Host: www.naver.com

Proxy-Connection: Keep-Alive

Cookie: NM_THEMECAST_NEW=tcc_lif%2Ctcc_fod; npic=mP7WswFNghnl3UZdeO33LPFoc49c1cqkV4XmoJnv6Q1srsxbSOtOARxFq1BPNsydCA==; NNB=6I3CCIVYVHPVM; nx_ssl=2




www.naver.com
received data: HTTP/1.1 200 OK

Server: nginx

Date: Wed, 14 Dec 2016 06:10:56 GMT

Content-Type: text/html; charset=UTF-8

Transfer-Encoding: chunked

Connection: close

Cache-Control: no-cache, no-store, must-revalidate

Pragma: no-cache

P3P: CP="CAO DSP CURa ADMa TAIa PSAa OUR LAW STP PHY ONL UNI PUR FIN COM NAV INT DEM STA PRE"

Content-Encoding: gzip

X-Frame-Options: SAMEORIGIN



5363

ﾋ
now send to client
Connected from :  ('127.0.0.1', 8391)
sending data : GET http://img.naver.net/static/newsstand/up/2014/0715/016.gif HTTP/1.1

Accept: image/png, image/svg+xml, image/jxr, image/*;q=0.8, */*;q=0.5

Referer: http://www.naver.com/

Accept-Language: ko-KR

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko

Accept-Encoding: gzip, deflate

If-Modified-Since: Tue, 15 Jul 2014 07:15:47 GMT

Host: img.naver.net

Proxy-Connection: Keep-Alive




img.naver.net
received data: HTTP/1.1 304 Not Modified

Date: Wed, 14 Dec 2016 06:10:57 GMT

Age: 14098

Expires: Thu, 15 Dec 2016 13:56:02 GMT




now send to client
sending data : GET http://www.naver.com/include/newsstand/press_info.json HTTP/1.1

Accept: */*

Content-Type: application/x-www-form-urlencoded; charset=utf-8

charset: utf-8

X-Requested-With: XMLHttpRequest

If-Modified-Since: Thu, 1 Jan 1970 00:00:00 GMT

Referer: http://www.naver.com/

Accept-Language: ko-KR

Accept-Encoding: gzip, deflate

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko

Host: www.naver.com

Proxy-Connection: Keep-Alive

Cookie: NM_THEMECAST_NEW=tcc_lif%2Ctcc_fod; nrefreshx=0; npic=mP7WswFNghnl3UZdeO33LPFoc49c1cqkV4XmoJnv6Q1srsxbSOtOARxFq1BPNsydCA==; NNB=6I3CCIVYVHPVM; nx_ssl=2; nid_iplevel=1




www.naver.com
received data: HTTP/1.1 200 OK

Server: nginx

Date: Wed, 14 Dec 2016 06:11:04 GMT

Content-Type: text/html; charset=UTF-8

Transfer-Encoding: chunked

Connection: close

Content-Encoding: gzip

Vary: Accept-Encoding



cc0

ﾋ
now send to client
Connected from :  ('127.0.0.1', 8394)
sending data : GET http://img.naver.net/static/newsstand/up/2014/0715/028.gif HTTP/1.1

Accept: image/png, image/svg+xml, image/jxr, image/*;q=0.8, */*;q=0.5

Referer: http://www.naver.com/

Accept-Language: ko-KR

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko

Accept-Encoding: gzip, deflate

If-Modified-Since: Tue, 15 Jul 2014 07:15:48 GMT

Host: img.naver.net

Proxy-Connection: Keep-Alive




img.naver.net
received data: HTTP/1.1 304 Not Modified

Date: Wed, 14 Dec 2016 06:11:04 GMT

Age: 454354

Expires: Mon, 12 Dec 2016 11:03:12 GMT




now send to client
"""
