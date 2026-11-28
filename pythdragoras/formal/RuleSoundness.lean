import Std

/-!
Set semantics of core/bitwise_surrogate.py's AND / NOT / positive-OR fragment.
Features are abstract: the statements hold for every feature type and every
total assignment, not only the bounded masks exercised by Python tests.
This is a mathematical model; bit packing and Python execution are checked
separately. A satisfying assignment need not correspond to a realizable row
when feature predicates have additional domain relationships.
-/

namespace PythDRagoras

universe u

structure Rule (Feature : Type u) where
  required : Feature → Prop
  forbidden : Feature → Prop
  clauses : List (Feature → Prop)

def Holds {Feature : Type u} (rule : Rule Feature) (row : Feature → Prop) : Prop :=
  (∀ bit, rule.required bit → row bit) ∧
  (∀ bit, rule.forbidden bit → ¬ row bit) ∧
  (∀ clause ∈ rule.clauses, ∃ bit, clause bit ∧ row bit)

/-- The two checks made by Python satisfiable(). -/
def Live {Feature : Type u} (rule : Rule Feature) : Prop :=
  (∀ bit, rule.required bit → ¬ rule.forbidden bit) ∧
  (∀ clause ∈ rule.clauses, ∃ bit, clause bit ∧ ¬ rule.forbidden bit)

theorem satisfiable_iff {Feature : Type u} (rule : Rule Feature) :
    (∃ row, Holds rule row) ↔ Live rule := by
  constructor
  · rintro ⟨row, required, forbidden, clauses⟩
    constructor
    · intro bit hr hf
      exact forbidden bit hf (required bit hr)
    · intro clause hc
      obtain ⟨bit, hb, hx⟩ := clauses clause hc
      exact ⟨bit, hb, fun hf => forbidden bit hf hx⟩
  · intro live
    refine ⟨fun bit => ¬ rule.forbidden bit, live.1, ?_, live.2⟩
    intro bit hf hn
    exact hn hf

theorem unsatisfiable_rejects_all {Feature : Type u} (rule : Rule Feature)
    (dead : ¬ Live rule) : ∀ row, ¬ Holds rule row := by
  intro row holds
  exact dead ((satisfiable_iff rule).mp ⟨row, holds⟩)

/-- Required features and singleton allowed OR clauses are forced true. -/
def Forced {Feature : Type u} (rule : Rule Feature) (bit : Feature) : Prop :=
  rule.required bit ∨
  ∃ clause ∈ rule.clauses,
    clause bit ∧ ¬ rule.forbidden bit ∧
      ∀ other, clause other → ¬ rule.forbidden other → other = bit

theorem forced_true {Feature : Type u} (rule : Rule Feature)
    (row : Feature → Prop) (holds : Holds rule row) (bit : Feature)
    (forced : Forced rule bit) : row bit := by
  rcases forced with required | ⟨clause, hc, _, _, singleton⟩
  · exact holds.1 bit required
  · obtain ⟨other, ho, hx⟩ := holds.2.2 clause hc
    have allowed : ¬ rule.forbidden other := fun hf => holds.2.1 other hf hx
    have equal : other = bit := singleton other ho allowed
    exact equal ▸ hx

/-- The successful branch of Python implies(), after its unsatisfiable check. -/
def ImplicationChecks {Feature : Type u} (a b : Rule Feature) : Prop :=
  (∀ bit, b.required bit → Forced a bit) ∧
  (∀ bit, b.forbidden bit → a.forbidden bit) ∧
  (∀ clause ∈ b.clauses,
    (∃ bit, clause bit ∧ Forced a bit) ∨
    (∃ own ∈ a.clauses,
      ∀ bit, own bit → ¬ a.forbidden bit → clause bit))

theorem implication_checks_sound {Feature : Type u} (a b : Rule Feature)
    (checks : ImplicationChecks a b) (row : Feature → Prop)
    (accepted : Holds a row) : Holds b row := by
  constructor
  · intro bit required
    exact forced_true a row accepted bit (checks.1 bit required)
  constructor
  · intro bit forbidden
    exact accepted.2.1 bit (checks.2.1 bit forbidden)
  · intro clause hc
    rcases checks.2.2 clause hc with ⟨bit, hb, hf⟩ | ⟨own, ho, included⟩
    · exact ⟨bit, hb, forced_true a row accepted bit hf⟩
    · obtain ⟨bit, hb, hx⟩ := accepted.2.2 own ho
      have allowed : ¬ a.forbidden bit := fun hf => accepted.2.1 bit hf hx
      exact ⟨bit, included bit hb allowed, hx⟩

/-- Includes the vacuous-implication branch for an impossible antecedent. -/
theorem reported_implication_sound {Feature : Type u} (a b : Rule Feature)
    (reported : ¬ Live a ∨ ImplicationChecks a b) :
    ∀ row, Holds a row → Holds b row := by
  intro row accepted
  rcases reported with dead | checks
  · exact False.elim (unsatisfiable_rejects_all a dead row accepted)
  · exact implication_checks_sound a b checks row accepted

/-- Python _both unions required/forbidden features and appends clauses. -/
def Both {Feature : Type u} (a b : Rule Feature) : Rule Feature where
  required := fun bit => a.required bit ∨ b.required bit
  forbidden := fun bit => a.forbidden bit ∨ b.forbidden bit
  clauses := a.clauses ++ b.clauses

theorem combined_rule_iff {Feature : Type u} (a b : Rule Feature)
    (row : Feature → Prop) : Holds (Both a b) row ↔ Holds a row ∧ Holds b row := by
  constructor
  · intro joint
    constructor
    · refine ⟨?_, ?_, ?_⟩
      · intro bit hr
        exact joint.1 bit (Or.inl hr)
      · intro bit hf
        exact joint.2.1 bit (Or.inl hf)
      · intro clause hc
        exact joint.2.2 clause (List.mem_append.mpr (Or.inl hc))
    · refine ⟨?_, ?_, ?_⟩
      · intro bit hr
        exact joint.1 bit (Or.inr hr)
      · intro bit hf
        exact joint.2.1 bit (Or.inr hf)
      · intro clause hc
        exact joint.2.2 clause (List.mem_append.mpr (Or.inr hc))
  · rintro ⟨left, right⟩
    refine ⟨?_, ?_, ?_⟩
    · intro bit hr
      exact hr.elim (left.1 bit) (right.1 bit)
    · intro bit hf
      exact hf.elim (left.2.1 bit) (right.2.1 bit)
    · intro clause hc
      exact (List.mem_append.mp hc).elim (left.2.2 clause) (right.2.2 clause)

theorem exclusive_sound {Feature : Type u} (a b : Rule Feature)
    (dead : ¬ Live (Both a b)) : ∀ row, ¬ (Holds a row ∧ Holds b row) := by
  intro row both
  exact unsatisfiable_rejects_all (Both a b) dead row ((combined_rule_iff a b row).mpr both)

end PythDRagoras
