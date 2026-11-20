# D-8: Enforce budgets with a serverless spend guard and one deny policy

| Field | Value |
|---|---|
| Decision ID | D-8 |
| Status | Proposed |
| Date | 2026-11-20 |
| Owner | TBD (Product owner, 2026-12-18) (01 Q-1); Platform engineering, with FinOps |
| Decided by | Platform lead and FinOps (pending approval of 02) |
| Requirements baseline | REQ-IGW 0.1 |
| Design version | SPEC-IGW 0.1 |
| Supersedes | — |

## 1. Context

LiteLLM refused a call before it reached the model when a budget was used up. Without a proxy, a budget can only be enforced after spend is seen, by denying further calls in IAM. AWS Budgets can apply an IAM policy or an SCP when a threshold is crossed, but its data lags by hours, and it cannot attach policies to the roles that IAM Identity Center manages, which are the roles people use (D-2). CUR 2.0 has the cost per principal, also with a lag. CloudTrail records every model call within minutes, and for streaming calls a stream-completion event with the caller and the token counts ([Bedrock CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html)). We must choose how budgets, per-person caps and runaway stops are enforced.

## 2. Decision drivers

| Driver | Source |
|---|---|
| Team budgets enforced, with a stated overshoot | 01 CST-002, CST-009 |
| Per-person caps across teams and tools | 01 CST-013, TEN-005 |
| A runaway caller is stopped | 01 CST-012 |
| Leavers' sessions end promptly | 01 IAM-006 |
| No content handled by anything of ours | 01 RES-005 |
| A failure of ours must not stop model calls | 01 AVL-007 |
| Little to run | 01 CON-2 |

## 3. Options considered

| Option | Drivers not met | Cost and effort | Risks | Outcome |
|---|---|---|---|---|
| 1. Spend guard: EventBridge (CloudTrail events) to SQS to Lambda, counters in DynamoDB, reconciled with CUR; denials through one customer managed policy `llm-guard-deny` attached to every LLM role; AWS Budgets with actions for workload roles and enrolled accounts | CST-002 only within the enforcement delay | Five small functions and a table; tests in V-13 and V-14 | Non-streaming calls have no per-call tokens (R-1); new AWS behaviour (R-30); policy size (R-15) | Chosen |
| 2. AWS Budgets only, with budget actions | CST-002 for people (actions cannot target Identity Center roles); CST-012, CST-013; IAM-006 | Configuration only | Overshoot of several hours of spend | Rejected for people; used for workload roles and enrolled accounts |
| 3. An AWS account per team, each with AWS Budgets actions that apply an SCP | CST-013 (per person); CST-012 | Hundreds of accounts, quotas and client configurations | Account sprawl; a lag of hours | Rejected; used only for large workloads (D-18) |
| 4. Bedrock model invocation logging as the metering source | RES-005, PRV-001 unless a metadata-only mode exists | Configuration and a log consumer | Logs content for every caller in the account if misconfigured | Rejected: whether it can log metadata only is not documented |
| 5. A proxy that counts before the call | D-1 | See D-1 | See D-1 | Rejected (D-1) |

How a denial is applied was also compared: resource tags are not available, because there are no application inference profiles (D-5); removing an IAM Identity Center assignment takes a SCIM cycle and fights CI; an SCP affects a whole account. One managed deny policy, keyed on role name patterns for teams and on `aws:userid` for people, acts within seconds and leaves an audit trail of versions.

## 4. Decision

We build the spend guard in option 1. It meters from CloudTrail events within minutes for streaming calls, corrects its estimates from CUR 2.0 several times a day, notifies at 80 % and 100 %, and denies a team, a person or a runaway caller by publishing a new version of `llm-guard-deny`. If it fails, the policy keeps its last version and calls continue. AWS Budgets with actions covers workload roles and enrolled accounts, where AWS can act on its own.

What it changes in the set:

| Document | Section | Change |
|---|---|---|
| 02 Architecture and design | §2.3.5, §5, §5.2 | Spend guard design |
| 04 Configuration reference | §4.4 | Budgets, caps, thresholds, delays |
| 07 Operations runbook | §3, §6 | Alerts and procedures for the spend guard |

## 5. Consequences

| Kind | Consequence | Tracked in |
|---|---|---|
| Benefit | Per-person caps and runaway stops, which AWS Budgets cannot give | 01 CST-012, CST-013 |
| Benefit | Leavers' sessions are ended by the same mechanism | 01 IAM-006 |
| Cost | Budgets can overshoot by the enforcement delay | R-1; 01 CST-009 |
| Cost | Code of ours that must be tested and maintained | R-13 |
| Cost | Estimates for cached calls are off until CUR arrives | R-22 |
| Follow-up | Measure delivery, delay and gaps before launch | V-13, V-14 |

## 6. Verification and review

- **Verified by:** V-4, V-13, V-14, T-022, T-023, T-026, T-072
- **Revisit when:** Bedrock adds quotas or budgets per principal or per project; or AWS Budgets can act on IAM Identity Center roles with a short lag

## 7. Change log

| Date | Author | Change | Status after |
|---|---|---|---|
| 2026-11-20 | Claude (AI assistant), for platform engineering | Proposed | Proposed |
