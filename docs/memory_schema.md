# Memory Schema

## Fact Registry
```json
{
  "claim": "Emergency funds reduce short-term financial stress.",
  "chapter": 2,
  "status": "softened",
  "source_ids": [],
  "confidence": "medium"
}
```

## Concept Bible
```json
{
  "id": "chapter-1",
  "name": "Chapter 1 Turning Point",
  "introduced_in": 1,
  "notes": "The first practical habit and why it returns later."
}
```

## Callback Index
```json
{
  "chapter": 3,
  "callback": "small choices compound",
  "source": "Chapter 3 Turning Point"
}
```

## Tonality Fingerprint
```json
{
  "tone": "Witty",
  "writing_style": "sharp and playful",
  "sentence_rhythm": "punchy",
  "humor_level": 0.9,
  "reader_address": "direct"
}
```

## Decision Log
```json
{
  "decision": "Chapter memory rebuilt after generation",
  "reason": "Keeps callback index, concept bible, and downstream glossary assembly repairable."
}
```

Insertion repair: after inserting a chapter, rerun Memory Keeper, References, Glossary, and Assembler. The TOC is generated from the current chapter array, so numbering and glossary derive from repaired state.
