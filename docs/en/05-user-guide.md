# IAM-native LLM gateway: User guide

<!--
Answers: how an engineer or a team lead gets access and does their job with the gateway.
Reader: engineers and team leads. Write in their words, organised by task, not by screen.
Owns: the rules on what may be sent, roles as users see them, tool setup, user tasks, notifications. Refers to: limits, session lengths and model IDs (04), API details (06), problems (08), notice periods (10 §1), contact details (11 §C).
Detail: every task in §5 follows the block template there, and a user can complete it without asking anyone. Client setup that Intune pushes says so: most users should have nothing to configure.
Status: stub written during design; [fill] markers are completed during the build and the pilot.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last reviewed: [fill: YYYY-MM-DD], for release [fill: version]

## 1. Getting started

- **Who can use it:** employees in an `llm-team-*` group, on the corporate network [CMP A-13].
- **How to get access:** ask your team lead to add you to your team's group in Entra; [fill: request process and approver]. Access appears after the next provisioning cycle, usually within [fill: minutes].
- **Which team you are charged to:** the team whose access you use. If you are in several teams, `llm team <name>` chooses one; your tools then charge that team until you switch (01 TEN-009).
- **Signing in:** `llm login` once a day. Your tools renew their credentials by themselves every hour; after 8 hours, or on a new day, a browser opens for Entra and Okta Verify again.
- **First thing to try:** open Claude Code in a repository and ask it to explain a file; expect a response within seconds.

## 2. What you may and may not send

<!-- Short, plain rules. Link to the internal AI use policy (11 §B). -->

- **Allowed:** [fill: source code, internal documents up to classification …]
- **Not allowed:** [fill: secrets and credentials, customer personal data unless your team is approved for it, …]
- **What is recorded:** who called which model, when, from where, and how many tokens, and the cost. Prompt and response text are not stored unless your team has opted in to content logging [CMP A-10].
- **Guardrails:** nothing screens your prompts before the model (02 D-10). You are responsible for not sending what the policy forbids.

## 3. Roles and permissions

| Role | Can do | Cannot do |
|---|---|---|
| User | Call the models of their team's tier; see their own usage (`llm usage`) | Create keys for others; change budgets; call models outside their tier or from outside the corporate network |
| Team lead | As user; see the team's spend in `llm usage --team` and in Quick Sight; ask for workload access, budget and tier changes by pull request | Raise their own budget; change anything directly |
| Operator (platform on-call) | Read everything except content; suspend or restore a person, team or workload | Change policies, teams or budgets outside CI; read prompt content (it is not stored) |

## 4. Set up your tools

| Tool | How it is configured | What you need to do | Reference |
|---|---|---|---|
| Claude Code | Bedrock mode with AWS profile `llm`; `awsAuthRefresh` runs `llm login`; pushed by Intune | Nothing beyond `llm login` | 04 §4.5 |
| Codex CLI | `amazon-bedrock` provider with AWS profile `llm`; pushed by Intune | Nothing beyond `llm login`; available once approved (04 §5) | 04 §4.5 |
| SDKs (AWS, Anthropic Bedrock client, OpenAI) | AWS profile `llm`, Region from the profile | [fill: code snippet per SDK] | 06 §2 |
| IDE plugins with Bedrock support | AWS profile `llm` | Choose "AWS profile" in the plugin's settings | [fill: list of tested plugins] |
| Tools that accept only a pasted key | Short-term key from `llm token`; it lasts at most the rest of your 1-hour session (01 Q-27) | Run `llm token` and paste the result | 04 §4.4 |
| DC workloads | IAM Roles Anywhere certificate and `aws_signing_helper` | Follow §5.2 | 06 §2 |

## 5. Tasks

Each task uses this block. Copy it for a new task, and keep every field.

```markdown
### 5.n <Task, starting with a verb>
- **Who:** <role from §3>
- **Before you start:** <what you need, or "Nothing">
- **Steps:**
  1. <action, with the exact link, command or form>
  2. <action>
- **Result:** <what you see when it worked, and how long it takes>
- **If something goes wrong:** <08 entry, or who to contact (11 §C)>
```

### 5.1 Check how much you or your team has spent
- **Who:** User, for their own usage; team lead, for the team
- **Before you start:** `llm login`
- **Steps:**
  1. Run `llm usage` (yourself) or `llm usage --team <team>` (team leads).
  2. For history and breakdowns, open the Quick Sight dashboard at [fill: link].
- **Result:** month-to-date spend against the budget or cap, by model; figures are estimates until the next CUR update, then billed amounts.
- **If something goes wrong:** 08 §1

### 5.2 Request access for a DC workload
- **Who:** Team lead
- **Before you start:** the workload name, owner, team, models, expected volume, egress IPs, and the host that will hold the certificate
- **Steps:**
  1. Open a pull request in [fill: configuration repository] adding the workload to `workloads.yaml`.
  2. After merge, CI creates the role, the budget and the certificate request; [fill: how the certificate reaches the host].
- **Result:** the workload gets 1-hour credentials with `aws_signing_helper` from its registered egress IPs only. Its certificate expires within 90 days and is renewed by [fill: certificate automation].
- **If something goes wrong:** [fill]

### 5.3 Request a new model
- **Who:** Team lead
- **Before you start:** the model, the use case and the expected volume
- **Steps:**
  1. Open a ticket in [fill: queue] with the details above.
  2. The platform team checks Japan processing and the legal position [CMP A-7], then adds the model to `models.yaml`.
- **Result:** the model appears in `llm models` and in the release notes (10).
- **If something goes wrong:** [fill]

### 5.4 Request a budget increase
- **Who:** Team lead
- **Before you start:** the new amount and the reason; FinOps approval if above [fill: threshold]
- **Steps:**
  1. Open a pull request changing the team's budget in `teams.yaml`.
- **Result:** after merge, the spend guard uses the new budget, and a suspension for budget is lifted within the enforcement delay (04 §4.4).
- **If something goes wrong:** [fill]

### 5.5 Switch team, or leave a team or the company
- **Who:** Any user, and their team lead
- **Before you start:** Nothing
- **Steps:**
  1. To charge another of your teams: run `llm team <name>`, then restart your tools.
  2. To leave a team: your team lead removes you from the team's Entra group.
- **Result:** after leaving a team, you can no longer use its access, and credentials you already have for it stop within the target in 01 Q-8. When your Entra account is disabled, all your access stops within the same target.
- **If something goes wrong:** [fill]

### 5.6 Move to Osaka during a Tokyo outage
- **Who:** Any user, when the status channel says so
- **Before you start:** Nothing
- **Steps:**
  1. Run `llm region osaka`.
  2. Restart Claude Code and Codex CLI.
- **Result:** your tools call Bedrock in Osaka; some models are not available there (01 §6.5). Run `llm region tokyo` when told.
- **If something goes wrong:** 08 §1

## 6. Notifications

| Notification | When | Sent to | Channel |
|---|---|---|---|
| Budget threshold | At 80 % and 100 % of the team budget | Team leads | [fill: email / chat] |
| Per-person cap reached, or runaway stop | When the spend guard suspends you | You, and on-call for runaway stops | [fill] |
| Workload certificate expiry | [fill: number of days before] | Workload owner | [fill] |
| Model retirement or default model change | The notice period in 10 §1 | All users of the model | Release notes and email |

## 7. Limits and good practice

- **Maximum request duration:** 01 PRF-M03; tool timeouts in 04 §4.3.
- **Budgets, caps and runaway stops:** 04 §4.4. There are no per-person rate limits; a runaway agent is suspended for a short period.
- Prefer prompt caching where the tool supports it; it lowers cost.
- Do not share your credentials or short-term keys; they name you in every log.
