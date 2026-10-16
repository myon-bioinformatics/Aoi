# Loss distribution follow-up (exploratory, recorded before calculation)

Use the same frozen 2013–2025 final scores, all CL team-years, keeping 2020 and reporting its exclusion separately. No additional acquisition. No claim of causal attribution or venue adjustment.

Preserve frequency at every integer runs-allowed value and survival P(RA >= k) at every k from 1 through the dataset maximum, by team-year and home/away. The sum of survival differences must reconstruct away-minus-home mean RA. Keep zeros and all large scores; do not discard extreme games.

For one explicit, provisional definition of concentration use k=6, chosen now: body=E[min(RA,6)] and tail=E[max(RA−6,0)]. This counts only runs beyond six in the tail, not all runs in games with seven or more. Preserve the same decomposition for every possible integer cap so conclusions cannot depend silently on the chosen six. No optimal cutoff search. Use unweighted annual means; separately compare Chunichi and other CL teams. Opponent adjustment is not part of this follow-up.

Finite-data proposition T1: if a team-year has higher away mean RA than home, then more than half that difference comes from runs beyond six (tail difference > body difference). Evaluate original, contrapositive, converse, inverse with existing PythDRAgoraS, all 78 CL team-years, retaining Chunichi counterexamples. Strength always refers to the observed finite table, not a population law. A contrary row refutes the universal wording, not the whole research program. Existing engine's inference statistics are supplementary only; team-years share games and are not independent.

Command analysis exit 0 means data/computation contracts passed; proposition exit is separately the existing judgement (0 no objection, 1–6 objection/hold). Infrastructure codes use existing conventions: 64 invalid proposition, 65 invalid data, 66 missing input, 70 internal invariant failure, 74 output I/O error. Sequential harness records every child return code and stdout/stderr; expected nonzero is tested and preserved, never converted into a successful proposition.
