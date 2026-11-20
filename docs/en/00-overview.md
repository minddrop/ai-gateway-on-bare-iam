# IAM-native LLM gateway: Overview

## Document control

| Field | Value |
|---|---|
| System name | IAM-native LLM gateway |
| Model endpoints | No gateway hostname. Clients call the AWS regional endpoints `bedrock-runtime.ap-northeast-1.amazonaws.com` (Tokyo) and `bedrock-mantle.ap-northeast-1.api.aws` (Tokyo, OpenAI-compatible models only), and `bedrock-runtime.ap-northeast-3.amazonaws.com` (Osaka) after a failover (02 D-1, D-13) |
| Sign-in | The IAM Identity Center access portal for the organization (start URL in 04 §2.1), federated from Entra ID |
| Documentation owner | TBD (Product owner, 2026-12-18) (01 Q-1) |
| Technical owner | TBD (Platform engineering, 2026-12-18) (01 Q-1) |
| Status | Draft |
| Review cadence | Every quarter, before each model is onboarded, and after every change to a security-critical policy (04 §4.2) |
| Next review | TBD (Product owner, 2026-12-18) (01 Q-1) |
| Source code / IaC | TBD (Platform engineering, 2027-01-29): none exists yet; the system is in the design phase (02 R-24) |
| Source analysis | llm-gateway-comparison commit `46699eb` (2026-11-17); the LiteLLM design, ai-gateway-on-aws commit `87ba355` (2026-11-20) |

**Approvals**

| Role | Name | Date |
|---|---|---|
| Platform engineering lead | TBD (Platform engineering, 2026-12-18) (01 Q-1) | Not approved |
| Security | TBD (Security / SOC, 2026-12-18) (01 Q-1) | Not approved |
| Legal / privacy (residency, content logging) | TBD (Legal / privacy, 2026-12-18) (01 Q-1) | Not approved |
| FinOps (chargeback) | TBD (FinOps, 2026-12-18) (01 Q-1) | Not approved |

Version history: system releases are in 10 Release notes. The two baselines keep their own change logs (01 §11, 02 §15).

## 1. System overview

IAM-native LLM gateway gives engineers and internal workloads governed access to large language models processed in Japan, without a gateway server in the request path. People sign in through IAM Identity Center with Entra ID (Okta Verify MFA, Intune-compliant device) and get AWS credentials that last one hour; workloads in the on-premises DC get them from IAM Roles Anywhere with a certificate. Their tools then call Amazon Bedrock directly, and IAM policies and SCPs decide on every call which models, Regions and networks are allowed (02 D-1). AWS bills every call to the IAM principal that made it, which gives chargeback per person and per team, and a small serverless spend guard stops a team or a person at its budget (02 D-8). What it replaces is TBD (Product owner, 2026-12-18) (01 Q-2); it serves about 5,000 employees, about 300 concurrent users at peak [CMP A-9]. The system is in the design phase: nothing is built yet.

### 1.1 Scope

- **In scope:** model access on Bedrock in Tokyo and Osaka; identity, team mapping and credentials; budgets, runaway protection and chargeback data; request metadata in CloudTrail; access and spend dashboards
- **Out of scope this phase:** remote and home access; external model APIs that cannot prove in-Japan processing; response caching; model training and fine-tuning; long-term API keys; in-path guardrails for Japanese text; translation between API formats; endpoint families other than those in 01 FUN-001 to FUN-004; residency of identity data. Each one is listed with its reason in 01 §1.3.

### 1.2 Key capabilities

| Capability | What it does | Primary users | Requirement IDs |
|---|---|---|---|
| Model access | Bedrock's native, Anthropic Messages and OpenAI-compatible APIs for the approved, Japan-processed models | Engineers, workloads | FUN-001 to FUN-009, MDL-001 to MDL-011, MDL-101 to MDL-105 |
| Identity | Entra sign-in (MFA, compliant device) to IAM Identity Center every 8 hours; 1-hour credentials; certificates for DC workloads; no long-lived keys | Engineers, workloads | IAM-001 to IAM-016, TEN-001 to TEN-009 |
| Cost control | Per-team budgets and per-person caps enforced by the spend guard; runaway stop; AWS Budgets for workloads; chargeback from CUR 2.0 by IAM principal | Team leads, FinOps | CST-001 to CST-014 |
| Residency and privacy | Only `jp.` profiles and Tokyo In-Region models, enforced by SCP; no prompt content stored | Legal, security | RES-001 to RES-008, PRV-001 to PRV-005 |
| Access lifecycle | Access granted and removed through Entra groups; an inventory dashboard of who can call which model, credential expiry and last use | Platform, Security | OBS-010, IAM-006, TEN-004, TEN-007 |

### 1.3 Stakeholders

Contact details for each role are in 11 §C. Team names are 01 Q-1.

| Role | Team | Responsibility |
|---|---|---|
| Product owner | TBD (Product owner, 2026-12-18) | Priorities, model catalog, roadmap |
| Platform engineering | TBD (Product owner, 2026-12-18) | IAM policies, SCPs, spend guard, client package, operations |
| On-call | TBD (Product owner, 2026-12-18) | Production incidents |
| Security / SOC | TBD (Product owner, 2026-12-18) | SCPs and data perimeter, guardrail decision, audit review, incidents involving prompts |
| Legal / privacy | TBD (Product owner, 2026-12-18) | Residency and content-logging approvals; who may see per-person usage |
| FinOps | TBD (Product owner, 2026-12-18) | Budgets, chargeback from CUR 2.0 |
| Network | TBD (Product owner, 2026-12-18) | Egress IPs, secure web gateway rules for AWS endpoints, TLS-inspection exemption, the private path if adopted (02 D-6) |
| Identity | TBD (Product owner, 2026-12-18) | Entra app for IAM Identity Center, SCIM, Conditional Access, Okta MFA, team groups |
| Endpoint / Intune | TBD (Product owner, 2026-12-18) | Client package (`llm` helper, Claude Code and Codex CLI settings) |
| Cloud platform (landing zone) | TBD (Product owner, 2026-12-18) | AWS Organizations, SCP attachment, IAM Identity Center instance, CUR 2.0 export |

### 1.4 Service levels

The targets are defined in 01. This table names them by ID, so that the two documents cannot disagree.

| Commitment | Defined in |
|---|---|
| Availability | AVL-M01 |
| Gateway latency overhead | PRF-M01 (zero by design: there is no hop of ours in the request path) |
| Recovery from loss of the Tokyo region | AVL-M02 (RTO), AVL-M03 (RPO) |
| Support hours | OPS-006 |
| Upstream model availability | Bedrock's own; not covered by the gateway SLO unless AVL-M01 says so |

### 1.5 Assumptions and constraints

The full list, with owners and confirmation dates, is in 01 §3–4. The ones a newcomer must know:

- Users are on the corporate network; IAM policies deny model calls from anywhere but the office and DC egress IPs [CMP A-13, A-14].
- Unmanaged devices cannot use those egress IPs; launch gate V-11 tests it [CMP A-16].
- Only models processed in Japan are allowed: `jp.` cross-Region inference profiles and In-Region models in Tokyo. Availability changes, so it is re-checked before onboarding [CMP A-5, A-7].
- Prompt and response content is not stored by default [CMP A-10]. Bedrock model invocation logging stays off, and an SCP stops anyone turning it on.
- There is no API key for people or workloads to lose: every credential that can call a model expires within one hour (01 IAM-016).

### 1.6 Differences from the LiteLLM design

This system meets the same goals as `[LGW]` with fewer moving parts, and gives up some controls that only a proxy can give. The full comparison, requirement by requirement, is in ADR D-1 §5.

| Aspect | LiteLLM design `[LGW]` | This design |
|---|---|---|
| Request path | Client → WAF and ALB → LiteLLM on ECS → Bedrock | Client → Bedrock |
| What we run | ECS tasks, Aurora, ElastiCache, ALB, WAF, Network Firewall egress, guardrail service, sync job | A spend guard (EventBridge, Lambda, DynamoDB) and a usage API |
| Credential | Virtual key, up to 90 days | AWS credentials, 1 hour; device and MFA checked at least every 8 hours |
| Budgets | Real time, per key, user and team | Within minutes for streaming calls, within a day for the rest (CST-009) |
| Rate limits | TPM/RPM per key, user and team | Account quotas, and a stop for a runaway caller (NG-12, CST-012) |
| Guardrails | In-VPC PII masking and prompt-attack checks, Japanese | None in the path by default; an optional Bedrock guardrail without Japanese support (D-10) |
| API translation | Any client format to any model | Each model's own APIs on Bedrock (FUN-003) |
| Chargeback | LiteLLM spend shares applied to CUR, with a residual | CUR 2.0 directly, by IAM principal |
