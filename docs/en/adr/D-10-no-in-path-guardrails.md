# D-10: Run no guardrail in the request path by default

| Field | Value |
|---|---|
| Decision ID | D-10 |
| Status | Proposed |
| Date | 2026-11-20 |
| Owner | TBD (Product owner, 2026-12-18) (01 Q-1); Security / SOC |
| Decided by | Security / SOC and platform lead (pending 01 Q-13) |
| Requirements baseline | REQ-IGW 0.1 |
| Design version | SPEC-IGW 0.1 |
| Supersedes | — (deviates from [LGW 02 D-9] and [CMP §4.8]) |

## 1. Context

The LiteLLM design screens every prompt in the VPC for personal information and prompt attacks, in Japanese and English, because Bedrock Guardrails cannot do it in Japan [LGW 02 D-9]. That is still true: Japanese is supported in the Standard tier, which uses the `apac.guardrail.v1:0` profile whose destinations from Tokyo include Seoul, Mumbai, Singapore and Sydney; the Classic tier stays in the Region but supports English, French and Spanish only ([languages](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported-languages.html), [guardrail profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region-support.html)). Without a proxy (D-1), nothing of ours sees the prompt. AWS Organizations can now enforce a guardrail on every inference call in chosen accounts through Bedrock policies ([Bedrock policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_bedrock.html)).

## 2. Decision drivers

| Driver | Source |
|---|---|
| Guardrail processing, like inference, stays in Japan | 01 RES-001; [CMP §2.5] |
| Personal information masked and prompt attacks detected, in Japanese and English | 01 SEC-008 |
| No proxy in the request path | 01 CON-2; D-1 |
| No content handled by anything of ours | 01 RES-005 |

## 3. Options considered

| Option | Drivers not met | Cost and effort | Risks | Outcome |
|---|---|---|---|---|
| 1. No guardrail in the path by default; Security may enforce a Classic-tier Bedrock guardrail in Tokyo, through a Bedrock policy, on selected OUs (for example workload accounts that handle customer data), for what the Classic tier supports | SEC-008 for Japanese | Nothing by default; per-OU guardrails and their per-text-unit cost if chosen | Personal data and injected instructions reach models unscreened (R-5) | Chosen, subject to Security's acceptance (01 Q-13) |
| 2. Bedrock Guardrails Standard tier, enforced through a Bedrock policy | RES-001: prompts are processed outside Japan | Configuration | — | Rejected |
| 3. A guarded path: a proxy in the VPC running Presidio and a Japanese classifier, as in `[LGW]` | D-1; RES-005 | A proxy to run, scale and patch | Becomes the gateway again | Rejected for everyone; revisit for workloads if Security requires it |
| 4. Guardrails inside each workload (for example a library such as Presidio before the call) | Not enforced centrally | Each workload owner's effort | Uneven coverage | Recommended in the enrolment checklist for workloads that handle customer data |

## 4. Decision

No guardrail runs in the request path by default, because no option keeps Japanese screening in Japan without a proxy. Security decides in 01 Q-13 whether to accept that, and whether to enforce a Classic-tier guardrail in Tokyo on selected OUs. Workloads that handle customer data are asked to screen their own inputs. SEC-008 and SEC-009 are Deferred, not Withdrawn, so the gap stays visible.

What it changes in the set:

| Document | Section | Change |
|---|---|---|
| 01 Requirements | NG-11, SEC-008, SEC-009 | Deferred, with the trigger to revisit |
| 02 Architecture and design | §8, §8.1 | No guardrail control; threat row |
| 05 User guide | §2 | What is and is not screened |

## 5. Consequences

| Kind | Consequence | Tracked in |
|---|---|---|
| Benefit | No guardrail cost or latency on large coding-agent contexts | 02 §12 |
| Cost | Personal data and prompt attacks are not screened before the model | R-5 |
| Cost | If the Classic-tier option is chosen, its sensitive-information support for Japanese must be tested, because AWS's pages disagree | R-5 |
| Follow-up | Security's decision | 01 Q-13 |

## 6. Verification and review

- **Verified by:** n/a until Security decides; if the Classic-tier option is chosen, a test like [LGW 02 T-045] with the Japanese and English test sets
- **Revisit when:** Bedrock Guardrails offers a guardrail profile that stays in Japan, or Japanese in the Classic tier; or Security requires guardrails for a class of data

## 7. Change log

| Date | Author | Change | Status after |
|---|---|---|---|
| 2026-11-20 | Claude (AI assistant), for platform engineering | Proposed | Proposed |
