from Crypto.Util.number import *
from Crypto import Random
import Crypto
import libnum
import sys
from random import randint
import hashlib
import uuid

# v = public key
# s = private key
# S1 = r
# S2 = s
def sign(msg): # sign using elGamal: generate (r,s) -> (S1, S2) || will be used to sign block

    bits=60
    if (len(sys.argv)>1):
            msg=str(sys.argv[1])
    if (len(sys.argv)>2):
            bits=int(sys.argv[2])

    p = Crypto.Util.number.getPrime(bits, randfunc=Crypto.Random.get_random_bytes)
    g=2
    
    s= randint(0, p-1)
    v = pow(g,s,p)

    e= Crypto.Util.number.getPrime(bits, randfunc=Crypto.Random.get_random_bytes)
    # e_1=(gmpy2.invert(e, p-1))
    e_1=(libnum.invmod(e, p-1))
    D = bytes_to_long(msg.encode('utf-8')) # if you want direct signing

    #D = int.from_bytes(hashlib.sha256(msg.encode()).digest(),byteorder='big')
    

    S_1=pow(g,e, p)
    S_2=((D-s*S_1)*e_1) % (p-1)

    return (S_1, S_2, g, v, p, D)

def verify(S_1, S_2, g, v, p, D):
    
    
    v_1 = (pow(v,S_1,p)*pow(S_1,S_2,p))%p
    v_2 = pow(g,D,p)
    if v_1 == v_2:
        return True
    else:
        return False




