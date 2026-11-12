import Lean

/- Appended after imports when replaying an isolated ProofNet declaration.
   Emit resolved constants separately for the statement and proof term.
   Expand local helpers, stopping at imported library declarations. -/
namespace ProofOntology
open Lean Elab Command

def valueConstants (ci : ConstantInfo) : Array Name :=
  match ci with
  | .thmInfo info => info.value.getUsedConstants
  | .defnInfo info => info.value.getUsedConstants
  | .opaqueInfo info => info.value.getUsedConstants
  | _ => #[]

def dependencyJson (env : Environment) (names : Array Name) : Json := Id.run do
  let mut pending := names
  let mut seen : NameSet := {}
  let mut output : Array Json := #[]
  let mut fuel := 10000
  while !pending.isEmpty && fuel > 0 do
    fuel := fuel - 1
    let name := pending[pending.size - 1]!
    pending := pending.pop
    if seen.contains name then continue
    seen := seen.insert name
    let moduleName := match env.getModuleIdxFor? name with
      | some idx => (env.header.moduleNames[idx.toNat]!).toString
      | none => "LOCAL"
    output := output.push <| Json.mkObj [("name", toJson name.toString), ("module", toJson moduleName)]
    if moduleName == "LOCAL" then
      if let some ci := env.find? name then
        pending := pending ++ ci.type.getUsedConstants ++ valueConstants ci
  return Json.mkObj [("constants", Json.arr output), ("complete", toJson (pending.isEmpty))]

elab "#proof_dependencies " target:ident : command => do
  let env ← getEnv
  let ci ← getConstInfo target.getId
  let result := Json.mkObj [
    ("target", toJson target.getId.toString),
    ("statement", dependencyJson env ci.type.getUsedConstants),
    ("proof", dependencyJson env (valueConstants ci))]
  liftIO <| IO.println ("PROOF_DEPENDENCIES " ++ result.compress)
end ProofOntology
