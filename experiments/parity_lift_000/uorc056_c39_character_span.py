from __future__ import annotations
import numpy as np
from uorc056_c39_half_miller import TOYS,Fp2,half_sequence,legendre,sigma

def factorint(value):
    out=[];d=2
    while d*d<=value:
        if value%d==0:
            out.append(d)
            while value%d==0:value//=d
        d=3 if d==2 else d+2
    if value>1:out.append(value)
    return out

def primitive_generator(E):
    q=E.p*E.p-1
    for a in range(E.p):
        for b in range(E.p):
            g=Fp2(a,b,E.p,E.d)
            if g and all(g**(q//r)!=1 for r in factorint(q)):return g
    raise AssertionError

def power_cycle(E,g):
    q=E.p*E.p-1;out=[];x=E.c(1)
    for _ in range(q):out.append(x);x=x*g
    assert x==1 and len({z.tuple() for z in out})==q;return out

def add_basis(piv,x):
    while x:
        j=x.bit_length()-1
        if j in piv:x^=piv[j]
        else:piv[j]=x;return
def reduce_basis(piv,x):
    while x:
        j=x.bit_length()-1
        if j in piv:x^=piv[j]
        else:return x
    return 0

def span_curve(row,batch=256):
    E,n,G,S,beta,lam,h,V=half_sequence(row);q=E.p*E.p-1;cycle=power_cycle(E,primitive_generator(E))
    logs={z.tuple():i for i,z in enumerate(cycle)};state=np.array([logs[z.tuple()] for z in V[1:]],dtype=np.int64)
    ca=np.array([z.a for z in cycle],dtype=np.int64);cb=np.array([z.b for z in cycle],dtype=np.int64)
    dirs=[(1,b) for b in range(E.p)]+[(0,1)];A=np.array([x for x,y in dirs],dtype=np.int64)[:,None];B=np.array([y for x,y in dirs],dtype=np.int64)[:,None]
    leg=np.array([legendre(x,E.p) for x in range(E.p)],dtype=np.int8);table=leg[(A*ca[None,:]+B*cb[None,:])%E.p]
    piv={};valid=0;unique=0
    for begin in range(0,q,batch):
        ex=np.arange(begin,min(begin+batch,q),dtype=np.int64);idx=(ex[:,None]*state[None,:])%q;samples=table[:,idx]
        mask=np.all(samples!=0,axis=2);bits=(samples*samples[:,:,:1]==-1).reshape(-1,n-1)[mask.reshape(-1)];valid+=len(bits)
        if not len(bits):continue
        packed=np.unique(np.packbits(bits,axis=1,bitorder='little'),axis=0);unique+=len(packed)
        for z in packed:add_basis(piv,int.from_bytes(z.tobytes(),'little'))
    target=0;anchor=sigma(1,n)
    for i,k in enumerate(range(1,n)):
        if sigma(k,n)*anchor==-1:target|=1<<i
    return {'p':E.p,'n':n,'all_declared_atoms':q*(E.p+1),'valid_nonzero_atoms':valid,'span_rank':len(piv),'normalized_target_dimension':n-2,'parity_in_span':reduce_basis(piv,target)==0,'batch_unique_rows_seen':unique}
def build_span_rows():return [span_curve(row) for row in TOYS]
