# Prompts Dossier

## Planner
Purpose: produce a publishable outline with chapter progression and callback candidates.
Inputs: user brief.
Outputs: `book_title`, `chapters[]`.
Failure modes: generic titles, invalid JSON, thin callbacks.
Why this prompt: forces sequencing, callback opportunities, and bans generic book phrasing.

## Researcher
Purpose: create grounded research notes and the contract for RAG/web fact tools.
Inputs: user brief, outline.
Outputs: `research_notes[]`.
Failure modes: fabricated citations, overconfident claims.
Why this prompt/contract: separates claims from prose before writing.

## Writer
Purpose: draft chapters with hooks, sections, callbacks, and tone.
Inputs: chapter plan, tone profile, callback memory.
Outputs: chapter JSON with content and callbacks used.
Failure modes: invalid JSON, too-short chapters, generic AI phrasing.
Why this prompt: makes tonality and memory explicit instead of relying on one broad instruction.

## Fact-Checker
Purpose: flag unsupported claims and soften unverifiable certainty.
Inputs: latest chapter.
Outputs: corrected content, flagged claims, softened claims.
Failure modes: inventing sources, excessive rewriting.
Why this prompt: uses abstention and no-fabricated-source rules.

## Humanizer
Purpose: remove robotic patterns while preserving meaning and tone.
Inputs: fact-checked chapter.
Outputs: humanized content.
Failure modes: changing claims, adding sentiment without substance.
Rules: remove “it's important to note,” “delve into,” “in today's fast-paced world,” “landscape of,” mechanical triads, and symmetric “not only...but also”; vary sentence length; use reader address when tone supports it; use domain metaphors; preserve callbacks.

## Editor
Purpose: deterministic cleanup pass for known AI tells.
Inputs: all chapters.
Outputs: edited chapters.
Failure modes: over-removing useful transition words.
Why this prompt/contract: low-cost guardrail after LLM generation.

## Memory Keeper
Purpose: rebuild fact registry, concept bible, callback index, tonality fingerprint, and decision log.
Inputs: chapters, callbacks, brief.
Outputs: memory stores and memory I/O log.
Failure modes: stale callbacks after chapter insertion.
Why this prompt/contract: downstream repair is based on memory stores, not the context window.

## Front/Back Matter
Purpose: generate dedication, epigraph, foreword, preface, acknowledgments, introduction, afterword, about-author, and back-cover copy in the selected tone.
Inputs: brief, outline, callback memory.
Outputs: front/back matter JSON.
Failure modes: tone only affecting chapters, invented author credentials.
Why this prompt: explicitly cascades tonality across every surface.

## References
Purpose: produce hallucination-safe broad reference categories.
Inputs: full book content.
Outputs: topical reference list.
Failure modes: fabricated papers, authors, journals.
Why this prompt: no fake bibliographic specificity in offline MVP.

## Glossary
Purpose: extract in-book terms and define them in the selected voice.
Inputs: full book content.
Outputs: glossary terms.
Failure modes: terms not appearing in book, dictionary boilerplate.
Why this prompt: glossary is derived after memory repair and editing.

## Assembler
Purpose: produce publication-structured DOCX/PDF and run ledger.
Inputs: final state.
Outputs: `generated_book.docx`, `generated_book.pdf`, `run_cost_summary.json`.
Failure modes: missing PDF converter, stale TOC list.
Why this contract: keeps assembly deterministic and cheap.
