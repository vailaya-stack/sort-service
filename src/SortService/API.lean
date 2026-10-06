import Mathlib.Tactic
import Contracts.SortService

/-! The sort service: its implementation, and the proof that it meets its contract in
`Contracts.SortService`. -/
namespace SortService

open Contracts.SortService

def SortServiceAPI : SortServiceStructure Id where
  sortList l := l.mergeSort

instance : SortServiceContract SortServiceAPI where
  isSorted l := by grind [SortServiceAPI, List.sortedLE_mergeSort]
  isPerm l := by
    ensures_intro [SortServiceAPI]
    exact List.isPerm_iff.2 (List.mergeSort_perm l _)

end SortService
