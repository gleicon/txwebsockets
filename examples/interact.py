from txwebsockets import WebSocketFactory, BasicOperations
import datetime

class MyOperations(BasicOperations):

    def on_read(self, line):
        print  "read:", line 
        self._out('clock!%s' % datetime.datetime.now())
        self._out('out!%s' % line)
    
    def on_connect(self):
        print "connected. writeHandler is ", self.writeHandler  

    def on_close(self, r):
        print "connection closed: ", r 

    def after_connection(self):
        self._out('out!after_connection')

if __name__ == '__main__':
    from twisted.internet import reactor
    mo = MyOperations()

    factory = WebSocketFactory(mo)

    reactor.listenTCP(8007, factory)
    reactor.run()

