# coding: utf-8
# (c) 2009 Gleicon Moraes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
import re
import struct
from hashlib import md5


class BasicOperations(object):
    """ Basic tx websockets operations handler. Overwrite it with your operations """
    def __init__(self):
        self.writeHandler=None

    def on_read(self, sendLine):
        pass
    
    def on_connect(self):
        pass
    
    def on_close(self, r):
        pass

    def setWriteHandler(self, handler):
        self.writeHandler=handler
   
    def _out(self, str):
        if self.writeHandler == None:
            print 'No handler'
        else:
            r = '\x00' + str.encode('utf-8') # no need for the last delimiter '\xff'
            self.writeHandler(r)

    def after_connection(self):
        pass

class WebSocketServer(LineReceiver):
    HDR_ORIGIN = re.compile('Origin\:\s+(.*)')
    HDR_LOCATION = re.compile('GET\s+(.*)\s+HTTP\/1.1', re.I)
    HDR_HOST = re.compile('Host\:\s+(.*)')
    
    SEC_WS_KEY1 = re.compile('Sec-WebSocket-Key1\:\s+(.*)')
    SEC_WS_KEY2 = re.compile('Sec-WebSocket-Key2\:\s+(.*)')

    def __init__(self):
        
        self.old_hdr = '''HTTP/1.1 101 Web Socket Protocol Handshake\r
Upgrade: WebSocket\r
Connection: Upgrade\r
WebSocket-Origin: %s\r
WebSocket-Location: ws://%s%s\r\n\r\n'''
        
        self.hdr = '''HTTP/1.1 101 Web Socket Protocol Handshake\r
Upgrade: WebSocket\r
Connection: Upgrade\r
Sec-WebSocket-Origin: %s\r
Sec-WebSocket-Location: ws://%s%s\r\n\r
%s\r\n'''


    def connectionMade(self):
        self.setRawMode()
        self.factory.oper.on_connect()
    
    def lineReceived(self, line):
        self.factory.oper.on_read(line)

    def rawDataReceived(self, line):
        origin, location, host, token = self._parseHeaders(line)
        if token == None:
            # ws spec 75
            self.sendLine(self.old_hdr % (origin, host, location))
        else:
            self.sendLine(self.hdr % (origin, host, location, token))
        self.delimiter='\xff'
        self.setLineMode()
        self.factory.oper.setWriteHandler(self.sendLine)
        self.factory.oper.after_connection()

    def connectionLost(self, reason):
        self.factory.oper.on_close(reason)

    def _parseHeaders(self, buf):
        if buf == None:
            return None, None, None, None
        o = l = h = None
        k1 = k2 = k3 = None
        token_ready = False

        for a in buf.split('\n\r'):
            if token_ready:
                k3 = a.strip()
                continue
            org = self.HDR_ORIGIN.search(a)
            loc = self.HDR_LOCATION.search(a)
            hst = self.HDR_HOST.search(a)
            key1 = self.SEC_WS_KEY1.search(a)
            key2 = self.SEC_WS_KEY2.search(a)

            if org != None: o = org.group(1).strip()
            if hst != None: h = hst.group(1).strip()
            if loc != None: l = loc.group(1).strip()
            if key1 != None: k1 = key1.group(1).strip()
            if key2 != None: 
                k2 = key2.group(1).strip()
                token_ready = True
        
        if k1 != None or k2 != None or k3 != None: 
            t4 = self._calculate_token(k1, k2, k3)
            return o,l,h,t4
        else: 
            return o, l, h, None

    def _calculate_token(self, k1, k2, k3):
        token = struct.pack('>ii8s', self._filterella(k1), self._filterella(k2), k3)
        return md5(token).digest()

    def _filterella(self, w):
        nums = []
        spaces = 0
        for l in w:
            if l.isdigit(): nums.append(l)
            if l.isspace(): spaces = spaces + 1
        x = int(''.join(nums))/spaces
        return x

class WebSocketFactory(Factory):
    protocol = WebSocketServer

    def __init__(self, oper=BasicOperations):
        self.oper=oper


