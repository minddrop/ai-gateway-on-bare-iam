# IAM-native LLM gateway: Requirements

| Field | Value |
|---|---|
| Document ID | REQ-IGW |
| Version | 0.1 |
| Status | Draft |
| Owner | TBD (Product owner, 2026-12-18): named in Q-1 |
| Approvers | Security, legal/privacy, network, FinOps, platform lead |
| Related design | 02 Architecture and design |
| Source analysis | llm-gateway-comparison commit `46699eb` (2026-11-17); requirement IDs taken over from REQ-GW 0.2 in ai-gateway-on-aws commit `87ba355` (2026-11-20) |
| Last updated | 2026-11-20 |

## 1. Purpose and scope

### 1.1 Problem statement

Engineers want to use AI coding agents such as Claude Code and Codex CLI, and internal workloads and agents want to call large language models [CMP A-4]. Company rules require that prompts, responses and everything derived from them are processed and stored only in Japan [CMP A-5, A-11], and that no prompt content is stored by default [CMP A-10]. Without one controlled path, nobody can show where prompts were processed, who used which model, or what each team spent. The LiteLLM design solves this with a proxy that we run, patch and re-test after every upgrade [LGW 02 §1.1]. This system meets the same rules with AWS's own controls instead: IAM Identity Center for sign-in, IAM policies and SCPs for authorization and residency, and AWS billing by IAM principal for chargeback (02 D-1). What engineers use today, and what the gateway replaces, is Q-2.

### 1.2 Goals

| ID | Goal (an outcome someone can check) | Measured by |
|---|---|---|
| G-1 | Every model call is charged to one team. | Share of Bedrock cost in the monthly CUR 2.0 export, for the accounts in scope, that carries a platform-assigned team: 100 % (CST-001, CST-007). |
| G-2 | No prompt, response or derived data is processed or stored outside Japan. | Resource inventory and SCP inspection find nothing outside Tokyo and Osaka; every catalog model is processed in Japan (RES-001, RES-002). |
| G-3 | No prompt or response content is stored by default. | Launch gate V-1 passes on the configuration that goes live (PRV-001). |
| G-4 | Engineers use the supported coding agents with no setup beyond signing in. | Pilot demonstration on an Intune-managed laptop (FUN-009). |
| G-5 | Every control that rests on AWS behaviour or on our network is tested before launch and after every change to it. | All launch gates in 02 §11.2 pass on the configuration that goes live (OPS-001). |
| G-6 | No long-lived credential can call a model. | Inspection and gate V-2 find no IAM user, access key or long-term Bedrock API key that can call a model, and no model credential that lives longer than 1 hour (IAM-015, IAM-016). |
| G-7 | Nothing the platform runs is in the request path. | With every platform component stopped in staging, model calls still succeed (AVL-007). |

### 1.3 Non-goals (out of scope for this phase)

| ID | Excluded | Why | Revisit when |
|---|---|---|---|
| NG-1 | Remote and home access | Users work from offices and the DC, and the network condition in every IAM policy depends on it [CMP A-13] | Remote access is requested. The network condition must then be replaced, for example by ZTNA egress IPs that only managed devices can use [CMP §8.6]. |
| NG-2 | External model APIs that cannot prove in-Japan processing | Not allowed until legal and security confirm in-Japan processing in writing [CMP A-7] | A provider gives a written commitment to process and store in Japan (REG-001) |
| NG-3 | Response caching and stored responses | Stored responses are content at rest [CMP §2.8]; this includes the Responses API's own response storage (PRV-005) | A use case needs it and legal/privacy approves storing responses (PRV-001) |
| NG-4 | Model training and fine-tuning | The gateway governs how models are consumed, not how they are built [CMP §10.1, §10.9] | n/a: belongs to a separate ML platform [CMP §10.9] |
| NG-5 | The private path (Route A) in the pilot | The pilot starts on the public regional endpoints with IAM network conditions; the private path is proposed for general availability (02 D-6) | General availability, if AS-8 holds (Q-24) |
| NG-6 | Device checks on each request (mTLS with Intune certificates) | AWS endpoints cannot check a client device certificate; the device is checked at sign-in, at least every 8 hours (IAM-001, IAM-011) [CMP §2.3.2] | Gate V-11 fails, or NG-1 is revisited (SEC-003) |
| NG-7 | Bedrock features other than model inference in FUN-001 to FUN-004: batch and asynchronous inference, agents, knowledge bases, flows, prompt management, custom models, provisioned throughput, file and vector stores, MCP, image and video generation | Each is a new data path that must pass the residency checklist first [CMP §10.8.7] | A team requests one and it passes [CMP §10.8.7] (Q-5) |
| NG-8 | Keeping identity data (Entra ID, Okta, Intune, IAM Identity Center user records) in Japan | The identity plane never processes prompts and is outside the residency scope [CMP A-11] | Legal requires identity data in Japan [CMP A-11] |
| NG-9 | Long-term API keys: IAM users, IAM access keys, and long-term Bedrock API keys, for people and workloads | AWS recommends long-term Bedrock API keys only for exploration and short-term keys for production ([Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)); federation gives the same access without a secret to lose (02 D-3) | An exploration sandbox is approved (Q-26) |
| NG-10 | Translating between API formats, for example the OpenAI chat format for Claude models | Translation needs a proxy in the request path, which this design does not have (02 D-1) | A tool that is a must-have can call none of the APIs Bedrock offers for the model it needs (R-20) |
| NG-11 | Guardrails in the request path for Japanese text | Bedrock Guardrails screens Japanese only in its Standard tier, which routes through `apac.guardrail.v1:0` to Regions outside Japan; the Classic tier stays in the Region but does not support Japanese [CMP §2.5] (02 D-10) | Bedrock offers a guardrail profile that stays in Japan, or Japanese in the Classic tier; or Security requires guardrails (Q-13) |
| NG-12 | Token and request rate limits per person, per key or per team | Bedrock quotas apply per account, Region and model, not per caller ([Bedrock quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html)); the runaway stop (CST-012) and per-account isolation replace them (02 D-8) | Bedrock adds quotas per principal or per project |

### 1.4 Phasing

The pilot teams and the target dates are Q-3.

| Phase | Scope | Target date | Exit criteria |
|---|---|---|---|
| Pilot | Pilot teams TBD (Product owner, 2026-12-18) on the corporate network; Claude Code, Codex CLI, SDKs and IDE plugins that use AWS credentials; Bedrock models processed in Japan from the catalog (§6.5); Route B, the public regional endpoints | TBD (Product owner, 2026-12-18) | Every launch gate in 02 §11.2 passed before the first pilot user is given access [CMP §2.10]; every Must requirement Verified |
| General availability | All engineers on the corporate network; workloads in the on-premises DC and in enrolled AWS accounts [CMP A-4, A-13]; Route A if adopted (02 D-6) | TBD (Product owner, 2026-12-18) | Pilot findings recorded in 08; a DR drill met AVL-M02 and AVL-M03; gates re-run on the configuration that goes live |

### 1.5 Relation to the LiteLLM design

This baseline keeps the requirement IDs of REQ-GW 0.2 [LGW 01] where the requirement means the same thing, so the designs can be compared row by row. A requirement whose wording changed says "Changed from LGW" in its rationale. A requirement that does not apply without a proxy keeps its row with status Withdrawn and the reason. New requirements have new numbers. ADR D-1 §5 summarises what is kept, changed and lost.

## 2. Stakeholders and users

Team names for each role are in 00 §1.3.

| Role | Description | Main needs | Represented by (team) |
|---|---|---|---|
| Engineer (interactive) | Uses Claude Code, Codex CLI, IDE plugins | Japan-processed frontier models in their usual tools; sign in once a day, with no keys to manage | Product owner |
| Workload / agent | On-prem DC service or an AWS workload calling Bedrock | A role with its own budget and model list; credentials from a certificate (DC) or its own IAM role (AWS); a dedicated egress IP or private path [CMP §2.3.5] | Product owner |
| Team lead | Leads a team that is charged for usage; an ordinary team member, with no admin role [LGW 02 D-27] | See team spend against budget; budget alerts; workload roles, budgets, members and models changed through a CI pull request | Product owner |
| Platform operator | Builds and runs the policies, the spend guard and the client package | IaC deploys, runbooks that match tested behaviour, alerts, SSO access with phishing-resistant MFA [CMP §2.9] | Platform engineering |
| FinOps | Charges usage back to teams | Per-team and per-person cost from CUR 2.0, with unattributed cost on its own line [CMP §4.5] | FinOps |
| Security / SOC | Watches for misuse and incidents | CloudTrail events and access changes in the SIEM, no content in logs [CMP §2.8]; an access inventory | Security / SOC |
| Legal / privacy | Owns residency and content-logging approvals | Evidence that data stays in Japan; control over who sees per-person usage, which CUR now holds [CMP A-11, §2.8] | Legal / privacy |
| Network | Owns egress IPs, the secure web gateway, Direct Connect | A stable list of egress CIDRs; the TLS-inspection exemption for AWS hostnames; the private path if adopted [CMP A-14, A-15, A-16] | Network |
| Identity | Owns Entra ID, Conditional Access, the Okta EAM link and the SCIM provisioning to IAM Identity Center | One enterprise app for IAM Identity Center with the policy set CA-GW-01 to CA-GW-06 (02 §4.4) [CMP §2.1] | Identity |
| Endpoint / Intune | Owns device compliance and client configuration | The `llm` helper, Claude Code managed settings and the Codex CLI configuration, pushed by Intune [CMP §2.3.4] | Endpoint / Intune |

### 2.1 Use cases

| ID | Actor | Scenario | Supported by |
|---|---|---|---|
| UC-1 | Engineer | Runs Claude Code or Codex CLI from the office against a model processed in Japan; usage is charged to their team. | FUN-001, FUN-002, FUN-009, IAM-002, CST-001, RES-002, SEC-001 |
| UC-2 | Workload in the on-prem DC | Gets 1-hour credentials with its certificate and calls Bedrock from a dedicated DC egress IP; spend is charged to the team. | FUN-003, IAM-016, TEN-002, TEN-006, SEC-002, OBS-008, CST-001 |
| UC-3 | Team lead | Checks team spend against the budget, and is notified as the budget is used up. | CST-002, CST-010, OBS-003 |
| UC-4 | Leaver | Access ends when the account is disabled in Entra: every AWS credential of the user stops working. | IAM-006 |
| UC-5 | Engineer | Signs in once in the morning (Entra, MFA, compliant device); the tools refresh their credentials silently for the rest of the day. | FUN-008, FUN-009, IAM-001, IAM-011, IAM-016 |
| UC-6 | FinOps | Produces the monthly chargeback directly from CUR 2.0, by team and department, with unattributed cost on its own line. | CST-007, CST-008, CST-011 |
| UC-7 | Platform operator | Moves users to Osaka when the Tokyo endpoint is lost. | AVL-001, AVL-M02, AVL-M03, OPS-007 |
| UC-8 | Team lead | Asks for a new model; it is added only after its processing locations are checked. | MDL-104, REG-001 |
| UC-9 | Engineer | Moves to another team: access charged to the old team stops, and new sessions are charged to the new team. | TEN-004, TEN-007, CST-001 |
| UC-10 | Team lead | Asks for a workload role, a budget change or a model tier change through a pull request that the CI pipeline applies. | TEN-002, OPS-003 |
| UC-11 | Security / SOC | Investigates who called which model, from where, with read-only access, and no way to change anything. | IAM-010, IAM-013, OBS-001, OBS-002 |
| UC-12 | Platform operator | Suspends a person or a team at once (lost device, runaway agent), and lifts a wrong suspension when the spend guard misbehaves. | CST-012, OPS-010 |
| UC-13 | Workload in an AWS account | Calls Bedrock in its own enrolled account with its own IAM role; cost lands in that account. | CST-007, CST-014, RES-002, SEC-020 |
| UC-14 | Engineer in two teams | Chooses which of their teams pays for a session. | TEN-009, CST-001 |

## 3. Assumptions and dependencies

IDs AS-1 to AS-22 keep the numbers of [LGW 01 §3]; AS-1 to AS-16 restate the comparison's assumptions A-1 to A-16. Due dates are proposed and are confirmed in review.

| ID | Assumption / dependency | Source | Owner | Confirm by | Status | If false |
|---|---|---|---|---|---|---|
| AS-1 | Entra ID is the authoritative IdP, with synced UPNs and group membership for every user. | [CMP A-1] | Identity | 2026-12-18 | Open | Team membership has no source of truth; 02 §4 changes. |
| AS-2 | Okta is used only for MFA, attached to Entra as an External Authentication Method. | [CMP A-2, §2.1] | Identity | 2026-12-18 | Open | Use the federation pattern in [CMP §2.1.2]; 02 §4 changes. |
| AS-3 | Entra ID P1 or P2 licences are in place, and Intune enforces compliance on Windows and macOS. | [CMP A-3] | Identity | 2026-12-18 | Open | Conditional Access cannot require a compliant device; IAM-001 cannot be met. |
| AS-4 | Clients are Claude Code, Codex CLI, IDE plugins, SDKs, internal apps and agents in the DC and in AWS, and a browser for sign-in and dashboards. | [CMP A-4] | Product owner | 2026-12-18 | Open | FUN requirements change. |
| AS-5 | Only Tokyo (primary) and Osaka (DR) are used for anything in scope of residency. | [CMP A-5] | Legal / privacy | 2026-12-18 | Open | Constraint CON-4 and every RES requirement change. |
| AS-6 | A LiteLLM Enterprise licence is bought. | [CMP A-6] | Product owner | — | Withdrawn | n/a: this design runs no LiteLLM. |
| AS-7 | External model APIs are not allowed unless legal and security confirm in-Japan processing in writing. | [CMP A-7] | Legal / privacy | 2026-12-18 | Open | REG-001 changes. |
| AS-8 | Existing Direct Connect circuits terminate in a hub already peered with landing-zone spokes. | [CMP A-8] | Network | 2027-01-29 | Open | The private path for general availability (02 D-6) costs more; GA stays on Route B and R-12 stays open. |
| AS-9 | Scale is about 5,000 employees, about 300 concurrent users at peak, and 50–200 RPS with streaming. | [CMP A-9] | Product owner | 2026-12-18 | Open | Bedrock quotas and the spend guard's sizing change. |
| AS-10 | Prompt and response content is not stored by default; content logging is a per-team opt-in. | [CMP A-10] | Legal / privacy | 2026-12-18 | Open | PRV-001 and PRV-002 change. |
| AS-11 | Residency covers prompts, completions, embeddings and everything derived from them, not the identity SaaS or the cloud's own billing systems. | [CMP A-11] | Legal / privacy | 2026-12-18 | Open | NG-8 is revisited [CMP A-11]. |
| AS-12 | Provider abuse monitoring is acceptable if its storage stays in Japan. | [CMP A-12] | Legal / privacy | 2026-12-18 | Open | REG-002 changes. |
| AS-13 | Users are on the corporate network; remote access is out of scope. | [CMP A-13] | Product owner | 2026-12-18 | Open | NG-1 is revisited (R-27). |
| AS-14 | Office and DC breakouts use a small, stable set of public NAT egress IPs. | [CMP A-14] | Network | 2026-12-18 | Open | The network condition in the IAM policies cannot be maintained; Route A becomes required (02 D-6). |
| AS-15 | The secure web gateway can exempt the Bedrock and IAM Identity Center hostnames in 02 §6 from TLS inspection and allow them by FQDN. | [CMP A-15] | Network | 2026-12-18 | Open | Route A becomes required, so that traffic to Bedrock does not pass the secure web gateway [CMP §8.0]. |
| AS-16 | Unmanaged devices cannot leave through the office or DC egress IPs. | [CMP A-16] | Network | 2027-01-29 | Open | A copied credential works from an unmanaged device in the office until it expires (≤ 1 h; the sign-in token ≤ 8 h); tested by V-11 (SEC-003). |
| AS-17 | The Bedrock models in §6.5 remain processed in Japan through `jp.` profiles or In-Region in Tokyo, as in the snapshot checked on 2026-10-30. | [CMP §2.5, §7.2] | Platform engineering | 2027-01-29 | Open | The catalog shrinks; a required model with no Japan option is a blocking question (§6.5). |
| AS-18 | A shared network account (`network-prod`) with a Transit Gateway exists in Tokyo and can host the VPC endpoints of the private path. | [CMP §4.6] | Network | 2027-01-29 | Open | Route A needs its own endpoint VPC (02 D-6). |
| AS-19 | A SIEM is available whose storage is in Japan. | [CMP §4.7] | Security / SOC | 2026-12-18 | Open | OBS-001 and OBS-004 cannot be met without breaking RES-004. |
| AS-20 | Intune can deploy the `llm` helper, Claude Code managed settings and a user-level Codex CLI `config.toml` to Windows and macOS. | [CMP §2.3.4] | Endpoint / Intune | 2026-12-18 | Open | FUN-009 is not met; users configure tools by hand. |
| AS-21 | Every user is enrolled in Okta Verify before first sign-in, because EAM does not support inline enrolment. | [CMP §2.1] | Identity | 2026-12-18 | Open | First sign-ins fail; an enrolment step is added to onboarding. |
| AS-22 | Operators and read-only roles can register an Entra-native phishing-resistant method on their managed devices. | [LGW 02 D-29] | Identity | 2026-12-18 | Open | IAM-003 and IAM-007 cannot be met: External MFA cannot satisfy an authentication strength [LGW 02 R-56]. |
| AS-23 | The organization has an IAM Identity Center organization instance with Entra ID as its external identity provider (SAML and SCIM), home Region Tokyo, that can be replicated to Osaka. | 02 D-2; [Identity Center multi-Region](https://docs.aws.amazon.com/singlesignon/latest/userguide/multi-region-iam-identity-center.html) | Cloud platform | 2026-12-18 | Open | Sign-in has to be built another way; AVL-001 loses sign-in in Osaka. |
| AS-24 | CUR 2.0 with IAM principal data records, for every Bedrock call on `bedrock-runtime` and `bedrock-mantle`, the caller's assumed-role session ARN, whose session name is the Identity Center user name. | [IAM principal cost allocation](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/iam-principal-cost-allocation.html) | FinOps | 2027-01-29 | Open | Per-person chargeback needs another source; CST-007 changes. Tested by V-15. |
| AS-25 | For every streaming call on `bedrock-runtime`, CloudTrail records a stream-completion event that carries the caller's identity and the input and output token counts, and EventBridge delivers it. | [Bedrock CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html) | Platform engineering | 2027-01-29 | Open | The spend guard falls back to CUR only, and its enforcement delay grows to a day (CST-009). Tested by V-13. |
| AS-26 | The number of teams stays within the IAM Identity Center quotas for permission sets, because each team has one. | 02 D-2 | Cloud platform | 2026-12-18 | Open | Teams are grouped, or the team comes from a user attribute instead (Q-22, R-9). |
| AS-27 | The supported clients use the AWS SDK credential chain: Claude Code in Bedrock mode and Codex CLI's `amazon-bedrock` provider. | [Codex with Bedrock](https://help.openai.com/en/articles/20001253-configure-codex-with-amazon-bedrock); 02 §4.1 | Endpoint / Intune | 2027-01-29 | Open | That tool needs short-term API keys, which expire with the session (R-20). |

## 4. Constraints

| ID | Constraint | Source / authority |
|---|---|---|
| CON-1 | The hosting cloud is AWS; primary Tokyo (`ap-northeast-1`), DR Osaka (`ap-northeast-3`). | [CMP §7.2] |
| CON-2 | Access control, attribution and budgets use AWS-managed services. No third-party gateway software is placed in the request path. | Direction from the platform owner, 2026-11-20 (02 D-1) |
| CON-3 | Entra ID is the only identity provider, through IAM Identity Center; Okta Verify supplies MFA through Entra External MFA, except where Entra must require a phishing-resistant method [LGW 02 D-29]; Intune supplies device compliance. | [CMP A-1, A-2, A-3, §2.1] |
| CON-4 | Every component, data store, backup, log, export and data pipeline is in Tokyo or Osaka; global AWS services (IAM, Organizations, billing) are used only for metadata. | [CMP A-5, §2.5] |
| CON-5 | Model calls are allowed only where processing, not just the endpoint, is in Japan. | [CMP §2.5] |
| CON-6 | Public model provider APIs are blocked by default. | [CMP A-7] |
| CON-7 | AWS security best practice applies: federation and temporary credentials for people, IAM roles for workloads, least privilege, no long-term Bedrock API keys in production. | [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html); [Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html) |

## 5. Requirement conventions

**ID format:** `<AREA>-<NNN>`, for example `RES-001`. IDs are never reused or renumbered. A deleted requirement keeps its row with status `Withdrawn`. Metric rows use `<AREA>-M<NN>`, for example `AVL-M01`. Model catalog rows use `MDL-0NN`, and requirements about model routing use `MDL-1NN`. IDs that existed in REQ-GW 0.2 keep their number when the meaning is the same.

**Areas:**

| Code | Area |
|---|---|
| FUN | Functional: API surface, models, clients |
| IAM | Identity, authentication, authorization, device trust |
| TEN | Tenancy: teams, people, workloads |
| CST | Cost allocation, budgets, runaway protection |
| RES | Data residency |
| PRV | Privacy: prompt/response content handling, retention |
| SEC | Security controls (network, policies, secrets) |
| AVL | Availability, DR, resilience |
| PRF | Performance and capacity |
| OBS | Observability, audit, logging |
| OPS | Operability: deploy, change, runbooks, support |
| REG | Compliance and regulatory |
| MDL | Model catalog and routing behaviour |

**Wording:** each requirement is one testable sentence. Use "shall" for mandatory statements. "The gateway" means the whole system: the policies, the accounts and the components in 02 §2.2. Use a pattern:
- Always: `The gateway shall <response>.`
- Event: `When <trigger>, the gateway shall <response>.`
- State: `While <state>, the gateway shall <response>.`
- Unwanted behaviour: `If <condition>, then the gateway shall <response>.`

Avoid words that cannot be tested: *fast, secure, user-friendly, as appropriate, etc., support*. Replace them with a number or an observable behaviour.

**Priority (MoSCoW):** Must (launch blocks without it) / Should / Could / Won't (this phase).

**Verification method:** T = test, D = demonstration, I = inspection (config/code/document review), A = analysis. A requirement with no feasible verification method is not ready for approval.

**Status:** Proposed → Approved → Implemented → Verified. Also: Deferred, Withdrawn.

**Metrics:** each row in a metric table (§7.4, §7.5) is a requirement too, with the same priority, verification and status. A target states its window, where it is measured, and what is excluded.

## 6. Functional requirements

### 6.1 API and clients (FUN)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| FUN-001 | The gateway shall make every Claude model in the catalog available through the Anthropic Messages format, with streaming. | Claude Code calls Bedrock natively in Bedrock mode; Bedrock serves the Messages API on `bedrock-runtime` ([Bedrock endpoints](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html)) [CMP §2.3.4]. Changed from LGW: served by Bedrock, not a proxy. | Must | Claude Code in Bedrock mode completes a streamed multi-turn session with tool use against each catalog Claude model; the Anthropic SDK's Bedrock client completes a streamed request. | D | Proposed |
| FUN-002 | The gateway shall let Codex CLI complete streamed sessions through its `amazon-bedrock` provider against the catalog models approved for it. | Codex CLI calls Bedrock's Responses API ([Codex with Bedrock](https://help.openai.com/en/articles/20001253-configure-codex-with-amazon-bedrock)); which Japan-processed models it can use is open (R-4). Changed from LGW. | Must | Codex CLI completes a streamed multi-turn session with tool use against each model approved for it; the approved list is recorded in 04 §4.1. | D | Proposed |
| FUN-003 | The gateway shall make every chat model in the catalog available through the Bedrock Converse API, and through the OpenAI-compatible Chat Completions API for each model that Bedrock offers on it. | SDKs, IDE plugins and workloads; Bedrock serves Chat Completions only for some models ([Bedrock APIs](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html)). Changed from LGW: no translation (NG-10). | Must | The AWS SDK completes a streamed and a non-streamed Converse request against each catalog chat model; the OpenAI SDK completes one against each model that Bedrock lists for Chat Completions. | T | Proposed |
| FUN-004 | The gateway shall make every embedding model in the catalog available through Bedrock's InvokeModel API. | Embeddings are processed in Tokyo In-Region [CMP §2.5]. Changed from LGW: Bedrock's native request format. | Should | The AWS SDK gets embeddings of the expected dimension from each catalog embedding model. | T | Proposed |
| FUN-005 | A caller shall be able to list the catalog models their team may use, with the model ID to send. | Bedrock's own list operations return every profile in the Region, whatever the caller may call. Changed from LGW. | Should | For two teams with different model tiers, `llm models` shows exactly each team's list. | T | Proposed |
| FUN-006 | If a request uses a Bedrock operation or endpoint family outside FUN-001 to FUN-004, then the gateway shall refuse it before any model is called. | Each endpoint family is a new data path [CMP §10.8.7, §2.5] (NG-7) | Must | Calls to batch, asynchronous invoke, agents, knowledge bases, flows, custom model and provisioned throughput operations, and image and video models, are each denied, and CUR shows no charge for them. | T | Proposed |
| FUN-007 | If a request names content by internet URL, then the gateway shall not fetch it. | Fetching would send traffic to arbitrary hosts; content must be sent inline [CMP §2.5]. Changed from LGW: Bedrock, not our proxy, would fetch. | Must | A request with an image URL fails on each API style; the same image sent inline succeeds on a model that accepts images. | T | Proposed |
| FUN-008 | A signed-in user shall be able to get credentials for each team they belong to, see which team their tools are using, and see their own usage, without help from an administrator. | Self-service, with no key to create or renew [CMP §2.3.5]. Changed from LGW: no web UI for keys (D-12, D-14). | Must | A user runs `llm login`, `llm team`, `llm usage`, and sees their assignments in the access portal; no administrator acts. | D | Proposed |
| FUN-009 | The supported coding agents shall reach Bedrock on an Intune-managed device with no configuration by the user other than signing in, and choosing a team if they are in several; no credential valid for longer than the access-portal session shall be stored on the device. | Keeps long-lived secrets off devices [CMP §2.3.4]. Changed from LGW: no key in the credential store, because there is no long-lived key. | Must | On a freshly enrolled Windows and macOS device, after `llm login`, Claude Code and Codex CLI each complete a request; no file under the user's home directory and no environment variable holds a credential that is valid for longer than the access-portal session (04 §4.4). | D | Proposed |

### 6.2 Identity and access (IAM)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| IAM-001 | Sign-in to IAM Identity Center shall be possible only through Entra ID, with MFA through Okta Verify and a compliant device required at sign-in. | Device and MFA are checked when credentials are issued [CMP §2.1 CA-GW-01, §2.3.1] | Must | Sign-in succeeds from a compliant device with MFA; it is refused from a non-compliant device, and without completed MFA. | T | Proposed |
| IAM-002 | If a model request is not signed with valid, unexpired AWS credentials or a valid short-term Bedrock API key, then the gateway shall refuse it before any model is called. | Every call is authenticated by AWS [CMP §2.3]. Changed from LGW: no virtual keys. | Must | Requests with no signature, a wrong signature, expired credentials, and an expired short-term key are each refused, and CUR shows no charge for them. | T | Proposed |
| IAM-003 | Users with an operator or read-only role in the production accounts shall sign in with a compliant device and phishing-resistant MFA, and shall sign in again at least every 8 hours. | These roles see everyone's usage and can suspend access [CMP §2.1 CA-GW-02, §2.9]; [LGW 02 D-29] | Must | A sign-in by a member of the operator group with Okta Verify only is refused; a passkey sign-in is accepted; a session older than 8 hours requires a new sign-in. | T | Proposed |
| IAM-004 | Each person's access shall come only from Entra group membership, provisioned to IAM Identity Center by SCIM and assigned to permission sets; no permission set shall be assigned to an individual user. | Entra is the source of truth [CMP §2.4, §4.4]. Changed from LGW: no app roles. | Must | An inspection of every assignment in the production accounts finds only groups; adding a user to a team group gives access after provisioning; removing them takes it away within the target in Q-8. | I, T | Proposed |
| IAM-005 | Device-code flow and legacy authentication shall be blocked for the Entra enterprise app of IAM Identity Center. | Device-code flow lets credentials land on another machine [CMP §2.1 CA-GW-04, CA-GW-05]; IAM Identity Center's own device authorization is R-7 | Must | A device-code sign-in to the app in Entra is refused. | T | Proposed |
| IAM-006 | When a user's Entra account is disabled, every AWS credential of that user shall stop working within TBD (Security, 2026-12-18) (Q-8). | Credentials and access-portal sessions outlive an Entra sign-in [CMP §2.3.6 row 6] | Must | After an account is disabled, a model call with the user's existing credentials is denied within the target time. | T | Proposed |
| IAM-007 | Operator sign-in to the AWS console and CLI shall require phishing-resistant MFA, a compliant device, and an office or DC egress IP. | Operator access has no gateway in front of it [CMP §2.1 CA-GW-05, §2.9 A2, A3] | Must | An operator sign-in from a non-compliant device, from a non-office IP, and with push-only MFA, are each refused. | T | Proposed |
| IAM-008 | Admin sessions in the AWS accounts shall last at most 1 hour, and AWS API calls made with operator credentials from outside the office and DC egress IPs shall be denied. | Cached CLI credentials can be copied [CMP §2.9, §4.4] | Must | An admin session expires after 1 hour; a CLI call with copied operator credentials from a non-office IP is denied. | T | Proposed |
| IAM-009 | Break-glass access to the AWS accounts shall exist, with credentials kept in a vault, and every use shall raise an alert to Security. | Operators need a path when SSO fails [CMP §4.4] | Should | A break-glass sign-in in a drill raises an alert in the SIEM. | D | Proposed |
| IAM-010 | A person without an operator or read-only role shall be able to read only their own usage, and their teams' usage as far as the PRV-003 agreement allows. | Per-person usage is personal data [CMP §2.8]. Changed from LGW: no key or user records to read. | Must | Through the usage API and the dashboards, reads of another person's usage, and of another team's, are refused. | T | Proposed |
| IAM-011 | The IAM Identity Center access-portal session shall end no later than 8 hours after sign-in, for every user. | The portal session can mint new credentials without Entra until it ends [LGW 02 D-28]. Changed from LGW: the portal, not a web UI of ours. | Must | A portal session older than the limit cannot get new credentials, and the next `llm login` opens an Entra sign-in. | T | Proposed |
| IAM-012 | Break-glass admin access to the gateway application shall exist. | [LGW 01 IAM-012] | — | — | — | Withdrawn: there is no gateway application. Break-glass for the spend guard is OPS-010. |
| IAM-013 | In production, people shall hold only read-only roles and the operator role, whose only write action is suspending or restoring access through the spend guard; everything else shall change only through the CI pipeline or break-glass. | Production changes go through CI [CMP §2.9] [LGW 02 D-27] | Should | An inspection finds no person with write permissions in production beyond the operator role, and a month of CloudTrail shows no change outside the CI role, the spend guard and recorded break-glass uses. | I | Proposed |
| IAM-014 | Dashboards built from gateway data shall accept sign-in only through Entra ID, with MFA and a compliant device. | They hold per-person data (PRV-003) | Should | Sign-in to each dashboard from a non-compliant device, and without MFA, is refused. | T | Proposed |
| IAM-015 | No IAM user, IAM access key or long-term Bedrock API key shall be able to call a model in any account of the organization. | CON-7; NG-9; long-lived keys are the commonest leak [CMP §2.3.6 row 1] (D-3) | Must | Creating a long-term Bedrock API key and calling a model with an IAM user's access key are each denied by SCP in every account; an inventory finds no IAM user with model permissions. | T, I | Proposed |
| IAM-016 | Every credential that can call a model shall expire no more than 1 hour after it is issued, and a short-term Bedrock API key shall not outlive the session that made it. | Bounded credential lifetime [CMP §2.3]; short-term keys inherit their session's expiry ([Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)) | Must | Credentials from each permission set and workload role expire after at most 1 hour; a short-term key made from them fails after the session ends. | T | Proposed |

### 6.3 Tenancy (TEN)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| TEN-001 | A person shall be able to call models only through the permission set of a team they belong to and only within that team's model tier, and shall not be able to create credentials for anyone else. | Self-service is safe only within limits [CMP §2.3.5]. Changed from LGW: no key creation. | Must | Launch gate V-12 passes. | T | Proposed |
| TEN-002 | Workload roles, Roles Anywhere trust anchors and profiles, workload certificates, and account enrolments shall be created only by the CI pipeline. | Workload credentials must not be created by individuals [CMP §2.3.5]; production changes go through CI [CMP §2.9] | Must | A person, whatever their team role, is refused when creating a workload role, a trust anchor or an enrolment in production. | T | Proposed |
| TEN-003 | Every principal that can call a model shall have an owner, a team, a maximum credential lifetime, an explicit model list and a budget. | Every caller must be attributable and bounded [CMP §2.3, §2.3.5]. Changed from LGW: principals, not keys. | Must | An inspection of every permission set, workload role and enrolled account finds each field set. | I | Proposed |
| TEN-004 | Each team shall correspond to one Entra security group `llm-team-<team>`; a user shall get the team's access after the group membership is provisioned, and shall lose it within TBD (Security, 2026-12-18) (Q-8) of leaving the group. | Entra is the source of truth for teams [CMP §2.4, §4.4] | Must | Adding a user to a team group gives access to the team's permission set; removing them takes it away within the target time. | T | Proposed |
| TEN-005 | Per-person caps shall apply to all of a person's usage, across all their teams, tools and Regions. | Extra teams or tools must not multiply the allowance [CMP §2.3.5]. Changed from LGW: per person, not across keys. | Must | With a small test cap, calls through two teams and two tools are counted together and are denied once the cap is reached. | T | Proposed |
| TEN-006 | Workload certificates used with IAM Roles Anywhere shall expire no more than 90 days after they are issued. | Bounded lifetime [CMP §2.3]. Changed from LGW: certificates, not keys; people's credentials are IAM-016. | Must | Issuing a workload certificate with a longer validity is refused by the CA template; an inspection finds none. | T, I | Proposed |
| TEN-007 | When a user stops being a member of a team, every credential of that user charged to that team shall stop working within TBD (Security, 2026-12-18) (Q-8). | A user who moves team must not keep the old team's models or charge the old team | Must | After a user is removed from a team group, a call with their credentials for that team is denied within the target time. | T | Proposed |
| TEN-008 | If a user belongs to no team, then the gateway shall give them no model access. | Every call is charged to one team (G-1, CST-001) | Must | A user in no `llm-team-*` group has no LLM permission set in the access portal, and `llm login` reports that they have no team. | T | Proposed |
| TEN-009 | A person in several teams shall choose, for each session, which of their teams is charged, and shall not be able to charge a team they do not belong to. | Which team pays for a person in two teams was open [LGW 01 Q-12]; the platform restricts the choice to the person's own teams | Must | A user in two teams can use either team's permission set; a user cannot get credentials for a team they are not in. | T | Proposed |

### 6.4 Cost allocation and limits (CST)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| CST-001 | The gateway shall charge each model call to the team that the platform assigns, whatever the client sends. | Clients must not choose who pays [CMP §2.4, V-7] | Must | Launch gate V-7 passes. | T | Proposed |
| CST-002 | When a team's month-to-date spend reaches its budget, the gateway shall deny further model calls charged to that team, within the enforcement delay in CST-009, until the month resets or the budget is raised. | Budgets are enforced [CMP §4.5]. Changed from LGW: within the enforcement delay, not before the call. | Must | Launch gate V-14 passes, with a small test budget. | T | Proposed |
| CST-003 | The gateway shall enforce user and key budgets and TPM/RPM limits across all gateway instances. | [LGW 01 CST-003] | — | — | — | Withdrawn: there are no gateway instances, and Bedrock has no per-caller quota (NG-12). Replaced by CST-012 and CST-013. |
| CST-004 | The spend guard's cost estimate shall be non-zero for every catalog model and within a tolerance of the CUR cost, including calls that use prompt caching. | A zero price makes budgets silent [CMP §2.4, V-4]. Changed from LGW: CUR is the price source; the estimate only drives enforcement. | Must | Launch gate V-4 passes; the tolerance is Q-12. | T | Proposed |
| CST-005 | No client setting shall stop a model call from being billed and attributed to its principal. | Clients must not skip tracking [CMP §2.4, V-6] | Must | Launch gate V-6 passes. | T | Proposed |
| CST-006 | The cost of calls that end before the response completes shall be charged to the caller, and the gap between the spend guard's estimate and CUR for such calls shall be measured. | Cancelled streams [CMP §2.4, V-5] | Must | Launch gate V-5 passes. | T, A | Proposed |
| CST-007 | Each month, each team's charge shall be the Bedrock cost that CUR 2.0 attributes to the team's principals and enrolled accounts, and cost that CUR does not attribute to a principal shall be reported as its own line. | CUR is the cost truth, and now names the caller [CMP §4.5] (D-9). Changed from LGW: no allocation of the bill by shares. | Must | A month's chargeback report reproduces from CUR 2.0 and the team configuration in Git, and shows the unattributed line. | A | Proposed |
| CST-008 | When the monthly unattributed cost, or the gap between the spend guard's estimate and CUR, exceeds a threshold, it shall be investigated and the cause recorded. | Gaps hide pricing errors and unmetered calls [CMP §4.5] | Should | A gap above the threshold (Q-12) has an investigation record in the following month. | I | Proposed |
| CST-009 | The budget policy signed off by finance shall state the maximum overshoot of a budget, derived from the enforcement delay for streaming and non-streaming calls and from the account quotas. | Enforcement is after the fact (D-8) [CMP §2.4] | Should | The signed policy states the bound and the calculation behind it (02 §5). | A | Proposed |
| CST-010 | When a team's spend reaches 80 % and 100 % of its budget, the team's leads shall be notified, with no prompt content in the notification. | Same thresholds as the AWS Budgets backstop [CMP §4.5]; alerts carry no content [CMP §2.5] | Should | Crossing each threshold in a test sends one notification to the team lead, and its text contains no prompt content. | T | Proposed |
| CST-011 | Every team shall be mapped to one department or cost centre for chargeback. | Department chargeback [CMP §2.4, §4.5] | Must | An inspection finds no team without a department; the monthly report totals by department. | I | Proposed |
| CST-012 | When one principal's token use in a 5-minute window exceeds the runaway threshold, the gateway shall deny that principal for the suspension period, and notify the principal's owner and on-call. | Replaces per-caller rate limits (NG-12): a runaway agent must not use the whole account quota or budget | Should | Launch gate V-14 passes: a test principal above the threshold is denied within the delay in CST-009 and restored after the suspension period; values Q-23. | T | Proposed |
| CST-013 | When a person's month-to-date spend reaches the per-person cap, the gateway shall deny that person's model calls until the month resets or the cap is raised. | Replaces user budgets [LGW 01 TEN-005] | Should | With a small test cap, calls are denied after the cap is reached and allowed after it is raised. | T | Proposed |
| CST-014 | Each enrolled AWS workload account and each workload role shall have an AWS Budget that notifies its owner at 80 % and denies model calls at 100 %. | AWS-native budgets where AWS can act on the target [CMP §4.5] (D-8) | Should | In staging, a workload role and an enrolled account each lose model access when their test budget is used up. | T | Proposed |

### 6.5 Model catalog and routing (MDL)

Availability is from the comparison's snapshot (checked 2026-10-30) and is re-checked before each model is onboarded (MDL-104). Which models are needed, by when and at what priority is Q-4. Models the snapshot lists as available from Tokyo only through global or multi-country routing (for example Claude Sonnet 5.5) are not in the catalog; a request for one goes to the residency owner, not to an exception [CMP §7.3]. Clients send Bedrock's own model IDs (MDL-105); the IDs are in 04 §4.1.

| ID | Model family / capability | Use case | Needed by (phase) | Japan availability (how processed, date checked) | Available in DR region? | Priority | Status |
|---|---|---|---|---|---|---|---|
| MDL-001 | Frontier coding model (Claude Opus 5.5) | UC-1 | TBD (Product owner, 2026-12-18) | Tokyo: yes, `jp.` cross-Region inference profile (checked 2026-10-30) [CMP §2.5] | Osaka: yes, the same `jp.` profile, with its own quota [CMP §4.5, §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-002 | Fast model (Claude Haiku 5.5) | UC-1, UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, `jp.` profile (checked 2026-10-30) [CMP §2.5] | Osaka: yes, the same `jp.` profile [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-003 | Previous frontier model (Claude Opus 4.8) | UC-1 | TBD (Product owner, 2026-12-18) | Tokyo: yes, `jp.` profile (checked 2026-10-30) [CMP §2.5] | Osaka: yes, the same `jp.` profile [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-004 | Mid-size model (Claude Sonnet 4.6) | UC-1, UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, `jp.` profile (checked 2026-10-30) [CMP §2.5] | Osaka: yes, the same `jp.` profile [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-005 | Previous fast model (Claude Haiku 4.5) | UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, `jp.` profile (checked 2026-10-30) [CMP §2.5] | Osaka: yes, the same `jp.` profile [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-006 | Low-cost general model (Amazon Nova 2 Lite) | UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, `jp.` profile (checked 2026-10-30) [CMP §2.5] | Osaka: yes, the same `jp.` profile [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-007 | Embeddings (Titan Text Embeddings V2) | UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, In-Region (checked 2026-10-30) [CMP §2.5] | TBD (Platform engineering, 2027-01-29): not checked; an embedding model cannot be swapped without re-indexing [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-008 | Embeddings (Cohere Embed v4) | UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, In-Region (checked 2026-10-30) [CMP §2.5] | TBD (Platform engineering, 2027-01-29): not checked [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-009 | Open-weight large model (Mistral Large 3) | UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, In-Region (checked 2026-10-30) [CMP §2.5] | TBD (Platform engineering, 2027-01-29): not checked [CMP §4.9] | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-010 | Open-weight model (gpt-oss-120b) | UC-1 (Codex CLI, R-4), UC-2 | TBD (Product owner, 2026-12-18) | Tokyo: yes, In-Region (checked 2026-10-30) [CMP §2.5]; the Responses API for it is served on `bedrock-mantle`, which is offered in Tokyo ([Bedrock endpoints](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html)) | No for the Responses API: `bedrock-mantle` is not offered in Osaka; In-Region model in Osaka not checked: TBD (Platform engineering, 2027-01-29) | TBD (Product owner, 2026-12-18) | Proposed |
| MDL-011 | OpenAI GPT models, only if required, as hosted on Bedrock | TBD (Product owner, 2026-12-18) | TBD (Product owner, 2026-12-18) | TBD (Platform engineering, 2027-01-29): Bedrock serves closed-weight GPT models through system inference profiles; whether a `jp.` profile exists is not checked. Changed from LGW: Azure OpenAI is not reachable without a proxy (NG-10) | TBD (Platform engineering, 2027-01-29) | TBD (Product owner, 2026-12-18): required only if OpenAI models are needed (Q-4) | Proposed |

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| MDL-101 | Every model call shall be processed only in Japan, whatever model, profile, Region or fallback the client configures. | A fallback outside Japan silently breaks residency [CMP A-7, §2.5]. Changed from LGW: `jp.` profiles route between Tokyo and Osaka; there is no router of ours. | Must | Calls to a `global.`, `apac.` and `us.` profile, and to a model in a non-Japan Region, are each denied by SCP from every principal type; CloudTrail shows no successful call to them. | T | Proposed |
| MDL-102 | If a request names a model that is not in the catalog, then the gateway shall refuse it. | Only catalog models are checked for Japan processing [CMP §2.5] | Must | A call to a model ID outside the catalog is denied, and CUR shows no charge for it. | T | Proposed |
| MDL-103 | If a request names a catalog model that the caller's team tier does not include, then the gateway shall refuse it. | Model access is granted per team [CMP §2.4] | Must | A principal of a team without access to a model is denied for that model and allowed for its tier's models. | T | Proposed |
| MDL-104 | A model shall be added to the catalog only after its processing locations have been confirmed to be only Tokyo and Osaka and recorded with the date, and every catalog model shall be re-checked every quarter. | Availability changes faster than the analysis [CMP §4.8, §7.2] | Must | Each catalog row has a check record dated before its onboarding and within the last quarter. | I | Proposed |
| MDL-105 | Clients shall use Bedrock's own versioned model IDs, and a change of the default model in the managed client settings shall be announced in advance. | Clients pin model names [CMP §4.5]. Changed from LGW: no aliases of ours. | Should | Each change of a default model in managed settings has a release note published before the change; the notice period is set in 10 §1. | I | Proposed |

## 7. Non-functional requirements

### 7.1 Data residency (RES)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| RES-001 | Prompts, completions, embeddings, and all data derived from them shall be processed and stored only in Japan. | [CMP A-5, A-11, §2.5] | Must | Every data store, backup, log, export and model call in the inventory is in Tokyo or Osaka; an attempt to create a store outside them fails. | I, T | Proposed |
| RES-002 | The gateway shall allow calls only to models processed in Japan, and a call to a global or multi-country profile shall be refused by an SCP, whatever the caller's own permissions are. | Enforcement must not depend on per-role configuration [CMP §2.5 rules 2 and 4] | Must | From an administrator role in a staging account, calls to a `global.` and an `apac.` profile are both denied by the SCP. | T | Proposed |
| RES-003 | Cloud policy shall deny creating resources outside Tokyo and Osaka in the gateway's accounts, except for global services. | [CMP §2.5 rule 4] | Must | An attempt to create a bucket and a log group in a non-Japan region is denied. | T | Proposed |
| RES-004 | CUR exports, CloudTrail copies, SIEM copies, analytics and dashboards built from gateway data shall be stored and processed only in Japan. | Pipelines are in scope [CMP §2.5 rule 3, §4.7] | Must | Each pipeline in the inventory names a Japanese region for every store and compute step. | I | Proposed |
| RES-005 | No component that the platform operates shall receive prompt or response content. | The spend guard, usage API and dashboards work on metadata only (D-8). Changed from LGW: no proxy holds content. | Must | An inspection of every event the spend guard and usage API read finds no content field; V-1 finds no canary in their stores or logs. | I, T | Proposed |
| RES-006 | For each supported client, what it sends to its vendor other than model calls shall be listed, turned off through managed settings where the client allows it, and the rest approved by legal/privacy. | Residency holds only if clients do not send data elsewhere [CMP §2.5 rule 5] | Must | A record per client lists its non-model traffic, the managed setting that turns each off, and legal's approval of what remains. | I | Proposed |
| RES-007 | Public model APIs, consumer AI services, and Bedrock in Regions outside Japan shall be blocked on the office secure web gateway. | Otherwise residency holds only for users who choose the gateway [CMP §2.5 rule 5]; Bedrock in Tokyo is reachable from personal AWS accounts on Route B (R-12) | Should | From an office device, connections to a sample of public model APIs, consumer AI sites and `bedrock-runtime` in a non-Japan Region are blocked. | T | Proposed |
| RES-008 | Bedrock model invocation logging shall be off in every account of the organization except accounts approved for content logging, and an SCP shall deny turning it on elsewhere. | It logs content for every caller in the account and Region [CMP §2.8] (D-11) | Must | An inspection shows it off in both Regions of every account except approved ones; an attempt to turn it on from an administrator role is denied. | I, T | Proposed |

### 7.2 Privacy (PRV)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| PRV-001 | The gateway shall not store prompt or response content anywhere unless the calling team is approved for content logging. | Content is not stored by default [CMP A-10, §2.8] | Must | Launch gate V-1 passes: a canary sent through every model and API style, including a refused and a cancelled call, is found in no store. | T | Proposed |
| PRV-002 | When a team is approved for content logging by legal/privacy, the gateway shall store that team's content only in that team's content-logging account, separate from all other stores. | Per-team opt-in [CMP A-10, §4.7]. Changed from LGW: now designed, as a dedicated account (D-11) | TBD (Legal / privacy, 2026-12-18) (Q-10) | V-1 run with the approved team's account finds that team's canary only in its log bucket, and other teams' canaries nowhere. | T | Proposed |
| PRV-003 | Access to per-person usage, including the per-person lines in CUR 2.0, and how long it is kept, shall be agreed with the privacy office before any per-person report is shared. | Metadata is personal data too [CMP §2.8]; CUR now names each person (D-9) | Must | A written agreement exists, and access to CUR, CloudTrail and the dashboards is limited to the roles it names. | I | Proposed |
| PRV-004 | Provider-side request logging that captures content shall be off for every model in the gateway's accounts. | It cannot be limited to one team in a shared account [CMP §2.8, §4.7] | Must | Covered by RES-008 for Bedrock; an inspection of both regions shows invocation logging off in every account in scope. | I | Proposed |
| PRV-005 | No response shall be stored by the Responses API, or retrievable after the call. | Bedrock keeps Responses API responses for 30 days unless the request turns storage off ([Responses API](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-responses-api.html)) (R-3) | Must | Launch gate V-16 passes for every client approved for the Responses API. | T | Proposed |

### 7.3 Security (SEC)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| SEC-001 | The gateway shall deny every model call that does not come from an office or DC egress IP, or from one of our VPC endpoints. | Users are on the corporate network [CMP A-13, A-14]. Changed from LGW: enforced in IAM policies, not at an ALB. | Must | A call from an IP outside the list with valid credentials is denied; a call from each office and DC egress IP succeeds. | T | Proposed |
| SEC-002 | The network list shall contain only dedicated egress IPs of ours, each with a named owner, and no shared NAT or SASE ranges. | A shared NAT admits every workload behind it [CMP §2.3.5, V-11] | Must | Launch gate V-11 passes, including its list of every CIDR and owner. | I, T | Proposed |
| SEC-003 | If gate V-11 finds that an unmanaged device can use an office or DC egress IP, or AS-16 cannot be confirmed, then launch shall wait for a design change approved by Security. | A copied credential works from any device behind the listed IPs until it expires. Changed from LGW: mTLS is not possible on AWS endpoints (NG-6). | Must | The V-11 record shows either a pass, or an approved design change tested before launch. | I | Proposed |
| SEC-004 | All model calls shall use TLS 1.2 or later to AWS regional endpoints in Tokyo or Osaka, with no CDN or global edge in between. | Residency [CMP §2.6, §4.8]. Changed from LGW: AWS endpoints, not our ALB. | Must | A TLS 1.1 handshake to each endpoint fails; the SCP denies non-Japan Regions (RES-003). | T, I | Proposed |
| SEC-005 | The Bedrock and IAM Identity Center hostnames listed in 02 §6 shall be exempt from TLS inspection on the corporate secure web gateway, and allowed by FQDN. | Inspection lets the proxy read prompts and short-term API keys [CMP A-15, §2.6] | Must | From an office device, the certificate presented for each hostname is AWS's own, not the proxy's. | T | Proposed |
| SEC-006 | The web application firewall shall pass legitimate API request bodies larger than 8 KB. | [LGW 01 SEC-006] | — | — | — | Withdrawn: there is no WAF or load balancer of ours. |
| SEC-007 | If a request body is larger than the maximum request size, then the gateway shall refuse it. | [LGW 01 SEC-007] | — | — | — | Withdrawn: Bedrock's own request limits apply; the budget overshoot that this bounded is in CST-009. |
| SEC-008 | The gateway shall check every request, before the model call and processed in Japan, for personal information to mask and for prompt attacks, in Japanese and in English. | Bedrock Guardrails cannot do this in Japan for Japanese [CMP §2.5, §4.8] (NG-11, D-10) | TBD (Security / SOC, 2026-12-18) (Q-13) | For a test set in Japanese and English, every listed personal-information type is masked and the detection rate meets the target. | T | Deferred: no option exists without a proxy (D-10, R-5) |
| SEC-009 | The behaviour of the gateway when the guardrail check fails shall be defined and approved by Security. | [LGW 01 SEC-009] | TBD (Security / SOC, 2026-12-18) (Q-13) | The approved behaviour is recorded and tested. | I, T | Deferred: with SEC-008 |
| SEC-010 | The gateway's master key shall be held only in the secrets store. | [LGW 01 SEC-010] | — | — | — | Withdrawn: there is no static admin credential. Privileged roles are SEC-021. |
| SEC-011 | While SSO is configured, password sign-in to the web UI shall be turned off. | [LGW 01 SEC-011] | — | — | — | Withdrawn: there is no web UI of ours; IAM Identity Center accepts only the external identity provider. |
| SEC-012 | No secret shall be stored in configuration, code or the repository, and the CI pipeline shall reach AWS through OIDC federation, not access keys. | [CMP §4.8]; CON-7 | Must | Secret scanning of the repository finds none; the CI role's trust policy names only the CI system's OIDC provider and protected branches. | I | Proposed |
| SEC-013 | The gateway's outbound traffic shall be limited to an allowlist of hostnames. | [LGW 01 SEC-013] | — | — | — | Withdrawn: no component of ours receives content (RES-005); model calls go from clients to Bedrock. |
| SEC-014 | In general availability, model calls from offices and the DC shall reach Bedrock over the private path, and its VPC endpoint policies shall allow only principals of our organization. | The only control that keeps personal AWS accounts off our network path to Bedrock [CMP §4.3, §8] (D-6, R-12) | Should | With Route A in place, a call through our endpoint with credentials from an account outside the organization is denied, and calls from our principals succeed. | T | Proposed |
| SEC-015 | Credentials and short-term Bedrock API keys shall not appear in any log or store of ours. | Keys must not land in logs [CMP §2.8] | Must | A call with a known test short-term key leaves no copy of it in CloudTrail, the spend guard's logs or tables, or the `llm` helper's logs. | T | Proposed |
| SEC-016 | Spend guard and usage API code shall be signed, scanned, and promoted through dev and staging to production. | Supply chain [CMP §4.8]. Changed from LGW: Lambda code, not container images. | Must | Production functions accept only code signed by our signing profile, and each deployed version has a scan result and ran in staging first. | I | Proposed |
| SEC-017 | No interactive shell access to running gateway containers shall be possible in production. | [LGW 01 SEC-017] | — | — | — | Withdrawn: there are no containers. |
| SEC-018 | Repositories shall be scanned for AWS access keys and Bedrock API keys, with pushes that contain one blocked. | Leaked keys are the commonest leak [CMP §2.3.6 row 1] | Should | A push containing a test key of each kind is rejected. | T | Proposed |
| SEC-019 | The gateway's AWS accounts shall run continuous threat detection, configuration compliance checks and unused-access analysis, with findings sent to the SIEM. | [CMP §4.8] | Should | A sample finding of each kind appears in the SIEM. | D | Proposed |
| SEC-020 | Every principal that can call a model shall be allowed only an explicit list of Bedrock actions and model resources, with no wildcard action in any allow statement. | A new Bedrock action must not become allowed by itself. Changed from LGW: actions, not URL paths. | Must | An inspection of every policy finds no wildcard action; launch gate V-12 passes. | I, T | Proposed |
| SEC-021 | The roles that can change access (the CI deploy role, the spend guard's enforcer role) shall be usable only by their own service, and every use of them from anywhere else shall raise an alert. | They are the new admin credentials. Replaces [LGW 01 SEC-010]. | Must | The trust policy of each role names only its service or OIDC provider; an attempt to assume each from an operator role is denied and alerts. | T | Proposed |
| SEC-022 | The S3 buckets that hold CUR exports, CloudTrail logs and spend data shall be readable only by principals of our organization. | Data perimeter for per-person data ([data perimeters](https://docs.aws.amazon.com/whitepapers/latest/building-a-data-perimeter-on-aws/perimeter-overview.html)) | Should | A read with credentials from an account outside the organization is denied by the bucket policy or a resource control policy. | T | Proposed |

### 7.4 Availability and DR (AVL)

| ID | Metric | Target | Measurement (window, point, method) | Conditions and exclusions | Priority | Verif. | Status |
|---|---|---|---|---|---|---|---|
| AVL-M01 | Availability (monthly) | TBD (Product owner, 2026-12-18) (Q-6) | Calendar month; a synthetic probe with its own workload role calls a small model from an office network; probe interval and the failure definition TBD (Platform engineering, 2026-12-18) | Whether Bedrock outages that affect every Japan deployment of a model are excluded: TBD (Product owner, 2026-12-18) | Must | A | Proposed |
| AVL-M02 | RTO (loss of the Tokyo region) | TBD (Product owner, 2026-12-18); no design estimate yet: it depends on how fast clients switch Region (R-11) | DR drill: time from the failover decision until the probe in AVL-M01 succeeds against Osaka, and until a sample of users is working there | Models with no Osaka option are excluded (§6.5) | Must | T | Proposed |
| AVL-M03 | RPO (spend and audit data) | TBD (Product owner, 2026-12-18); design estimate: seconds for the spend guard's counters, none for CloudTrail and CUR, which AWS keeps | DR drill: spend guard counters in Osaka compared with the last ones written in Tokyo | Requests in flight in Tokyo | Must | T | Proposed |
| AVL-M04 | Maximum planned downtime per change | 0 min: no change of ours restarts anything in the request path | Minutes in which the AVL-M01 probe fails during a policy or spend guard deployment | — | Should | T | Proposed |

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| AVL-001 | When Bedrock in Tokyo is unavailable, people and workloads shall be able to call every catalog model that is available in Osaka, from Osaka, with sign-in still working. | Warm DR in Osaka [CMP A-5, §4.9]; IAM Identity Center replicated to Osaka (D-13). Changed from LGW: no gateway to fail over. | Must | In a DR drill, with Tokyo treated as lost, users sign in and call each model marked as available in Osaka within the RTO (AVL-M02). | T | Proposed |
| AVL-002 | The gateway's behaviour while its database is unavailable shall be measured. | [LGW 01 AVL-002] | — | — | — | Withdrawn: there is no database in the request path. |
| AVL-003 | While Entra ID cannot be reached, people already signed in shall keep working until their access-portal session ends, workloads shall be unaffected, and an alert shall be raised. | Sign-in depends on Entra; credentials do not [CMP §4.9, V-10]. Changed from LGW. | Must | Launch gate V-10 passes. | T | Proposed |
| AVL-004 | While the licence endpoint cannot be reached, a restarted gateway instance shall still serve requests. | [LGW 01 AVL-004] | — | — | — | Withdrawn: there is no licensed software. |
| AVL-005 | Loss of one availability zone in Tokyo shall not stop the service. | [LGW 01 AVL-005] | — | — | — | Withdrawn: every component is a regional AWS service; nothing of ours is zonal. |
| AVL-006 | When the shared counter store is unavailable, an alert shall be raised. | [LGW 01 AVL-006] | — | — | — | Withdrawn: replaced by AVL-007. |
| AVL-007 | If the spend guard or any other platform component fails, model calls shall continue, enforcement shall stay at its last state, and an alert shall be raised within 15 minutes. | Nothing of ours is in the request path (G-7, D-1) | Must | Launch gate V-14 passes, including its failure case. | T | Proposed |

### 7.5 Performance and capacity (PRF)

| ID | Metric | Target | Measurement (window, point, method) | Conditions and exclusions | Priority | Verif. | Status |
|---|---|---|---|---|---|---|---|
| PRF-M01 | Added latency to first token from anything the platform runs | 0 ms: nothing of ours is in the request path | Comparison of time to first token from the same client with and without the platform's policies attached; p95 over a load test | At the throughput in PRF-M02 with a streaming mix | Should | T | Proposed |
| PRF-M02 | Sustained throughput | TBD (Product owner, 2026-12-18); sizing basis 50–200 RPS [CMP A-9] | Load test against Bedrock for 1 hour with no throttling below the target | Bedrock quotas per account, Region and model (02 §9) | Must | T | Proposed |
| PRF-M03 | Maximum request duration | At least 570 s [CMP §2.7, §4.9] | From the client's request to the last byte of the response | Long agent turns, including a long silence before the first token; client and SDK read timeouts in 04 §4.3 | Must | T | Proposed |
| PRF-M04 | Concurrent streams | TBD (Product owner, 2026-12-18); sizing basis about 300 concurrent users at peak [CMP A-9] | Open streams held during a load test | Streaming responses | Must | T | Proposed |

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| PRF-001 | A streamed call that lasts up to the maximum request duration (PRF-M03), including a long silence before the first token, shall complete without any layer cutting it, also while a policy or spend guard deployment is in progress. | Reasoning models can be silent for minutes before the first token [CMP §2.7] | Must | A streamed call with 300 s before its first token and 550 s in total completes from Claude Code and from the AWS SDK with the timeouts in 04 §4.3; a deployment started during it does not cut it. | T | Proposed |

### 7.6 Observability and audit (OBS)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| OBS-001 | Every change to access (group-to-permission-set assignments, permission sets, IAM policies, roles, trust anchors, enrolments, budgets, and spend guard suspensions) shall be recorded with who did it and when, and delivered to the SIEM. | Access changes must be auditable [CMP §2.3.5, §4.7]. Changed from LGW: CloudTrail, not an application audit log. | Must | Each change, made in staging, appears in the SIEM naming the actor, within TBD (Security, 2026-12-18). | T | Proposed |
| OBS-002 | For every model call, the gateway shall record the principal, model, Region, source IP, user agent, time and result, with no content, and for streaming calls the input and output tokens. | Metadata is the audit record [CMP A-10, §4.3]. Changed from LGW: CloudTrail; non-streaming calls have no per-call tokens (R-1). | Must | Each call in a test produces one CloudTrail record with every field, and V-1 finds no content in it. | T | Proposed |
| OBS-003 | Spend, tokens, remaining budget and failures shall be available per team and per person on dashboards, and latency and throttling per model. | [CMP §2.4]. Changed from LGW: per person, not per key; latency per model only. | Should | A dashboard shows each metric for a chosen team and person, and per model. | D | Proposed |
| OBS-004 | CloudTrail, network flow and secure web gateway logs for the gateway's traffic shall be delivered to the SIEM, stored in Japan. | [CMP §4.7, §2.5] | Must | A sample event of each type is found in the SIEM. | I, T | Proposed |
| OBS-005 | When one person's credentials are used from several source IPs or user agents at once, an alert shall be raised. | Detects copied credentials and sharing [CMP §2.3.3, §8.8] | Should | Using one test session's credentials from two user agents and two IPs raises the alert. | T | Proposed |
| OBS-006 | An alert shall be raised when the spend guard, SCIM provisioning, Entra sign-in to IAM Identity Center, the delivery of CloudTrail events to EventBridge, or the CUR refresh fails. | Each is a known failure mode (02 §9) | Must | Each failure, caused in staging, raises its alert. | T | Proposed |
| OBS-007 | Every operator and break-glass action in the gateway's AWS accounts shall be recorded in an audit trail delivered to the SIEM, and reviewed on a schedule. | Operator access is the most powerful path [CMP §2.9] | Must | A sample console action appears in the SIEM; the review schedule is recorded (TBD (Security, 2026-12-18)). | T, I | Proposed |
| OBS-008 | A workload role shall work only from the egress IPs registered for its workload, and every denied use from elsewhere shall raise an alert. | Changed from LGW: IAM can bind a role to a source IP, which LiteLLM could not [LGW 02 R-57] | Must | A call with a test workload role from an office IP is denied and raises the alert. | T | Proposed |
| OBS-009 | Every database session that a person opens on the gateway database shall be recorded. | [LGW 01 OBS-009] | — | — | — | Withdrawn: there is no database that people open; the spend guard's table is read through IAM, and every change to it comes from the guard. |
| OBS-010 | An access inventory shall show, for every principal that can call a model, its owner, team, model tier, credential lifetime, certificate expiry, last use and month-to-date spend, refreshed daily and reviewed monthly by Security. | The key-lifecycle view of [LGW], for principals instead of keys (D-14) | Should | The inventory lists every permission set and workload role in production with every field; the review is recorded. | I | Proposed |

### 7.7 Operability (OPS)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| OPS-001 | A change to a security-critical policy or setting (04 §4.2) shall reach production only after the launch gates that verify it pass on staging, and every gate shall be re-run quarterly and when AWS announces a change to a behaviour that a gate depends on. | Launch gates are valid only for the behaviour they ran on [CMP §2.10]. Changed from LGW: no software upgrades of ours. | Must | The release record of each such change links a passing gate result dated after the change reached staging; the quarterly runs are recorded. | I | Proposed |
| OPS-002 | All gateway infrastructure, IAM policies, SCPs, permission sets and assignments shall be deployed from infrastructure as code. | Osaka and every environment are built from the same code [CMP §4.9] | Must | A plan against each environment shows no drift; no resource lacks an IaC owner. | I | Proposed |
| OPS-003 | Production changes to teams, tiers, budgets, workload roles and enrolments shall be made through the CI pipeline. | [CMP §2.3, §2.9] | Should | CloudTrail for a month shows no such change in production made outside the CI role. | I | Proposed |
| OPS-004 | Gate V-11 shall be re-run after every change to egress NAT, guest networks or the network list. | [CMP V-11] | Must | Each network change record links a V-11 result dated after the change. | I | Proposed |
| OPS-005 | When an office or DC egress IP changes, the network list in the IAM policies shall be updated before the change takes effect. | Otherwise users are locked out [CMP A-14] | Must | Each egress change record shows the policy update deployed before the cutover. | I | Proposed |
| OPS-006 | Production incidents shall be handled within support hours of TBD (Product owner, 2026-12-18) (Q-6). | Service commitment (00 §1.4) | Must | The on-call rota covers the agreed hours. | I | Proposed |
| OPS-007 | A DR drill shall be run before launch, and then at least every TBD (Product owner, 2026-12-18). | DR must be proven, not assumed [CMP §4.9] | Must | A drill record exists before launch and within each later interval. | I | Proposed |
| OPS-008 | Changes to the secure web gateway rules for AWS hostnames, and to the private path if adopted, shall follow the gateway's change process. | They are owned by another team [CMP §4.9] | Should | Each such change has a gateway change record. | I | Proposed |
| OPS-009 | The model allowlist in the SCP and in every permission policy shall be generated from the catalog in Git, and a drift check shall run daily. | One source of truth for which models are allowed (MDL-104) | Should | Editing a policy by hand in staging is reported by the next drift check. | T | Proposed |
| OPS-010 | Operators shall be able to remove the spend guard's denials without the spend guard, and every such use shall alert Security. | The guard can deny everyone if it fails wrongly (UC-12) | Should | In a drill, an operator clears the deny policy through the documented break-glass path (07 §6), calls succeed again, and Security is alerted. | D | Proposed |

### 7.8 Compliance (REG)

| ID | Requirement | Rationale / source | Priority | Acceptance criteria | Verif. | Status |
|---|---|---|---|---|---|---|
| REG-001 | The gateway shall allow calls only to model providers that legal and security have approved in writing for in-Japan processing. | External providers are not allowed by default [CMP A-7] | Must | Every model in the catalog has a written approval on file; an inspection of the generated allowlist finds none without one. | I | Proposed |
| REG-002 | Provider abuse monitoring for every model shall store data only in Japan, and legal/privacy shall decide in writing whether human review from outside Japan is acceptable before a model that allows it is used. | [CMP A-12, §2.5] | Should | A written decision exists for each model provider. | I | Proposed |
| REG-003 | The retention periods in §8 shall be approved by legal/privacy and FinOps. | [CMP §4.7, §2.8] | Must | §8 has no TBD, and its approval is recorded in §11. | I | Proposed |
| REG-004 | Before first use, each user shall accept an acceptable-use policy that forbids sharing credentials. | Each person's credentials must be used only by them [CMP §2.3.3] | Should | Sign-in to IAM Identity Center is possible only for users with a recorded acceptance of the Entra Terms of Use. | I | Proposed |

## 8. Data classification and retention

The classification scheme and the open retention periods are Q-9.

| Data item | Contains prompt content? | Classification | Store (logical) | Retention | Who can read | Residency |
|---|---|---|---|---|---|---|
| CloudTrail model-call events (principal, model, source IP, user agent, tokens for streams) | No: checked by V-1 | TBD (Legal / privacy, 2026-12-18) | Organization trail in the log-archive account, and the SIEM | 7 years [CMP §4.7]; to be confirmed for per-person data: TBD (Legal / privacy, 2026-12-18) | Security / SOC | Japan |
| Spend guard counters (per person, team, workload and month) | No | TBD (Legal / privacy, 2026-12-18) | DynamoDB table in `llm-prod`, Tokyo, replicated to Osaka | 13 months, by item expiry: TBD (FinOps, 2026-12-18) | The person (own rows), team leads per PRV-003, FinOps, platform operators | Japan |
| CUR 2.0 export with IAM principal data (cost per person and per role) | No | TBD (Legal / privacy, 2026-12-18) | Billing export bucket and Athena tables | TBD (FinOps, 2026-12-18) | FinOps; per-person rows only as PRV-003 allows | Japan |
| Opt-in content log | Yes | TBD (Legal / privacy, 2026-12-18) | Bedrock invocation logging in the approved team's own account, to an S3 bucket in Tokyo (D-11) (Q-10) | Per team's legal requirement; 30 days if none is set [CMP §4.7] | TBD (Legal / privacy, 2026-12-18) | Japan |
| Responses stored by the Responses API | Yes | n/a: must not exist (PRV-005) | Bedrock, if a client leaves storage on | n/a: V-16 proves none is kept | — | Japan |
| Audit log (access changes, operator actions) | No | TBD (Legal / privacy, 2026-12-18) | Immutable archive in the log-archive account, and the SIEM | 7 years [CMP §4.7] | Security / SOC | Japan |
| Network logs (VPC Flow Logs for the private path, secure web gateway logs) | No | TBD (Legal / privacy, 2026-12-18) | Log service, then archive | 90 days hot, then archived for TBD (Security, 2026-12-18) [CMP §4.7] | Security / SOC, Network | Japan |
| Access inventory snapshots | No | TBD (Legal / privacy, 2026-12-18) | S3 bucket in `llm-prod`, read by Quick Sight | 13 months: TBD (Security, 2026-12-18) | Security / SOC, platform operators | Japan |
| Gateway configuration (teams, tiers, budgets, catalog, prices, workloads) | No | TBD (Legal / privacy, 2026-12-18) | Git repository, and the configuration bucket the spend guard reads | Life of the platform | Platform engineering; everyone for the catalog | Japan for the bucket; the Git host is Q-20 |

## 9. Open questions

Due dates are proposed and are confirmed in review. Design-level open items are in 02 §14. Q-1 to Q-21 keep the numbers of [LGW 01 §9].

| ID | Question | Blocks | Owner | Due | Resolution |
|---|---|---|---|---|---|
| Q-1 | Who fills each role in 00 §1.3, under which team name, and with which contact details in 11 §C? Who owns and approves each document? | 00 Document control, 00 §1.3, 11 §C, this header | Product owner | 2026-12-18 | Open |
| Q-2 | What do engineers and workloads use today (direct provider accounts, personal API keys, Bedrock in their own accounts, nothing), and what will the gateway replace? | §1.1, 00 §1 | Product owner | 2026-12-18 | Open |
| Q-3 | Which teams are in the pilot, and what are the target dates for the pilot and general availability? | §1.4 | Product owner | 2026-12-18 | Open |
| Q-4 | Which catalog models (§6.5) are needed, by which phase and at which priority? Are OpenAI models required, and does Bedrock offer any of them processed only in Japan? | §6.5, MDL-010, MDL-011 | Product owner | 2026-12-18 | Open |
| Q-5 | Which optional capabilities are in the first phase: embeddings (FUN-004), any NG-7 feature? | NG-7, FUN-004 | Product owner | 2026-12-18 | Open |
| Q-6 | What are the service levels: the availability target and what counts as down, whether Bedrock outages are excluded, RTO and RPO targets, support hours, and the DR drill interval? | AVL-M01 to AVL-M03, OPS-006, OPS-007, 00 §1.4 | Product owner | 2026-12-18 | Open |
| Q-7 | What are the performance targets: throughput, concurrent streams, and expected growth at 12 and 24 months? They set the Bedrock quotas to request. | PRF-M02, PRF-M04 | Product owner | 2026-12-18 | Open |
| Q-8 | Security timings: how soon after an Entra account is disabled, or a team membership removed, must the user's credentials stop working; how soon must access changes reach the SIEM; how often are audit events and operator activity reviewed? | IAM-006, TEN-004, TEN-007, OBS-001, OBS-007, 02 §4.5 | Security / SOC | 2026-12-18 | Open |
| Q-9 | What is the classification of each data item in §8, the retention of each, and who may read per-person data, including whether team members may see each other's usage, and who may read the per-person lines in CUR 2.0? | §8, PRV-003, REG-003, IAM-010 | Legal / privacy | 2026-12-18 | Open |
| Q-10 | Is per-team content logging needed in this phase? If so, which teams, who approves, and what retention applies? | PRV-002, D-11 | Legal / privacy | 2026-12-18 | Open |
| Q-11 | Does legal confirm the residency scope in A-11 and the abuse-monitoring position in A-12? | AS-11, AS-12, REG-002 | Legal / privacy | 2026-12-18 | Open |
| Q-12 | Chargeback rules: is the team that a person chooses per session (TEN-009) acceptable for chargeback; the V-4 tolerance between the spend guard's estimate and CUR; the investigation threshold for unattributed cost; how fixed platform costs are allocated; how teams map to departments; and the overshoot bound in the budget policy. | CST-001, CST-004, CST-008, CST-009, CST-011, TEN-009 | FinOps | 2026-12-18 | Open |
| Q-13 | Guardrails: does Security accept no guardrail in the request path for Japanese text (D-10)? If not, which option in D-10 applies, and should a Classic-tier Bedrock guardrail be enforced for some OUs? | SEC-008, SEC-009, NG-11 | Security / SOC | 2026-12-18 | Open |
| Q-14 | Network: which office and DC egress CIDRs go on the network list and who owns each (A-14); can A-16 be confirmed; can the Bedrock and Identity Center hostnames be exempted from TLS inspection and allowed by FQDN (A-15); which dedicated egress IPs will DC workloads use? | SEC-001, SEC-002, SEC-005, AS-14 to AS-16 | Network | 2026-12-18 | Open |
| Q-15 | Identity: are AS-1 to AS-3, AS-21 and AS-22 confirmed; is External MFA (EAM) with Okta enabled in our tenant; which phishing-resistant methods do operators use; and which sign-in frequency, within 4–8 hours, applies to everyone? | AS-1 to AS-3, AS-21, AS-22, IAM-003, IAM-007, IAM-011 | Identity | 2026-12-18 | Open |
| Q-16 | Can Intune deploy the `llm` helper and the settings for Claude Code and Codex CLI, and which client telemetry can be turned off? | AS-20, FUN-009, RES-006 | Endpoint / Intune | 2026-12-18 | Open |
| Q-17 | Is the LiteLLM Enterprise licence bought? | [LGW 01 Q-17] | Product owner | — | Withdrawn: no LiteLLM |
| Q-18 | Does an internal AI use policy and an acceptable-use policy exist that forbid sharing credentials? Where are they published? May `llm login` be used on servers, shared development VMs or CI jobs, or only on the owner's managed device? | REG-004, 11 §B | Legal / privacy | 2026-12-18 | Open |
| Q-19 | Which compliance frameworks (for example ISO 27001, SOC 2) apply to the gateway? | 02 §8.2 | Security / SOC | 2026-12-18 | Open |
| Q-20 | Which AWS Support plan covers the gateway, which help desk gives first-line support, which issue tracker and Git host are used? | 11 §B, 11 §C | Product owner | 2027-01-29 | Open |
| Q-21 | May contractors and B2B guest accounts use the gateway? If so, is compliant-device trust from their home tenant accepted, and are they provisioned to IAM Identity Center? | IAM-001, 02 §4.6 | Identity | 2026-12-18 | Open |
| Q-22 | How many teams are there, and is one permission set per team acceptable within the IAM Identity Center quotas (AS-26)? If not, which Entra user attribute holds a person's team? | AS-26, TEN-004, D-2 | Identity | 2026-12-18 | Open |
| Q-23 | What are the default team budget, the per-person monthly cap, the runaway threshold and suspension period, and the target enforcement delay for streaming calls? | CST-002, CST-009, CST-012, CST-013 | FinOps, with Security / SOC | 2026-12-18 | Open |
| Q-24 | Is the private path (Route A) adopted for general availability (D-6), given AS-8 and the cost of interface endpoints? | SEC-014, RES-007, NG-5 | Network | 2027-01-29 | Open |
| Q-25 | Which AWS accounts outside `llm-prod` may call Bedrock directly (enrolment), who approves an enrolment, and who owns each enrolled account's budget? | UC-13, CST-014, D-4 | Cloud platform, with FinOps | 2026-12-18 | Open |
| Q-26 | Is an exploration sandbox with long-term Bedrock API keys wanted (D-3)? If so, which users, data rules and key lifetime apply? | NG-9, IAM-015 | Security / SOC | 2027-01-29 | Open |
| Q-27 | Are IDE plugins that accept only a pasted key in scope, given that the key lasts at most the 1-hour session (R-20)? | FUN-009, IAM-016 | Product owner | 2026-12-18 | Open |

## 10. Traceability

The traceability matrix is kept in 02 §11.3, built from the Satisfies line and columns of each design section. Approval of 02 requires:
- every Must requirement maps to at least one design section and at least one test or launch gate;
- every launch gate in [CMP §2.10] maps to at least one requirement here, or is marked n/a in 02 §11.2 with a reason.

## 11. Change control

- Changes after approval go through a pull request that updates the Version, the change log, and any affected design and test references in the same PR.
- A change to a Must requirement, a constraint, or an assumption that turns out false needs the approvers listed in the header.

| Version | Date | Author | Change | Approved by |
|---|---|---|---|---|
| 0.1 | 2026-11-20 | Claude (AI assistant), for platform engineering | Initial draft: REQ-GW 0.2 [LGW 01] restated for a design with no gateway in the request path; IDs kept where the meaning is the same; IAM-012, CST-003, SEC-006, SEC-007, SEC-010, SEC-011, SEC-013, SEC-017, AVL-002, AVL-004 to AVL-006 and OBS-009 withdrawn; SEC-008 and SEC-009 deferred; IAM-015, IAM-016, TEN-009, CST-012 to CST-014, RES-008, PRV-005, SEC-021, SEC-022, AVL-007, OBS-010, OPS-009, OPS-010, AS-23 to AS-27, NG-9 to NG-12, UC-13, UC-14 and Q-22 to Q-27 added | — |

## 12. Glossary

Terms are defined in 11 §A. Add a new term there in the same pull request as the requirement that uses it. Changing the meaning of a term used here is a change to this document (§11).
