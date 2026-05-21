# Evals Report

## Rubric

- Structural completeness: required front matter, body, and back matter are present.
- Tonality fidelity: selected tone appears in chapter and non-chapter surfaces.
- AI-tell detection: banned phrases are absent after editor/humanizer.
- Fact coverage: unsupported claims are flagged or softened.
- Callback recall: callbacks used in chapters are present in the callback index.
- Deliverables: DOCX, PDF, trace, prompt log, and cost ledger are emitted.

## MVP Run

Command:

```powershell
$env:AIUTHOR_OFFLINE="1"
python -m app.main --topic "Personal Finance" --tone Conversational --chapters 3
```

Expected scores:

- Structural completeness: pass for MVP sections.
- Tonality fidelity: partial, heuristic until LLM-as-judge is enabled.
- AI-tell detection: pass for configured banned phrase list.
- Fact coverage: partial, offline mode does not call external sources.
- Callback recall: pass, rebuilt by Memory Keeper.
- Deliverables: pass when dependencies are installed.

## Test D Run

Command:

```powershell
python -m app.evals.test_d_insert_eval
```

Latest offline result:

- Started with 10 chapters: pass
- Ends with 11 chapters: pass
- Chapter numbers repaired: pass
- Outline numbers repaired: pass
- Inserted chapter lands at Chapter 5: pass
- Callback index rebuilt: pass
- Glossary rebuilt: pass
- DOCX generated from repaired state: pass
- Visible TOC uses repaired chapter list: pass

## Test A Run

Command:

```powershell
python -m app.evals.test_a_personal_finance_eval
```

Latest offline result:

- Ten chapters: pass
- Conversational tone preserved: pass
- Beginner reader profile preserved: pass
- Callback index built: pass
- Glossary generated: pass
- DOCX/PDF generated: pass
- No failure artifacts: pass

## Test B Run

Command:

```powershell
python -m app.evals.test_b_novella_eval
```

Latest offline result:

- Five chapters: pass
- Storyteller tone preserved in brief/state: pass
- Novella genre preserved in brief/state: pass
- Mira and Jonah appear in every chapter: pass
- Mira and Jonah appear in every outline summary: pass
- Callback index built: pass
- DOCX generated: pass
- No nonfiction recovery bleed: pass

## Test C Run

Command:

```powershell
python -m app.evals.test_c_tone_regeneration_eval
```

Latest offline result:

- Test A outline has 10 chapters: pass
- Academic, Motivational, and Witty variants created: pass
- All variants keep 10 chapters: pass
- Chapter 3 exists in every variant: pass
- Variant tone recorded in state: pass
- Glossary rebuilt each time: pass
- DOCX generated each time: pass

## Failure Analysis

The largest remaining gap is full RAG grounding for nonfiction claims. The code has clean tool boundaries for retrieval, but the current offline mode intentionally avoids web/vector calls to conserve free API usage. For the final submission, run live generation once per required test case and attach the generated logs as the trace bundle.
