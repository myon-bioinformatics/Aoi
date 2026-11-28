import Std

/-!
The finite row-index partition constructed by `dragowing.load_overlap`.

Each row has one Boolean signature, represented by its code below `2^sets`.
Every code is enumerated, and each region filters the original row indices.
Indices distinguish repeated rows and repeated display labels. Condition
evaluation, Python's bit-code conversion, and Plotly rendering are not proved.
-/

namespace DRAgoWing

variable {rows sets : Nat}

abbrev Signature (sets : Nat) := Fin (2 ^ sets)

def region (signature : Fin rows → Signature sets) (pattern : Signature sets) :
    List (Fin rows) :=
  (List.finRange rows).filter (fun row => signature row == pattern)

def partition (signature : Fin rows → Signature sets) : List (Fin rows) :=
  (List.finRange (2 ^ sets)).flatMap (region signature)

theorem region_contains_exact_signature (signature : Fin rows → Signature sets)
    (pattern : Signature sets) (row : Fin rows) :
    row ∈ region signature pattern ↔ signature row = pattern := by
  simp [region, List.mem_finRange]

private theorem region_count (signature : Fin rows → Signature sets)
    (pattern : Signature sets) (row : Fin rows) :
    (region signature pattern).count row = if signature row = pattern then 1 else 0 := by
  by_cases equal : signature row = pattern
  · simp only [ite_eq_left equal]
    rw [region, List.count_filter (by simpa only [equal] using beq_self_eq_true pattern)]
    exact (List.nodup_finRange rows).count_of_mem (List.mem_finRange row)
  · simp only [ite_eq_right equal]
    apply List.count_eq_zero_of_not_mem
    simpa only [region_contains_exact_signature] using equal

private theorem partition_count (signature : Fin rows → Signature sets)
    (patterns : List (Signature sets)) (row : Fin rows) :
    (patterns.flatMap (region signature)).count row = patterns.count (signature row) := by
  induction patterns with
  | nil => simp
  | cons pattern rest ih =>
      simp only [List.flatMap_cons, List.count_append, ih, region_count, List.count_cons]
      by_cases equal : signature row = pattern
      · simp [equal, Nat.add_comm]
      · simp [equal, Ne.symm equal]

/-- Every original index occurs once across all regions, without count cancellation. -/
theorem every_row_once (signature : Fin rows → Signature sets) (row : Fin rows) :
    (partition signature).count row = 1 := by
  rw [partition, partition_count]
  exact (List.nodup_finRange (2 ^ sets)).count_of_mem (List.mem_finRange (signature row))

end DRAgoWing
