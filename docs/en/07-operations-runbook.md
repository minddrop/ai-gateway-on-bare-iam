# IAM-native LLM gateway: Operations runbook

<!--
Answers: how to deploy, roll back, monitor, recover and maintain the gateway.
Reader: the on-call engineer at 3 a.m. who has never touched the system. Exact commands, exact dashboards, no assumed knowledge.
Owns: operational procedures, alerts and their thresholds, incident procedures, the escalation path, the maintenance schedule. Refers to: design (02), setting values (04), environments (03 §2), contact details (11 §C).
Detail: every alert in §3 has an entry in §6, written from the block template there with every field filled. Every entry says whether prompt content could be involved, because that changes who is called. Every procedure step has Run: and Expect: lines.
Status: stub written during design; [fill] markers are completed during the build.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last reviewed: [fill: YYYY-MM-DD], for release [fill: version]

## 1. Deployment

| Item | Value |
|---|---|
| Pipeline | [fill: CI/CD tool and link], federated to `llm-platform-deploy` by OIDC |
| Release unit | Configuration version + IaC version + spend guard code version + client package version (02 §10) |
| Trigger | [default: merge to `main` → dev; tag → staging; approval → production] |
| Strategy | IaC apply; IAM and SCP changes take effect after propagation; Lambda versions shifted by alias (02 §10) |
| Expected duration | [fill: minutes]; no restart of anything in the request path |
| Change window | [fill]; policy changes that can deny callers (SCP, permission policies) only in working hours |

**Before deploying to production:**
- [ ] Staging runs the same release unit.
- [ ] If a security-critical setting (04 §4.2) changed: the gates that verify it passed on staging (OPS-001).
- [ ] If the SCP changed: V-12 passed on staging, and the SCP size is within the limit (R-23).
- [ ] Change ticket raised in [fill: change system] and linked in the pipeline run.

**After deploying:**
- Run: `[fill: smoke test command]` (a call from an office IP with a test team, a denied call from a non-listed IP, a metered call visible in `llm-spend`)
- Expect: all checks pass, and [fill: CloudWatch dashboard link] shows no rise in `AccessDenied` or Bedrock errors for 15 minutes.

## 2. Rollback

1. **Redeploy the previous release unit.**
   - Run: `[fill: command or pipeline button]`
   - Expect: [fill: what the pipeline shows when it is done]
2. **If the spend guard misbehaves, roll back its alias.**
   - Run: `aws lambda update-alias --function-name <function> --name live --function-version <previous version>`
   - Expect: the alias points to the previous version.
3. **If a wrong denial is in `llm-guard-deny`, restore an earlier policy version.**
   - Run: `aws iam set-default-policy-version --policy-arn <llm-guard-deny ARN> --version-id <earlier version>`
   - Expect: calls from the wrongly denied principals succeed; Security is alerted (OPS-010).
4. **Confirm.**
   - Run: `[fill: smoke test command]`
   - Expect: the smoke test passes and `AccessDenied` is back to baseline.

## 3. Monitoring and alerts

Severity levels are defined in [fill: link to the incident severity definitions].

| Signal | Source | Threshold | Severity | Runbook |
|---|---|---|---|---|
| `AccessDenied` on model calls rises | CloudTrail metric filter or SIEM | [fill: > x per 5 min above baseline] | [default: P2] | §6.1 |
| Bedrock errors or latency for a model | Bedrock CloudWatch metrics (`InvocationServerErrors`, time to first token) | [fill] | [default: P2] | §6.2 |
| Bedrock throttling or quota consumption above 80 % | Bedrock CloudWatch metrics | [fill] | [default: P2] | §6.3 |
| Bedrock in Tokyo unavailable | AVL-M01 probe | [fill: consecutive failures] | [default: P1] | §6.4 |
| Spend guard: no events metered, or function errors | `llm-meter` and `llm-enforce` metrics; SQS age of oldest message | No event for 15 min in working hours; any error rate above [fill] | [default: P2] | §6.5 |
| Entra sign-in or SCIM provisioning failing | Entra provisioning logs; Identity Center sign-in events | Any failed provisioning cycle; sign-in failures above [fill] | [default: P1 for sign-in] | §6.6 |
| A team, person or caller suspended | `llm-enforce` notifications | Any runaway stop; any team suspension | [default: P3] | §6.7 |
| CUR export late, or estimate-to-bill gap above threshold | `llm-reconcile` | No export for 36 h; gap above [fill] (CST-008) | [default: P3] | §6.8 |
| Prompt content found outside approved stores | V-1 canary, or invocation logging found on (Config rule) | Any | **P1, privacy incident** | §6.9 |
| `llm-guard-deny` changed outside the spend guard, or the deploy role used outside CI | CloudTrail | Any | [default: P1, security] | §6.10 |
| Workload certificate or SCIM token about to expire | Private CA inventory; Identity Center | 30 days before | [default: P3] | §6.11 |

- **Logs:** spend guard functions in CloudWatch Logs `/aws/lambda/llm-*`; model calls in CloudTrail (SIEM query: [fill: query by `requestID`])
- **Metrics and dashboards:** [fill: CloudWatch dashboard link]; spend in [fill: Quick Sight link]
- **Synthetic probe:** [fill: what it calls, from where, how often] (AVL-M01)

## 4. Backups, recovery and DR

| Data | Backup | Where | Restore last tested |
|---|---|---|---|
| `llm-spend` | DynamoDB point-in-time recovery, 35 days; global table replica | Tokyo, Osaka | [fill: YYYY-MM-DD] |
| Configuration, policies and IaC | Git | [fill] | n/a: rebuilt from Git |
| CloudTrail, CUR, access inventory | S3 with versioning; Object Lock for CloudTrail | Japan only | [fill: YYYY-MM-DD] |
| IAM Identity Center | Multi-Region replica | Osaka | [fill: YYYY-MM-DD] |

### 4.1 Failover to Osaka

The trigger, the decision owner and the known differences in Osaka (models, quotas) are in 02 §9.

1. **Confirm sign-in works in Osaka.**
   - Run: `llm login --region osaka` on a test device
   - Expect: Entra sign-in succeeds and `llm` lists the test user's teams (R-35).
2. **Make the spend guard enforce from Osaka.**
   - Run: [fill: change the active-Region parameter (04 §2) and deploy]
   - Expect: `llm-enforce` in `ap-northeast-3` runs every minute; the one in Tokyo is idle.
3. **Tell users to switch.**
   - Run: post the prepared message in [fill: status channel]; [fill: optional Intune push of the Region change]
   - Expect: users run `llm region osaka` and restart their tools (05 §5.6).
4. **Confirm models in Osaka.**
   - Run: the probe against `ap-northeast-3` for every model marked available in Osaka (01 §6.5)
   - Expect: every such model answers; the probe in Osaka is green.

### 4.2 Failback to Tokyo

1. [fill: step, with Run: and Expect: lines]

### 4.3 DR drills

| Last drill | Result | Measured RTO / RPO, against AVL-M02 / AVL-M03 | Next drill |
|---|---|---|---|
| EXAMPLE: 2027-05-14 | Passed, with one finding: the Osaka quota for the main Claude model was too low | RTO 42 min, RPO 2 s | 2027-11-12 |

## 5. Routine maintenance

| Task | Frequency | How | Owner |
|---|---|---|---|
| Re-run every launch gate | Quarterly, and when AWS announces a change a gate depends on (OPS-001) | 02 §11.2 | [fill] |
| Japan model availability re-check | Quarterly and before onboarding [CMP §7.2] | `GetInferenceProfile` from each source Region; record in `models.yaml` | [fill] |
| Access inventory review | Monthly | Quick Sight access inventory (OBS-010) | Security / SOC |
| Unused workload roles | Monthly | IAM Access Analyzer unused-access findings | [fill] |
| Estimate-to-bill reconciliation | Monthly | `llm-reconcile` report; investigate above the threshold (CST-008) | FinOps |
| Price table update | When AWS prices change, and monthly with V-4 | `models.yaml` | [fill] |
| Egress CIDR review | [default: quarterly, and on any network change] | Update the policies **before** the IPs change [CMP A-14] (OPS-005) | [fill] |
| SCIM token and SAML certificate renewal | Before expiry | 04 §3 | Identity |
| Private CA and CRL | [fill] | [fill] | [fill] |
| Client package update (Claude Code, Codex CLI minimum versions) | [fill] | Intune | Endpoint / Intune |

## 6. Incident procedures

One entry per alert in §3. Each entry uses this block; copy it for a new alert, and keep every field.

```markdown
### 6.n <Alert, as named in §3>
- **What it means:** <what is broken, and what the launch gates showed about this failure>
- **Impact:** <who is affected, and how>
- **Prompt content involved?** <No / Possibly / Yes, and why. If not No, call security and privacy (11 §C).>
- **Diagnose:** <dashboards, queries and commands, in order>
- **Mitigate:** <actions, in order, with commands or links>
- **Escalate:** <to whom (§7), and after how long>
- **Follow-up:** <what to check or re-run afterwards>
```

### 6.1 Model calls denied unexpectedly
- **What it means:** a policy layer (SCP, permission policy, `llm-guard-deny`) denies calls it should allow, usually after a deploy or a network change.
- **Impact:** [fill: the affected teams or everyone]
- **Prompt content involved?** No
- **Diagnose:** find the `errorCode` and principal in CloudTrail; compare with recent deploys and `llm-guard-deny` versions; check the caller's source IP against the network list.
- **Mitigate:** roll back the deploy (§2); restore the previous `llm-guard-deny` version (§2 step 3); for a changed office IP, deploy the new CIDR (OPS-005).
- **Escalate:** [fill]
- **Follow-up:** re-run V-12 on staging with the fix.

### 6.2 Bedrock errors or slow responses
- **What it means:** Bedrock is failing or slow for a model; nothing of ours is in the path.
- **Impact:** [default: calls to the affected model fail or slow down]
- **Prompt content involved?** No
- **Diagnose:** Bedrock CloudWatch metrics by model; the AWS Health dashboard for Bedrock in Tokyo and Osaka.
- **Mitigate:** tell users to switch to another catalog model; if Tokyo is down, §4.1.
- **Escalate:** AWS Support (§7)
- **Follow-up:** [fill]

### 6.3 Throttling or quota near its limit
- **What it means:** the account quota for a model is nearly used up, often by one caller.
- **Impact:** [default: calls to the model get 429]
- **Prompt content involved?** No
- **Diagnose:** the top principals by tokens in the last hour from `llm-spend` (5-minute counters); quota-consumption metrics.
- **Mitigate:** suspend a runaway caller with `llm-admin` if the runaway stop has not; request a quota increase; move a heavy workload to its own account (D-18).
- **Escalate:** [fill]
- **Follow-up:** review the runaway threshold (04 §4.4).

### 6.4 Bedrock in Tokyo unavailable
- **What it means:** the Tokyo endpoint is down for every model.
- **Impact:** [default: all users]
- **Prompt content involved?** No
- **Diagnose:** probe; AWS Health dashboard.
- **Mitigate:** decide on failover with the decision owner (02 §9); §4.1.
- **Escalate:** platform lead and AWS Support at once.
- **Follow-up:** failback (§4.2); record the measured RTO.

### 6.5 Spend guard not metering or failing
- **What it means:** events are not reaching `llm-meter`, or a function errors; enforcement is frozen at its last state and calls continue (AVL-007).
- **Impact:** budgets are not enforced until it recovers; no user impact otherwise.
- **Prompt content involved?** No
- **Diagnose:** the EventBridge rule state (03 §4 step 7); SQS age of oldest message; function errors in CloudWatch Logs.
- **Mitigate:** fix or roll back (§2); after recovery, `llm-reconcile` corrects counters from CUR.
- **Escalate:** [fill]
- **Follow-up:** re-run V-14.

### 6.6 Sign-in or provisioning failing
- **What it means:** Entra, the SCIM provisioning to IAM Identity Center, or Identity Center itself is failing.
- **Impact:** new sign-ins fail; people already signed in keep working until their portal session ends (V-10).
- **Prompt content involved?** No
- **Diagnose:** Entra sign-in and provisioning logs; Identity Center events in CloudTrail; AWS Health.
- **Mitigate:** [fill]
- **Escalate:** Identity team at once.
- **Follow-up:** [fill]

### 6.7 A team, person or caller suspended
- **What it means:** the spend guard denied a target for budget, cap or runaway; or `llm-lifecycle` for a leaver.
- **Impact:** that target cannot call models.
- **Prompt content involved?** No
- **Diagnose:** the suspension's reason and expiry in `llm-spend`; the spend that caused it.
- **Mitigate:** if wrong, restore with `llm-admin` and record why; a budget raise goes through a pull request (05 §5.4).
- **Escalate:** FinOps for a budget dispute.
- **Follow-up:** [fill]

### 6.8 CUR late, or estimates far from the bill
- **What it means:** the CUR export did not arrive, or the estimate-to-bill gap is above the threshold.
- **Impact:** enforcement runs on estimates for longer.
- **Prompt content involved?** No
- **Diagnose:** the export's status in the management account; `llm-reconcile` logs; per-model gaps.
- **Mitigate:** fix prices in `models.yaml`; [fill]
- **Escalate:** FinOps
- **Follow-up:** V-4

### 6.9 Prompt content found where it must not be
- **What it means:** content was written outside the approved stores, for example because invocation logging was turned on, or a Responses API response was stored.
- **Impact:** [fill]
- **Prompt content involved?** **Yes. This is a privacy incident.** Call security and privacy (11 §C) immediately.
- **Diagnose:** which account and Region; who changed the setting (CloudTrail); which store holds content.
- **Mitigate:** turn the writer off; restrict access to the store. **Do not delete evidence** until security decides; note any Object Lock on the store.
- **Escalate:** security and privacy, at once (§7)
- **Follow-up:** re-run V-1 and V-16; find how the SCP or the client setting allowed it.

### 6.10 Access-control change outside CI or the spend guard
- **What it means:** `llm-guard-deny`, a permission set, a role or the SCP was changed by someone other than CI or the spend guard, or the deploy role was used from outside CI.
- **Impact:** possibly a compromised role or break-glass use.
- **Prompt content involved?** No
- **Diagnose:** CloudTrail for the actor, source IP and change.
- **Mitigate:** if not a recorded break-glass use, treat as a security incident: [fill]
- **Escalate:** Security / SOC at once.
- **Follow-up:** [fill]

### 6.11 Certificate, token or CRL about to expire
- **What it means:** a workload certificate, the SCIM token, the SAML certificate or a CRL is close to expiry.
- **Impact:** [fill: workload calls, provisioning or sign-in fail after expiry]
- **Prompt content involved?** No
- **Diagnose:** [fill]
- **Mitigate:** [fill]
- **Escalate:** [fill]
- **Follow-up:** [fill]

## 7. Escalation

Contact details for every role below are in 11 §C.

| Level | Who | Escalate when |
|---|---|---|
| 1 | On-call engineer | An alert in §3 fires |
| 2 | Platform lead | [fill: after how many minutes without mitigation; any P1] |
| Security / privacy | Security / SOC, Legal / privacy | Prompt content may be involved (§6.9), or a security control fails (§6.10) |
| AWS | AWS Support ([fill: plan]) | Bedrock, IAM Identity Center or IAM faults |
| Network | Network team | Egress IPs, secure web gateway, TLS inspection, Route A |
| Identity | Identity team | Entra ID, Okta, Conditional Access, SCIM |
