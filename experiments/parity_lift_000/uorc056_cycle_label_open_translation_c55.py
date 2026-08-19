#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from uorc056_c55_cycle_analysis import build_payload

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path); args=parser.parse_args()
    payload=build_payload()
    if args.out: args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print('UORC056_CYCLE_LABEL_OPEN_TRANSLATION_C55_OK')
    print(json.dumps(payload['aggregate'],indent=2,sort_keys=True))
    print('digest='+payload['digest'])
if __name__=='__main__': main()
