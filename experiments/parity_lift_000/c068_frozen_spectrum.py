#!/usr/bin/env python3
"""Frozen toy-only C6 quotient spectrum replay for package C068."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np

CASES=((14113051,1085431,"a"),(14919511,414259,"b"),(28468039,451837,"c"),(48468247,932101,"d"),(49435999,1765741,"e"),(54919927,677947,"f"))
POWERS=np.array((1,2,3,5,7,11,13,17),dtype=np.int64)
TRIALS=32

def factors(value):
 out=[]; divisor=2
 while divisor*divisor<=value:
  if value%divisor==0:
   out.append(divisor)
   while value%divisor==0:value//=divisor
  divisor=3 if divisor==2 else divisor+2
 if value>1:out.append(value)
 return out

def primitive_root(prime):
 fs=factors(prime-1)
 for candidate in range(2,prime):
  if all(pow(candidate,(prime-1)//factor,prime)!=1 for factor in fs):return candidate
 raise AssertionError

def metric(values):
 transform=np.fft.fft(values)/len(values); nonzero=np.abs(transform[1:]); index=int(np.argmax(nonzero))
 return float(nonzero[index]),index+1,float(nonzero.sum())

def quantile(values,probability):
 ordered=sorted(values); return ordered[math.ceil(probability*len(ordered))-1]

def analyze(directory,p,order,suffix):
 digits=np.fromfile(directory/f"ux_{suffix}.bin",dtype=np.uint32)
 if len(digits)!=order:raise AssertionError("wrong frozen digit length")
 root=primitive_root(order); length=order-1; quotient_length=length//6
 indices=np.empty(length,dtype=np.int64); scalar=1
 for index in range(length):indices[index]=scalar;scalar=scalar*root%order
 sequence=digits[indices]; quotient=sequence[:quotient_length].astype(np.int64)
 if not np.array_equal(sequence,np.tile(quotient,6)):raise AssertionError("C6 period failed")
 phases=np.exp(2j*np.pi*((POWERS[:,None]*quotient[None,:])%p)/p)
 observed=np.abs(np.fft.fft(phases,axis=1)/quotient_length)[:,1:]
 best=float(observed.max()); best_power=int(POWERS[np.unravel_index(np.argmax(observed),observed.shape)[0]])
 quadratic=np.array([0 if int(v)==0 else (1 if pow(int(v),(p-1)//2,p)==1 else -1) for v in quotient],dtype=np.float64)
 quadratic_best=metric(quadratic)[0]
 random=np.random.default_rng(20260813+order); phase_null=[]; quadratic_null=[]
 for _ in range(TRIALS):
  permutation=random.permutation(quotient_length)
  phase_null.append(float(np.abs(np.fft.fft(phases[:,permutation],axis=1)/quotient_length)[:,1:].max()))
  quadratic_null.append(metric(quadratic[permutation])[0])
 return {"p":p,"n":order,"quotient_length":quotient_length,"best_power":best_power,"phase_maximum":best,"phase_null_q95":quantile(phase_null,.95),"phase_null_q99":quantile(phase_null,.99),"phase_above_q95":best>quantile(phase_null,.95),"phase_above_q99":best>quantile(phase_null,.99),"phase_sqrt_m_scaled":math.sqrt(quotient_length)*best,"phase_reaches_inverse_log":best>=1/math.log(order),"quadratic_maximum":quadratic_best,"quadratic_null_q95":quantile(quadratic_null,.95),"quadratic_null_q99":quantile(quadratic_null,.99),"quadratic_above_q95":quadratic_best>quantile(quadratic_null,.95),"quadratic_above_q99":quadratic_best>quantile(quadratic_null,.99),"quadratic_sqrt_m_scaled":math.sqrt(quotient_length)*quadratic_best}

def main():
 directory=Path("/tmp/c068"); rows=sorted((analyze(directory,*case) for case in CASES),key=lambda row:row["n"]); largest=rows[-2:]
 phase_q99=sum(row["phase_above_q99"] for row in rows); quadratic_q99=sum(row["quadratic_above_q99"] for row in rows)
 payload={"schema_version":1,"scope":"six fixed toy cases only","null_trials":TRIALS,"cases":rows,"aggregate":{"phase_q99_exceedances":phase_q99,"quadratic_q99_exceedances":quadratic_q99,"phase_largest_two_above_q95":all(row["phase_above_q95"] for row in largest),"quadratic_largest_two_above_q95":all(row["quadratic_above_q95"] for row in largest),"any_phase_reaches_inverse_log":any(row["phase_reaches_inverse_log"] for row in rows),"admitted_phase_signal":False,"admitted_quadratic_signal":False}}
 Path("/tmp/c068_results.json").write_text(json.dumps(payload,indent=2),encoding="utf-8"); print(json.dumps(payload,indent=2))

if __name__=="__main__":main()
