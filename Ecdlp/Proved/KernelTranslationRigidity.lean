import Mathlib

/-!
# Kernel-translation rigidity for compact endomorphism maps

Let `f` be an additive group homomorphism and let `q` lie in its kernel.  Then
translation by `q` leaves `f` unchanged:

```text
f(x+q)=f(x).
```

For the Frobenius endomorphism on rational points, `q` lies in the kernel of
`pi-1`.  Consequently the translated local germ of the compact map `pi-1` is
the same at every rational kernel point.  Invariantly trivialized jets of the
map itself therefore cannot distinguish the hidden scalar.  This file
formalizes the exact group-theoretic identity.  It does not formalize local
rings, derivatives, theta sections, or an ECDLP lower bound.
-/

namespace Ecdlp.ParityLift

/-- Translation on the right by a kernel element leaves an additive
homomorphism unchanged. -/
theorem addHom_add_kernel_right
    {A B : Type*} [AddMonoid A] [AddMonoid B]
    (f : A →+ B) (x q : A) (hq : f q = 0) :
    f (x + q) = f x := by
  rw [map_add, hq, add_zero]

/-- Translation on the left by a kernel element also leaves an additive
homomorphism unchanged. -/
theorem addHom_add_kernel_left
    {A B : Type*} [AddMonoid A] [AddMonoid B]
    (f : A →+ B) (q x : A) (hq : f q = 0) :
    f (q + x) = f x := by
  rw [map_add, hq, zero_add]

/-- Functional form of kernel-translation invariance. -/
theorem addHom_comp_kernel_translation
    {A B : Type*} [AddMonoid A] [AddMonoid B]
    (f : A →+ B) (q : A) (hq : f q = 0) :
    (fun x : A => f (x + q)) = fun x : A => f x := by
  funext x
  exact addHom_add_kernel_right f x q hq

/-- In an additive group, subtraction of a kernel element is equally
invisible to the homomorphism. -/
theorem addHom_sub_kernel
    {A B : Type*} [AddGroup A] [AddGroup B]
    (f : A →+ B) (x q : A) (hq : f q = 0) :
    f (x - q) = f x := by
  rw [map_sub, hq, sub_zero]

/-- Two points in the same kernel coset have identical images. -/
theorem addHom_eq_on_kernel_coset
    {A B : Type*} [AddGroup A] [AddGroup B]
    (f : A →+ B) (x y : A) (hxy : f (x - y) = 0) :
    f x = f y := by
  have h := addHom_sub_kernel f y (y - x) ?_
  · simpa [sub_sub_cancel] using h.symm
  · calc
      f (y - x) = -(f (x - y)) := by
        rw [map_sub, map_sub]
        abel
      _ = 0 := by rw [hxy, neg_zero]

end Ecdlp.ParityLift
