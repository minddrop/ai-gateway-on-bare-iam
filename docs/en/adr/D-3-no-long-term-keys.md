# D-3: Allow no long-term keys; manage access, not keys

| Field | Value |
|---|---|
| Decision ID | D-3 |
| Status | Proposed |
| Date | 2026-11-20 |
| Owner | TBD (Product owner, 2026-12-18) (01 Q-1); Security / SOC |
| Decided by | Platform lead and Security / SOC (pending approval of 02) |
| Requirements baseline | REQ-IGW 0.1 |
| Design version | SPEC-IGW 0.1 |
| Supersedes | — |

## 1. Context

Bedrock now has its own API keys. A long-term key is an IAM service-specific credential on an IAM user: it can be created, deactivated, given an expiry and deleted in the IAM console, which looks like the key lifecycle that LiteLLM's Admin UI gave [LGW 02 §4.5]. A short-term key is a pre-signed token made from an existing session, valid for at most 12 hours or the rest of that session, and it cannot be revoked by itself. AWS's documentation says long-term keys are for exploration only and short-term keys are for production ([Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)), and AWS added condition keys to govern both kinds ([announcement](https://aws.amazon.com/about-aws/whats-new/2025/09/aws-api-keys-conditions-govern-amazon-bedrock)). We must decide which keys exist and how their lifecycle is managed.

## 2. Decision drivers

| Driver | Source |
|---|---|
| AWS best practice: federation and temporary credentials for people, roles for workloads | 01 CON-7; [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) |
| No long-lived credential can call a model | 01 G-6, IAM-015 |
| Every model credential expires within 1 hour | 01 IAM-016 |
| Device and MFA re-checked regularly, not only at issue | 01 IAM-001, IAM-011 |
| Leavers lose access without a person remembering to delete a key | 01 IAM-006 |
| Tools that accept only a bearer key can still be used | 01 FUN-009; R-20 |
| A view of who can call which model, with expiry and last use | 01 OBS-010 |

## 3. Options considered

| Option | Drivers not met | Cost and effort | Risks | Outcome |
|---|---|---|---|---|
| 1. No long-term keys anywhere (SCP); people use permission set credentials and, where a tool needs a bearer key, a short-term key from their session; DC workloads use Roles Anywhere; the lifecycle managed is access (groups, roles, certificates), shown in an access inventory | — | SCP statements; `llm token`; an inventory export and dashboard | Tools that take only a pasted key need a new key every hour (R-20) | Chosen |
| 2. Long-term keys per person on IAM users, maximum 90 days through `iam:ServiceSpecificCredentialAgeDays`, with an IP condition, managed in the IAM console | CON-7 (IAM users for people; AWS calls long-term keys exploration-only); IAM-015; IAM-016; IAM-006 needs a job to find leavers' keys | An IAM user and key per person, 5,000 of them; reminders; rotation | A pasted key in dotfiles, chat and repositories works for up to 90 days from every allowlisted IP, with no device or MFA check | Rejected |
| 3. Long-term keys per workload | CON-7; IAM-015 | A key per workload; rotation by CI | Static secrets on servers | Rejected: Roles Anywhere gives 1-hour credentials from a certificate (D-4) |
| 4. A separate exploration sandbox account in which long-term keys of at most 30 days are allowed, with a small budget and synthetic data only | — for exploration; it would be outside the production controls | One account, an SCP exception, a policy for its use | People use it for real work with real code | Not now: 01 Q-26 |

## 4. Decision

No long-term key can call a model in any account: the SCP denies model calls by IAM users, the creation of Bedrock service-specific credentials, and calls with `LONG_TERM` bearer tokens. People and workloads get credentials that last at most 1 hour; a tool that needs a bearer key gets a short-term key made from the person's own session by `llm token`. The lifecycle that operators manage is access, not keys: group membership in Entra, permission sets and workload roles in Git, certificates from the private CA, suspensions in the spend guard, all shown in one access inventory (OBS-010, D-14).

What it changes in the set:

| Document | Section | Change |
|---|---|---|
| 01 Requirements | NG-9, IAM-015, IAM-016 | No long-term keys |
| 02 Architecture and design | §4.5, §4.7 | Credential lifecycle; SCP statements |
| 04 Configuration reference | §4.2 | The SCP text |
| 05 User guide | §4 | `llm token` for tools that need a bearer key |

## 5. Consequences

| Kind | Consequence | Tracked in |
|---|---|---|
| Benefit | A leaked credential works for at most 1 hour, and only from our network | 01 IAM-016, SEC-001 |
| Benefit | No key inventory to rotate, remind or clean up | 01 OBS-010 |
| Cost | Pasted short-term keys last at most the rest of the 1-hour session | R-20; 01 Q-27 |
| Cost | A short-term key cannot be revoked by itself; ending it means denying its session | 02 §4.5 |
| Follow-up | Decide whether an exploration sandbox is wanted | 01 Q-26 |

## 6. Verification and review

- **Verified by:** V-2, T-081, T-082, T-045
- **Revisit when:** AWS changes its guidance on long-term Bedrock API keys, or an exploration sandbox is approved (01 Q-26)

## 7. Change log

| Date | Author | Change | Status after |
|---|---|---|---|
| 2026-11-20 | Claude (AI assistant), for platform engineering | Proposed | Proposed |
