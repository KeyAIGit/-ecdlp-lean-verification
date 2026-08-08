-- Research OS — non-ECDLP domains verified by the same Lean kernel.
-- Root of the `ResearchOS` library (a second lake target alongside `Ecdlp`), holding
-- kernel-verified facts for domains OTHER than elliptic curves. Its existence is the
-- machine-checked evidence that the Research OS pipeline is not ECC-only.
import ResearchOS.NumberTheory.Elementary
import ResearchOS.NumberTheory.MoreFacts
-- Domain-neutral analysis shelf: generic lemmas with zero repo prerequisites, owned by
-- no conjecture program. Listed before the RH chain because nothing in that chain (or
-- anywhere else) depends on it today.
import ResearchOS.Analysis.MellinBound
import ResearchOS.Analysis.HarnackDisc
import ResearchOS.Analysis.PolyLiouville
import ResearchOS.Analysis.ThreeCircles
import ResearchOS.Analysis.GrowthOrder
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.TargetBridge
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Xi
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Conj
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Mult
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.ZeroSetSlice
