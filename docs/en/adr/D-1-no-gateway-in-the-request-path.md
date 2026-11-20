# D-1: Use AWS controls as the gateway, with no proxy in the request path

| Field | Value |
|---|---|
| Decision ID | D-1 |
| Status | Proposed |
| Date | 2026-11-20 |
| Owner | TBD (Product owner, 2026-12-18) (01 Q-1); Platform engineering |
| Decided by | Platform lead and Security / SOC (pending approval of 02) |
| Requirements baseline | REQ-IGW 0.1 |
| Design version | SPEC-IGW 0.1 |
| Supersedes | — (an alternative to the whole LiteLLM design `[LGW]`) |

## 1. Context

The LiteLLM design puts LiteLLM Proxy on ECS between every client and Bedrock [LGW 02 §1.1]. Writing it showed how much of the design exists to make the proxy safe: its master key, Admin UI sessions, password sign-in, team-admin rights, runtime configuration routes, a sync job to remove memberships it never removes, a WAF path allowlist, a key policy hook, twelve launch gates to re-run on every upgrade, and Aurora, ElastiCache, ALB, WAF and Network Firewall to run it [LGW 02 D-26 to D-33, R-47 to R-59]. Meanwhile AWS added cost allocation by IAM principal to CUR 2.0 (April 2026), short-term Bedrock API keys and condition keys to govern them (2025), Anthropic and OpenAI-compatible APIs on `bedrock-runtime`, Codex CLI's `amazon-bedrock` provider, and multi-Region IAM Identity Center (2026). The platform owner asked whether IAM and AWS's own tools can do the gateway's job instead (01 CON-2).

## 2. Decision drivers

| Driver | Source |
|---|---|
| Prompts and completions are processed only in Japan, enforced by policy | 01 RES-001, RES-002; [CMP §2.5] |
| No prompt content is stored by default | 01 PRV-001; [CMP A-10] |
| Every call is charged to a team the platform assigns | 01 G-1, CST-001 |
| Access needs Entra sign-in with MFA and a compliant device | 01 IAM-001; [CMP §2.1] |
| Budgets are enforced | 01 CST-002 |
| Claude Code and Codex CLI work with no setup beyond signing in | 01 FUN-001, FUN-002, FUN-009 |
| AWS security best practice, no long-term keys | 01 CON-7 |
| As little as possible for us to run, patch and re-test | 01 CON-2, G-7 |

## 3. Options considered

| Option | Drivers not met | Cost and effort | Risks | Outcome |
|---|---|---|---|---|
| A. No proxy: IAM Identity Center and Roles Anywhere for credentials, SCPs and IAM policies for authorization and residency, CUR 2.0 by principal for chargeback, a serverless spend guard for budgets | Budgets are enforced within minutes for streams and within a day for the rest, not before the call (CST-002 weaker); no in-path Japanese guardrails (SEC-008); no per-caller rate limits (NG-12); no API translation | A small serverless spend guard, a client helper, policies as code | Depends on AWS features that are new (R-2, R-30); clients call AWS endpoints, so on Route B other AWS accounts share the network path (R-12) | Chosen |
| B. LiteLLM Proxy on ECS `[LGW]` | — | ECS, Aurora, ElastiCache, ALB, WAF, Network Firewall share, a guardrail service, an Enterprise licence, upgrade gates | Many settings must stay right across upgrades [LGW 02 R-47 to R-59]; 90-day static keys | Rejected: meets every driver but the last, at a cost the owner wants to avoid |
| C. A thin proxy of our own (API Gateway or ECS) that checks IAM and forwards to Bedrock | — | A proxy we write and run: streaming for up to 10 minutes, every API style, retries | We own a security-critical component in the request path; the caller seen by Bedrock and CUR becomes the proxy's role, losing per-person attribution | Rejected: the cost of B with less function |
| D. Long-term Bedrock API keys per person or team, managed in the IAM console | CON-7: AWS recommends long-term keys only for exploration; people as IAM users | Low to build; key handling by hand | Long-lived secrets on laptops; no MFA or device check after creation; leavers handled by hand | Rejected (D-3) |

## 4. Decision

We build option A: there is no gateway server, and AWS's own controls are the gateway. It meets the residency, privacy, identity and chargeback drivers at least as well as LiteLLM, and better on credentials (1 hour instead of 90 days) and on attribution (CUR names the caller). It gives up real-time budgets, in-path guardrails, per-caller rate limits and API translation, which the requirements record as changed, deferred or out of scope (§5.1).

What it changes in the set:

| Document | Section | Change |
|---|---|---|
| 01 Requirements | §1.3, §6, §7 | NG-9 to NG-12 added; LiteLLM-only requirements withdrawn; budget, rate-limit and guardrail requirements changed or deferred |
| 02 Architecture and design | All | The design itself |
| 03 to 10 | All | No server to deploy, upgrade or fail over; policies, the spend guard and the client package instead |

## 5. Consequences

| Kind | Consequence | Tracked in |
|---|---|---|
| Benefit | No static key exists for a person or a workload; every model credential lasts at most 1 hour, and the device and MFA are re-checked at least every 8 hours | 01 IAM-015, IAM-016 |
| Benefit | Nothing of ours is in the request path or holds content: no added latency, no AZ or upgrade outages, and the content controls shrink to "invocation logging stays off" | 01 G-7, RES-005, PRV-001 |
| Benefit | CUR is both cost truth and allocation key; cancelled streams and client fields cannot cause a metering gap | D-9; 01 CST-005, CST-006 |
| Cost | Budgets are enforced after the fact, with a delay | R-1, R-13; 01 CST-009 |
| Cost | No per-caller rate limits; one caller can throttle others in the account | R-6 |
| Cost | No guardrails in the request path | R-5; D-10 |
| Cost | Clients must speak an API that Bedrock offers for the model; no translation | R-20 |
| Cost | Sign-in depends on Entra and IAM Identity Center being up, at least every 8 hours | R-10, R-35 |
| Follow-up | Verify the new AWS behaviours this rests on before launch | V-13, V-15, V-16 |
| Follow-up | Decide Route A for general availability | D-6; 01 Q-24 |

### 5.1 What happens to each capability of the LiteLLM design

Kept: the same outcome. Improved: a stronger outcome. Changed: the outcome is met differently, or less well. Lost: not available in this design.

| Capability | LiteLLM design `[LGW]` | This design | Verdict |
|---|---|---|---|
| Claude Code (Anthropic Messages API) | `/v1/messages` on LiteLLM | Bedrock natively, in Claude Code's Bedrock mode | Kept |
| Codex CLI (Responses API) | `/v1/responses` on LiteLLM; non-OpenAI models unverified | Codex's `amazon-bedrock` provider; only models Bedrock serves through the Responses API in Japan (R-4) | Changed |
| OpenAI chat format for every model | LiteLLM translates | Converse for every model; Chat Completions only where Bedrock offers it | Lost, in part |
| Embeddings in OpenAI format | LiteLLM translates | Bedrock's native format | Changed |
| Model list per caller | `/v1/models`, filtered by key | `llm models`, from the catalog and the team's tier | Changed |
| Stable aliases (`claude-opus`) | Ours | Bedrock's versioned IDs; the default model in managed settings | Changed |
| Fallback to another model | LiteLLM router | `jp.` profiles route between Tokyo and Osaka; another model only in the client | Changed |
| Credential for people | Virtual key, up to 90 days, made in the Admin UI | AWS credentials, 1 hour; sign-in at least every 8 hours | Improved |
| Device and MFA check | At key creation | At every sign-in | Improved |
| Credential for DC workloads | Static service-account key from CI | Certificate (at most 90 days) to 1-hour credentials | Improved |
| Binding a workload credential to its egress IP | Not possible; alert only [LGW 02 R-57] | IAM condition on the role | Improved |
| Admin UI, master key, password sign-in, session cookies | Ours to secure [LGW 02 D-28] | None | Improved |
| Team admins and runtime configuration by admins | Ours to restrict [LGW 02 D-27, R-55] | None; every change through CI | Improved |
| Leavers and movers | A sync job we write, because LiteLLM never removes memberships [LGW 02 D-30] | SCIM to IAM Identity Center, and `llm-lifecycle` for sessions already issued | Kept |
| Team budget | Real time, before the call | Within minutes for streams, within a day for the rest | Changed |
| Per-person budget across keys | User budget | Per-person cap | Kept |
| TPM/RPM per key, user and team | Redis counters | Account quotas, and a runaway stop | Lost |
| Chargeback | LiteLLM spend shares applied to the bill, with a residual | CUR 2.0 by principal directly | Improved |
| Cancelled streams, `no-log`, client-set tags | Gates V-5, V-6, V-7 against LiteLLM | Billed by AWS to the principal; nothing for the client to set | Improved |
| Price table for profile ARNs | Custom pricing, or the price is zero [LGW 02 R-5] | CUR has the price; our table only drives estimates | Improved |
| Guardrails | In-VPC PII masking and prompt-attack checks, Japanese | None in the path; an optional Classic-tier Bedrock guardrail (D-10) | Lost |
| Request size limit | `max_request_size_mb` | Bedrock's own limits | Changed |
| Exposed surface | WAF path allowlist [LGW 02 D-31] | IAM action allowlist | Kept |
| Office and DC only | ALB security group and WAF IP set | IAM network condition; Route A endpoint policy | Kept |
| mTLS if V-11 fails | Available on the ALB | Not available on AWS endpoints | Lost |
| Residency | SCP, task-role and endpoint policies | SCP and permission policies | Kept |
| No content at rest | Many LiteLLM settings, re-tested on every upgrade | Nothing of ours sees content; invocation logging locked; V-16 for the Responses API | Improved |
| Per-team content logging | Not designed [LGW 02 R-6] | An account per approved team (D-11) | Improved |
| Per-request record | Spend log with cost, latency, guardrail result | CloudTrail with principal and tokens for streams; cost from CUR | Changed |
| Dashboards | Grafana per team and key | CloudWatch per model; Quick Sight per team and person | Changed |
| DR | Warm standby gateway, Aurora Global Database, Route 53 failover | IAM Identity Center replica; clients switch Region | Changed |
| Entra outage | Keys keep working | Signed-in people work until their portal session ends | Changed |
| Other AWS accounts on our network path | Blocked: only the gateway hostname is allowed | Open on Route B; closed by Route A (D-6) | Changed |
| Latency added by the gateway | A hop through ALB and LiteLLM | None | Improved |
| Upgrade gates | Every LiteLLM upgrade | On policy changes and quarterly | Improved |

## 6. Verification and review

- **Verified by:** V-1, V-2, V-7, V-12, V-13, V-14, V-15, V-16; T-001, T-002, T-056
- **Revisit when:** a must-have requirement that only a proxy can meet is approved: real-time budgets, Japanese guardrails in the path, per-caller rate limits, or API translation for a must-have tool; or a launch gate shows that an AWS behaviour this design relies on is not as documented

## 7. Change log

| Date | Author | Change | Status after |
|---|---|---|---|
| 2026-11-20 | Claude (AI assistant), for platform engineering | Proposed | Proposed |
