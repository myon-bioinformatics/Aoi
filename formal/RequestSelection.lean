import Std

/-!
Snapshot model of research_loop/autonomous.py::next_request.
The ordered list contains registered seed jobs after feedback ordering. File
loading, TOML validation and digest construction precede this model; it does not
model concurrent writes or prove that the underlying research judgment is true.
-/

namespace Aoi

inductive JobStatus where
  | completed | bounded | blocked | error | retryable
  deriving DecidableEq, Repr

def terminal : JobStatus → Bool
  | .completed | .bounded | .blocked | .error => true
  | .retryable => false

structure SeedJob where
  seed : Nat
  stopped : Bool
  status : JobStatus
  deriving DecidableEq, Repr

def runnable (job : SeedJob) : Bool := !job.stopped && !terminal job.status

def nextRequest (ordered : List SeedJob) : Option SeedJob := ordered.find? runnable

/-- Selection cannot invent a seed absent from the registered ordered list. -/
theorem selected_registered (ordered : List SeedJob) (job : SeedJob)
    (selected : nextRequest ordered = some job) : job ∈ ordered := by
  exact List.mem_of_find?_eq_some selected

/-- Priority changes never bypass a stop or a terminal state. -/
theorem selected_runnable (ordered : List SeedJob) (job : SeedJob)
    (selected : nextRequest ordered = some job) :
    job.stopped = false ∧ terminal job.status = false := by
  have allowed := List.find?_some selected
  simpa [runnable] using allowed

/-- Every stopped job is excluded, regardless of its position. -/
theorem stopped_not_selected (ordered : List SeedJob) (job : SeedJob)
    (stopped : job.stopped = true) : nextRequest ordered ≠ some job := by
  intro selected
  have allowed := (selected_runnable ordered job selected).1
  simp [stopped] at allowed

/-- Completed, bounded, blocked and errored work is excluded. -/
theorem terminal_not_selected (ordered : List SeedJob) (job : SeedJob)
    (finished : terminal job.status = true) : nextRequest ordered ≠ some job := by
  intro selected
  have allowed := (selected_runnable ordered job selected).2
  simp [finished] at allowed

/-- Exhaustion is exactly the absence of a runnable registered job. -/
theorem exhausted_iff (ordered : List SeedJob) :
    nextRequest ordered = none ↔ ∀ job ∈ ordered, runnable job = false := by
  simp [nextRequest]

/-- Later candidates cannot displace the first runnable request. -/
theorem selected_prefix_stable (before after : List SeedJob) (job : SeedJob)
    (selected : nextRequest before = some job) :
    nextRequest (before ++ after) = some job := by
  exact List.IsPrefix.find?_eq_some (List.prefix_append before after) selected

end Aoi
