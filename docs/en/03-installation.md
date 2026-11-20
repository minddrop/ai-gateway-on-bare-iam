# IAM-native LLM gateway: Installation and setup

<!--
Answers: how a new engineer goes from nothing to (a) a working sign-in and model call in a development account and (b) a new AWS environment.
Reader: a new team member who has been given access but has no history with this system.
Owns: prerequisites, the environment list, one-time setup and teardown. Refers to: policy and setting values (04), day-to-day deploys (07 §1), design (02).
Detail: every step is one action, then a Run: line with the exact command or console path, then an Expect: line with the result. Have someone new follow it word for word, and record the date in the status line.
Status: stub written during design. There is no local stack: there is no server to run locally. Steps keep [fill] markers for what is decided during the build.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last tested end to end: [fill: YYYY-MM-DD] by [fill: name], with client package [fill: version]

## 1. Prerequisites

| Requirement | Version | Notes / how to get it |
|---|---|---|
| [fill: Terraform or CDK] | [fill: x.y] | Pinned in [fill: file] (02 R-24) |
| AWS CLI v2 | [fill: x.y or later] | Sign in with IAM Identity Center (`aws sso login`), never long-lived keys; the SCP denies model calls by IAM users |
| Python | [fill: x.y] | Spend guard functions, launch-gate and smoke-test scripts |
| `llm` helper | [fill: version] | From the client package (09 §1) |
| Claude Code, Codex CLI | 02 §1.3 | For client tests |
| Access: repository | — | [fill: who grants it] |
| Access: AWS accounts | — | `LLM-Admin` on `llm-dev` and `llm-staging` through the `llm-admins` group; `LLM-ReadOnly` on production; [fill: who approves] |
| Access: management account | — | Cloud platform only, for SCPs, IAM Identity Center and CUR; changes through CI |
| Access: Entra app for IAM Identity Center | — | [fill: who can change SAML, SCIM and Conditional Access] |

## 2. Environments

| Environment | URL | AWS account / region | Purpose | Deployed from | Models |
|---|---|---|---|---|---|
| Local | n/a: there is no local stack; developers use `llm-dev` | — | — | — | — |
| Dev | Access portal [fill] | `llm-dev` / ap-northeast-1 | Integration, spend guard development | `main` | [fill: a small tier; no real company data] |
| Staging | Access portal [fill] | `llm-staging` / ap-northeast-1 | Pre-release, launch gates | [default: release tag] | Same as production |
| Production | Access portal [fill] | `llm-prod` / ap-northeast-1 | Live | [default: release tag] | The catalog in 01 §6.5 |
| DR | Access portal, Osaka replica (R-35) | `llm-prod` / ap-northeast-3 | Warm DR | Same tag as production | Those available in Osaka (02 §9) |

## 3. First call from a development account

<!-- Calls from dev must not send real company data to a model. -->

1. **Install the client package.**
   - Run: [fill: package install command, or Company Portal path]
   - Expect: `llm --version` prints [fill: version].
2. **Sign in.**
   - Run: `llm login --env dev`
   - Expect: a browser opens Entra; after MFA, `llm login` prints your teams in `llm-dev` and writes the `llm` profile.
3. **Check your identity.**
   - Run: `aws sts get-caller-identity --profile llm`
   - Expect: an ARN of the form `arn:aws:sts::<llm-dev>:assumed-role/AWSReservedSSO_LLM-Team-<team>_<suffix>/<your user name>`.
4. **Call a model.**
   - Run: `aws bedrock-runtime converse --profile llm --model-id <dev model ID from 04 §4.1> --messages '[{"role":"user","content":[{"text":"Say hello"}]}]'`
   - Expect: a JSON response with `"stopReason": "end_turn"`.
5. **See the call metered.**
   - Run: `llm usage --env dev`
   - Expect: [fill: within the enforcement delay (04 §4.4), one call and its estimated cost for today].

## 4. New AWS environment

<!-- One-time bootstrap. Day-to-day deploys are in 07 §1. -->

1. **Account and guardrails.** Create the account in the right OU, and confirm that `scp-llm-baseline` and the landing zone's Region-deny SCP are attached. SCPs do not apply to the management account, so no model calls are made there.
   - Run: `aws organizations list-policies-for-target --target-id <account ID> --filter SERVICE_CONTROL_POLICY`, from the management account
   - Expect: both SCPs are listed.
2. **Model check.** For every catalog model, confirm the Japan-only destinations from each source Region.
   - Run: `aws bedrock get-inference-profile --inference-profile-identifier <jp. profile ID> --region ap-northeast-1` (and `--region ap-northeast-3`)
   - Expect: only `ap-northeast-1` and `ap-northeast-3` models; record the date in `models.yaml` (MDL-104).
3. **Quotas.** Request Bedrock TPM and RPM increases to the capacity plan (02 §9), in Tokyo and in Osaka, for `bedrock-runtime` and, where used, `bedrock-mantle`.
   - Run: the Service Quotas console, or `aws service-quotas request-service-quota-increase` for each quota
   - Expect: [fill: where the approved values are recorded]
4. **Network prerequisites.** Get the office and DC egress CIDRs from Network [CMP A-14], and confirm the TLS-inspection exemption and FQDN allow rules for the hostnames in 02 §6 [CMP A-15].
   - Run: [fill: how to request them from the network team]
   - Expect: the CIDRs are in [fill: IaC variable file]; the exemption request is closed as done.
5. **IAM Identity Center.** Confirm SAML and SCIM from Entra, the 8-hour session, replication to Osaka, and the Conditional Access set in 02 §4.4.
   - Run: IAM Identity Center console → Settings; Entra admin center → Enterprise applications → [fill: app name] → Provisioning
   - Expect: identity source "External identity provider"; provisioning "Automatic" with a recent successful cycle; session duration 8 hours; Regions Tokyo and Osaka.
6. **Infrastructure.** Apply the IaC: permission sets and assignments, `llm-guard-deny`, Roles Anywhere, spend guard, usage API, dashboards, budgets.
   - Run: `[fill: IaC command]` with `[fill: environment variable file]`
   - Expect: the apply finishes without errors, and a second plan shows no changes.
7. **CloudTrail to EventBridge.** Confirm that the metering rule is in the state that receives read-only management events.
   - Run: `aws events describe-rule --name llm-meter-bedrock --region ap-northeast-1`
   - Expect: `"State": "ENABLED_WITH_ALL_CLOUDTRAIL_MANAGEMENT_EVENTS"`.
8. **CUR 2.0.** Confirm the data export with IAM principal data, delivering to the billing bucket in Tokyo.
   - Run: `aws bcm-data-exports get-export --export-arn <export ARN>`, from the management account
   - Expect: [fill: the field that shows caller identity allocation data is included], destination bucket in `ap-northeast-1`.
9. **Post-install checks.**
   - Run: the smoke tests (`[fill: smoke test command]`), then the launch gates (02 §11.2).
   - Expect: a call from a listed IP succeeds and is metered; a call from outside the list is denied; a `global.` profile is denied; every launch gate passes before any real user is given access.

## 5. Teardown

<!-- Teardown is where residency and retention obligations are easiest to break. -->

1. **Record retained data.** Data under retention (CloudTrail under Object Lock, CUR exports, the access inventory) cannot be deleted early.
   - Run: [fill: where the record is kept]
   - Expect: the record names each bucket, the date its retention ends, and the team that owns it after teardown.
2. **Remove access.** Remove the assignments of the `llm-team-*` groups to the permission sets, then the permission sets; remove the Intune client configuration.
   - Run: [fill: IaC change]
   - Expect: `llm login` shows no teams for a test user.
3. **Remove workload access.** Revoke the workload certificates, then delete the Roles Anywhere profiles, trust anchors and workload roles; remove the account from the enrolment list.
   - Run: [fill: IaC change]
   - Expect: a test workload's `aws_signing_helper` fails to get credentials.
4. **Remove network entries.** Remove the Route A endpoints and DNS forwarding, if built; ask Network to remove the secure web gateway rules.
   - Run: [fill: request to the network team; IaC change]
   - Expect: [fill]
5. **Confirm nothing is left.**
   - Run: [fill: Cost Explorer filter or CUR query on the account]
   - Expect: no Bedrock charges for the account after [fill: number of days].
