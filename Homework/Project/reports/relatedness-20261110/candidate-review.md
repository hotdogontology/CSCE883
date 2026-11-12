# Related-proof candidate review index

Six examples spanning the heuristic ranking. These are unreviewed candidates,
not asserted mismatches. Full paired payloads are in the ignored artifact
`artifacts/relatedness-20261110/validation-candidates.jsonl`. No model
predictions or labels were used to select this index.

## proofnet-285 / proofnet-284

Heuristic relatedness: 0.666.

**Anchor English statement:** If $p=2^{n}+1$ is a Fermat prime, show that 3 is a primitive root modulo $p$.

**Donor English statement:** Consider a prime $p$ of the form $4 t+1$. Show that $a$ is a primitive root modulo $p$ iff $-a$ is a primitive root modulo $p$.

**Anchor English proof:** \newcommand{\legendre}[2]{\genfrac{(}{)}{}{}{#1}{#2}}
Write $p = 2^k + 1$, with $k = 2^n$.

We suppose that $n>0$, so $k\geq 2, p \geq 5$. As $p$ is prime, $3^{p-1} \equiv 1 \pmod p$. 

In other words, $3^{2^k} \equiv 1 \pmod p$ : the order of $3$ is a divisor of $2^k$, a power of $2$.

$3$ has order $2^k$ modulo $p$ iff $3^{2^{k-1}} \not \equiv 1 \pmod p$. As $\left (3^{2^{k-1}} \right)^2 \equiv 1 \pmod p$, where $p$ is prime, this is equivalent to $3^{2^{k-1}}  \equiv -1 \pmod p$, which remains to prove.

$3^{2^{k-1}} = 3^{(p-1)/2} \equiv \legendre{3}{p} \pmod p$.

As the result is true for $p=5$, we can suppose $n\geq 2$.
From the law of quadratic reciprocity :
$$\legendre{3}{p} \legendre{p}{3} = (-1)^{(p-1)/2} = (-1)^{2^{k-1}} = 1.$$
So $\legendre{3}{p} = \legendre{p}{3}$
 
\begin{align*}
p = 2^{2^n}+1 &\equiv (-1)^{2^n} + 1 \pmod 3\\
&\equiv 2 \equiv -1 \pmod 3,
\end{align*}
so $\legendre{3}{p} = \legendre {p}{3} = -1$, that is to say
$$3^{2^{k-1}}  \equiv -1 \pmod p.$$
The order of $3$ modulo $p = 2^{2^n} + 1$ is $p-1 = 2^{2^n}$ : $3$ is a primitive root modulo $p$.

(On the other hand, if $3$ is of order $p-1$ modulo $p$, then $p$ is prime, so
$$ F_n = 2^{2^n} + 1 \ \mathrm{is}\ \mathrm{prime}\ \iff 3^{(F_n-1)/2} = 3^{2^{2^n - 1}} \equiv -1 \pmod {F_n}.)$$

**Donor English proof:** Suppose that $a$ is a primitive root modulo $p$. As $p-1$ is even, $(-a)^{p-1}=a^{p-1} \equiv 1$ $(\bmod p)$
If $(-a)^n \equiv 1(\bmod p)$, with $n \in \mathbb{N}$, then $a^n \equiv(-1)^n(\bmod p)$.
Therefore $a^{2 n} \equiv 1(\bmod p)$. As $a$ is a primitive root modulo $p, p-1|2 n, 2 t| n$, so $n$ is even.

Hence $a^n \equiv 1(\bmod p)$, and $p-1 \mid n$. So the least $n \in \mathbb{N}^*$ such that $(-a)^n \equiv 1$ $(\bmod p)$ is $p-1:$ the order of $-a$ modulo $p$ is $p-1,-a$ is a primitive root modulo $p$. Conversely, if $-a$ is a primitive root modulo $p$, we apply the previous result at $-a$ to to obtain that $-(-a)=a$ is a primitive root.

**Anchor Lean statement:**

```lean
theorem Ireland_Rosen_exercise_4_6_corrected {p n : ℕ} (hp : p.Prime) (hpn : p = 2 ^ n + 1)
    (hn : 2 ≤ n) :
    IsPrimitiveRoot (3 : ZMod p) (p - 1)
```

**Donor Lean statement:**

```lean
theorem Ireland_Rosen_exercise_4_4_corrected {p t : ℕ} (hp0 : p.Prime) (hp1 : p = 4 * t + 1)
  (a : ZMod p) :
  IsPrimitiveRoot a (p - 1) ↔ IsPrimitiveRoot (-a) (p - 1)
```

## proofnet-115 / proofnet-116

Heuristic relatedness: 0.3952.

**Anchor English statement:** Define $f_{n}:[0,1] \rightarrow \mathbb{R}$ by the equation $f_{n}(x)=x^{n}$. Show that the sequence $\left(f_{n}(x)\right)$ converges for each $x \in[0,1]$.

**Donor English statement:** Let $X$ be a topological space and let $Y$ be a metric space. Let $f_{n}: X \rightarrow Y$ be a sequence of continuous functions. Let $x_{n}$ be a sequence of points of $X$ converging to $x$. Show that if the sequence $\left(f_{n}\right)$ converges uniformly to $f$, then $\left(f_{n}\left(x_{n}\right)\right)$ converges to $f(x)$.

**Anchor English proof:** If $0 \leq x<1$ is fixed, then $f_n(x) \rightarrow 0$ as $n \rightarrow \infty$. As $f_n(1)=1$ for all $n, f_n(1) \rightarrow 1$. Thus $\left(f_n\right)_n$ converges to $f:[0,1] \rightarrow \mathbb{R}$ given by $f(x)=0$ if $x=0$ and $f(1)=1$. The sequence

**Donor English proof:** Let $d$ be the metric on $Y$. Let $V$ be a neighbourhood of $f(x)$, and let $\varepsilon>0$ be such that $f(x) \in B_d(f(x), \varepsilon) \subset V$. Since $\left(f_n\right)_n$ converges uniformly to $f$, there exists $N_1 \in \mathbb{Z}_{+}$such that $d\left(f_n(x), f(x)\right)<\varepsilon / 2$ for all $x \in X$ and all $n \geq N_1$, so that $d\left(f_n\left(x_n\right), f\left(x_n\right)\right)<\varepsilon / 2$ for all $n \geq N_1$. Moreover, $f$ is continuous, so there exists $N_2 \in \mathbb{Z}_{+}$such that $d\left(f\left(x_n\right), f(x)\right)<\varepsilon / 2$ for all $n \geq N_2$. Thus, if $N>\max \left\{N_1, N_2\right\}$, then
$$
d\left(f_n\left(x_n\right), f(x)\right) \leq d\left(f_n\left(x_n\right), f\left(x_n\right)\right)+d\left(f\left(x_n\right), f(x)\right)<\frac{\varepsilon}{2}+\frac{\varepsilon}{2}=\varepsilon
$$
for all $n \geq N$, so $f_n\left(x_n\right) \in V$ for all $n \geq N$. It follows that $\left(f_n\left(x_n\right)\right)_n$ converges to $f(x)$.

**Anchor Lean statement:**

```lean
theorem Munkres_exercise_21_6a
  (f : ℕ → I → ℝ)
  (h : ∀ x n, f n x = ↑x ^ n) :
  ∀ x, ∃ y, Tendsto (λ n => f n x) atTop (𝓝 y)
```

**Donor Lean statement:**

```lean
theorem Munkres_exercise_21_8
  {X : Type*} [TopologicalSpace X] {Y : Type*} [MetricSpace Y]
  {f : ℕ → X → Y} {x : ℕ → X}
  (hf : ∀ n, Continuous (f n))
  (x₀ : X)
  (hx : Tendsto x atTop (𝓝 x₀))
  (f₀ : X → Y)
  (hh : TendstoUniformly f f₀ atTop) :
  Tendsto (λ n => f n (x n)) atTop (𝓝 (f₀ x₀))
```

## proofnet-128 / proofnet-339

Heuristic relatedness: 0.2675.

**Anchor English statement:** Show that if $X$ has a countable dense subset, every collection of disjoint open sets in $X$ is countable.

**Donor English statement:** Prove that every compact metric space $K$ has a countable base.

**Anchor English proof:** Let $\mathcal{U}$ be a collection of disjoint open sets in $X$ and let $A$ be a countable dense subset of $X$.
Since $A$ is dense in $X$, every $U \in \mathcal{U}$ intersects $S$. Therefore, there exists a point $x_U \in U \cap S$.
Let $U_1, U_2 \in \mathcal{U}, U_1 \neq U_2$. Then $x_{U_1} \neq x_{U_2}$ since $U_1 \cap U_2=\emptyset$.
Thus, the function $\mathcal{U} \rightarrow S$ given by $U \mapsto x_U$ is injective and therefore, since $S$ is countable, it follows that $\mathcal{U}$ is countable.

**Donor English proof:** $K$ can be covered by a finite union of neighborhoods of radius $1 / n$, and this shows that this implies that $K$ is separable.

It is not entirely obvious that a metric space with a countable base is separable. To prove this, let $\left\{V_n\right\}_{n=1}^{\infty}$ be a countable base, and let $x_n \in V_n$. The points $V_n$ must be dense in $X$. For if $G$ is any non-empty open set, then $G$ contains $V_n$ for some $n$, and hence $x_n \in G$. (Thus for a metric space, having a countable base and being separable are equivalent.)

**Anchor Lean statement:**

```lean
theorem Munkres_exercise_30_13_corrected {X : Type*} [TopologicalSpace X]
  (h : ∃ (s : Set X), Countable s ∧ Dense s) (U : Set (Set X))
  (hU : ∀ (x y : Set X), x ∈ U → y ∈ U → x ≠ y → x ∩ y = ∅)
  (hUopen : ∀ (u : Set X), u ∈ U → IsOpen u) :
  Countable U
```

**Donor Lean statement:**

```lean
theorem Rudin_exercise_2_25 {K : Type*} [MetricSpace K] [CompactSpace K] :
  ∃ (B : Set (Set K)), Set.Countable B ∧ IsTopologicalBasis B
```

## proofnet-88 / proofnet-70

Heuristic relatedness: 0.1999.

**Anchor English statement:** Let $F = \mathbb{Z}_p$ be the field of integers $\mod p$, where $p$ is a prime, and let $q(x) \in F[x]$ be irreducible of degree $n$. Show that $F[x]/(q(x))$ is a field having at exactly $p^n$ elements.

**Donor English statement:** Prove that $x^2+y^2-1$ is irreducible in $\mathbb{Q}[x,y]$.

**Anchor English proof:** In the previous problem we have shown that any for any $p(x) \in F[x]$, we have that
$$
p(x)+(q(x))=a_{n-1} x^{n-1}+\cdots+a_1 x+a_0+(q(x))
$$
for some $a_{n-1}, \ldots, a_0 \in F$, and that there are $p^n$ choices for these numbers, so that $F[x] /(q(x)) \leq p^n$. In order to show that equality holds, we have to show that each of these choices induces a different element of $F[x] /(q(x))$; in other words, that each different polynomial of degree $n-1$ or lower belongs to a different coset of $(q(x))$ in $F[x]$.

Suppose now, then, that
$$
a_{n-1} x^{n-1}+\cdots+a_1 x+a_0+(q(x))=b_{n-1} x^{n-1}+\cdots+b_1 x+b_0+(q(x))
$$
which is equivalent with $\left(a_{n-1}-b_{n-1}\right)^{n-1}+\cdots\left(a_1-b_1\right) x+\left(a_0-b_0\right) \in(q(x))$, which is in turn equivalent with there being a $w(x) \in F[x]$ such that
$$
q(x) w(x)=\left(a_{n-1}-b_{n-1}\right)^{n-1}+\cdots\left(a_1-b_1\right) x+\left(a_0-b_0\right) .
$$
Degree of the right hand side is strictly smaller than $n$, while the degree of the left hand side is greater or equal to $n$ except if $w(x)=0$, so that if equality is hold we must have that $w(x)=0$, but then since polynomials are equal iff all of their coefficient are equal we get that $a_{n-1}-b_{n-1}=$ $0, \ldots, a_1-b_1=0, a_0-b_0=0$, i.e.
$$
a_{n-1}=b_{n-1}, \ldots, a_1=b_1, a_0=b_0
$$
which is what we needed to prove.

**Donor English proof:** $$
p(x)=x^2+y^2-1 \in Q[y][x] \cong Q[y, x]
$$
We have that $y+1 \in Q[y]$ is prime and $Q[y]$ is an UFD, since $p(x)=x^2+y^2-1=x^2+$ $(y+1)(y-1)$ by the Eisenstein's Criterion $x^2+y^2-1$ is irreducibile in $Q[x, y]$.

**Anchor Lean statement:**

```lean
theorem Herstein_exercise_4_5_16_corrected {p n: ℕ} (hp : Nat.Prime p)
  {q : Polynomial (ZMod p)} (hq : Irreducible q) (hn : q.degree = n) :
  (∃ is_fin : Fintype $ Polynomial (ZMod p) ⧸ span ({q}),
  @card (Polynomial (ZMod p) ⧸ span {q}) is_fin = p ^ n) ∧
  IsField (Polynomial (ZMod p) ⧸ span {q})
```

**Donor Lean statement:**

```lean
theorem Dummit_Foote_exercise_9_4_11 :
  Irreducible ((MvPolynomial.X 0)^2 + (MvPolynomial.X 1)^2 - 1 : MvPolynomial (Fin 2) ℚ)
```

## proofnet-354 / proofnet-360

Heuristic relatedness: 0.1459.

**Anchor English statement:** Suppose $K$ and $F$ are disjoint sets in a metric space $X, K$ is compact, $F$ is closed. Prove that there exists $\delta>0$ such that $d(p, q)>\delta$ if $p \in K, q \in F$.

**Donor English statement:** Suppose that $f$ is holomorphic in an open set $\Omega$. Prove that if $\text{Im}(f)$ is constant, then $f$ is constant.

**Anchor English proof:** Following the hint, we observe that $\rho_F(x)$ must attain its minimum value on $K$, i.e., there is some point $r \in K$ such that
$$
\rho_F(r)=\min _{q \in K} \rho_F(q) .
$$
Since $F$ is closed and $r \notin F$, it follows from Exercise $4.20$ that $\rho_F(r)>0$. Let $\delta$ be any positive number smaller than $\rho_F(r)$. Then for any $p \in F, q \in K$, we have
$$
d(p, q) \geq \rho_F(q) \geq \rho_F(r)>\delta .
$$
This proves the positive assertion.

**Donor English proof:** Let $f(z)=f(x, y)=u(x, y)+i v(x, y)$, where $z=x+i y$.
Since $\operatorname{Im}(f)=$ constant,
$$
\frac{\partial v}{\partial x}=0, \frac{\partial v}{\partial y}=0 .
$$
By the Cauchy-Riemann equations,
$$
\frac{\partial u}{\partial x}=\frac{\partial v}{\partial y}=0 .
$$
Thus in $\Omega$,
$$
f^{\prime}(z)=\frac{\partial f}{\partial x}=\frac{\partial u}{\partial x}+i \frac{\partial v}{\partial x}=0+0=0 .
$$
Thus $f$ is constant.

**Anchor Lean statement:**

```lean
theorem Rudin_exercise_4_21a_corrected {X : Type*} [MetricSpace X]
  (K F : Set X) (hK : IsCompact K) (hF : IsClosed F) (hKF : Disjoint K F) :
  ∃ (δ : ℝ), δ > 0 ∧ ∀ (p q : X), p ∈ K → q ∈ F → dist p q > δ
```

**Donor Lean statement:**

```lean
theorem Shakarchi_exercise_1_13b_corrected {f : ℂ → ℂ} {Ω : Set ℂ}
    (hΩ : IsOpen Ω) (hConn : IsPreconnected Ω)
    (hf : DifferentiableOn ℂ f Ω)
    (hc : ∃ c : ℝ, ∀ z ∈ Ω, (f z).im = c) :
    ∀ a b : Ω, f a = f b
```

## proofnet-243 / proofnet-67

Heuristic relatedness: 0.0662.

**Anchor English statement:** Prove that any subring of a field which contains the identity is an integral domain.

**Donor English statement:** Prove that if $f(x)$ and $g(x)$ are polynomials with rational coefficients whose product $f(x) g(x)$ has integer coefficients, then the product of any coefficient of $g(x)$ with any coefficient of $f(x)$ is an integer.

**Anchor English proof:** Solution: Let $R \subseteq F$ be a subring of a field. (We need not yet assume that $1 \in R$ ). Suppose $x, y \in R$ with $x y=0$. Since $x, y \in F$ and the zero element in $R$ is the same as that in $F$, either $x=0$ or $y=0$. Thus $R$ has no zero divisors. If $R$ also contains 1 , then $R$ is an integral domain.

**Donor English proof:** Let $f(x), g(x) \in \mathbb{Q}[x]$ be such that $f(x) g(x) \in \mathbb{Z}[x]$.
By Gauss' Lemma there exists $r, s \in \mathbb{Q}$ such that $r f(x), s g(x) \in \mathbb{Z}[x]$, and $(r f(x))(s g(x))=r s f(x) g(x)=f(x) g(x)$. From this last relation we can conclude that $s=r^{-1}$.

Therefore for any coefficient $f_i$ of $f(x)$ and $g_j$ of $g(x)$ we have that $r f_i, r^{-1} g_j \in$ $\mathbb{Z}$ and by multiplicative closure and commutativity of $\mathbb{Z}$ we have that $r f_i r^{-1} g_j=$ $f_i g_j \in \mathbb{Z}$

**Anchor Lean statement:**

```lean
theorem Dummit_Foote_exercise_7_1_12 {F : Type*} [Field F] {K : Subring F}
  (hK : (1 : F) ∈ K) : IsDomain K
```

**Donor Lean statement:**

```lean
theorem Dummit_Foote_exercise_9_3_2_corrected {f g : Polynomial ℚ} (i j : ℕ)
    (hfg : ∀ n : ℕ, ∃ a : ℤ, (f * g).coeff n = a) :
    ∃ a : ℤ, f.coeff i * g.coeff j = a
```
