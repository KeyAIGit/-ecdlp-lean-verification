# Endpoint segment normal form

Date: 2026-08-13

Status: scoped theorem note.

For an additive edge sequence

```text
edge(i) = defect + potential(i+1) - potential(i),
```

every consecutive segment satisfies

```text
segment(start,length)
  = length • defect
    + potential(start+length)
    - potential(start).
```

All internal values telescope, and removing the endpoint contribution leaves
exactly `length • defect`.

For a transfer system

```text
T_i = B_(i+1) C B_i^(-1),
```

the ordered segment product is

```text
T_(b-1) ... T_a = B_b C^(b-a) B_a^(-1).
```

Removing endpoint gauges leaves `C^(b-a)`.

These identities close only the declared endpoint-coboundary and
conjugated-constant grammars. They do not address genuinely nonconstant jump
systems or representations outside those grammars.
