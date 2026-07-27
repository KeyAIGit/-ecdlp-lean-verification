# ML-P1E R2 qualification summary

Status: independently validated bounded null.

The valid R2 assay used 1,105,920 deterministic records on 40 certified
`y^2=x^3+7` curves at 13, 16, 20, and 24 field bits. The first 1,097,078-record
corpus belongs to the invalidated run and is not pooled with R2.

## Methods checked

The preregistered AutoML screen completed all 219 required pre-blind fits:

| family | configurations | representations |
|---|---:|---|
| Ridge multi-output | 5 | compressed, affine, GLV |
| MLP multi-output | 4 | compressed, affine, GLV |
| Extra Trees multi-output | 4 | compressed, affine, GLV |
| RBF random features plus logistic heads | 1 | compressed |

The screen covered MLP widths `64` and `128x64`, six screen epochs, ten
confirmation/blind epochs, tree depths `6` and `8`, and seven independent
model seeds. Controls included random labels, within-cluster label
permutation, opaque point labels, curve/generator-only features, mismatched
public points, and one-bit, four-bit, and all-bit leak canaries. Matched BSGS
and Pollard-rho baselines were also run at every rung.

The selected frozen recipe was `trees-compressed-d6-l16`. Selection used only
development shards. Its corrected transfer gate was false before blind data
was opened.

## Blind curve and generator results

| bits | information bits/key, 99% CI | bit-accuracy lift, 99% CI | exact | top-256 |
|---:|---:|---:|---:|---:|
| 13 | -0.2042 [-1.2471, 0.8388] | -0.000532 [-0.015611, 0.014546] | 4 / 12,288 | 4.3945% |
| 16 | -0.03753 [-0.14404, 0.06898] | -0.000300 [-0.002258, 0.001658] | 1 / 24,576 | 0.6836% |
| 20 | -0.1852 [-0.8966, 0.5263] | -0.000240 [-0.002509, 0.002029] | 0 / 98,304 | 0% |
| 24 | -0.02792 [-0.15033, 0.09450] | -0.000704 [-0.001688, 0.000280] | 0 / 196,608 | 0% |

No rung produced positive information gain over the exact public scalar-bit
prior. The 20- and 24-bit blind sets had no exact or top-256 recovery. There
is therefore no transferable direct-inversion signal in the tested model,
representation, data, and compute envelope.

## Validation

- curve validation: 40/40 pass;
- dataset validation: 1,105,920/1,105,920 independent `[d]G=Q` checks;
- selection ledger: 219/219 unique successful fits;
- pre-blind selection validation: pass, zero errors, zero dataset files opened;
- frozen evaluation: 28/28 successful fits;
- final independent replay: pass with zero errors after 905,382 EC scalar
  multiplications;
- deliberate leak canaries and all negative controls: pass.

## Decision

Do not open the deferred 28- or 32-bit rungs for this direct scalar-prediction
route. More examples, epochs, or layers are not justified by this bounded
result because the corrected transfer gate already failed and the 24-bit
blind recovery was zero.

AutoML remains useful as a controlled hypothesis-screening and falsification
system. A later ML phase should search for explicit executable mechanisms or
programs and test them against generic complexity baselines, under a new
preregistration and new blind data. This result does not make a secp256k1,
asymptotic, or impossibility claim.
