# AIuthor

AIuthor is a quota-aware MVP for the Gateway Digital AI Engineer assessment. It uses a multi-agent book pipeline with explicit planning, research scaffolding, writing, fact-checking, humanizing, editing, memory keeping, glossary/reference generation, and assembly into DOCX plus PDF.

## Quick Start

```powershell
pip install -r requirements.txt
$env:AIUTHOR_OFFLINE="1"
python -m app.main --topic "Personal Finance" --tone Conversational --chapters 3
```

For a real free-model run, set `GROQ_API_KEY` in `.env` and remove `AIUTHOR_OFFLINE=1`. Offline mode is deterministic and intended for smoke tests without spending tokens.

Normal runs keep terminal output quiet. Set `AIUTHOR_VERBOSE=1` only when you want raw prompts, model responses, and converter diagnostics for debugging.

Streamlit UI:

```powershell
streamlit run streamlit_app.py
```

## Outputs

- `outputs/generated_book.docx`
- `outputs/generated_book.pdf`
- `logs/prompt_logs.jsonl`
- `logs/run_cost_summary.json`
- `traces/agent_trace.jsonl`

## Assessment Smoke Tests

```powershell
python -m app.evals.run_all
```

Or run individual cases:

```powershell
python -m app.evals.test_a_personal_finance_eval
python -m app.evals.test_b_novella_eval
python -m app.evals.test_c_tone_regeneration_eval
python -m app.evals.test_d_insert_eval
python -m app.evals.smoke_eval
```

`test_a_personal_finance_eval` verifies a 10-chapter beginner personal finance book in Conversational tone.

`test_b_novella_eval` verifies a 5-chapter Storyteller novella with Mira and Jonah present in every chapter and in the outline continuity.

`test_c_tone_regeneration_eval` verifies regenerating Chapter 3 from the Test A outline in Academic, Motivational, and Witty tones.

`test_d_insert_eval` generates the Test A-style 10-chapter book, inserts a new chapter between chapters 4 and 5, renumbers the outline/body to 11 chapters, rebuilds callbacks and glossary, and reassembles DOCX/PDF from the repaired state.

The evals write distinct sample files under `outputs/`, for example `test_a_personal_finance.docx`, `test_b_novella.docx`, `test_c_chapter_3_witty.docx`, and `test_d_after_insert.docx`.

## Assessment Docs

- [Architecture](docs/architecture.md)
- [Prompt dossier](docs/prompts_dossier.md)
- [Memory schema](docs/memory_schema.md)
- [Evals report](docs/evals_report.md)
- [Design decisions](docs/design_decisions.md)

## Current MVP Notes

The project is intentionally token-frugal: smoke tests use the deterministic LLM fallback, while live generation routes all agents through the configured Groq model. The RAG/research layer is currently a grounded scaffold with clean contracts; production web/vector retrieval is documented as the next extension point.
