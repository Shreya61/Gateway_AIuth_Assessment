# Design Decisions

1. Use a DAG-style orchestrator so each agent has a narrow responsibility.
2. Keep deterministic offline mode to avoid spending limited free API tokens on smoke tests.
3. Route generation and extraction through separate LLM accessors for future mixed-model control.
4. Store callbacks outside the prompt context so chapter insertion can trigger repair.
5. Use Pydantic schemas on structured agent outputs rather than regex parsing.
6. Make references broad in offline mode to avoid fabricated citations.
7. Rebuild glossary after memory repair so it reflects inserted or regenerated chapters.
8. Generate DOCX directly with `python-docx` for predictable local assembly.
9. Add ReportLab PDF fallback because LibreOffice is not guaranteed in assessment sandboxes.
10. Keep prompt logs explicit and append-only because hidden prompts are a rejection gate.
