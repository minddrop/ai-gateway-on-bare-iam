# IAM-native LLM gateway: Release notes

<!--
Answers: what changed for users and callers, newest first.
Reader: anyone who must act on a change. Call out breaking changes, model retirements, default model changes and new limits.
Owns: the release history, release versioning, notice periods. Refers to: launch gate evidence (02 §11.2), setting values (04).
Detail: a gateway release = configuration version + IaC version + spend guard version + client package version. A model added or retired is a release even if no code changed. Every release gets a row in §2 and an entry in §4, written from the block template in §3.
Status: stub written during design; nothing is released yet.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last reviewed: [fill: YYYY-MM-DD], for release [fill: version]

## 1. Release policy

- **Versioning:** [fill: calendar versioning, for example 2026.11.1, or semantic versioning]
- **Where users are told:** [fill: channel, email list]
- **Notice for breaking changes, model retirements and default model changes:** [fill: number of weeks]

## 2. Summary

| Version | Date | Client package | Highlights | Action needed by users |
|---|---|---|---|---|
| EXAMPLE: 2027.03.0 | 2027-03-01 | 1.0.0 | First pilot release | Run `llm login` once; Intune sets up Claude Code and Codex CLI |

## 3. Entry template

Copy this block into §4 for each release, newest first. Keep every heading; write "None" under a heading that has nothing to report.

```markdown
### <version> — <YYYY-MM-DD>
Config: <commit> · IaC: <commit> · Spend guard: <version> · Client package: <version>
Launch gates: <all passed on staging on YYYY-MM-DD; evidence in 02 §11.2>

#### Models
- Added: <model IDs, or "None">
- Retired: <IDs, and the replacement, or "None">
- Default model changes: <managed setting and new ID, or "None">

#### Changes
- <change, from the user's point of view>

#### Breaking changes and action needed
- <what breaks, who must act, and by when, or "None">

#### Fixed
- <fix, or "None">
```

## 4. Releases

### EXAMPLE: 2027.03.0 — 2027-03-01
Config: `a1b2c3d` · IaC: `d4e5f6a` · Spend guard: 1.0.0 · Client package: 1.0.0
Launch gates: all passed on staging on 2027-02-22; evidence in 02 §11.2

#### Models
- Added: the Claude Opus 5.5 and Claude Haiku 5.5 `jp.` profiles
- Retired: None
- Default model changes: None

#### Changes
- First pilot release, for the pilot teams in the Tokyo offices.

#### Breaking changes and action needed
- None. Run `llm login` once a day; Intune sets up Claude Code and Codex CLI.

#### Fixed
- None
