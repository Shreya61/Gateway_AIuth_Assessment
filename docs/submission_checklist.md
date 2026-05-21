# Submission Checklist

## Ready in Code

- Test A eval command exists and passes offline.
- Test B eval command exists and passes offline.
- Test C eval command exists and passes offline.
- Test D eval command exists and passes offline.
- UI accepts topic, reader profile, length target, genre, tone, chapter count, and named characters.
- Sample output filenames are distinct per test case.
- DOCX and PDF are generated.
- Prompt, trace, memory, and cost logs are emitted.

## Still Required Before Emailing

- Run one final live or offline package generation for A, B, C, and D and save distinct output filenames.
- Export the prompts dossier as standalone PDF.
- Zip sample books and trace bundles.
- Record the 5-8 minute demo video without hiding state.
- Make a clean commit history or at least a clean final commit.
- Confirm `.env` is not committed.

## Known Risk

The offline evals prove orchestration behavior without spending API tokens. For final book-quality evaluation, run live generation with the free API at least once per test case if quota allows. Full 2,500-word chapters for Test A may exceed free-tier comfort; document the cost strategy if using shorter smoke outputs.
