"""Bounded self-describing RE Engine streams. SPDX-License-Identifier: GPL-3.0-or-later.

Offsets refer to the original stream, so unrelated fields need no serialization.
No implementation or schema assets from other editors are included.
"""
from dataclasses import dataclass
import struct

SCALARS={2:'<B',3:'<b',4:'<B',5:'<h',6:'<H',7:'<i',8:'<I',9:'<q',10:'<Q',11:'<f',12:'<d',13:'<B',14:'<H'}


@dataclass
class Node:
    owner: int
    field: int
    kind: int
    offset: int
    size: int
    path: tuple
    fmt: str=''


class StreamReader:
    def __init__(self,data,offset=0,end=None):
        self.data=data;self.pos=offset;self.end=len(data) if end is None else end
        self.nodes=[];self.classes=set();self.total=0

    def take(self,size):
        if size<0 or self.pos+size>self.end:raise ValueError('The RE Engine stream is truncated.')
        offset=self.pos;self.pos+=size;return offset

    def read(self,fmt):
        return struct.unpack_from(fmt,self.data,self.take(struct.calcsize(fmt)))[0]

    def align(self,size):
        if not 1<=size<=65536:raise ValueError('Unsupported RE Engine value alignment.')
        offset=(self.pos+size-1)&~(size-1)
        if offset<self.pos:raise ValueError('Invalid RE Engine alignment.')
        self.take(offset-self.pos)

    def guard(self,depth):
        self.total+=1
        if depth>64 or self.total>1000000:raise ValueError('The RE Engine stream exceeds safe complexity limits.')

    def clazz(self,path,depth):
        self.guard(depth)
        count=self.read('<I');owner=self.read('<I');self.classes.add(owner)
        if count>100000 or count>(self.end-self.pos)//8:raise ValueError('Invalid RE Engine class field count.')
        for index in range(count):
            field=self.read('<I');kind=self.read('<i')
            self.value(owner,field,kind,path+((owner,field,index),),depth+1)
            self.align(4)

    def value(self,owner,field,kind,path,depth):
        self.guard(depth)
        if kind==17:self.clazz(path,depth+1);return
        if kind==15:
            self.align(4);length=self.read('<I');self.take(length*2);return
        if kind==-1:self.array(owner,field,path,depth+1);return
        self.align(4);size=self.read('<I')
        self.sized(owner,field,kind,size,path,depth)

    def sized(self,owner,field,kind,size,path,depth):
        self.guard(depth)
        if size:self.align(size)
        offset=self.pos
        if kind==1:
            fmt={1:'<b',2:'<h',4:'<i',8:'<q'}.get(size)
            if fmt is None:raise ValueError('Unsupported RE Engine enum size.')
        elif kind==16:
            if size>65536:raise ValueError('The RE Engine struct is too large.')
            fmt=''
        elif kind in SCALARS:
            fmt=SCALARS[kind]
            if struct.calcsize(fmt)!=size:raise ValueError('Inconsistent RE Engine scalar size.')
        else:raise ValueError('Unsupported RE Engine serialized field type '+str(kind)+'.')
        self.take(size)
        self.nodes.append(Node(owner,field,kind,offset,size,path,fmt))

    def array(self,owner,field,path,depth):
        self.guard(depth);self.align(4)
        kind=self.read('<i');size=self.read('<I');length=self.read('<I');mode=self.read('<i')
        if length>1000000 or mode not in (0,1):raise ValueError('Unsupported RE Engine array.')
        if mode==1:
            if self.pos+4<=self.end and struct.unpack_from('<I',self.data,self.pos)[0]==0xffeeffee:
                self.take(4+length*4)
        elif size and length>(self.end-self.pos)//size:raise ValueError('The RE Engine array is truncated.')
        for index in range(length):
            current=path+((owner,field,index),)
            if mode==1:self.clazz(current,depth+1)
            elif kind==15:
                self.align(4);count=self.read('<I');self.take(count*2)
            else:self.sized(owner,field,kind,size,current,depth+1)
        self.align(4)

    def parse(self):
        root=0
        while self.pos<self.end:
            if self.end-self.pos<=7 and not any(self.data[self.pos:self.end]):break
            field=self.read('<I')
            self.clazz(((0,field,root),),0);root+=1
        return self.nodes
