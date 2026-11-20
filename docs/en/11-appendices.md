# IAM-native LLM gateway: Appendices

> Owner: TBD (Product owner, 2026-12-18) (01 Q-1) · Last reviewed: 2026-11-20, for design version SPEC-IGW 0.1 (nothing is released yet)

## A. Glossary

| Term | Meaning |
|---|---|
| Access portal session | The IAM Identity Center session a person gets by signing in through Entra; it lasts 8 hours and lets the AWS CLI and SDKs get new role credentials without signing in again |
| Access inventory | The daily list of every principal that can call a model, with owner, team, tier, credential lifetime, certificate expiry, last use and spend (OBS-010) |
| Application inference profile | A Bedrock profile an account creates, usually to tag usage; not used in this design (D-5) |
| `bedrock-mantle` | Bedrock's endpoint for OpenAI-compatible APIs (Responses, Chat Completions), offered in Tokyo but not in Osaka |
| `bedrock-runtime` | Bedrock's main inference endpoint: InvokeModel, Converse, and the Messages, Chat Completions and Responses APIs |
| Chargeback / showback | Charging a team's budget for usage / only reporting it |
| CUR 2.0 | The AWS Cost and Usage Report data export; with IAM principal data, each Bedrock line names the role session that made the call |
| Enrolled account | An AWS account outside `llm-prod` whose own roles may call Bedrock, listed in the SCP |
| Enforcement delay | The time from a call that crosses a limit until the spend guard's denial takes effect (CST-009) |
| IAM Identity Center | The AWS service that federates people from Entra ID and gives them role credentials for AWS accounts |
| IAM Roles Anywhere | The AWS service that gives workloads outside AWS role credentials in exchange for an X.509 certificate |
| `jp.` profile | A Bedrock geographic cross-Region inference profile that routes only between Tokyo and Osaka |
| Launch gate | A test that must pass before launch, after every change to the setting it verifies, and every quarter [CMP §2.10] |
| `llm` helper | Our command-line tool for signing in, choosing a team and Region, showing usage and making short-term keys |
| `llm-guard-deny` | The managed IAM policy in which the spend guard lists suspended teams, people and callers |
| Long-term / short-term Bedrock API key | A key on an IAM user, valid until its expiry / a pre-signed token made from a session, valid until that session ends; only short-term keys are allowed (D-3) |
| Permission set | An IAM Identity Center definition of a role and its policies; one per team here (D-2) |
| Principal | The IAM identity that makes a call: a role session (person or workload), a role, or a user |
| Route A / Route B | Private path over Direct Connect and VPC endpoints / the public regional endpoints over the internet [CMP §2.6] |
| RTO / RPO | Recovery time / point objective |
| Runaway stop | A short suspension of a principal whose token use in 5 minutes is above a threshold (CST-012) |
| SCIM | The protocol Entra uses to provision users and groups to IAM Identity Center |
| SCP | Service control policy: an AWS Organizations policy that limits what any principal in an account can do |
| Spend guard | Our serverless component that meters spend from CloudTrail and CUR and enforces budgets through `llm-guard-deny` (D-8) |
| Team | A group that is charged, mapped from an Entra group `llm-team-<team>` to a permission set `LLM-Team-<team>` |
| Tier | A list of catalog models a team may call (`standard`, `premium`) |

## B. Related documents and links

- Comparison and design analysis: [../../../llm-gateway-comparison/README.md](../../../llm-gateway-comparison/README.md)
- The LiteLLM design (`[LGW]`): [../../../ai-gateway-on-aws/README.md](../../../ai-gateway-on-aws/README.md)
- Documentation template: [../../../llm-gateway-docs-template/README.md](../../../llm-gateway-docs-template/README.md)
- Source code and IaC: TBD (Platform engineering, 2027-01-29) (02 R-24)
- Dashboards: TBD (Platform engineering, 2027-01-29)
- Issue tracker: TBD (Product owner, 2027-01-29) (01 Q-20)
- Internal AI use policy: TBD (Legal / privacy, 2026-12-18) (01 Q-18)
- AWS documentation this design relies on:
  - [Amazon Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)
  - [Bedrock inference endpoints](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html) and [APIs](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html)
  - [Bedrock Responses API](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-responses-api.html)
  - [Bedrock and CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html)
  - [IAM principal cost allocation](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/iam-principal-cost-allocation.html)
  - [IAM Identity Center across multiple Regions](https://docs.aws.amazon.com/singlesignon/latest/userguide/multi-region-iam-identity-center.html)
  - [EventBridge and CloudTrail management events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-service-event-cloudtrail-management.html)
  - [Bedrock Guardrails languages](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-supported-languages.html) and [guardrail profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-cross-region-support.html)
  - [Bedrock policies in AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_bedrock.html)
  - [Codex CLI with Amazon Bedrock](https://help.openai.com/en/articles/20001253-configure-codex-with-amazon-bedrock)

## C. Contacts

| Role | Contact person | Channel | Use for |
|---|---|---|---|
| Product owner | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Product questions, the model catalog |
| Platform engineering | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Integration help, platform changes |
| On-call | TBD (Product owner, 2026-12-18) (01 Q-6) | TBD (Product owner, 2026-12-18) | Production incidents |
| Security / SOC | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Security concerns, the guardrail decision, incidents involving prompts |
| Legal / privacy | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Residency and content-logging approvals, per-person data |
| FinOps | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Budgets and chargeback |
| Network | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Egress IPs, secure web gateway, TLS inspection, Route A |
| Identity | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Entra ID, Okta, Conditional Access, SCIM to IAM Identity Center |
| Endpoint / Intune | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | Client package |
| Cloud platform (landing zone) | TBD (Product owner, 2026-12-18) (01 Q-1) | TBD (Product owner, 2026-12-18) | AWS Organizations, SCPs, IAM Identity Center, CUR |
| Help desk | TBD (Product owner, 2027-01-29) (01 Q-20) | TBD (Product owner, 2027-01-29) | First-line user support |
| AWS Support | TBD (Product owner, 2027-01-29) (01 Q-20) | TBD (Product owner, 2027-01-29) | AWS service problems |

## D. Documentation checklist (tick before marking the set Approved)

- [ ] The check in the README's "Checking a document", run over `docs/`, prints nothing: no markers, examples, instruction comments or blank cells
- [ ] Every remaining TBD is also tracked in 01 §9 or 02 §14
- [ ] Text that came pre-filled (no marker) checked against the system as built
- [ ] Setup (03) tested by someone new, date recorded
- [ ] Every alert in 07 §3 has an incident entry in 07 §6, with every field filled
- [ ] Every security-critical setting in 04 §4.2 has a passing launch gate
- [ ] Every Must requirement appears in the traceability matrix (02 §11.3)
- [ ] Every section from 02 §2 to §10 has a Satisfies line
- [ ] Every decision in 02 §13 that needs an ADR links one in `docs/en/adr/`, and the status in the row matches the status in the ADR
- [ ] Each fact appears only in its home, as listed in the README's "Where each fact lives"
- [ ] Links checked
- [ ] Owner and next review date set in 00 Document control; owner and last-reviewed date set in the status line of 03–11
- [ ] Japanese translation updated, if kept
