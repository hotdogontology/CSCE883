# Presentation notes

Title slide plus 14 numbered content slides (15 PDF pages); planned delivery: 10 minutes. Opening sequence: OpenAI releases, Lean and formalization, research question.

## Title slide: 10 seconds

Introduce the title and authors, then advance to the OpenAI context.

## Slide 1: 35 seconds

Introduce the public interest in OpenAI proof releases and the difficulty of reviewing their English and Lean artifacts. Attribute the reported discrepancies to the Navier--Stokes critique; this alone does not establish that the English theorem is false.

## Slide 2: 70 seconds

Define Lean, formalization, and kernel checking. Connect Pollack, FaithformBench, and Buzzard to the need to inspect semantic correspondence. The Navier--Stokes example on slide 1 supplies the motivating case; kernel implementation defects are a separate trust question.

## Slide 3: 35 seconds

Use two valid routes to explain why proving the same theorem is insufficient.

## Slide 4: 45 seconds

Explain why reverse-direction translation supervision is useful even without binary labels.

## Slide 5: 40 seconds

State the scope of each row. Avoid an across-protocol model leaderboard.

## Slide 6: 50 seconds

Walk through the four pairings and the witness-versus-IVT example. Qualify the small synthetic diagnostic.

## Slide 7: 45 seconds

Follow the arrows. The original English cannot leak into stage-one inference.

## Slide 8: 40 seconds

Describe fresh adapters and unchanged original judge; the corpora differ in size and evaluation.

## Slide 9: 30 seconds

Describe the acceptance counts. Independent correspondence labels would allow us to measure accuracy.

## Slide 10: 50 seconds

Read the matrix: all scored mismatches caught, but 17 faithful-assumed pairs rejected. Mention eight exclusions.

## Slide 11: 45 seconds

Explain how a correct flag can arise for the wrong reason after incomplete translation.

## Slide 12: 35 seconds

Explain why unequal coverage and compilation failures leave the relative benefit of controlled intermediaries unresolved.

## Slide 13: 40 seconds

Distinguish compute limitations from the central lack of independently adjudicated labels.

## Slide 14: 30 seconds

Close with the need for interpretable evidence and public human-reviewed pairs.
