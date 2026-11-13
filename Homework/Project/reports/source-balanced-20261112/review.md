# Source-balanced pilot review

Provisional agent review; labels are not human gold.

## faithform-llms-row-14 (train; MISMATCH)

Assumes the asserted total=sum as a hypothesis, rather than establishing the counting claim.

```text
Context:

Step:
Total distinct books (in the collection) = Dolly's books + Pandora's books.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (dolly_books pandora_books total_distinct_books : ℕ)
    (h : total_distinct_books = dolly_books + pandora_books) :
    total_distinct_books = dolly_books + pandora_books := by
  sorry
```

## faithform-llms-row-15 (train; MISMATCH)

Assumes the asserted total=product as a hypothesis; this changes the obligation to a tautology.

```text
Context:

Step:
Total distinct books (in the collection) = Dolly's books × Pandora's books.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (dolly_books pandora_books total_distinct_books : ℕ)
    (h : total_distinct_books = dolly_books * pandora_books) :
    total_distinct_books = dolly_books * pandora_books := by
  sorry
```

## faithform-llms-row-16 (train; MATCH)

Preserves the explicit local arithmetic calculation 2+1=3; book interpretation remains supplied by English context.

```text
Context:
Dolly has 2 books.
Pandora has 1 book.
Total distinct books (in the collection) = Dolly's books + Pandora's books.
Step:
Total distinct books = 2 + 1 = 3.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target : 2 + 1 = 3 := by
  sorry
```

## faithform-llms-row-18 (train; MATCH)

Four hypotheses preserve each reader reading each collection; the union conclusion covers both readers for every book.

```text
Context:

Step:
Both Dolly and Pandora read each other's books as well as their own; hence each person reads all books in the combined collection.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target
    (Book : Type)
    (DollyBooks PandoraBooks : Book → Prop)
    (DollyReads PandoraReads : Book → Prop)
    (h1 : ∀ b, DollyBooks b → DollyReads b)
    (h2 : ∀ b, PandoraBooks b → DollyReads b)
    (h3 : ∀ b, DollyBooks b → PandoraReads b)
    (h4 : ∀ b, PandoraBooks b → PandoraReads b) :
    ∀ b, (DollyBooks b ∨ PandoraBooks b) → (DollyReads b ∧ PandoraReads b) := by
  sorry
```

## faithform-llms-row-28 (train; MATCH)

Preserves the explicit local calculation 9+5=14; color interpretation is supplied by source context.

```text
Context:
There are 9 red sticks.
The number of blue sticks is 5 more than the number of red sticks.
Step:
Blue sticks = 9 + 5 = 14.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target : 9 + 5 = 14 := by
  sorry
```

## faithform-llms-row-30 (train; MATCH)

Preserves 14-3=11; natural subtraction agrees with the nonnegative counts in this local step.

```text
Context:
The number of yellow sticks is 3 less than the number of blue sticks.
Blue sticks = 9 + 5 = 14.
Step:
Yellow sticks = 14 - 3 = 11.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target : 14 - 3 = 11 := by
  sorry
```

## faithform-llms-row-32 (train; MISMATCH)

Adds total=red+blue+yellow as a premise, assuming the claim instead of deriving the total.

```text
Context:

Step:
Total sticks = red + blue + yellow.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (red blue yellow total : ℕ) (h : total = red + blue + yellow) : total = red + blue + yellow := by
  sorry
```

## faithform-llms-row-33 (train; MISMATCH)

Adds the claimed total=red+blue-yellow as a premise; does not establish the original counting relation.

```text
Context:

Step:
Total sticks = red + blue - yellow.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (total red blue yellow : ℤ)
    (h : total = red + blue - yellow) : total = red + blue - yellow := by
  sorry
```

## faithform-llms-row-38 (validation; MISMATCH)

Assumes the total-count formula it was asked to establish, leaving only identity of premise and conclusion.

```text
Context:
Last night Rick killed 10 wolves.
Last night Rick killed 15 cougars.
Let x be the number of cougars Rick killed today.
Then the number of wolves killed today is 3x.
Step:
Total animals killed = (wolves last night) + (cougars last night) + (wolves today) + (cougars today).
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (x : ℕ) (total_animals_killed : ℕ)
    (h : total_animals_killed = 10 + 15 + 3 * x + x) :
    total_animals_killed = 10 + 15 + 3 * x + x := by
  sorry
```

## faithform-llms-row-41 (validation; MISMATCH)

Replaces a claim about total animals with expression=itself; removes the connection to the total.

```text
Context:
Total animals killed = (wolves last night) + (cougars last night) + (wolves today) + (cougars today).
Last night Rick killed 10 wolves.
Last night Rick killed 15 cougars.
x = 12.
Wolves today = 3x = 3(12) = 36.
Step:
Total animals killed = 10 + 15 + 36 - 12.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target : (10 + 15 + 36 - 12 : ℤ) = 10 + 15 + 36 - 12 := by
  sorry
```

## faithform-llms-row-42 (validation; MATCH)

Preserves the source total via its dependency counts: 10+15+36+12=73. Local arithmetic fidelity, not full story certification.

```text
Context:
Total animals killed = 10 + 15 + 36 + 12.
Step:
Total animals killed = 73.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target : 10 + 15 + 36 + 12 = 73 := by
  sorry
```

## faithform-llms-row-52 (validation; MATCH)

Preserves x=12 as a hypothesis and 3*x=36 as conclusion, representing the stated substitution/calculation.

```text
Context:
Then the number of wolves killed today is 3x.
x = 12.
Step:
Wolves today = 3x = 3(12) = 36.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (x : ℝ) (hx : x = 12) : 3 * x = 36 := by
  sorry
```

## faithform-llms-row-54 (test; MISMATCH)

Omits the observation that five fries remain and universally asserts the resulting equation for arbitrary x.

```text
Context:
After ants carry off 1 fry, remaining fries are (1/3)(x − 30) − 1.
Step:
Given that 5 fries were left at the end, set (1/3)(x − 30) − 1 = 5.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (x : ℝ) : (1/3) * (x - 30) - 1 = 5 := by
  sorry
```

## faithform-llms-row-55 (test; MISMATCH)

Changes an equation about the given initial quantity into existence of some real quantity satisfying an equation.

```text
Context:
After ants carry off 1 fry, remaining fries are (1/3)(x − 30) − 1.
Step:
Given that 5 fries were left at the end, set \(frac{1}{3}(x - 30) + 1 = 5.\)
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target : ∃ x : ℝ, (1 / 3) * (x - 30) + 1 = 5 := by
  sorry
```

## faithform-llms-row-56 (test; MATCH)

Preserves the preceding equation as a hypothesis and the add-one inference as conclusion.

```text
Context:
Given that 5 fries were left at the end, set (1/3)(x − 30) − 1 = 5.
Step:
Add 1 to both sides: (1/3)(x − 30) = 6.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (x : ℝ) (h : (1/3) * (x - 30) - 1 = 5) : (1/3) * (x - 30) = 6 := by
  sorry
```

## faithform-llms-row-58 (test; MATCH)

Preserves the one-third equation as hypothesis and multiplication-by-three conclusion.

```text
Context:
Add 1 to both sides: (1/3)(x − 30) = 6.
Step:
Multiply both sides by 3: x − 30 = 18.
```

```lean
import Mathlib
import Aesop
set_option maxHeartbeats 0
open BigOperators Real Nat Topology Rat
theorem target (x : ℝ) (h : (1/3) * (x - 30) = 6) : x - 30 = 18 := by
  sorry
```

## proofnet-164-hard-positive (train; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
If $f$ is a continuous mapping of a metric space $X$ into a metric space $Y$, prove that $f(\overline{E}) \subset \overline{f(E)}$ for every set $E \subset X$. ($\overline{E}$ denotes the closure of $E$).
Proof:
Let $x \in \bar{E}$. We need to show that $f(x) \in \overline{f(E)}$. To this end, let $O$ be any neighborhood of $f(x)$. Since $f$ is continuous, $f^{-1}(O)$ contains (is) a neighborhood of $x$. Since $x \in \bar{E}$, there is a point $u$ of $E$ in $f^{-1}(O)$. Hence $\frac{f(u)}{f(E)} \in O \cap f(E)$. Since $O$ was any neighborhood of $f(x)$, it follows that $f(x) \in \overline{f(E)}$
```

```lean
import Mathlib
open Topology Filter Real Complex TopologicalSpace Finset
open scoped BigOperators
theorem target
  {α : Type} [MetricSpace α]
  {β : Type} [MetricSpace β]
  (f : α → β)
  (h₁ : Continuous f)
  : ∀ (x : Set α), f '' (closure x) ⊆ closure (f '' x) := by
  classical
  intro x
  simpa using image_closure_subset_closure_image (f := f) (s := x) h₁
```

## proofnet-164-hard-bundle (train; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
Let $f$ and $g$ be continuous mappings of a metric space $X$ into a metric space $Y$, and let $E$ be a dense subset of $X$. Prove that $f(E)$ is dense in $f(X)$.
Proof:
To prove that $f(E)$ is dense in $f(X)$, simply use that $f(X)=f(\bar{E}) \subseteq \overline{f(E)}$.
```

```lean
import Mathlib
open Topology Filter Real Complex TopologicalSpace Finset
open scoped BigOperators
theorem target
  {α : Type} [MetricSpace α]
  {β : Type} [MetricSpace β]
  (f : α → β)
  (h₁ : Continuous f)
  : ∀ (x : Set α), f '' (closure x) ⊆ closure (f '' x) := by
  classical
  intro x
  simpa using image_closure_subset_closure_image (f := f) (s := x) h₁
```

## proofnet-301-hard-positive (train; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
Let $p \colon X \rightarrow Y$ be an open map. Show that if $A$ is open in $X$, then the map $q \colon A \rightarrow p(A)$ obtained by restricting $p$ is an open map.
Proof:
Let $U$ be open in $A$. Since $A$ is open in $X, U$ is open in $X$ as well, so $p(U)$ is open in $Y$. Since $q(U)=p(U)=p(U) \cap p(A)$, the set $q(U)$ is open in $p(A)$. Thus $q$ is an open map.
```

```lean
import Mathlib
open Filter Set TopologicalSpace
open scoped Topology
theorem target {X Y : Type*} [TopologicalSpace X]
  [TopologicalSpace Y] (p : X → Y) (hp : IsOpenMap p)
  (A : Set X) (hA : IsOpen A) :
  IsOpenMap (Set.MapsTo.restrict p A (p '' A) (Set.mapsTo_image p A)) := by
  exact hp.mapsToRestrict hA (Set.mapsTo_image p A)
```

## proofnet-301-hard-bundle (train; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
A map $f: X \rightarrow Y$ is said to be an open map if for every open set $U$ of $X$, the set $f(U)$ is open in $Y$. Show that $\pi_{1}: X \times Y \rightarrow X$ and $\pi_{2}: X \times Y \rightarrow Y$ are open maps.
Proof:
Exercise 16.4. Let $U \times V$ be a (standard) basis element for $X \times Y$, so that $U$ is open in $X$ and $V$ is open in $Y$. Then $\pi_1(U \times V)=U$ is open in $X$ and $\pi_2(U \times V)=V$ is open in $Y$. Since arbitrary maps and unions satisfy $f\left(\bigcup_\alpha W_\alpha\right)=\bigcup_\alpha f\left(W_\alpha\right)$, it follows that $\pi_1$ and $\pi_2$ are open maps.
```

```lean
import Mathlib
open Filter Set TopologicalSpace
open scoped Topology
theorem target {X Y : Type*} [TopologicalSpace X]
  [TopologicalSpace Y] (p : X → Y) (hp : IsOpenMap p)
  (A : Set X) (hA : IsOpen A) :
  IsOpenMap (Set.MapsTo.restrict p A (p '' A) (Set.mapsTo_image p A)) := by
  exact hp.mapsToRestrict hA (Set.mapsTo_image p A)
```

## proofnet-132-hard-positive (train; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
Show that every locally compact Hausdorff space is regular.
Proof:
Let $X$ be a LCH space.
Then it follows that for every $x \in X$ and for every open neighborhood $U \subseteq X$ of $x$ there exists an open neighborhood $V \subseteq X$ of $x$ such that $\bar{V} \subseteq U$ (and $\bar{V}$ is compact, but this is not important here).
Since $X$ is a Hausdorff space, it satisfies the $T_1$ axiom.
Then it follows that $X$ is regular.
```

```lean
import Mathlib
open Filter Set TopologicalSpace
open scoped Topology
theorem target {X : Type*} [TopologicalSpace X]
  (hX : LocallyCompactSpace X) (hX' : T2Space X) :
  RegularSpace X := by
  haveI : LocallyCompactSpace X := hX
  haveI : T2Space X := hX'
  exact inferInstance
```

## proofnet-132-hard-bundle (train; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
Show that every locally compact Hausdorff space is completely regular.
Proof:
$X$ is a subspace of a compact Hausdorff space $Y$, its one-point compactification. $Y$ is normal, and so by the Urysohn lemma $Y$ is completely regular. Therefore by corollary $X$ is completely regular.
```

```lean
import Mathlib
open Filter Set TopologicalSpace
open scoped Topology
theorem target {X : Type*} [TopologicalSpace X]
  (hX : LocallyCompactSpace X) (hX' : T2Space X) :
  RegularSpace X := by
  haveI : LocallyCompactSpace X := hX
  haveI : T2Space X := hX'
  exact inferInstance
```

## proofnet-246-hard-positive (train; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
Let $R$ be a commutative ring with $1 \neq 0$. Prove that if $a$ is a nilpotent element of $R$ then $1-a b$ is a unit for all $b \in R$.
Proof:
$\mathfrak{N}(R)$ is an ideal of $R$. Thus for all $b \in R,-a b$ is nilpotent. Hence $1-a b$ is a unit in $R$.
```

```lean
import Mathlib
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
theorem target {R : Type*} [CommRing R] (hR : (0 : R) ≠ 1)
  {a : R} (ha : IsNilpotent a) (b : R) :
  IsUnit (1-a*b) := by
  obtain ⟨n, hn⟩ := ha
  by_cases hzero : n = 0
  ·
    have hcontr : (1 : R) = 0 := by simpa [hzero] using hn
    exact (hR hcontr.symm).elim
  ·
    have hnil : IsNilpotent (a * b) := by
      refine ⟨n, ?_⟩
      simp [mul_pow, hn]
    simpa using hnil.isUnit_one_sub
```

## proofnet-246-hard-bundle (train; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
Prove that if $R$ is an integral domain and $x^{2}=1$ for some $x \in R$ then $x=\pm 1$.
Proof:
Solution: If $x^2=1$, then $x^2-1=0$. Evidently, then,
$$
(x-1)(x+1)=0 .
$$
Since $R$ is an integral domain, we must have $x-1=0$ or $x+1=0$; thus $x=1$ or $x=-1$.
```

```lean
import Mathlib
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
theorem target {R : Type*} [CommRing R] (hR : (0 : R) ≠ 1)
  {a : R} (ha : IsNilpotent a) (b : R) :
  IsUnit (1-a*b) := by
  obtain ⟨n, hn⟩ := ha
  by_cases hzero : n = 0
  ·
    have hcontr : (1 : R) = 0 := by simpa [hzero] using hn
    exact (hR hcontr.symm).elim
  ·
    have hnil : IsNilpotent (a * b) := by
      refine ⟨n, ?_⟩
      simp [mul_pow, hn]
    simpa using hnil.isUnit_one_sub
```

## proofnet-190-hard-positive (validation; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
An element $x$ of a ring $R$ is called nilpotent if some power of $x$ is zero. Prove that if $x$ is nilpotent, then $1+x$ is a unit in $R$.
Proof:
If $x^n=0$, then
$$
(1+x)\left(\sum_{k=0}^{n-1}(-1)^k x^k\right)=1+(-1)^{n-1} x^n=1 .
$$
```

```lean
import Mathlib
open Function Fintype Subgroup Ideal Polynomial Submodule Zsqrtd
open scoped BigOperators
theorem target {R : Type*} [Ring R] {x : R}
  (hx : IsNilpotent x) : IsUnit (1 + x) := by
  exact hx.isUnit_one_add
```

## proofnet-190-hard-bundle (validation; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
Prove that if $u$ is a unit in $R$ then so is $-u$.
Proof:
Solution: Since $u$ is a unit, we have $u v=v u=1$ for some $v \in R$. Thus, we have
$$
(-v)(-u)=v u=1
$$
and
$$
(-u)(-v)=u v=1 .
$$
Thus $-u$ is a unit.
```

```lean
import Mathlib
open Function Fintype Subgroup Ideal Polynomial Submodule Zsqrtd
open scoped BigOperators
theorem target {R : Type*} [Ring R] {x : R}
  (hx : IsNilpotent x) : IsUnit (1 + x) := by
  exact hx.isUnit_one_add
```

## proofnet-242-hard-positive (validation; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
Prove that if $u$ is a unit in $R$ then so is $-u$.
Proof:
Solution: Since $u$ is a unit, we have $u v=v u=1$ for some $v \in R$. Thus, we have
$$
(-v)(-u)=v u=1
$$
and
$$
(-u)(-v)=u v=1 .
$$
Thus $-u$ is a unit.
```

```lean
import Mathlib
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
theorem target {R : Type*} [Ring R] {u : R}
  (hu : IsUnit u) : IsUnit (-u) := by
  rcases hu with ⟨u', rfl⟩
  refine ⟨-u', ?_⟩
  simp
```

## proofnet-242-hard-bundle (validation; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
An element $x$ of a ring $R$ is called nilpotent if some power of $x$ is zero. Prove that if $x$ is nilpotent, then $1+x$ is a unit in $R$.
Proof:
If $x^n=0$, then
$$
(1+x)\left(\sum_{k=0}^{n-1}(-1)^k x^k\right)=1+(-1)^{n-1} x^n=1 .
$$
```

```lean
import Mathlib
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
theorem target {R : Type*} [Ring R] {u : R}
  (hu : IsUnit u) : IsUnit (-u) := by
  rcases hu with ⟨u', rfl⟩
  refine ⟨-u', ?_⟩
  simp
```

## proofnet-15-hard-positive (test; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
Prove that $-(-v) = v$ for every $v \in V$.
Proof:
By definition, we have
$$
(-v)+(-(-v))=0 \quad \text { and } \quad v+(-v)=0 .
$$
This implies both $v$ and $-(-v)$ are additive inverses of $-v$, by the uniqueness of additive inverse, it follows that $-(-v)=v$.
```

```lean
import Mathlib
open Fintype Complex Polynomial LinearMap FiniteDimensional Module Module.End
open scoped BigOperators
theorem target {F V : Type*} [AddCommGroup V] [Field F]
  [Module F V] {v : V} : -(-v) = v := by
  simp
```

## proofnet-15-hard-bundle (test; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
Suppose that $T \in \mathcal{L}(V)$ has $\operatorname{dim} V$ distinct eigenvalues and that $S \in \mathcal{L}(V)$ has the same eigenvectors as $T$ (not necessarily with the same eigenvalues). Prove that $S T=T S$.
Proof:
First off, let $n=\operatorname{dim} V$. so, there is a basis of $\left(v_1, \ldots, v_j\right)$ of $V$ that consist of eigenvectors of $T$. Now, let $\lambda_1, \ldots, \lambda_n$ be the corresponding eigenvalues, then we would have $T v_j=\lambda_1 v_j$ for every single $j$.

Now, for every $v_j$ is also an eigenvector of S, so $S v_j=a_j v_j$ for some $a_j \in F$. For each $j$, we would then have $(S T) v_j=S\left(T v_j\right)=\lambda_j S v_j=a_j \lambda_j v_j$ and $(T S) v_j=T\left(S v_j\right)=a_j T v_j=a_j \lambda_j v_j$. Since both operators, which are $S T$ and $T S$, agree on a basis, then both are equal.
```

```lean
import Mathlib
open Fintype Complex Polynomial LinearMap FiniteDimensional Module Module.End
open scoped BigOperators
theorem target {F V : Type*} [AddCommGroup V] [Field F]
  [Module F V] {v : V} : -(-v) = v := by
  simp
```

## proofnet-42-hard-positive (test; MATCH)

Source argument correspondence assumed by user; not independently audited.

```text
Let $H \leq K \leq G$. Prove that $|G: H|=|G: K| \cdot|K: H|$ (do not assume $G$ is finite).
Proof:
Proof. Let $G$ be a group and let $I$ be a nonempty set of indices, not necessarily countable. Consider the collection of subgroups $\left\{N_\alpha \mid \alpha \in I\right\}$, where $N_\alpha \unlhd G$ for each $\alpha \in I$. Let
$$
N=\bigcap_{\alpha \in I} N_\alpha .
$$
We know $N$ is a subgroup of $G$.
For any $g \in G$ and any $n \in N$, we must have $n \in N_\alpha$ for each $\alpha$. And since $N_\alpha \unlhd G$, we have $g n g^{-1} \in N_\alpha$ for each $\alpha$. Therefore $g n g^{-1} \in N$, which shows that $g N g^{-1} \subseteq N$ for each $g \in G$. As before, this is enough to complete the proof.
```

```lean
import Mathlib
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
noncomputable section
end
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
noncomputable def Subgroup.relindex {G : Type*} [Group G] (H K : Subgroup G) : ℕ :=
  H.relIndex K
theorem target {G : Type*} [Group G] {H K : Subgroup G}
  (hHK : H ≤ K) :
  H.index = K.index * H.relindex K := by
  classical
  have h := Subgroup.relIndex_mul_index (H := H) (K := K) hHK
  simpa [mul_comm] using h.symm
```

## proofnet-42-hard-bundle (test; MISMATCH)

Different related source assumed semantically mismatched; not independently reviewed.

```text
Prove that $\mathbb{Q}$ has no proper subgroups of finite index.
Proof:
Solution: We begin with a lemma.
Lemma: If $D$ is a divisible abelian group, then no proper subgroup of $D$ has finite index.
Proof: We saw previously that no finite group is divisible and that every proper quotient $D / A$ of a divisible group is divisible; thus no proper quotient of a divisible group is finite. Equivalently, $[D: A]$ is not finite.
Because $\mathbb{Q}$ and $\mathbb{Q} / \mathbb{Z}$ are divisible, the conclusion follows.
```

```lean
import Mathlib
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
noncomputable section
end
open Fintype Subgroup Set Polynomial Ideal
open scoped BigOperators
noncomputable def Subgroup.relindex {G : Type*} [Group G] (H K : Subgroup G) : ℕ :=
  H.relIndex K
theorem target {G : Type*} [Group G] {H K : Subgroup G}
  (hHK : H ≤ K) :
  H.index = K.index * H.relindex K := by
  classical
  have h := Subgroup.relIndex_mul_index (H := H) (K := K) hHK
  simpa [mul_comm] using h.symm
```
