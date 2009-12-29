from txwebsockets import WebSocketFactory, BasicOperations
import datetime

class MyOperations(BasicOperations):

    def on_read(self, sl, line):
        print  "read:", line 
        sl('\x00clock!%s\xff' % datetime.datetime.now())
        sl('\x00out!%s\xff' % line)
    
    def on_connect(self):
        print "connected"  

    def on_close(self, r):
        print "connection closed: ", r 

if __name__ == '__main__':
    from twisted.internet import reactor
    mo = MyOperations()

    factory = WebSocketFactory(mo)

    reactor.listenTCP(8007, factory)
    reactor.run()

