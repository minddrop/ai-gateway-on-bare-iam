# IAM-native LLM gateway: Development guide

<!--
Answers: how the repository is organised and how a change gets from a laptop to production.
Reader: engineers changing policies, IaC, the spend guard, the client package or tests. Pair it with 03 for setup.
Owns: the repository layout, standards, the change workflow, policy change steps, test levels, the definition of done. Refers to: deploys (07 §1), design (02), settings (04).
Detail: every check and test has its exact command. "Development" here is mostly policy generation, IaC, the spend guard and the client package.
Status: stub written during design; [fill] markers are completed during the build.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last reviewed: [fill: YYYY-MM-DD], for release [fill: version]

## 1. Repository layout

```text
[fill: repo name]/
├── config/            # teams.yaml, models.yaml, workloads.yaml per environment
├── policies/          # SCP and permission policy templates; the generator
├── infra/             # IaC modules and per-environment variables
├── spend-guard/       # llm-meter, llm-reconcile, llm-enforce, llm-lifecycle, llm-admin, llm-usage
├── clients/           # llm helper; Intune payloads for Claude Code and Codex CLI
├── tests/
│   ├── smoke/         # Post-deploy checks
│   └── gates/         # Automated launch gates V-1 … V-16
├── scripts/
└── docs/              # This documentation set
```

## 2. Standards

- **Formatting and linting:** [fill: tools and commands]
- **Policies:** generated from `config/`, never hand-written per team; no wildcard action in an allow statement (SEC-020); IAM Access Analyzer policy validation on every generated policy
- **IaC:** [fill: module conventions]; tags required on every resource; workload roles carry `Team`, `CostCenter`, `Workload`, `Owner`
- **Secrets:** none in the repo; CI reaches AWS through OIDC (SEC-012); [fill: secret-scanning tool]
- **Region:** resources only in `ap-northeast-1` / `ap-northeast-3` (the SCP also enforces this)
- **Spend guard code:** signed with the AWS Signer profile (SEC-016); never logs request content (there is none in its input) or credentials

## 3. Workflow

1. Branch from `main`, named [default: `<type>/<ticket-id>-<short-name>`].
2. Make the change, with tests.
3. Run the checks locally: `[fill: lint, policy generation, policy validation, unit test and IaC plan commands]`.
4. Open a pull request. The template asks:
    - Which requirement IDs does this change?
    - Does it change a security-critical setting (04 §4.2)? Which gate verifies it?
    - Are the docs updated (and the Japanese translation, if kept)?
5. [fill: number] approvals, and CI passes. Changes to `policies/`, the SCP or `infra/` for production also need [fill: role, for example Security] approval.
6. Merge with [default: squash]. Deployment follows 07 §1.

### 3.1 Policy and SCP changes

1. Change the template or the configuration; regenerate the policies.
2. Validate with IAM Access Analyzer and check the SCP size (R-23).
3. Deploy to staging and run V-12, and every other gate that verifies the changed setting (04 §4.2). Record the results in 02 §11.2.
4. Plan the rollback (07 §2): the previous policy versions and the previous SCP.

### 3.2 When AWS changes Bedrock, IAM Identity Center or CloudTrail

1. Read the announcement and the changed documentation.
2. Decide which gates depend on it (02 §11.2) and re-run them on staging (OPS-001).
3. Record the result and any design change (02 §13, §14).

## 4. Testing

| Level | What it checks | Command | Runs | Target |
|---|---|---|---|---|
| Policy validation | Generated policies parse, pass IAM Access Analyzer, have no wildcard allow actions, and match the catalog | [fill] | Every PR | 100 % of policies |
| Unit | Spend guard logic: pricing, counters, thresholds, policy rendering | [fill] | Every PR | [fill] |
| IaC checks | Plan, policy checks (Region, tags, public exposure) | [fill] | Every PR | [fill] |
| Smoke | Allowed call, denied call, metered call | [fill] | After every deploy | [fill] |
| Launch gates | V-1 … V-16 | [fill] | Before release; on security-critical changes; quarterly | All pass |
| Load | Throughput against the quotas; spend guard under 17 million events a day | [fill] | [default: before launch; quarterly] | PRF-M02, PRF-M04 |
| DR drill | Failover to Osaka | [fill] | [default: twice a year] | AVL-M02, AVL-M03 |

## 5. Dependencies

- **Clients:** Claude Code, Codex CLI and AWS CLI minimum versions in 02 §1.3; raised through the client package after T-001, T-002 and T-009 pass.
- **Spend guard packages:** [fill: scanning (Inspector Lambda scanning); update bot; approval for new dependencies; licence check]

## 6. Definition of done

- [ ] Code, policies and config reviewed and merged
- [ ] Tests added; affected launch gates pass
- [ ] Requirement IDs linked in the PR
- [ ] Documentation updated: this set, release notes, translation if kept
- [ ] Monitoring and alerts cover the new behaviour, with an incident entry in 07 §6
