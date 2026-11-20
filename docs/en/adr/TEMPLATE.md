# D-[fill: n]: [fill: the decision as a short imperative phrase, for example "Run guardrails in the VPC"]

<!--
Answers: why one significant design choice was made, what else was considered, and what it costs.
Reader: reviewers of 02; engineers who later want to change or reverse the choice.
Owns: the context, options, reasoning and consequences of one decision. Refers to: the one-row summary in 02 §13, requirement text (01), setting values (04), tests and gates (02 §11).
Detail: write an ADR when a decision does not fit in one row of 02 §13: three or more options, a deviation from [CMP], a security-critical setting (04 §4.2), or a choice that is expensive to reverse. Copy this file to docs/en/adr/D-<n>-<short-title>.md, using the same D-n as the row in 02 §13, and link the file from that row. Once a decision is Accepted, do not rewrite its reasoning: record a new decision that supersedes it, and update the status of both.
Fill it in using the writing conventions in ../../../README.md. Delete this comment when done.
-->

| Field | Value |
|---|---|
| Decision ID | [fill: D-n, the same as its row in 02 §13] |
| Status | [fill: Proposed / Accepted / Superseded by D-n] |
| Date | [fill: YYYY-MM-DD, when the status last changed] |
| Owner | [fill: name, team] |
| Decided by | [default: platform lead; also security for a security-critical setting] |
| Requirements baseline | [fill: REQ-GW version] |
| Design version | [fill: SPEC-GW version that first includes this decision] |
| Supersedes | [fill: D-n, or —] |

## 1. Context

[fill: two to five sentences: the problem, why a choice is needed now, and what happens if nothing is decided]

## 2. Decision drivers

<!-- What any option must satisfy. Refer to requirements, constraints and assumptions by ID; do not copy their text. -->

| Driver | Source |
|---|---|
| EXAMPLE: Prompts and completions are processed only in Japan | RES-001; [CMP §2.5] |

## 3. Options considered

<!-- One row per option, the chosen one first. Include the option that [CMP] recommends, and "do nothing" when it is a real option. Every option that is rejected names the driver it fails or the cost that rules it out. -->

| Option | Drivers not met | Cost and effort | Risks | Outcome |
|---|---|---|---|---|
| EXAMPLE: Guardrail runtime as an ECS service in the VPC | — | One more service to run, patch and scale; cost in 02 §12 | Detection quality for Japanese depends on the model we run | Chosen |

## 4. Decision

[fill: two to five sentences: what we will do, and the main reason it beats the next-best option]

What it changes in the set:

| Document | Section | Change |
|---|---|---|
| EXAMPLE: 02 Architecture and design | §2.2, §8 | Adds the guardrail service to the component table and the security controls |

## 5. Consequences

<!-- Kind is Benefit, Cost or Follow-up. A Cost that is a risk, and every Follow-up, is tracked in 02 §14 or 01 §9; write its ID. -->

| Kind | Consequence | Tracked in |
|---|---|---|
| EXAMPLE: Cost | We must evaluate and update Japanese detection rules ourselves | R-2 |

## 6. Verification and review

- **Verified by:** [fill: test or gate IDs from 02 §11, for example T-001, V-1]
- **Revisit when:** [fill: the event that would reopen this decision, for example "Bedrock Guardrails supports Japanese with a `jp.` profile"]

## 7. Change log

| Date | Author | Change | Status after |
|---|---|---|---|
| [fill: YYYY-MM-DD] | [fill: name] | Proposed | Proposed |
