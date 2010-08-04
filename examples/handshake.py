import struct
from hashlib import md5
import re
# spec 56 handshake workbench

def _calculate_token(k1, k2, k3):
    token = struct.pack('>II8s', _filterella(k1), _filterella(k2), k3)
    #token = struct.pack('>II8s', 544790785, 2008475658, k3)

    return md5(token).digest()

def _filterella(w):
    nums = []
    spaces = 0
    for l in w:
        if l.isdigit(): nums.append(l)
        if l.isspace(): spaces = spaces + 1
    x = int(''.join(nums))/spaces
    print x
    return x

def _hexify(s):
    return re.sub(".", lambda x: "%02x " % ord(x.group(0)), s)


if __name__ == '__main__':
    n = [0x81, 0xb4, 0xc7, 0xc3, 0xdb, 0x44, 0xad, 0x4e]
    nonce = ''.join([chr(item) for item in n])
    print nonce
    print _hexify(nonce)
    cc = _calculate_token("2h7n 2  3 9539 25#Tj","Sa40? 1y6i9k513_Lju16F +", nonce)
    print 'calculated:\t', _hexify(cc)
    print "correct:\t01 0f 15 3a 72 8f 5d 93 ec 68 d4 fa f3 94 2f 0c"
