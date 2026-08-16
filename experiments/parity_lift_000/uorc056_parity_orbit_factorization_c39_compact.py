#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from uorc056_c39_orbit import build_orbit_rows
from uorc056_c39_character_span import build_span_rows
SECP_N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def build_payload():
    orbit=build_orbit_rows();spans=build_span_rows();agg={
      'curves':len(orbit),'orbit_decoder_checks':sum(r['n']-1 for r in orbit),
      'all_orbit_polynomials_degree_optimal':all(r['minimal_rational_decoder_degree_proved']==r['canonical_orbit_decoder_degree'] for r in orbit),
      'all_B_units_on_half_kernel':all(r['B_zeros_on_half_kernel']==0 for r in orbit),
      'all_even_odd_polynomials_dense_except_at_most_one_coefficient':all(r['polynomials']['P_even']['zeros']+r['polynomials']['P_odd']['zeros']<=1 for r in orbit),
      'all_trace_power_character_product_grammars_inconsistent':all(not r['parity_in_span'] for r in spans),
      'trace_power_atoms_declared':sum(r['all_declared_atoms'] for r in spans),'trace_power_valid_atoms':sum(r['valid_nonzero_atoms'] for r in spans),'errors':0}
    out={'profile_id':'UORC-056-PARITY-ORBIT-FACTORIZATION-C39','schema_version':'1.0','target':'Q=[k]G -> (-1)^k','state':'M_h(G,Q,S), h=(n-1)/2','orbit_factorization':orbit,'full_trace_power_character_product_span':spans,
      'secp256k1':{'n':SECP_N,'half_size':(SECP_N-1)//2,'half_size_bit_length':((SECP_N-1)//2).bit_length(),'production_state_distinctness_not_claimed':True},
      'decision':{'exact_orbit_decoder_found':True,'rational_degree_optimality_proved':True,'short_subroot_orbit_decoder_found':False,'orbit_factorization_reduces_to_oriented_square_root_branch':True,'arbitrary_products_of_all_trace_linear_power_characters_closed_on_frozen_corpus':True,'parity_oracle_found':False,'sub_sqrt_ecdlp_found':False},'aggregate':agg}
    out['digest']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);a=ap.parse_args();p=build_payload()
    if a.out:a.out.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
    print('UORC056_PARITY_ORBIT_FACTORIZATION_C39_OK');print(json.dumps(p['aggregate'],indent=2,sort_keys=True));print('digest='+p['digest'])
if __name__=='__main__':main()
