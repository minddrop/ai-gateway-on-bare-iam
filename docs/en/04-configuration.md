# IAM-native LLM gateway: Configuration reference

<!--
Answers: every policy and setting the gateway depends on, where it comes from, its value per environment, and what breaks if it is wrong.
Reader: platform engineers changing configuration, reviewers of configuration PRs, on-call engineers checking a value.
Owns: policy text, setting names and values, including session lengths, budgets, thresholds, model configuration and client settings. Refers to: the reasons behind them (02), the environment list (03 §2). The config repository is the source of truth: link to the file rather than pasting it whole once it exists.
Detail: every row names the exact key or policy statement. Settings marked security-critical name the launch gate that proves them (§4.2), and that gate runs again after every change to them.
Status: stub written during design. The policy text in §4.2 is the design's intent; it becomes the source in the repository during the build.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last reviewed: [fill: YYYY-MM-DD], for release [fill: version]

## 1. How configuration is loaded

| Source | Holds | Changed by | Takes effect |
|---|---|---|---|
| `teams.yaml` (in [fill: repo path]) | Teams: Entra group, tier, monthly budget, leads, department, cost centre, Codex CLI approval. Team names use only lower-case letters, digits and hyphens, so that the role name pattern `AWSReservedSSO_LLM-Team-<team>_*` in `llm-guard-deny` cannot match another team | Pull request; CI generates permission sets, assignments and the spend guard's configuration | On deploy; IAM changes after propagation (seconds) |
| `models.yaml` | Catalog: model IDs, tier, prices per token (including cache), Regions, approval reference, Japan check record | Pull request; CI generates the model lists in permission policies and the client defaults (02 OPS-009) | On deploy |
| `workloads.yaml` | DC workloads: team, owner, egress CIDRs, model list, budget, certificate subject; enrolled AWS accounts and their owners | Pull request | On deploy |
| IaC (in [fill: repo path]) | SCP, permission sets, roles, Roles Anywhere, spend guard, usage API, dashboards, budgets | Pull request | On deploy |
| Policy `llm-guard-deny` | Current suspensions | The spend guard; `llm-admin`; CI or break-glass to reset | Immediately, after IAM propagation |
| Client package (Intune) | `llm` helper, Claude Code managed settings, Codex CLI `config.toml` | Endpoint / Intune, from the client package release | On the next Intune sync; tools restarted |

**Precedence:** an explicit deny in any layer wins (02 §4.7). Between Git and the account, Git wins: the daily drift check reports any difference (OPS-009).

**Drift rule:** nothing in production is changed in the console. The only runtime changes are `llm-guard-deny` versions made by the spend guard or `llm-admin`, which are recorded in `llm-spend` and CloudTrail.

## 2. Parameters

| Name | Type | Required | Default | Description | Security-critical |
|---|---|---|---|---|---|
| Access portal start URL | string | Yes | — | `sso_start_url` written by `llm login` | No |
| `sso_region` / client Region | string | Yes | `ap-northeast-1` | Changed to `ap-northeast-3` by `llm region osaka` in DR (02 D-13) | No |
| `llm-prod` account ID | string | Yes | — | `sso_account_id` in the `llm` profile | No |
| Office and DC egress CIDRs | list | Yes | — | The network condition in every permission policy (§4.2); from Network, with an owner per CIDR (01 Q-14) | Yes |
| Route A VPC endpoint IDs | list | No | — | Added to the network condition when Route A is live (02 D-6) | Yes |
| Enrolled account IDs | list | Yes | — | The enrolment statement in the SCP | Yes |
| Spend guard active Region | string | Yes | `ap-northeast-1` | Where `llm-enforce` runs (02 D-13) | No |
| [fill: every other parameter, one per row] | [fill] | [fill] | [fill] | [fill] | [fill] |

### 2.1 Values per environment

<!-- One row per parameter in §2. The environments are those in 03 §2. -->

| Name | Local | Dev | Staging | Production | DR |
|---|---|---|---|---|---|
| Access portal start URL | n/a: no local stack | [fill] | [fill] | [fill] | The same URL; `sso_region` `ap-northeast-3` (R-35) |
| `llm-prod` account ID | n/a | [fill: `llm-dev`] | [fill: `llm-staging`] | [fill] | Same account |
| Office and DC egress CIDRs | n/a | [fill] | [fill] | [fill] | Same |
| Enrolled account IDs | n/a | [fill] | [fill] | [fill] | Same |
| [fill: every other parameter in §2] | [fill] | [fill] | [fill] | [fill] | [fill] |

## 3. Secrets

There are almost none: no API keys, no master key, no database password (02 D-3).

| Secret | Used for | Who can read it | Rotation | Runbook |
|---|---|---|---|---|
| Entra SCIM token for IAM Identity Center | Entra's provisioning to the Identity Store | Stored in Entra's provisioning configuration; created in the Identity Center console by Cloud platform | [default: before its 1-year expiry]; an alarm 30 days before | 07 §5 |
| SAML signing certificate (Entra app for IAM Identity Center) | Federation | Identity | [default: before expiry; Entra's certificate rollover] | 07 §5 |
| Private CA keys (workload certificates) | Signing workload certificates | Held by AWS Private CA; not readable | Per the CA's validity | 07 §5 |
| Break-glass IAM user credentials | 02 §4.3 | Vault holders (R-34) | After every use | 07 §6 |

Secrets are never committed. [fill: secret-scanning tool] runs on every push, with patterns for AWS access keys and Bedrock API keys (SEC-018).

## 4. Settings

### 4.1 Models

<!-- One row per catalog model. The design is in 02 §5.1; the catalog of what is needed is in 01 §6.5. -->

| Model ID (what clients send) | Backend model / profile | Region | Tier | Pricing source | Requirement |
|---|---|---|---|---|---|
| EXAMPLE: `jp.anthropic.claude-opus-5-5-<version>` | `jp.` system inference profile; destinations Tokyo and Osaka, checked with `GetInferenceProfile` on [fill: date] | ap-northeast-1 (ap-northeast-3 in DR) | premium | CUR; per-token prices for estimates in `models.yaml`, checked by V-4 | MDL-001 |
| [fill: one row per catalog model in 01 §6.5] | [fill] | [fill] | [fill] | [fill] | [fill] |

Models approved for Codex CLI (FUN-002): [fill: after T-002 (R-4)].

Default models in the managed client settings: [fill: Claude Code main and fast model IDs; Codex CLI model ID].

### 4.2 Security- and privacy-critical settings

<!-- A wrong value here leaks prompts or lets callers bypass controls. Each row names the launch gate that proves it. -->

| Setting | Section | Required value | Why | Verified by |
|---|---|---|---|---|
| `scp-llm-baseline` | SCP, attached at [fill: root or OUs] | The statements below, plus the landing zone's Region-deny statement | Residency, no long-term keys, no content logging (02 D-7) | V-2, V-12, T-028, T-039 |
| Permission policy of `LLM-Team-<team>` | Permission set inline policy, generated | The template below | Model tier and network condition (02 §4.7 L2) | V-12, T-040 |
| `llm-guard-deny` | Customer managed policy, attached to every `LLM-Team-*` permission set and workload role | The template below | Spend guard denials (02 D-8) | V-14 |
| Workload role permission policy | IAM role inline policy, generated | As the team template, with only the workload's models and its own egress CIDRs | OBS-008 | V-12, T-063 |
| Bedrock model invocation logging | Each account, each Region | Off, except in content-logging accounts (02 D-11) | No content at rest | V-1, T-039 |
| Responses API storage | Client setting, per client | Off (`store: false`) | PRV-005 | V-16 |
| `llm-platform-deploy` trust policy | IAM role | The CI system's OIDC provider, repository and protected branches only | SEC-012, SEC-021 | T-043, T-050 |
| Lambda code signing configuration | Spend guard and usage API functions | Enforce: reject unsigned code | SEC-016 | T-046 |

**`scp-llm-baseline`** (the LLM statements; the Region-deny statement is the landing zone's). The size must stay under the SCP limit (R-23). Action names are checked against the [Bedrock service authorization reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonbedrock.html) during the build.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyModelCallsExceptJpProfilesAndJapanModels",
      "Effect": "Deny",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
      "NotResource": [
        "arn:aws:bedrock:ap-northeast-1:*:inference-profile/jp.*",
        "arn:aws:bedrock:ap-northeast-3:*:inference-profile/jp.*",
        "arn:aws:bedrock:ap-northeast-1::foundation-model/*",
        "arn:aws:bedrock:ap-northeast-3::foundation-model/*"
      ]
    },
    {
      "Sid": "DenyModelCallsByIamUsers",
      "Effect": "Deny",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:CallWithBearerToken", "bedrock-mantle:*"],
      "Resource": "*",
      "Condition": {"ArnLike": {"aws:PrincipalArn": "arn:aws:iam::*:user/*"}}
    },
    {
      "Sid": "DenyCreatingBedrockApiKeys",
      "Effect": "Deny",
      "Action": "iam:CreateServiceSpecificCredential",
      "Resource": "*",
      "Condition": {"StringLike": {"iam:ServiceSpecificCredentialServiceName": "bedrock*"}}
    },
    {
      "Sid": "DenyLongTermBearerTokens",
      "Effect": "Deny",
      "Action": ["bedrock:CallWithBearerToken", "bedrock-mantle:CallWithBearerToken"],
      "Resource": "*",
      "Condition": {"StringEquals": {"bedrock:bearerTokenType": "LONG_TERM"}}
    },
    {
      "Sid": "DenyInvocationLoggingChangesExceptDeployRole",
      "Effect": "Deny",
      "Action": ["bedrock:PutModelInvocationLoggingConfiguration", "bedrock:DeleteModelInvocationLoggingConfiguration"],
      "Resource": "*",
      "Condition": {"ArnNotLike": {"aws:PrincipalArn": "arn:aws:iam::*:role/llm-platform-deploy"}}
    },
    {
      "Sid": "DenyModelCallsFromAccountsNotEnrolled",
      "Effect": "Deny",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:CallWithBearerToken", "bedrock-mantle:CreateInference"],
      "Resource": "*",
      "Condition": {"StringNotEquals": {"aws:PrincipalAccount": ["<llm-prod>", "<llm-staging>", "<llm-dev>", "<each enrolled account>"]}}
    },
    {
      "Sid": "DenyBedrockFeaturesOutOfScope",
      "Effect": "Deny",
      "Action": [
        "bedrock:CreateModelInvocationJob", "bedrock:StartAsyncInvoke",
        "bedrock:CreateModelCustomizationJob", "bedrock:CreateProvisionedModelThroughput",
        "bedrock:CreateInferenceProfile",
        "bedrock:CreateAgent", "bedrock:InvokeAgent",
        "bedrock:CreateKnowledgeBase", "bedrock:Retrieve", "bedrock:RetrieveAndGenerate",
        "bedrock:CreateFlow", "bedrock:InvokeFlow"
      ],
      "Resource": "*"
    }
  ]
}
```

The first statement denies every inference profile except `jp.*`, which covers `global.`, `apac.`, other geographies and application inference profiles; foundation models are reachable only in Tokyo and Osaka. If T-002 shows that Codex CLI uses the Responses API on `bedrock-runtime`, the resource that API authorizes against is added only after V-12 (R-4).

**Permission policy of `LLM-Team-<team>`** (generated per team from `teams.yaml` and `models.yaml`; tier `standard` shown with one model of each kind):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InvokeTierModelsThroughJpProfiles",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
      "Resource": [
        "arn:aws:bedrock:ap-northeast-1:<llm-prod>:inference-profile/<jp. profile ID>",
        "arn:aws:bedrock:ap-northeast-3:<llm-prod>:inference-profile/<jp. profile ID>"
      ]
    },
    {
      "Sid": "InvokeUnderlyingModelsOnlyThroughJpProfiles",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
      "Resource": [
        "arn:aws:bedrock:ap-northeast-1::foundation-model/<model ID>",
        "arn:aws:bedrock:ap-northeast-3::foundation-model/<model ID>"
      ],
      "Condition": {"StringLike": {"bedrock:InferenceProfileArn": "arn:aws:bedrock:ap-northeast-*:<llm-prod>:inference-profile/jp.*"}}
    },
    {
      "Sid": "InvokeTokyoInRegionModels",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": ["arn:aws:bedrock:ap-northeast-1::foundation-model/<In-Region model ID>"]
    },
    {
      "Sid": "ShortTermApiKeysOnly",
      "Effect": "Allow",
      "Action": "bedrock:CallWithBearerToken",
      "Resource": "*",
      "Condition": {"StringEquals": {"bedrock:bearerTokenType": "SHORT_TERM"}}
    },
    {
      "Sid": "ListProfilesForClients",
      "Effect": "Allow",
      "Action": ["bedrock:ListInferenceProfiles", "bedrock:GetInferenceProfile"],
      "Resource": "*"
    },
    {
      "Sid": "UsageApi",
      "Effect": "Allow",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:ap-northeast-1:<llm-prod>:<usage API ID>/prod/GET/usage/*"
    },
    {
      "Sid": "DenyOutsideCorporateNetwork",
      "Effect": "Deny",
      "Action": ["bedrock:*", "bedrock-mantle:*", "execute-api:Invoke"],
      "Resource": "*",
      "Condition": {
        "NotIpAddressIfExists": {"aws:SourceIp": ["<office and DC egress CIDRs>"]},
        "StringNotEqualsIfExists": {"aws:SourceVpce": ["<Route A endpoint IDs>"]},
        "BoolIfExists": {"aws:ViaAWSService": "false"}
      }
    }
  ]
}
```

Teams approved for Codex CLI also get `bedrock-mantle:CreateInference` on [fill: the project resource, after T-002 and T-029 (R-4, R-29)].

**`llm-guard-deny`** (rendered by `llm-enforce`; the placeholder values match nothing when no one is suspended):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SuspendedTeamsAndWorkloads",
      "Effect": "Deny",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:CallWithBearerToken", "bedrock-mantle:CreateInference", "execute-api:Invoke"],
      "Resource": "*",
      "Condition": {"ArnLike": {"aws:PrincipalArn": [
        "arn:aws:iam::<llm-prod>:role/llm-none",
        "arn:aws:iam::<llm-prod>:role/aws-reserved/sso.amazonaws.com/*AWSReservedSSO_LLM-Team-<suspended team>_*",
        "arn:aws:iam::<llm-prod>:role/llm-wl-<suspended workload>"
      ]}}
    },
    {
      "Sid": "SuspendedPeople",
      "Effect": "Deny",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:CallWithBearerToken", "bedrock-mantle:CreateInference", "execute-api:Invoke"],
      "Resource": "*",
      "Condition": {"StringLike": {"aws:userid": ["*:llm-none", "*:<suspended user name>"]}}
    }
  ]
}
```

### 4.3 Timeouts

<!-- Every layer must agree; the shortest one fires first [CMP §2.7]. There is no layer of ours. -->

| Layer | Setting | Value |
|---|---|---|
| AWS SDK (workloads) | Read timeout (`read_timeout` in botocore, or the SDK's equivalent) | [default: 600 s, above the longest silence before the first token] |
| AWS SDK (workloads) | Retry mode | [default: adaptive, 3 attempts] |
| Claude Code | [fill: request timeout setting, checked in T-055] | [default: 600 s] |
| Codex CLI | `stream_idle_timeout_ms` for the provider | [default: 600000] |
| Office secure web gateway | Idle timeout for the hostnames in 02 §6 | [fill: at least 600 s] |

### 4.4 Sessions, budgets and limits

| Item | Setting | Value |
|---|---|---|
| Access-portal session | IAM Identity Center session duration | 8 h (IAM-011) |
| Entra sign-in frequency | CA-GW-01; CA-GW-02 and CA-GW-05 | 8 h; 4–8 h (01 Q-15) |
| Permission set session (`LLM-Team-*`, operator sets) | Permission set session duration | 1 h (IAM-016, IAM-008) |
| Workload role session | Roles Anywhere profile `durationSeconds` | 3600 |
| Workload certificate validity | Private CA template | [default: 30 days], maximum 90 days (TEN-006) |
| Default team budget and period | `teams.yaml` | [fill: amount] per calendar month (01 Q-23) |
| Budget notification thresholds | `teams.yaml` | 80 %, 100 % (CST-010) |
| Per-person monthly cap | `teams.yaml` defaults | [fill: amount] (01 Q-23) |
| Runaway threshold and suspension period | `teams.yaml` defaults | [fill: tokens per 5 minutes]; [default: 30 minutes] (01 Q-23) |
| Leaver denial duration | `llm-lifecycle` | 9 h (portal session plus role session) |
| Enforcement delay target, streaming calls | Measured by V-14 | [default: 15 minutes] (01 Q-23) |
| Non-streaming estimate | `llm-meter` | Average cost per non-streaming call per model, last full month of CUR (R-1) |
| Workload budgets | AWS Budgets per workload role and enrolled account | From `workloads.yaml`; action at 100 % (CST-014) |
| Bedrock quotas | Service Quotas, per model, per Region | [fill: requested values, Tokyo and Osaka] (02 §9) |

### 4.5 Guardrails and client settings

| Name | Type | Mode (pre-call, post-call, during call) | Applies to | Failure behaviour (fail open or closed) |
|---|---|---|---|---|
| Guardrail in the request path | None by default (02 D-10) | n/a | n/a | n/a |
| Optional Classic-tier guardrail | Bedrock Guardrails in Tokyo, enforced by a Bedrock policy in AWS Organizations | Pre-call | [fill: OUs, if Security chooses it (01 Q-13)] | [fill] |

**Claude Code managed settings** (pushed by Intune; checked in T-001 and T-009):

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_PROFILE": "llm",
    "ANTHROPIC_MODEL": "<main model ID from §4.1>",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "<fast model ID from §4.1>",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  },
  "awsAuthRefresh": "llm login"
}
```

`AWS_REGION` is written by `llm region` into the user-level Claude Code settings, so that it can change in DR (02 D-12); whether the managed and user `env` blocks merge as intended is checked in T-009.

**Codex CLI** (user-level `~/.codex/config.toml`, pushed by Intune; the Region comes from the `llm` profile):

```toml
model_provider = "amazon-bedrock"
model = "<model approved for Codex CLI, §4.1>"

[model_providers.amazon-bedrock.aws]
profile = "llm"
```

**AWS profile written by `llm login`:**

```ini
[sso-session corp]
sso_start_url = <access portal start URL>
sso_region = ap-northeast-1
sso_registration_scopes = sso:account:access

[profile llm]
sso_session = corp
sso_account_id = <llm-prod account ID>
sso_role_name = LLM-Team-<team>
region = ap-northeast-1
```

**DC workload profile:**

```ini
[profile llm-wl]
credential_process = aws_signing_helper credential-process --certificate <certificate path> --private-key <key path> --trust-anchor-arn <trust anchor ARN> --profile-arn <profile ARN> --role-arn <workload role ARN>
region = ap-northeast-1
```

## 5. Feature switches

| Switch | Default | Effect when on | Owner | Review or remove by |
|---|---|---|---|---|
| Route A network condition | Off in the pilot | The permission policies also accept calls through our VPC endpoints; on-premises DNS points the AWS hostnames at them (02 D-6) | Network | [fill: YYYY-MM-DD] |
| Content-logging account for a team | Off | Bedrock invocation logging on in that team's own account only (02 D-11); needs legal approval [CMP A-10] | Legal / privacy | [fill: YYYY-MM-DD] |
| Codex CLI and the Responses API | Off until V-16 and T-002 pass | `bedrock-mantle` and the Responses API granted to approved teams | Platform engineering | [fill: YYYY-MM-DD] |
| Classic-tier guardrail on selected OUs | Off | A Bedrock policy enforces the guardrail on those OUs (02 D-10) | Security / SOC | [fill: YYYY-MM-DD] |
| Spend guard enforcement | On | Off: metering and notifications only, no denials; used during a spend guard incident | Platform engineering | [fill: YYYY-MM-DD] |
