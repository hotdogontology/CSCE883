import Mathlib

open scoped BigOperators

namespace ArgumentCore

-- Constructed held-out diagnostic. Route labels are agent-authored, not human audited.

-- BEGIN odd_sum A
theorem odd_sum_induction (n : ℕ) :
    (∑ k ∈ Finset.range n, (2 * (k : ℤ) + 1)) = (n : ℤ) ^ 2 := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Finset.sum_range_succ, ih]
      push_cast
      ring
-- END odd_sum A

-- BEGIN odd_sum B
theorem odd_sum_telescoping (n : ℕ) :
    (∑ k ∈ Finset.range n, (2 * (k : ℤ) + 1)) = (n : ℤ) ^ 2 := by
  calc
    (∑ k ∈ Finset.range n, (2 * (k : ℤ) + 1)) =
        ∑ k ∈ Finset.range n, (((k : ℤ) + 1) ^ 2 - (k : ℤ) ^ 2) := by
          apply Finset.sum_congr rfl
          intro k _hk
          ring
    _ = (n : ℤ) ^ 2 := by
      simpa using (Finset.sum_range_sub (fun k : ℕ => (k : ℤ) ^ 2) n)
-- END odd_sum B

-- BEGIN consecutive_even A
theorem consecutive_even_induction (n : ℕ) : ∃ k : ℕ, n * (n + 1) = 2 * k := by
  induction n with
  | zero => exact ⟨0, by norm_num⟩
  | succ n ih =>
      obtain ⟨k, hk⟩ := ih
      refine ⟨k + n + 1, ?_⟩
      calc
        (n + 1) * (n + 1 + 1) = n * (n + 1) + 2 * (n + 1) := by ring
        _ = 2 * k + 2 * (n + 1) := by rw [hk]
        _ = 2 * (k + n + 1) := by ring
-- END consecutive_even A

-- BEGIN consecutive_even B
theorem consecutive_even_parity (n : ℕ) : ∃ k : ℕ, n * (n + 1) = 2 * k := by
  obtain ⟨m, hm | hm⟩ := Nat.even_or_odd' n
  · refine ⟨m * (n + 1), ?_⟩
    rw [hm]
    ring
  · refine ⟨n * (m + 1), ?_⟩
    rw [hm]
    ring
-- END consecutive_even B

-- BEGIN cubic_root A
theorem cubic_root_explicit : ∃ x : ℝ, x ^ 3 + x = 2 := by
  refine ⟨1, ?_⟩
  norm_num
-- END cubic_root A

-- BEGIN cubic_root B
theorem cubic_root_ivt : ∃ x : ℝ, x ^ 3 + x = 2 := by
  have hc : Continuous (fun x : ℝ => x ^ 3 + x) := by fun_prop
  have hmem : (2 : ℝ) ∈ Set.Icc ((0 : ℝ) ^ 3 + 0) ((2 : ℝ) ^ 3 + 2) := by
    norm_num
  obtain ⟨x, _hx, hvalue⟩ := intermediate_value_Icc (by norm_num : (0 : ℝ) ≤ 2)
    hc.continuousOn hmem
  exact ⟨x, hvalue⟩
-- END cubic_root B

-- BEGIN power_divisibility A
theorem power_divisibility_induction (n : ℕ) : (3 : ℤ) ∣ 4 ^ n - 1 := by
  induction n with
  | zero => norm_num
  | succ n ih =>
      obtain ⟨k, hk⟩ := ih
      refine ⟨4 * k + 1, ?_⟩
      rw [pow_succ]
      linarith
-- END power_divisibility A

-- BEGIN power_divisibility B
theorem power_divisibility_geometric (n : ℕ) : (3 : ℤ) ∣ 4 ^ n - 1 := by
  refine ⟨∑ k ∈ Finset.range n, (4 : ℤ) ^ k, ?_⟩
  have h := mul_geom_sum (4 : ℤ) n
  norm_num at h
  exact h.symm
-- END power_divisibility B

#print axioms odd_sum_induction
#print axioms odd_sum_telescoping
#print axioms consecutive_even_induction
#print axioms consecutive_even_parity
#print axioms cubic_root_explicit
#print axioms cubic_root_ivt
#print axioms power_divisibility_induction
#print axioms power_divisibility_geometric

end ArgumentCore
