# Pocket Lawyer — AI Personality Archive

This directory contains **versioned snapshots** of the AI's personality, behaviour, and prompt engineering decisions. Each version is a frozen snapshot — never edited after creation.

## Why?
When we train our own AI model, this archive gives us:
- **Full evolution history** of how the AI personality was shaped
- **Every decision and its reasoning** — what we tried, what we changed, and why
- **Training data annotations** — each version documents the exact tone, rules, and edge cases

## Versions

| Version | Date | Key Changes |
|:---|:---|:---|
| [v1.0](AI_PERSONALITY_v1.0.md) | Apr 2, 2026 | Initial baseline. 4 personality modes (chat, chat_doc, doc_analysis, analyze_case). Parallel streaming architecture. No-disclaimer rules. |

## Rules
- **Never edit** an existing version file. Always create a new version.
- **Always document** what changed and why in the new version's changelog section.
- Naming convention: `AI_PERSONALITY_v{MAJOR}.{MINOR}.md`
  - **Major bump** (v2.0): Fundamental personality shift, new mode added, architecture change
  - **Minor bump** (v1.1): Tone tweak, rule adjustment, edge case fix
