"""Resident Evil integrity hashes.

CityHash64 is adapted from Google CityHash (Copyright 2011 Google, Inc.), MIT.
The full permission notice is included in THIRD_PARTY_NOTICES.txt.
Other Python code: SPDX-License-Identifier: GPL-3.0-or-later.
"""
import struct

MASK64=(1<<64)-1
K0=0xC3A5C85C97CB3127
K1=0xB492B66FBE98F273
K2=0x9AE16A3B2F90404F


def murmur32(data,seed=0xffffffff):
    value=seed&0xffffffff
    def rotate32(n,bits):return ((n<<bits)|(n>>(32-bits)))&0xffffffff
    def mix(n):return (rotate32((n*0xcc9e2d51)&0xffffffff,15)*0x1b873593)&0xffffffff
    end=len(data)&~3
    for offset in range(0,end,4):
        value=rotate32(value^mix(struct.unpack_from('<I',data,offset)[0]),13)
        value=(value*5+0xe6546b64)&0xffffffff
    tail=int.from_bytes(data[end:],'little')
    if len(data)>end:value^=mix(tail)
    value^=len(data);value^=value>>16
    value=(value*0x85ebca6b)&0xffffffff;value^=value>>13
    value=(value*0xc2b2ae35)&0xffffffff;value^=value>>16
    return value


def _rotate(n,bits):
    n&=MASK64
    return ((n>>bits)|(n<<(64-bits)))&MASK64


def _shift(n):
    n&=MASK64
    return n^(n>>47)


def _hash16(a,b,mul=0x9ddfea08eb382d69):
    a=((a^b)*mul)&MASK64;a^=a>>47
    b=((b^a)*mul)&MASK64;b^=b>>47
    return (b*mul)&MASK64


def _swap(n):return int.from_bytes((n&MASK64).to_bytes(8,'little'),'big')


def city64(data):
    n=len(data)
    def f(offset):return struct.unpack_from('<Q',data,offset)[0]
    if n<=16:
        if n>=8:
            mul=(K2+n*2)&MASK64;a=(f(0)+K2)&MASK64;b=f(n-8)
            return _hash16((_rotate(b,37)*mul+a)&MASK64,((_rotate(a,25)+b)*mul)&MASK64,mul)
        if n>=4:
            return _hash16(n+(struct.unpack_from('<I',data)[0]<<3),struct.unpack_from('<I',data,n-4)[0],(K2+n*2)&MASK64)
        if n:
            y=data[0]+(data[n>>1]<<8);z=n+(data[-1]<<2)
            return (_shift((y*K2)^(z*K0))*K2)&MASK64
        return K2
    if n<=32:
        mul=(K2+n*2)&MASK64;a=(f(0)*K1)&MASK64;b=f(8);c=(f(n-8)*mul)&MASK64;d=(f(n-16)*K2)&MASK64
        return _hash16((_rotate(a+b,43)+_rotate(c,30)+d)&MASK64,(a+_rotate(b+K2,18)+c)&MASK64,mul)
    if n<=64:
        mul=(K2+n*2)&MASK64;a=(f(0)*K2)&MASK64;b=f(8);c=f(n-24);d=f(n-32)
        e=(f(16)*K2)&MASK64;fval=(f(24)*9)&MASK64;g=f(n-8);h=(f(n-16)*mul)&MASK64
        u=(_rotate(a+g,43)+(_rotate(b,30)+c)*9)&MASK64
        v=(((a+g)&MASK64)^d)+fval+1;v&=MASK64
        w=(_swap((u+v)*mul)+h)&MASK64;x=(_rotate(e+fval,42)+c)&MASK64
        y=((_swap((v+w)*mul)+g)*mul)&MASK64;z=(e+fval+c)&MASK64
        a=(_swap((x+z)*mul+y)+b)&MASK64
        b=(_shift((z+a)*mul+d+h)*mul)&MASK64
        return (b+x)&MASK64
    def weak(offset,a,b):
        w,x,y,z=struct.unpack_from('<4Q',data,offset)
        a=(a+w)&MASK64;b=_rotate(b+a+z,21);c=a
        a=(a+x+y)&MASK64;b=(b+_rotate(a,44))&MASK64
        return ((a+z)&MASK64,(b+c)&MASK64)
    x=f(n-40);y=(f(n-16)+f(n-56))&MASK64;z=_hash16((f(n-48)+n)&MASK64,f(n-24))
    v=weak(n-64,n,z);w=weak(n-32,(y+K1)&MASK64,x);x=(x*K1+f(0))&MASK64
    for offset in range(0,(n-1)&~63,64):
        x=(_rotate(x+y+v[0]+f(offset+8),37)*K1)&MASK64
        y=(_rotate(y+v[1]+f(offset+48),42)*K1)&MASK64
        x^=w[1];y=(y+v[0]+f(offset+40))&MASK64;z=(_rotate(z+w[0],33)*K1)&MASK64
        v=weak(offset,(v[1]*K1)&MASK64,(x+w[0])&MASK64)
        w=weak(offset+32,(z+w[1])&MASK64,(y+f(offset+16))&MASK64)
        x,z=z,x
    return _hash16((_hash16(v[0],w[0])+_shift(y)*K1+z)&MASK64,(_hash16(v[1],w[1])+x)&MASK64)
