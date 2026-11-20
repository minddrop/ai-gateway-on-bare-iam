# Cost Estimate — IAM-native LLM gateway on AWS, v0.1

> **Generated, read-only snapshot of the estimate model.** The master is the Excel workbook built from the cost estimate template (`CostEstimate_IAMNativeLLMGateway_v0.1.xlsx`; Japanese workbook: `CostEstimate_IAMNativeLLMGateway_v0.1_jp.xlsx`); it holds the formulas, dropdowns, rate lookups and checks. Numbers here do not recalculate — change the workbook instead. A Japanese version is in `cost_estimate_IAMNativeLLMGateway_v0.1_jp.md`.

> Purpose: internal budget approval in the design phase — **a budget estimate, not a quote** · Currency: JPY (line items excl. tax) · Prices: AWS list prices checked 2026-11-20, JPY 160/USD · Parameters: PM 10%, contingency 15% (applied to recurring: Yes), tax 10%, **24 recurring months in grand total** (24-month operation period). Model inference (Bedrock tokens charged to the calling principal) is **not** in the totals; see §8. Schedule, usage basis, rates and parameters are those of the LiteLLM design's estimate `[LGW]`, so that §7 compares the two like for like.

Sections 1–6 mirror the workbook sheets (Summary · Estimate · Rates · Assumptions · Lists · Calculation rules). Sections 7–12 are additions for this estimate: the comparison with `[LGW]`, model usage, separately priced options, infrastructure sizing detail, open pricing items by owner, and findings for the design documents.

## 1. Summary / サマリー

### Project information / 案件情報

| Item | Value |
|---|---|
| Project name / 案件名 | IAM-native LLM gateway on AWS (build and 24-month operation) |
| Estimate version / 版数 | v0.1 |
| Estimate date / 作成日 | 2026-11-20 |
| Prepared by / 作成者 | Claude (AI assistant), for platform engineering |
| Status / ステータス | Draft / 作成中 |

### Parameters / パラメータ

| Parameter | Value | Notes |
|---|---:|---|
| PM cost (% of development cost) / PM費率 | 10.0% | Template default kept, as [LGW]; the design docs give no reason to change it. |
| Contingency (% of cost) / 予備費率 | 15.0% | Template default kept, as [LGW]. Identified risks from 02 §14 and 01 §9 are line items with a likelihood (§2, Contingency). |
| Apply contingency to recurring cost? / 継続費用にも予備費を適用 | Yes | Template default, as [LGW]. |
| Consumption tax rate / 消費税率 | 10.0% | Calculated once on each total and rounded down to JPY 1. |
| Recurring months in grand total / 総額に含める継続月数 | 24 | Operation period of 2 years (2027-08 to 2029-07), as [LGW]. 12- and 36-month views are in the multi-year table below. |

### Totals / 合計

| Item | Excl. tax (JPY) / 税抜 | Consumption tax (JPY) / 消費税 | Incl. tax (JPY) / 税込 | Notes |
|---|---:|---:|---:|---|
| Total initial cost (one-time) / 初期費用合計 | 41,509,110 | 4,150,911 | 45,660,021 | All one-time costs incl. PM and contingency |
| Total recurring cost – monthly / 継続費用（月額） | 1,400,096 | 140,009 | 1,540,105 | Recurring rows per month (+ contingency) |
| Total recurring cost – annual / 継続費用（年額） | 16,801,152 | 1,680,115 | 18,481,267 | Monthly × 12 |
| **Grand total (initial + 24 months recurring) / 総額** | **75,111,414** | **7,511,141** | **82,622,555** | Tax calculated on this total |

### Multi-year views / 複数年試算

The same initial cost with 12, 24 (the grand total above) and 36 months of recurring cost. Model inference is excluded in every view.

| View | Recurring months | Excl. tax (JPY) | Consumption tax (JPY) | Incl. tax (JPY) |
|---|---:|---:|---:|---:|
| Initial + first year | 12 | 58,310,262 | 5,831,026 | 64,141,288 |
| Initial + operation period (grand total) | 24 | 75,111,414 | 7,511,141 | 82,622,555 |
| Initial + 3 years | 36 | 91,912,566 | 9,191,256 | 101,103,822 |

### Checks / チェック

| Check | Value | Result |
|---|---:|---|
| Line items not in any total (JPY) / 集計漏れ金額 | 0 | OK |
| Rows with quantity but no amount / 単価未設定の行数 | 0 | OK |
| Rows with unit 'one-time' marked Recurring / 一式×継続の行数 | 0 | OK |
| PM line items while PM % > 0 / PM費の二重計上 | 0 | OK |
| Likelihood on rows outside Contingency / 予備費以外の発生確率 | 0 | OK |

The workbook could not be recalculated with LibreOffice in this environment (not installed). The Summary values above were computed independently in Python with the workbook's formulas (unit cost lookup, likelihood, ROUND for PM and contingency, ROUNDDOWN for tax), from the filled workbook and from the model, and the two agree; Excel recalculates the workbook when it is opened.

### Cost breakdown by category / 費目別内訳

| Category / 費目 | One-time (JPY) / 初期 | Recurring monthly (JPY) / 月額 | Recurring annual (JPY) / 年額 | Notes / 備考 | Share of dev. cost |
|---|---:|---:|---:|---|---:|
| ***1. Phase-based costs / 工程別費用*** |  |  |  |  |  |
| Requirements definition / 要件定義 | 1,480,000 | - | - |  | 5.6% |
| Basic & detailed design / 基本・詳細設計 | 4,115,000 | - | - |  | 15.6% |
| Implementation / 実装 | 10,175,000 | - | - |  | 38.6% |
| Testing (unit, integration, system, UAT) / テスト | 5,562,500 | - | - |  | 21.1% |
| Data migration / データ移行 | - | - | - | No rows: no data migration in 01/02 (A19) | - |
| Setup, build & deployment / 構築・リリース | 1,435,000 | - | - |  | 5.4% |
| Training & documentation / 教育・ドキュメント | 1,895,000 | - | - |  | 7.2% |
| Cutover & go-live support / 本番移行・稼働支援 | 1,727,500 | - | - |  | 6.5% |
| Operation / 運用 | - | 610,600 | 7,327,200 |  | - |
| Maintenance / 保守 | - | 390,000 | 4,680,000 |  | - |
| **Subtotal – phase-based / 小計（工程別）** | **26,390,000** | **1,000,600** | **12,007,200** | One-time part = development cost | **100.0%** |
| ***2. Cross-cutting costs / 横断費用*** |  |  |  |  |  |
| Project management / プロジェクト管理 | - | - | - | No bottom-up PM rows |  |
| Project management: 10.0% of development cost / PM費（自動計算） | 2,639,000 |  |  | PM % × development cost |  |
| Quality assurance & reviews / 品質保証 | 510,000 | - | - |  |  |
| Infrastructure / インフラ | 872,400 | 187,399 | 2,248,788 |  |  |
| Software licenses & tools / ライセンス・ツール | - | - | - | No licensed software (A16) |  |
| Security / セキュリティ | 2,640,000 | - | - |  |  |
| Contingency & risk buffer / 予備費 | 3,500,000 | 33,897 | 406,764 | Identified risks at expected value (02 §14, 01 §9) |  |
| Contingency buffer: 15.0% of initial and recurring cost / 予備費（自動計算） | 4,957,710 | 178,200 | 2,138,400 | Contingency % × cost before contingency |  |
| **Subtotal – cross-cutting / 小計（横断）** | **15,119,110** | **399,496** | **4,793,952** |  |  |
| **Total (excl. tax) / 合計（税抜）** | **41,509,110** | **1,400,096** | **16,801,152** |  |  |

### Calculation bases and indicators / 計算基礎・指標

| Item | Value | Definition |
|---|---:|---|
| Development cost (base for PM %) / 開発費 | 26,390,000 | One-time costs of all phase-based categories |
| Initial cost before contingency / 予備費控除前の初期費用 | 33,051,400 | All one-time costs except the Contingency category (incl. calculated PM) |
| Recurring cost before contingency (monthly) / 予備費控除前の継続月額 | 1,187,999 | Used because contingency applies to recurring |
| Total one-time effort / 初期工数合計 | 34.1 person-months | Person-months + person-days ÷ 20 (One-time rows) |
| Testing share of development cost / テスト比率 | 21.1% | Typical range 20–30% |

## 2. Estimate details / 見積明細

Subtotal = Quantity × Unit cost. **Recurring rows show the cost per month.** Prices for monthly fees and one-time items are entered in column J (Unit cost override) in Excel; here they are shown directly as the unit cost. The bold subtotal rows are for reading convenience. In Excel each category also has a blank spare row with formulas. On Contingency rows with a likelihood (column K), Subtotal = Quantity × Unit cost × likelihood, and Impact (column L) shows Quantity × Unit cost. [PL] = AWS Price List API offer file for the region, checked 2026-11-20; USD amounts are converted at JPY 160/USD. [LGW] = the LiteLLM design's estimate.

### 1. PHASE-BASED COSTS / 工程別費用

| Category / phase | Task or item description | Role | Unit | Quantity | Unit cost (JPY) | Subtotal (JPY) | One-time / Recurring | Notes / assumptions | Likelihood | Impact (JPY) |
|---|---|---|---:|---:|---:|---:|---|---|---:|---:|
| Requirements definition / 要件定義 | Close the 26 open questions in 01 §9 and confirm assumptions AS-1–AS-27 with their owner teams; update 01 to v1.0 | Business analyst / SE / 業務SE | person-days / 人日 | 20.0 | 60,000 | 1,200,000 | One-time / 初期 | 01 §9 (Q-1–Q-27; Q-17 withdrawn), 01 §3. Sizing: ~0.75 pd per question incl. workshop and write-up |  |  |
| Requirements definition / 要件定義 | Requirements review and approval (security, legal/privacy, network, FinOps, platform lead) | Architect / tech lead / アーキテクト | person-days / 人日 | 4.0 | 70,000 | 280,000 | One-time / 初期 | 01 header Approvers, 01 §11, REG-003. Sizing: 2 review rounds × 2 pd |  |  |
| **Subtotal 1-1** | **Requirements definition / 要件定義** |  |  |  |  | **1,480,000** | One-time / 初期 |  |  |  |
| Basic & detailed design / 基本・詳細設計 | Design v0.2: close uncovered requirements and open decisions — guardrail position (SEC-008, R-5), content-logging accounts (PRV-002, D-11), Codex CLI models (FUN-002, R-4), Route A for GA (SEC-014, D-6), sign-in DR (R-35), budget overshoot bound (CST-009, R-1), Private CA or corporate CA (R-24) | Architect / tech lead / アーキテクト | person-months / 人月 | 1.0 | 1,400,000 | 1,400,000 | One-time / 初期 | 02 §1.2, §12, §14 (target 2027-01-29). Sizing: ~7 design topics × ~3 pd |  |  |
| Basic & detailed design / 基本・詳細設計 | Detailed design of remaining TBDs: IaC tool and CI federation (R-24), SCP size and landing-zone fit (R-23), team count and permission-set quotas (R-9), llm-guard-deny size (R-15), Lambda concurrency, Bedrock quota plan for Tokyo and Osaka (R-28), enrolment checklist (R-32), alert thresholds (OBS-006) | Infra / DevOps engineer / インフラ | person-months / 人月 | 1.0 | 1,100,000 | 1,100,000 | One-time / 初期 | 02 §1.3, §9, §10, §14. Sizing: ~8 topics × ~2.5 pd |  |  |
| Basic & detailed design / 基本・詳細設計 | Early spikes on a sandbox for the AWS behaviours the design rests on: CUR attribution by principal and Budgets tag filters (R-2), stream-completion events on EventBridge and their delay (R-30), network condition with jp. routing, bedrock-mantle and short-term keys (R-25), IAM model control on bedrock-mantle (R-29), Responses API storage (R-3), Codex CLI provider (R-4), SCIM deprovisioning event (R-33), device-code flow (R-7) | Senior engineer / シニアエンジニア | person-days / 人日 | 20.0 | 55,000 | 1,100,000 | One-time / 初期 | 02 §14 mitigations 'V-n before launch'; 01 AS-24, AS-25. Sizing: 8 spikes × 2.5 pd; CUR results arrive a day later, so elapsed time is longer than effort |  |  |
| Basic & detailed design / 基本・詳細設計 | Guardrail decision support for 01 Q-13: test the Classic-tier Bedrock guardrail option (regex filters, Japanese samples) enforced through a Bedrock policy on a test OU | Senior engineer / シニアエンジニア | person-days / 人日 | 3.0 | 55,000 | 165,000 | One-time / 初期 | 02 §8, D-10, R-5; 01 SEC-008, Q-13. Sizing: 1 test setup + report; [LGW] spent 10 pd selecting a classifier |  |  |
| Basic & detailed design / 基本・詳細設計 | Design review and approval (security, network, platform lead, FinOps, SRE), incl. Security sign-off of R-34 parameters | Architect / tech lead / アーキテクト | person-days / 人日 | 5.0 | 70,000 | 350,000 | One-time / 初期 | 02 header Approvers, R-34. Sizing: 2 rounds + 1 pd follow-up |  |  |
| **Subtotal 1-2** | **Basic & detailed design / 基本・詳細設計** |  |  |  |  | **4,115,000** | One-time / 初期 |  |  |  |
| Implementation / 実装 | IaC for the accounts and both Regions: SCP baseline and resource control policies, Config rules, permission-set and operator roles, Roles Anywhere trust anchors and profiles, Private CA with certificate template and CRL, KMS, S3 buckets, AWS Budgets with actions, IAM Identity Center replication to Osaka | Infra / DevOps engineer / インフラ | person-months / 人月 | 1.5 | 1,100,000 | 1,650,000 | One-time / 初期 | 02 §2.2, §4.3, §4.7, §7.1, §9; D-4, D-7, D-13, D-15; OPS-002. Sizing: ~15 components, mostly IAM and organization level; no VPC, cluster or database ([LGW]: 3.0 pm) |  |  |
| Implementation / 実装 | Policy generator and model catalog: models.yaml and teams.yaml to permission policies per tier with network conditions, short-term key and bedrock-mantle permissions, workload-role policies bound to CIDRs, client defaults; policy tests with the IAM policy simulator | Senior engineer / シニアエンジニア | person-months / 人月 | 1.0 | 1,100,000 | 1,100,000 | One-time / 初期 | 02 §4.2, §4.7, §5, §5.1; D-5, D-15; 01 MDL-101–MDL-105, OPS-009, SEC-020. Takes the place of [LGW]'s LiteLLM configuration (1.0 pm) |  |  |
| Implementation / 実装 | Spend guard core: llm-meter (CloudTrail events to estimated cost; counters per person, team, workload and 5-minute window), llm-enforce (budgets, caps, runaway stop, llm-guard-deny policy versions and size limit), DynamoDB global table, active Region switch, failure behaviour | Senior engineer / シニアエンジニア | person-months / 人月 | 2.0 | 1,100,000 | 2,200,000 | One-time / 初期 | 02 §5.2, D-8, R-13, R-15, R-16; 01 CST-002, CST-004, CST-009, CST-010, CST-012, CST-013, AVL-007. Sizing: our only security-critical code; it can deny everyone |  |  |
| Implementation / 実装 | llm-reconcile and chargeback: CUR 2.0 export with IAM principal data, cost allocation tags, Athena views per principal, team and department, reconciliation of estimates with billed cost, Quick Sight chargeback with unattributed line | Engineer / エンジニア | person-months / 人月 | 1.0 | 850,000 | 850,000 | One-time / 初期 | 02 §5, §7.1, D-9, D-14; 01 CST-007, CST-008, CST-011 [CMP §4.5] |  |  |
| Implementation / 実装 | llm-lifecycle and llm-admin: leaver denial from SCIM events with a 5-minute Identity Store poll; operator suspend and restore with reason, expiry and Security alert | Engineer / エンジニア | person-days / 人日 | 10.0 | 42,500 | 425,000 | One-time / 初期 | 02 §4.5, §5.2 (R-33); 01 IAM-006, TEN-007, UC-12 |  |  |
| Implementation / 実装 | Usage API: API Gateway with IAM authorization and llm-usage; own and team usage as PRV-003 allows | Engineer / エンジニア | person-days / 人日 | 5.0 | 42,500 | 212,500 | One-time / 初期 | 02 §3.1, §5.2, D-14; 01 FUN-008, IAM-010 |  |  |
| Implementation / 実装 | IAM Identity Center integration: Entra enterprise app (SAML, SCIM), llm-team-* and operator group assignments by CI, session lengths, Conditional Access requirements handed to Identity | Engineer / エンジニア | person-days / 人日 | 10.0 | 42,500 | 425,000 | One-time / 初期 | 02 §4.2–§4.4, D-2, D-16; 01 IAM-001, IAM-003, IAM-004, IAM-011, TEN-004. One app instead of [LGW]'s three; Conditional Access itself is Identity's (B5) |  |  |
| Implementation / 実装 | Configuration pipeline: CI with OIDC to llm-platform-deploy; pull requests for teams, budgets, tiers, workload roles, certificates and enrolments; plan, review, apply | Engineer / エンジニア | person-months / 人月 | 1.0 | 850,000 | 850,000 | One-time / 初期 | 02 §4.5, §10, D-15; 01 OPS-002, OPS-003, TEN-002, SEC-012, SEC-021 |  |  |
| Implementation / 実装 | Client package: llm helper (login with PKCE, team choice, profile, Region switch, usage, short-term keys) for Windows and macOS; Claude Code managed settings with awsAuthRefresh; Codex CLI config.toml (deployed by Intune team) | Engineer / エンジニア | person-months / 人月 | 1.0 | 850,000 | 850,000 | One-time / 初期 | 02 §2.2, §4.1, §4.5, D-12; 01 FUN-005, FUN-008, FUN-009, TEN-009. Larger than [LGW]'s key helper (10 pd): sign-in, team and Region logic. Intune deployment itself excluded (B5) |  |  |
| Implementation / 実装 | DC workload onboarding kit: aws_signing_helper profile, certificate request and renewal guide, workload role request template | Engineer / エンジニア | person-days / 人日 | 5.0 | 42,500 | 212,500 | One-time / 初期 | 02 §2.3.3, §4.5, D-4; 01 TEN-002, TEN-006, OBS-008 |  |  |
| Implementation / 実装 | Logging and audit: bedrock-mantle data-event selector on the organization trail, EventBridge rules in both Regions, log groups with KMS and retention, subscription to the SIEM, alerts on llm-guard-deny changes and break-glass use | Infra / DevOps engineer / インフラ | person-days / 人日 | 10.0 | 55,000 | 550,000 | One-time / 初期 | 02 §4.3, §7.1, §7.4; 01 OBS-001, OBS-002, OBS-004, OBS-007, OPS-010. SIEM-side ingestion and correlation rules excluded (B6) |  |  |
| Implementation / 実装 | Dashboards and alarms: CloudWatch operations dashboards and alarms (no events for 15 min, function errors, quota use at 80 %, CUR late 36 h), daily access-inventory snapshot job, Quick Sight spend and access-inventory dashboards with row-level security, synthetic availability probe | Engineer / エンジニア | person-months / 人月 | 1.0 | 850,000 | 850,000 | One-time / 初期 | 02 §2.2, §7.1, §9, D-14; 01 OBS-003, OBS-006, OBS-010, AVL-M01 |  |  |
| **Subtotal 1-3** | **Implementation / 実装** |  |  |  |  | **10,175,000** | One-time / 初期 |  |  |  |
| Testing (unit, integration, system, UAT) / テスト | Unit tests for custom code (spend guard, usage API, inventory job, policy generator, llm helper) | Engineer / エンジニア | person-days / 人日 | 18.0 | 42,500 | 765,000 | One-time / 初期 | Sizing: ≈15 % of custom-code build effort (≈6 pm) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Integration, security and inspection tests T-001–T-086 on staging: automate, run, retest | QA / test engineer / テスト担当 | person-months / 人月 | 2.8 | 800,000 | 2,240,000 | One-time / 初期 | 02 §11.1 (86 tests; [LGW] 75). Sizing: avg 0.65 pd per test incl. automation + 1 retest cycle |  |  |
| Testing (unit, integration, system, UAT) / テスト | Load and long-stream tests: spend guard at the A-9 event rate (replayed CloudTrail events), long streams (T-055), Bedrock quota checks (T-056) | Infra / DevOps engineer / インフラ | person-days / 人日 | 5.0 | 55,000 | 275,000 | One-time / 初期 | 02 §9, §11.1; 01 PRF-M02, PRF-M04, PRF-001 (sizing basis A-9). Replayed events need no Bedrock tokens; no task sizing ([LGW]: 8 pd) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-1: No prompt content outside the approved stores: canary through every model, API style and endpoint, incl. refused and cancelled calls; search every store | Senior engineer / シニアエンジニア | person-days / 人日 | 4.0 | 55,000 | 220,000 | One-time / 初期 | 02 §11.2 [CMP V-1, §2.10]; 01 PRV-001, PRV-002, RES-005, OBS-002; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-2: Credential issuance stays within its limits: no long-term keys or IAM-user calls, 1 h sessions, 90-day certificates | QA / test engineer / テスト担当 | person-days / 人日 | 2.0 | 40,000 | 80,000 | One-time / 初期 | 02 §11.2 [CMP V-2, §2.10]; 01 IAM-015, IAM-016, TEN-006; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-4: Spend correct per model (10 models, with and without prompt caching), estimate against CUR | Engineer / エンジニア | person-days / 人日 | 4.0 | 42,500 | 170,000 | One-time / 初期 | 02 §11.2 [CMP V-4, §2.10]; 01 CST-004; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-5: Cancelled requests are metered | Engineer / エンジニア | person-days / 人日 | 3.0 | 42,500 | 127,500 | One-time / 初期 | 02 §11.2 [CMP V-5, §2.10]; 01 CST-006; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-6: Clients cannot skip tracking: every API, endpoint and auth mode in CloudTrail and CUR | QA / test engineer / テスト担当 | person-days / 人日 | 2.0 | 40,000 | 80,000 | One-time / 初期 | 02 §11.2 [CMP V-6, §2.10]; 01 CST-005, OBS-002; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-7: Clients cannot choose who pays, incl. user in two teams | QA / test engineer / テスト担当 | person-days / 人日 | 2.0 | 40,000 | 80,000 | One-time / 初期 | 02 §11.2 [CMP V-7, §2.10]; 01 CST-001, TEN-009; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-10: Identity endpoints unavailable | Infra / DevOps engineer / インフラ | person-days / 人日 | 2.0 | 55,000 | 110,000 | One-time / 初期 | 02 §11.2 [CMP V-10, §2.10]; 01 AVL-003; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-11: Unmanaged devices cannot use the office or DC egress IPs (with Network; CIDR list and owners) | Security specialist / セキュリティ | person-days / 人日 | 3.0 | 80,000 | 240,000 | One-time / 初期 | 02 §11.2 [CMP V-11, §2.10]; 01 SEC-001–SEC-003, OPS-004; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-12: Authorization matrix: every principal type × action family × endpoint × auth mode × model class × network origin, automated | Senior engineer / シニアエンジニア | person-days / 人日 | 8.0 | 55,000 | 440,000 | One-time / 初期 | 02 §11.2 [CMP V-12, §2.10]; 01 TEN-001, TEN-008, MDL-101–MDL-103, SEC-001, SEC-020, FUN-006; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-13: Metering feed: events, tokens and delay per API and endpoint | Engineer / エンジニア | person-days / 人日 | 3.0 | 42,500 | 127,500 | One-time / 初期 | 02 §11.2 [CMP V-13, §2.10]; 01 OBS-002, CST-009; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-14: Spend guard enforcement and failure: budget, cap, runaway, leaver; each function stopped in turn | Senior engineer / シニアエンジニア | person-days / 人日 | 4.0 | 55,000 | 220,000 | One-time / 初期 | 02 §11.2 [CMP V-14, §2.10]; 01 CST-002, CST-012, CST-013, AVL-007, IAM-006; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-15: Cost allocation by principal in CUR 2.0, incl. Budgets tag filters | Engineer / エンジニア | person-days / 人日 | 3.0 | 42,500 | 127,500 | One-time / 初期 | 02 §11.2 [CMP V-15, §2.10]; 01 CST-001, CST-007, CST-014; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | Launch gate V-16: No stored responses (Responses API on both endpoints) | QA / test engineer / テスト担当 | person-days / 人日 | 1.0 | 40,000 | 40,000 | One-time / 初期 | 02 §11.2 [CMP V-16, §2.10]; 01 PRV-005; must pass before first pilot user (01 §1.4) |  |  |
| Testing (unit, integration, system, UAT) / テスト | DR drill before launch: sign in through Osaka (Identity Center replica), switch clients with llm region, move llm-enforce, call each model available in Osaka, fail back | Infra / DevOps engineer / インフラ | person-days / 人日 | 4.0 | 55,000 | 220,000 | One-time / 初期 | 02 §9, §11.1 T-052, D-13, R-11, R-35; 01 OPS-007, AVL-M02, AVL-M03, GA exit (01 §1.4). No AZ-loss test: regional services only ([LGW]: 6 pd) |  |  |
| **Subtotal 1-4** | **Testing (unit, integration, system, UAT) / テスト** |  |  |  |  | **5,562,500** | One-time / 初期 |  |  |  |
| Data migration / データ移行 | *No line items: 01 and 02 define no data migration; what the gateway replaces is open (01 Q-2).* |  |  |  |  |  |  |  |  |  |
| Setup, build & deployment / 構築・リリース | AWS accounts and landing-zone onboarding: llm-dev, llm-staging, llm-prod; SCP attachment, IAM Identity Center instance settings, CUR 2.0 export with IAM principal data and cost allocation tags in the management account, break-glass users and vault | Infra / DevOps engineer / インフラ | person-days / 人日 | 10.0 | 55,000 | 550,000 | One-time / 初期 | 02 §4.3, §10, D-18; 01 IAM-007–IAM-009, RES-003, CST-007 |  |  |
| Setup, build & deployment / 構築・リリース | CI/CD: OIDC federation, IaC plan/apply with drift check, Lambda code signing with AWS Signer, promotion dev → staging → prod, configuration deploy | Infra / DevOps engineer / インフラ | person-days / 人日 | 10.0 | 55,000 | 550,000 | One-time / 初期 | 02 §8, §10, D-15; 01 SEC-016, OPS-002. No image mirror ([LGW]: 15 pd) |  |  |
| Setup, build & deployment / 構築・リリース | Bedrock setup in both Regions: model access, quota requests for jp. profiles in Tokyo and Osaka and for bedrock-mantle, GetInferenceProfile records, invocation logging off and locked | Engineer / エンジニア | person-days / 人日 | 4.0 | 42,500 | 170,000 | One-time / 初期 | 02 §5.1, §9 (R-28), D-5, D-11; 01 MDL-104, RES-008 |  |  |
| Setup, build & deployment / 構築・リリース | Production and DR deployment and release | Infra / DevOps engineer / インフラ | person-days / 人日 | 3.0 | 55,000 | 165,000 | One-time / 初期 | 02 §10 (no restart; Lambda alias shift) |  |  |
| **Subtotal 1-6** | **Setup, build & deployment / 構築・リリース** |  |  |  |  | **1,435,000** | One-time / 初期 |  |  |  |
| Training & documentation / 教育・ドキュメント | Technical docs 03, 04, 06, 07, 09 written to the design, incl. the policy text in 04 §4.2 | Senior engineer / シニアエンジニア | person-months / 人月 | 1.0 | 1,100,000 | 1,100,000 | One-time / 初期 | README doc set, 02 R-21. Sizing: 5 docs × 4 pd |  |  |
| Training & documentation / 教育・ドキュメント | User-facing docs 05, 08, 10 and editing of the set to the 11 §D checklist | Tech writer / trainer / ライター・講師 | person-days / 人日 | 12.0 | 35,000 | 420,000 | One-time / 初期 | README doc set, 11 §D |  |  |
| Training & documentation / 教育・ドキュメント | User onboarding: guide and short video (Okta Verify enrolment, llm login, team choice), 2 live sessions for pilot and GA cohorts, team-lead training (budget and workload-role pull requests) | Tech writer / trainer / ライター・講師 | person-days / 人日 | 6.0 | 35,000 | 210,000 | One-time / 初期 | 01 §1.4, AS-21; 30 engineers (A14). Sizing: 2 sessions × 1 pd + 4 pd material |  |  |
| Training & documentation / 教育・ドキュメント | Operations handover to on-call: 07 runbook walk-through and alert drills | Senior engineer / シニアエンジニア | person-days / 人日 | 3.0 | 55,000 | 165,000 | One-time / 初期 | 02 §10 on-call; 01 OPS-006 |  |  |
| **Subtotal 1-7** | **Training & documentation / 教育・ドキュメント** |  |  |  |  | **1,895,000** | One-time / 初期 |  |  |  |
| Cutover & go-live support / 本番移行・稼働支援 | Pilot (1 month): onboard pilot teams, triage, fixes, findings into 08 | Engineer / エンジニア | person-months / 人月 | 1.0 | 850,000 | 850,000 | One-time / 初期 | 01 §1.4 (pilot teams Q-3) |  |  |
| Cutover & go-live support / 本番移行・稼働支援 | GA readiness: re-run launch gates on the release that goes live | QA / test engineer / テスト担当 | person-days / 人日 | 6.0 | 40,000 | 240,000 | One-time / 初期 | 01 §1.4 GA exit, OPS-001; 13 applicable gates ([LGW]: 11, 5 pd) |  |  |
| Cutover & go-live support / 本番移行・稼働支援 | Hypercare 2 weeks after GA | Engineer / エンジニア | person-days / 人日 | 15.0 | 42,500 | 637,500 | One-time / 初期 | Sizing: 1.5 engineers × 10 days |  |  |
| **Subtotal 1-8** | **Cutover & go-live support / 本番移行・稼働支援** |  |  |  |  | **1,727,500** | One-time / 初期 |  |  |  |
| Operation / 運用 | On-call and incident response in support hours (business hours assumed): sign-in, wrong suspensions, quota throttling | Operations engineer / 運用担当 | person-months / 人月 | 0.25 | 750,000 | 187,500 | Recurring / 継続 | Per month. 01 OPS-006 (hours open, Q-6); 00 §1.4. Half of [LGW]: no servers, database or proxy of ours |  |  |
| Operation / 運用 | Monitoring, alert triage and pull requests for teams, budgets, tiers, workload roles and certificates | Operations engineer / 運用担当 | person-months / 人月 | 0.25 | 750,000 | 187,500 | Recurring / 継続 | Per month. 01 OPS-003, OBS-006; 02 §10 |  |  |
| Operation / 運用 | First-line help desk: sign-in and Okta Verify issues, team choice, Region switch, onboarding questions | Help desk / ヘルプデスク | person-days / 人日 | 2.0 | 27,500 | 55,000 | Recurring / 継続 | Per month. 01 Q-20; 30 engineers (A14). No keys to renew |  |  |
| Operation / 運用 | Monthly chargeback run, estimate-to-bill gap check and unattributed-cost investigation | Engineer / エンジニア | person-days / 人日 | 1.5 | 42,500 | 63,750 | Recurring / 継続 | Per month. 01 CST-007, CST-008; 02 §5, D-9. CUR names the caller, so no share model ([LGW]: 2 pd) |  |  |
| Operation / 運用 | Periodic reviews: operator and break-glass activity, access inventory, unused workload roles | Security specialist / セキュリティ | person-days / 人日 | 1.0 | 80,000 | 80,000 | Recurring / 継続 | Per month. 01 OBS-007, OBS-010 (frequency Q-8) |  |  |
| Operation / 運用 | Recurring DR drill (assumed every 6 months × 4 pd) | Infra / DevOps engineer / インフラ | person-days / 人日 | 0.67 | 55,000 | 36,850 | Recurring / 継続 | Per month equivalent. 01 OPS-007 (interval Q-6) |  |  |
| **Subtotal 1-9** | **Operation / 運用** |  |  |  |  | **610,600** | Recurring / 継続 | per month |  |  |
| Maintenance / 保守 | Quarterly re-run of every launch gate on staging, and on each AWS change a gate depends on (assumed 6 pd per quarter) | Senior engineer / シニアエンジニア | person-days / 人日 | 2.0 | 55,000 | 110,000 | Recurring / 継続 | Per month. 01 OPS-001; 02 §10 change gate [CMP §2.10]. Takes the place of [LGW]'s LiteLLM upgrade cycle (12 pd per quarter) |  |  |
| Maintenance / 保守 | Policy upkeep for new Bedrock operations, endpoints and condition keys; SCP and permission-policy updates | Senior engineer / シニアエンジニア | person-days / 人日 | 1.0 | 55,000 | 55,000 | Recurring / 継続 | Per month. 02 R-14, R-23; 01 SEC-020 |  |  |
| Maintenance / 保守 | Quarterly Japan model snapshot re-check of every catalog model and catalog updates (≈3 pd per quarter) | Engineer / エンジニア | person-days / 人日 | 1.0 | 42,500 | 42,500 | Recurring / 継続 | Per month. 01 MDL-104, AS-17; 02 §5.1 (R-19) |  |  |
| Maintenance / 保守 | Client package upkeep for new Claude Code, Codex CLI and AWS CLI releases | Engineer / エンジニア | person-days / 人日 | 1.0 | 42,500 | 42,500 | Recurring / 継続 | Per month. 02 §1.3 pinned versions, D-12 |  |  |
| Maintenance / 保守 | Patching: Lambda runtimes and dependencies, Inspector findings, advisories | Infra / DevOps engineer / インフラ | person-days / 人日 | 1.0 | 55,000 | 55,000 | Recurring / 継続 | Per month. 02 §8.3, SEC-016 ([LGW]: 2 pd for images, Aurora and Valkey) |  |  |
| Maintenance / 保守 | Bug fixes and minor changes to the spend guard, usage API, inventory job and llm helper | Engineer / エンジニア | person-days / 人日 | 2.0 | 42,500 | 85,000 | Recurring / 継続 | Per month. 02 R-13 |  |  |
| **Subtotal 1-10** | **Maintenance / 保守** |  |  |  |  | **390,000** | Recurring / 継続 | per month |  |  |

### 2. CROSS-CUTTING COSTS / 横断費用

| Category / phase | Task or item description | Role | Unit | Quantity | Unit cost (JPY) | Subtotal (JPY) | One-time / Recurring | Notes / assumptions | Likelihood | Impact (JPY) |
|---|---|---|---:|---:|---:|---:|---|---|---:|---:|
| Project management / プロジェクト管理 | *No line items: PM is calculated on Summary (PM % x development cost).* |  |  |  |  |  |  |  |  |  |
| Quality assurance & reviews / 品質保証 | Independent review of IaC and security-critical configuration (SCP, permission and trust policies, llm-guard-deny logic, bucket and resource control policies) before launch | Architect / tech lead / アーキテクト | person-days / 人日 | 5.0 | 70,000 | 350,000 | One-time / 初期 | 02 §4.7, §8, 04 §4.2, D-7 |  |  |
| Quality assurance & reviews / 品質保証 | Phase-gate reviews: design, build complete, launch readiness, GA | QA / test engineer / テスト担当 | person-days / 人日 | 4.0 | 40,000 | 160,000 | One-time / 初期 | 01 §1.4 exit criteria. 4 gates × 1 pd |  |  |
| **Subtotal 2-2** | **Quality assurance & reviews / 品質保証** |  |  |  |  | **510,000** | One-time / 初期 |  |  |  |
| Infrastructure / インフラ | Dev environment during the project (Tokyo) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 6.0 | 2,640 | 15,840 | One-time / 初期 | Quantity = 6 months (2027-02 to 2027-07). USD 16.50/month × 160 = J. Spend guard, usage API and stores at test volume USD 2.00; KMS (3 keys), S3, CloudWatch USD 6.50; GuardDuty, Security Hub, Config, Access Analyzer USD 8.00. 02 §10, 03 §2. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Staging environment during the project (Tokyo, same policies and spend guard as production) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 4.0 | 73,120 | 292,480 | One-time / 初期 | Quantity = 4 months (2027-04 to 2027-07). USD 457.00/month. AWS Private CA (general-purpose mode) for workload-certificate tests USD 401.50; Spend guard, usage API and stores at gate-test volume USD 3.00; Quick Sight: 1 author, 2 test readers (row-level security tests) USD 30.00; KMS (4 keys), S3, CloudWatch USD 10.50; GuardDuty, Security Hub, Config, Access Analyzer USD 12.00. 02 §10 (valid launch gates). [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo before GA (build and pilot) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 2.0 | 109,842 | 219,684 | One-time / 初期 | Quantity = 2 months (2027-06 to 2027-07). Same components as the recurring production rows below: USD 686.51/month. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | DR Osaka before GA (build and DR drill) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 2.0 | 1,798 | 3,596 | One-time / 初期 | Quantity = 2 months. Same components as the recurring DR rows below: USD 11.24/month. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Bedrock tokens used by the platform team during the project (development, tests, launch gates, DR drill) | Vendor / non-labor / 外部・非人件費 | one-time / 一式 | 1.0 | 340,800 | 340,800 | One-time / 初期 | Sizing: dev use ≈ USD 300/month × 6 + functional and gate tests ≈ USD 300 + quota checks ≈ USD 30 → ≈ USD 2,130 (as [LGW]; the spend guard load test replays events). Not charged back |  |  |
| Infrastructure / インフラ | Production Tokyo: Spend guard intake: SQS queue llm-meter-events | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 171 | 171 | Recurring / 継続 | Per month from GA. (1.68 M events × 1.2 + 0.66 M polls) × 0.40/M = USD 1.07. 02 §5.2, D-8; 1.68 M CloudTrail events a month from 1.09 M calls (2 per streaming call); send + batch receive/delete; Lambda long polling. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: Spend guard compute: 7 Lambda functions (arm64, 256 MB) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 67 | 67 | Recurring / 継続 | Per month from GA. 0.17 M invocations × 0.20/M + 29.0k GB-s × 0.0000133 = USD 0.42. 02 §5.2: llm-meter (batches of 100), llm-enforce (stream + every minute), llm-lifecycle (5-minute poll), llm-reconcile (4 CUR deliveries a day), llm-admin, llm-usage, inventory job. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: Spend guard store: DynamoDB global table llm-spend (Tokyo) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 728 | 728 | Recurring / 継続 | Per month from GA. 5.45 M writes × 0.715/M + 1 M reads × 0.1425/M + 1 GB × 0.285 + 1 GB PITR × 0.228 = USD 4.55. 02 §5.2, §7.1; on-demand; 5 counter updates per metered call, not batched (batching in llm-meter cuts this); stream reads by Lambda are free. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: Usage API: API Gateway REST API with IAM authorization | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 6 | 6 | Recurring / 継続 | Per month from GA. 0.01 M requests × 4.25/M = USD 0.04. 02 §3.1, D-14; llm usage by 30 engineers and team leads. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: CloudTrail data events: bedrock-mantle inference (Codex CLI) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 3 | 3 | Recurring / 継続 | Per month from GA. 18,000 events × 0.10/100k = USD 0.02. 02 §2.2, §7.4, R-18; Codex CLI assumed 20 % of coding-agent calls; management events are in the existing organization trail (first copy free). [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: Chargeback: CUR 2.0 with IAM principal data, Athena, Quick Sight | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 25,280 | 25,280 | Recurring / 継続 | Per month from GA. Athena 1 TB × 5 + 2 authors × 24 + 35 readers × 3 (CUR export and non-action Budgets free) = USD 158.00. 02 §5, D-9, D-14; readers = team leads and department contacts (30, as [LGW]) + 5 for the access inventory; Quick Sight reader [PL], author price as [LGW]. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: S3: configuration, access inventory, CUR export share | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 222 | 222 | Recurring / 継続 | Per month from GA. avg 30 GB × 0.025 + 50k PUT × 0.0047/1k + GET 0.40 = USD 1.39. 02 §7.1; daily inventory snapshot, versioned configuration, CUR rows per principal. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: KMS customer-managed keys | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 880 | 880 | Recurring / 継続 | Per month from GA. 4 CMKs × 1 + 0.5 M requests × 0.03/10k = USD 5.50. 02 §7.1: llm-spend (multi-Region primary), S3, CloudWatch Logs, CUR bucket. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: CloudWatch Logs, alarms, metrics and dashboards | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 1,578 | 1,578 | Recurring / 継続 | Per month from GA. 1.0 GB ingest × 0.76 + 3 GB stored × 0.033 + 30 alarms × 0.10 + 20 metrics × 0.30 (2 dashboards within the free 3) = USD 9.86. 02 §7.1, §9, OBS-006: function logs (metadata only), metering-delay and estimate-gap metrics, quota alarms at 80 %. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: AWS Private CA (general-purpose mode) for workload certificates | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 64,600 | 64,600 | Recurring / 継続 | Per month from GA. 1 CA × 400 + 5 certificates × 0.75 = USD 403.75. 02 §2.2, D-4, R-24; 10 DC workloads, 90-day certificates renewed at 60 days; short-lived mode (USD 50) issues only certificates of 7 days or less (finding F-1); the Osaka trust anchor uses this CA's certificate. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: GuardDuty (CloudTrail management events, Lambda network activity) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 1,438 | 1,438 | Recurring / 継続 | Per month from GA. (1.68 + 0.2) M events × 4.72/M + 0.1 GB × 1.18 = USD 8.99. 02 §2.2 threat detection, SEC-019; every Bedrock call is a management event; no ECS runtime monitoring. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: Security Hub CSPM, AWS Config, Inspector (Lambda), IAM Access Analyzer (unused access) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 2,867 | 2,867 | Recurring / 継続 | Per month from GA. 3k checks × 0.001 + 1k CIs × 0.003 + 3k evals × 0.001 + 8 functions × 0.0005/h × 730 h + 30 roles × 0.20 = USD 17.92. 02 §8, §8.3: Config rules (invocation logging off, no IAM users with Bedrock access, SCP attached), Lambda scanning, unused workload roles. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Production Tokyo: Bedrock tokens for platform tests (gate re-runs, probe) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 12,000 | 12,000 | Recurring / 継続 | Per month from GA. ≈ USD 200 per full gate run × 1 run/quarter + probe on Haiku 5.5 (< USD 1) = USD 75.00. OPS-001, AVL-M01; as [LGW]; platform's own usage, not charged back. [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | DR Osaka: DynamoDB global table llm-spend (Osaka replica) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 706 | 706 | Recurring / 継続 | Per month from GA. 5.45 M replicated writes × 0.715/M + 1 GB × 0.285 + 1 GB PITR × 0.228 = USD 4.41. 02 §7.1, §9, D-13, AVL-M03. [PL 2026-11-20] (ap-northeast-3) |  |  |
| Infrastructure / インフラ | DR Osaka: Spend guard standby: SQS polling and Lambda (Osaka) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 50 | 50 | Recurring / 継続 | Per month from GA. 0.66 M polls × 0.40/M + Lambda 0.05 = USD 0.31. 02 §9, D-13; deployed in both Regions, llm-enforce active in one. [PL 2026-11-20] (ap-northeast-3) |  |  |
| Infrastructure / インフラ | DR Osaka: KMS multi-Region replica keys (Osaka) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 320 | 320 | Recurring / 継続 | Per month from GA. 2 replica keys × 1 = USD 2.00. 02 §7.1. [PL 2026-11-20] (ap-northeast-3) |  |  |
| Infrastructure / インフラ | DR Osaka: CloudWatch alarms and logs (Osaka) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 184 | 184 | Recurring / 継続 | Per month from GA. 10 alarms × 0.10 + 0.2 GB × 0.76 = USD 1.15. 02 §9, OBS-006. [PL 2026-11-20] (ap-northeast-3) |  |  |
| Infrastructure / インフラ | DR Osaka: GuardDuty, Security Hub, Config (Osaka) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 539 | 539 | Recurring / 継続 | Per month from GA. 0.1 M events × 4.72/M + 1k checks × 0.001 + 300 CIs × 0.003 + 1k evals × 0.001 = USD 3.37. 02 §2.2 threat detection in both Regions; IAM Identity Center replica and Roles Anywhere have no charge. [PL 2026-11-20] (ap-northeast-3) |  |  |
| Infrastructure / インフラ | Dev environment after GA (Tokyo) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 2,640 | 2,640 | Recurring / 継続 | Per month. Same sizing as the project-period row: USD 16.50. Kept for maintenance (02 §10). [PL 2026-11-20] |  |  |
| Infrastructure / インフラ | Staging environment after GA (Tokyo) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 73,120 | 73,120 | Recurring / 継続 | Per month. Same sizing as the project-period row: USD 457.00, of which the Private CA is USD 401.50 (finding F-1). Needed for gate re-runs (OPS-001). [PL 2026-11-20] |  |  |
| **Subtotal 2-3** | **Infrastructure / インフラ** |  |  |  |  | **872,400** | One-time / 初期 |  |  |  |
| **Subtotal 2-3** | **Infrastructure / インフラ** |  |  |  |  | **187,399** | Recurring / 継続 | per month |  |  |
| Software licenses & tools / ライセンス・ツール | *No line items: no licensed software (01 AS-6 and Q-17 withdrawn; no LiteLLM).* |  |  |  |  |  |  |  |  |  |
| Security / セキュリティ | Security design review: threat model and residual-risk acceptance (R-34), SCP and policy layers, spend guard failure modes, break-glass | Security specialist / セキュリティ | person-days / 人日 | 8.0 | 80,000 | 640,000 | One-time / 初期 | 02 §4.7, §8, §8.1, R-34. No guardrail service or proxy to review ([LGW]: 10 pd) |  |  |
| Security / セキュリティ | Third-party penetration test before launch, focused on the policy layers | Vendor / non-labor / 外部・非人件費 | one-time / 一式 | 1.0 | 2,000,000 | 2,000,000 | One-time / 初期 | 02 §8.3 (R-34). Price = template sample value, as [LGW], placeholder until a vendor quote (Security); no web application is in scope, so a quote may be lower |  |  |
| **Subtotal 2-5** | **Security / セキュリティ** |  |  |  |  | **2,640,000** | One-time / 初期 |  |  |  |
| Contingency & risk buffer / 予備費 | Risk R-12 / Q-24: Route A adopted for GA (D-6) — endpoint VPC, endpoints, Resolver, DNS forwarding, endpoint policies | Infra / DevOps engineer / インフラ | person-days / 人日 | 15.0 | 55,000 | 412,500 | One-time / 初期 | 02 §14 R-12 / Q-24 (likelihood Medium = 50 %, column K). Impact 15 pd, as [LGW]'s Route A option. 01 SEC-014, RES-007 | 50.0% | 825,000 |
| Contingency & risk buffer / 予備費 | Risk R-12 / Q-24: Route A recurring part — interface endpoints over Direct Connect (Tokyo) | Vendor / non-labor / 外部・非人件費 | monthly fee / 月額 | 1.0 | 67,794 | 33,897 | Recurring / 継続 | 02 §14 R-12 / Q-24 (likelihood Medium = 50 %, column K). Impact USD 423.71/month (§9). Osaka endpoints created at failover, not priced. [PL 2026-11-20] | 50.0% | 67,794 |
| Contingency & risk buffer / 予備費 | Risk R-2: CUR lacks the session name, bedrock-mantle or short-term-key attribution — per-person attribution from CloudTrail joined to CUR | Engineer / エンジニア | person-months / 人月 | 1.0 | 850,000 | 425,000 | One-time / 初期 | 02 §14 R-2 (likelihood Medium = 50 %, column K). Impact 1.0 pm. 01 AS-24, CST-007; V-15 | 50.0% | 850,000 |
| Contingency & risk buffer / 予備費 | Risk R-30 / AS-25: stream-completion events do not reach EventBridge — meter from the trail's S3 delivery instead (longer delay) | Senior engineer / シニアエンジニア | person-months / 人月 | 1.0 | 1,100,000 | 550,000 | One-time / 初期 | 02 §14 R-30 / AS-25 (likelihood Medium = 50 %, column K). Impact 1.0 pm. 01 CST-009; V-13 | 50.0% | 1,100,000 |
| Contingency & risk buffer / 予備費 | Risk R-9: one permission set per team exceeds the Identity Center quotas — team from an Entra attribute (ABAC, ADR D-2 option 2) | Senior engineer / シニアエンジニア | person-months / 人月 | 1.0 | 1,100,000 | 550,000 | One-time / 初期 | 02 §14 R-9 (likelihood Medium = 50 %, column K). Impact 1.0 pm: policies, spend guard, CUR views. 01 Q-22, AS-26 | 50.0% | 1,100,000 |
| Contingency & risk buffer / 予備費 | Risk R-35: Identity Center replication not available for our instance — another sign-in path for DR | Senior engineer / シニアエンジニア | person-days / 人日 | 10.0 | 55,000 | 275,000 | One-time / 初期 | 02 §14 R-35 (likelihood Medium = 50 %, column K). Impact 10 pd. 01 AVL-001, AS-23 | 50.0% | 550,000 |
| Contingency & risk buffer / 予備費 | Risk R-5 / Q-13: Security requires screening for some OUs — Classic-tier Bedrock guardrail with regex filters through a Bedrock policy | Senior engineer / シニアエンジニア | person-days / 人日 | 10.0 | 55,000 | 275,000 | One-time / 初期 | 02 §14 R-5 / Q-13 (likelihood Medium = 50 %, column K). Impact 10 pd; regex sensitive-information filters have no charge [PL AmazonBedrock 2026-11-11]. 01 SEC-008, D-10 | 50.0% | 550,000 |
| Contingency & risk buffer / 予備費 | Risk Q-10 / D-11: per-team content logging required this phase — content-logging account, invocation logging, Macie, V-1 re-run | Senior engineer / シニアエンジニア | person-months / 人月 | 0.5 | 1,100,000 | 275,000 | One-time / 初期 | 01 Q-10 / D-11 (likelihood Medium = 50 %, column K). Impact 0.5 pm: account-level configuration ([LGW] R-6: 1.0 pm). 01 PRV-002 | 50.0% | 550,000 |
| Contingency & risk buffer / 予備費 | Risk R-8: AWS CLI caches credentials in files — llm helper keeps the cache in the OS credential store | Engineer / エンジニア | person-days / 人日 | 10.0 | 42,500 | 212,500 | One-time / 初期 | 02 §14 R-8 (likelihood Medium = 50 %, column K). Impact 10 pd. 02 §8.1 | 50.0% | 425,000 |
| Contingency & risk buffer / 予備費 | Risk R-4: Codex CLI's model choice in Japan is unclear — workaround or limited approval | Engineer / エンジニア | person-days / 人日 | 10.0 | 42,500 | 318,750 | One-time / 初期 | 02 §14 R-4 (likelihood High = 75 %, column K). Impact 10 pd. 01 FUN-002; T-002 | 75.0% | 425,000 |
| Contingency & risk buffer / 予備費 | Risk R-1 / R-6: heavy or non-streaming workloads need their own enrolled accounts — enrolment, quotas, budgets | Infra / DevOps engineer / インフラ | person-days / 人日 | 5.0 | 55,000 | 206,250 | One-time / 初期 | 02 §14 R-1 / R-6 (likelihood High = 75 %, column K). Impact 5 pd. D-18; 01 CST-009, CST-014 | 75.0% | 275,000 |
| **Subtotal 2-6** | **Contingency & risk buffer / 予備費** |  |  |  |  | **3,500,000** | One-time / 初期 |  |  |  |
| **Subtotal 2-6** | **Contingency & risk buffer / 予備費** |  |  |  |  | **33,897** | Recurring / 継続 | per month |  |  |

## 3. Rates / 単価表

Working days per month / 月間稼働日数: **20** (1 person-month = 20 person-days = 160 h)

**OPEN ITEM (FinOps): there are no internal rates yet. These are the template's sample rates (indicative blended market rates, excl. tax), kept unchanged as in [LGW]; replace them on the Rates sheet.**

| Role / 役割 | Monthly rate (JPY / person-month) | Daily rate (JPY / person-day) | Used in this estimate |
|---|---:|---:|---|
| Project manager / PM | 1,500,000 | 75,000 | - |
| Architect / tech lead / アーキテクト | 1,400,000 | 70,000 | 4 rows |
| Business analyst / SE / 業務SE | 1,200,000 | 60,000 | 1 rows |
| Senior engineer / シニアエンジニア | 1,100,000 | 55,000 | 16 rows |
| Engineer / エンジニア | 850,000 | 42,500 | 23 rows |
| UI/UX designer / デザイナー | 1,000,000 | 50,000 | - |
| QA / test engineer / テスト担当 | 800,000 | 40,000 | 7 rows |
| Infra / DevOps engineer / インフラ | 1,100,000 | 55,000 | 13 rows |
| Security specialist / セキュリティ | 1,600,000 | 80,000 | 3 rows |
| Tech writer / trainer / ライター・講師 | 700,000 | 35,000 | 2 rows |
| Operations engineer / 運用担当 | 750,000 | 37,500 | 2 rows |
| Help desk / ヘルプデスク | 550,000 | 27,500 | 1 rows |
| Vendor / non-labor / 外部・非人件費 |  |  | No rate: prices in column J |

## 4. Assumptions and exclusions / 前提条件・対象外事項

### A. Assumptions / 前提条件

| No. | Area / 区分 | Description (English) | 内容（日本語） |
|---|---|---|---|
| A1 | Scope / 範囲 | Build and 24-month operation of the IAM-native LLM gateway as designed in 01 and 02 v0.1 (Draft, 2026-11-20): no gateway server; IAM Identity Center, IAM policies and SCPs, CUR 2.0 by IAM principal and a serverless spend guard; Tokyo with DR in Osaka; the Bedrock catalog in 01 §6.5; Route B for the pilot and GA, with Route A as a contingency row (02 D-6, 01 Q-24). | 01・02 v0.1（作成中、2026-11-20）で設計されたIAMネイティブLLMゲートウェイの構築と24か月の運用を対象とする。ゲートウェイサーバーなし。IAM Identity Center、IAMポリシーとSCP、IAMプリンシパル別のCUR 2.0、サーバーレスのスペンドガード。東京、DRは大阪。01 §6.5のBedrockモデル。パイロット・GAともRoute Bとし、Route Aは予備費の行として計上（02 D-6、01 Q-24）。 |
| A2 | Comparability / 比較の前提 | To compare with the LiteLLM design's estimate ([LGW] cost/, commit 87ba355), this estimate keeps its schedule, usage basis, rates, exchange rate, template parameters, penetration-test placeholder and platform Bedrock usage. Differences come only from the design. | LiteLLM設計の見積（[LGW]のcost/、コミット87ba355）と比較するため、スケジュール、利用量の前提、単価、為替レート、テンプレートのパラメータ、ペネトレーションテストの仮価格、基盤のBedrock利用量は同じとする。差は設計の違いからのみ生じる。 |
| A3 | Schedule / スケジュール | Project 2027-01 to 2027-07 (7 months), as [LGW]: M1 remaining requirements, design and spikes; M2–M5 build; M4–M6 tests and launch gates; M6 production and DR build, penetration test; M7 pilot and DR drill. GA 2027-08. Recurring costs start at GA; operation period 24 months (2027-08 to 2029-07). Dates are open (01 Q-3); the smaller build may allow an earlier GA. | プロジェクト期間 2027年1月〜7月（7か月、[LGW]と同じ）：1か月目 残りの要件・設計・早期検証、2〜5か月目 構築、4〜6か月目 テスト・ローンチゲート、6か月目 本番・DR構築とペネトレーションテスト、7か月目 パイロットとDR訓練。2027年8月GA。継続費用はGAから発生し、運用期間は24か月（2027年8月〜2029年7月）。日程は未確定（01 Q-3）。構築規模が小さいためGAを早められる可能性がある。 |
| A4 | Effort unit / 工数単位 | 1 person-month = 20 person-days = 160 hours (Rates sheet). Rates are blended and exclude tax. | 1人月＝20人日＝160時間（Ratesシート）。単価は平均単価・税抜。 |
| A5 | Rates / 単価 | OPEN ITEM (FinOps): no internal rates exist yet. The template's sample rates (indicative FY2026 market rates) are kept unchanged, as in [LGW], and are not quotes. Replace them on the Rates sheet; every labor row updates. | 【未決事項・FinOps】社内単価が未設定のため、[LGW]と同じくテンプレートのサンプル単価（2026年度の参考相場）をそのまま使用しており、見積回答ではない。Ratesシートで置き換えると全工数行が更新される。 |
| A6 | Recurring costs / 継続費用 | Recurring lines are monthly amounts; annual = monthly x 12. The grand total includes 24 recurring months (the operation period). The markdown output also gives 12- and 36-month views. | 継続費用は月額で計上し、年額＝月額×12。総額には運用期間の24か月分の継続費用を含む。Markdown出力には12か月・36か月の試算も記載。 |
| A7 | Project management / PM費 | Project management = PM % (10 %, template default) x development cost (one-time phase-based costs). PM effort is not included in phase rows. | PM費＝PM費率（10%、テンプレート既定値）×開発費（工程別の初期費用）。工程別の行にはPM工数を含めない。 |
| A8 | Contingency / 予備費 | Contingency = 15 % (template default) of initial cost excluding contingency, plus 15 % of monthly recurring cost. Identified risks from 02 §14 and 01 §9 are line items with their impact as Quantity x Unit cost and their likelihood in column K (Low 25 %, Medium 50 %, High 75 %), so Subtotal = impact x likelihood. Tax is never included in the base. | 予備費＝予備費を除く初期費用×15%（既定値）＋継続月額×15%。02 §14・01 §9の特定済みリスクは、影響額を数量×単価、発生確率をK列（低25%、中50%、高75%）に入力した明細とし、小計＝影響額×発生確率。消費税は算定基礎に含めない。 |
| A9 | Tax / 消費税 | Consumption tax is calculated once on each total at the rate on Summary; amounts below JPY 1 are rounded down. | 消費税はSummaryの税率で各合計に対して1回計算し、1円未満は切り捨て。 |
| A10 | Cloud / クラウド | AWS On-Demand list prices from the AWS Price List API offer files for ap-northeast-1 and ap-northeast-3 (publications 2026-10-30 to 2026-11-19, checked 2026-11-20), cited as [PL]; the Quick Sight author price is [LGW]'s (pricing page, 2026-11-17). 730 h per month; no Savings Plans or EDP discounts; free tiers are not applied. Budget exchange rate JPY 160 / USD, as [LGW]. OPEN ITEM (FinOps): confirm the budget rate. | AWSの価格はAWS Price List API（ap-northeast-1／ap-northeast-3、2026-10-30〜2026-11-19公開版、2026-11-20確認）のオンデマンド定価（[PL]と表記）。Quick Sightの作成者の価格は[LGW]の値（料金ページ、2026-11-17）。1か月730時間、Savings Plans・EDP割引は考慮せず、無料枠も適用しない。予算レートは[LGW]と同じ1USD＝160円。【未決事項・FinOps】予算レートの確認。 |
| A11 | No-charge services / 無料のサービス | IAM, IAM Identity Center (incl. its Osaka replica), AWS Organizations and SCPs, IAM Roles Anywhere, AWS Signer for Lambda, CUR 2.0 data exports, AWS Budgets without actions, and AWS service events on the EventBridge default bus have no charge (AWS pricing pages; not in [PL]). Organization trail management events are its first copy. | IAM、IAM Identity Center（大阪のレプリカを含む）、AWS OrganizationsとSCP、IAM Roles Anywhere、Lambda向けAWS Signer、CUR 2.0のデータエクスポート、アクションなしのAWS Budgets、EventBridgeのデフォルトバス上のAWSサービスイベントは無料（AWSの料金ページ。[PL]には含まれない）。組織証跡の管理イベントは最初のコピー。 |
| A12 | Environments / 環境 | Accounts llm-dev, llm-staging and llm-prod (Tokyo, with DR in Osaka in the same account), as 02 §10 and D-18. Staging has the same SCP, policy shapes, catalog and spend guard as production, so that launch gates are valid, and a Private CA of its own. Dev and staging remain after GA. | アカウントはllm-dev、llm-staging、llm-prod（東京、DRは同一アカウントの大阪）（02 §10、D-18）。ステージングは、ローンチゲートが有効となるよう本番と同じSCP・ポリシーの形・カタログ・スペンドガードを持ち、専用のPrivate CAを持つ。開発・ステージングはGA後も維持する。 |
| A13 | Sizing / サイジング | No fixed capacity: every component is serverless or a regional AWS service. Per-call charges use [LGW]'s expected usage: about 1.09 million model calls a month (30 engineers plus workloads), 1.68 million CloudTrail events (2 per streaming call; workloads half streaming), 5 counter updates per metered call, 6 teams, 10 DC workloads. §10 shows the per-call charges at higher volumes. | 固定容量なし：全コンポーネントがサーバーレスまたはリージョンのAWSサービス。従量部分は[LGW]の想定利用量による：モデル呼び出し月約109万回（エンジニア30人とワークロード）、CloudTrailイベント月168万件（ストリーミング1回につき2件、ワークロードは半数がストリーミング）、計測1回につきカウンター更新5件、6チーム、DCワークロード10件。§10に利用量が多い場合の従量費用を示す。 |
| A14 | Users / 利用者 | 30 engineers use the gateway with coding agents (set by the requester on 2026-11-17 for [LGW], kept here). CMP A-9 (about 5,000 employees, about 300 concurrent users) is not used for sizing. Workload volume (UC-2) is as in the markdown usage table. | コーディングエージェントでゲートウェイを利用するエンジニアは30人（2026-11-17に依頼者が[LGW]用に設定した値を踏襲）。CMP A-9（従業員約5,000人、同時約300人）はサイジングに使わない。ワークロード（UC-2）の利用量はMarkdownの利用試算表のとおり。 |
| A15 | Model usage / モデル利用料 | Bedrock token charges for teams are not in the totals: CUR 2.0 charges them to the calling principal (01 CST-007). The markdown output gives the same low / expected / high usage table as [LGW]. Bedrock tokens used by the platform team itself (development, tests, gates, probe) are included. | チームのBedrockトークン料金は合計に含めない（CUR 2.0で呼び出し元のプリンシパルに配賦、01 CST-007）。Markdown出力に[LGW]と同じ低・想定・高の利用試算を記載。基盤チーム自身の利用（開発・テスト・ゲート・監視プローブ）は計上する。 |
| A16 | Licences / ライセンス | No licensed software: no LiteLLM (01 AS-6 and Q-17 withdrawn). The Bedrock guardrail option uses regex filters, which have no charge. | ライセンスが必要なソフトウェアなし：LiteLLMを使わない（01 AS-6・Q-17は取り下げ）。Bedrockガードレールの選択肢は無料の正規表現フィルターを使う。 |
| A17 | Certificates / 証明書 | AWS Private CA in general-purpose mode, one in llm-prod and one in llm-staging, because workload certificates last up to 90 days (02 D-4) and short-lived mode issues only certificates of 7 days or less. Using an existing corporate CA as the trust anchor would remove both (finding F-1). | ワークロード証明書の有効期間は最大90日（02 D-4）で、短期証明書モードは7日以下の証明書しか発行できないため、汎用モードのAWS Private CAをllm-prodとllm-stagingに1つずつ置く。既存の社内CAをトラストアンカーにすれば両方とも不要になる（指摘F-1）。 |
| A18 | Delivery team / 実施体制 | Platform engineering does all build and run work estimated here, using the template roles. Penetration test is by a third party; its price is the template sample value until a vendor quote (OPEN ITEM, Security). | 本見積の構築・運用作業はプラットフォームエンジニアリングがテンプレートの役割で実施する。ペネトレーションテストは外部委託で、ベンダー見積までテンプレートのサンプル価格を使用（【未決事項・セキュリティ】）。 |
| A19 | Data migration / データ移行 | No data migration: 01 and 02 define none, and what the gateway replaces is still open (01 Q-2). | データ移行なし：01・02に定義がなく、置き換え対象も未確定（01 Q-2）。 |
| A20 | Support hours / サポート時間 | On-call covers business hours (01 OPS-006, Q-6 open). 24x7 on-call would increase the Operation rows. | オンコールは業務時間帯を前提（01 OPS-006、Q-6未確定）。24時間365日対応の場合、運用の行が増える。 |

### B. Exclusions (not covered by this estimate) / 対象外事項

| No. | Area / 区分 | Description (English) | 内容（日本語） |
|---|---|---|---|
| B1 | Model inference / モデル利用料 | Bedrock token charges for teams' usage (charged to the calling principal through CUR 2.0, 01 CST-007). See the separate usage table in the markdown output. | 各チームの利用によるBedrockトークン料金（CUR 2.0で呼び出し元のプリンシパルに配賦、01 CST-007）。Markdown出力の別表を参照。 |
| B2 | Route A at full cost / Route Aの全額 | Route A is in the totals only at its expected value (contingency, 50 %). Its full cost is in §9 of the markdown output. | Route Aは期待値（予備費、50%）でのみ合計に含める。全額はMarkdown出力の§9に記載。 |
| B3 | Azure OpenAI / Azure OpenAI | Azure OpenAI is not reachable without a proxy (01 NG-10, MDL-011), so it has no option here. | Azure OpenAIはプロキシなしでは利用できないため（01 NG-10、MDL-011）、本見積に選択肢はない。 |
| B4 | Remote access / リモートアクセス | Remote and home access (01 NG-1, R-27). | リモート・在宅アクセス（01 NG-1、R-27）。 |
| B5 | Internal staff / 社内要員 | Time of other internal teams for their own deliverables: Network (egress list, secure web gateway rules, V-11 data), Identity (Entra app, Conditional Access, groups), Endpoint/Intune (client deployment), Cloud platform (SCP attachment, Identity Center, CUR), Legal/privacy and FinOps approvals, users attending training. | 他部門の要員工数：ネットワーク（出口IP一覧、セキュアWebゲートウェイのルール、V-11の情報）、ID管理（Entraアプリ、条件付きアクセス、グループ）、端末/Intune（クライアント配布）、クラウド基盤（SCPの適用、Identity Center、CUR）、法務・FinOpsの承認、研修受講者。 |
| B6 | Shared platforms / 共有基盤 | Costs of shared platforms already paid elsewhere: the organization CloudTrail trail and log-archive account, SIEM licence, ingestion and correlation rules (02 R-34), Direct Connect circuits, corporate Git/CI, Entra ID P1/P2, Okta and Intune licences. | 他で負担済みの共有基盤費用：組織のCloudTrail証跡とログアーカイブアカウント、SIEMのライセンス・取り込み・相関ルール（02 R-34）、Direct Connect回線、社内Git/CI、Entra ID P1/P2・Okta・Intuneのライセンス。 |
| B7 | Support contracts / サポート契約 | AWS Support plan (01 Q-20). | AWSサポートプラン（01 Q-20）。 |
| B8 | Enhancements / 機能追加 | New endpoint families (01 NG-7), response caching, API translation for tools that speak only the OpenAI format (NG-10), per-caller rate limits (NG-12), and features beyond the maintenance allowance. | 新しいエンドポイント種別（01 NG-7）、レスポンスキャッシュ、OpenAI形式のみのツール向けのAPI変換（NG-10）、呼び出し元ごとのレート制限（NG-12）、保守範囲を超える機能追加。 |
| B9 | Enrolled accounts / 登録アカウント | AWS charges in enrolled workload accounts (D-18) other than their Bedrock tokens; their VPC endpoints and budgets belong to their owners (R-32). | 登録されたワークロードアカウント（D-18）のBedrockトークン以外のAWS料金。そのVPCエンドポイントと予算は各所有者が負担（R-32）。 |
| B10 | Expenses / 経費 | Travel, accommodation and on-site expenses. | 出張・宿泊・現地作業に伴う経費。 |
| B11 | Unlisted purchases / 記載外の購入 | Hardware or software not listed on the Estimate sheet; end-user devices and office network changes. | Estimateシートに記載のないハードウェア・ソフトウェア、利用者端末および社内ネットワークの変更。 |
| B12 | Price changes / 価格変動 | Exchange-rate movements beyond JPY 160 / USD and AWS price changes after 2026-11-20. | 1USD＝160円を超える為替変動、および2026-11-20以降のAWSの価格改定。 |
| B13 | Legal & audit / 法務・監査 | Legal, regulatory or external audit fees, incl. any ISO 27001 / SOC 2 work (01 Q-19). | 法務・規制対応・外部監査の費用（ISO 27001／SOC 2対応を含む、01 Q-19）。 |
| B14 | Decommissioning / 旧システム廃止 | Decommissioning of anything the gateway replaces (01 Q-2 open). | ゲートウェイが置き換えるものの廃止作業（01 Q-2未確定）。 |

## 5. Lists / プルダウン用リスト

Unchanged from the template: units person-months / person-days / monthly fee / one-time; types One-time / Recurring; the 10 phase-based and 6 cross-cutting categories in the breakdown above.

## 6. Calculation rules / 計算ルール

| Item | Rule |
|---|---|
| Unit cost / 単価 | Override (column J) if entered, else role rate from Rates (monthly for person-months, daily for person-days) |
| Subtotal / 小計 | Quantity × Unit cost; on Contingency rows with a likelihood in K: Quantity × Unit cost × likelihood |
| Development cost / 開発費 | Sum of one-time costs in phase-based categories |
| Project management / PM費 | PM % × development cost |
| Contingency / 予備費 | Contingency % × initial cost before contingency, + contingency % × monthly recurring cost; plus identified-risk line items at expected value (impact × likelihood) |
| Total initial cost / 初期費用 | All one-time costs (phase-based + cross-cutting, incl. PM and contingency) |
| Recurring – monthly / 継続月額 | Sum of recurring rows (+ recurring contingency) |
| Grand total / 総額 | Initial cost + monthly recurring × 24 months |
| Consumption tax / 消費税 | Each total × tax rate, calculated once per total, rounded down to JPY 1 |

## 7. Comparison with the LiteLLM design's estimate [LGW]

[LGW] is the estimate in ai-gateway-on-aws cost/ (commit 87ba355): the same template, schedule, usage basis (30 engineers, about 1.1 million calls a month), rates, exchange rate and parameters. Both exclude model inference, which is the same in both designs (§8). Amounts in JPY, excl. tax.

### 7.1 Totals

| Item | This design | [LGW] | Difference | This / [LGW] |
|---|---:|---:|---:|---:|
| Total initial cost (one-time) | 41,509,110 | 43,820,838 | −2,311,728 | 95% |
| Total recurring cost – monthly | 1,400,096 | 3,019,657 | −1,619,561 | 46% |
| Total recurring cost – annual | 16,801,152 | 36,235,887 | −19,434,735 | 46% |
| **Grand total (initial + 24 months), excl. tax** | **75,111,414** | **116,292,612** | **−41,181,198** | **65%** |
| Grand total, incl. tax | 82,622,555 | 127,921,873 | −45,299,318 | 65% |
| Development cost (base for PM %) | 26,390,000 | 26,620,000 | −230,000 | 99% |
| One-time effort excl. contingency rows (person-months) | 27.6 | 27.6 | +0.1 | 100% |

The template's own indicator 'Total one-time effort' (§1) counts risk rows at their full impact when the likelihood is in column K, as here; [LGW] put the expected value into Quantity instead. The row above leaves contingency rows out of both, so the two are comparable.

### 7.2 By category

| Category | One-time: this | One-time: [LGW] | Difference | Monthly: this | Monthly: [LGW] | Difference |
|---|---:|---:|---:|---:|---:|---:|
| Requirements definition / 要件定義 | 1,480,000 | 1,180,000 | +300,000 | - | - | - |
| Basic & detailed design / 基本・詳細設計 | 4,115,000 | 3,825,000 | +290,000 | - | - | - |
| Implementation / 実装 | 10,175,000 | 11,312,500 | −1,137,500 | - | - | - |
| Testing (unit, integration, system, UAT) / テスト | 5,562,500 | 4,900,000 | +662,500 | - | - | - |
| Data migration / データ移行 | - | - | - | - | - | - |
| Setup, build & deployment / 構築・リリース | 1,435,000 | 1,820,000 | −385,000 | - | - | - |
| Training & documentation / 教育・ドキュメント | 1,895,000 | 1,895,000 | - | - | - | - |
| Cutover & go-live support / 本番移行・稼働支援 | 1,727,500 | 1,687,500 | +40,000 | - | - | - |
| Operation / 運用 | - | - | - | 610,600 | 837,500 | −226,900 |
| Maintenance / 保守 | - | - | - | 390,000 | 512,500 | −122,500 |
| Project management / プロジェクト管理 | - | - | - | - | - | - |
| Project management (PM % of development cost) | 2,639,000 | 2,662,000 | −23,000 |  |  |  |
| Quality assurance & reviews / 品質保証 | 510,000 | 510,000 | - | - | - | - |
| Infrastructure / インフラ | 872,400 | 3,257,642 | −2,385,242 | 187,399 | 963,892 | −776,493 |
| Software licenses & tools / ライセンス・ツール | - | - | - | - | - | - |
| Security / セキュリティ | 2,640,000 | 2,800,000 | −160,000 | - | - | - |
| Contingency & risk buffer / 予備費 | 3,500,000 | 2,593,750 | +906,250 | 33,897 | 358,681 | −324,784 |
| Contingency buffer (15 %) | 4,957,710 | 5,377,446 | −419,736 | 178,200 | 347,084 | −168,884 |
| **Total (excl. tax)** | **41,509,110** | **43,820,838** | **−2,311,728** | **1,400,096** | **3,019,657** | **−1,619,561** |

### 7.3 Monthly AWS cost by environment (USD, before conversion)

| Environment | This design | [LGW] | Difference |
|---|---:|---:|---:|
| Production (Tokyo) | 686.51 | 2,480.32 | −1,793.81 |
| DR (Osaka) | 11.24 | 955.05 | −943.81 |
| Dev (Tokyo) | 16.50 | 501.86 | −485.36 |
| Staging (Tokyo) | 457.00 | 2,087.09 | −1,630.09 |
| **Total** | **1,171.25** | **6,024.32** | **−4,853.07** |

Two general-purpose Private CAs (production and staging) are USD 800 of this design's USD 1,171 a month (finding F-1). [LGW] also had no Private CA in its base (only in contingency row R-3).

### 7.4 Where the difference comes from

| Driver | Category | One-time (JPY) | Monthly (JPY) |
|---|---|---:|---:|
| No servers, database, cache, load balancer, WAF or VPC endpoints to run (02 §2.2, 00 §1.6) | Infrastructure | −2,385,242 | −776,493 |
| Less to build: no guardrail service (D-10), no LiteLLM configuration or images; new: the spend guard, policy generator and a larger llm helper | Implementation | −1,137,500 | - |
| More open questions (26 vs 20) and early spikes: the design rests on AWS behaviours not yet checked (R-2, R-25, R-29, R-30, AS-24, AS-25); a smaller guardrail decision | Design, requirements | +590,000 | - |
| More tests (86 vs 75) and project gates V-12 to V-16; V-3, V-8, V-9 are n/a; no AZ-loss or task-sizing tests | Testing | +662,500 | - |
| No LiteLLM upgrades or guardrail upkeep; quarterly gate re-runs and policy upkeep instead; half the on-call load | Operation, maintenance | - | −349,400 |
| Setup, training, cutover, QA, security: smaller CI/CD, fewer components to review | Other phases | −505,000 | - |
| Identified risks: Route A for GA at 50 % (D-6), AWS-behaviour fallbacks; [LGW]'s GPU guardrail, mTLS and egress risks do not apply | Contingency (identified risks) | +906,250 | −324,784 |
| PM % and the 15 % buffer follow the base | PM, contingency buffer | −442,736 | −168,884 |
| **Total difference** |  | **−2,311,728** | **−1,619,561** |

The build costs about the same as [LGW]'s: what this design saves in components it spends on custom code, spikes and tests. The saving is in running it: 46 % of [LGW]'s monthly cost.

Labor is most of both estimates: one-time labor excl. contingency is JPY 27,540,000 here; in [LGW] it is JPY 27,930,000.

### 7.5 What the totals do not show

- **[LGW] is understated by its licence.** Its LiteLLM Enterprise licence row has no price (its check 'Rows with quantity but no amount' = 1), so its totals exclude a recurring licence fee that this design does not pay.
- **Capabilities differ.** This design gives up in-path guardrails for Japanese text (SEC-008 deferred, D-10), per-caller rate limits (NG-12), API translation (NG-10) and Azure OpenAI; budgets act within minutes instead of in real time (CST-009). ADR D-1 §5 lists every difference. The estimate prices the design as it is, not these gaps.
- **Per-call charges scale with use.** [LGW]'s AWS cost is mostly fixed capacity; this design's is mostly fixed (Private CA, Quick Sight) at 30 engineers, but its per-call charges grow linearly with calls (§10).
- **Route A is counted differently.** [LGW] kept Route B for GA and priced Route A outside its totals; this design proposes Route A for GA (D-6), so it is in contingency at 50 % here and at full cost in §9.

## 8. Model usage (Bedrock tokens) — not in the totals

Model inference is a variable cost charged to the principal that makes each call (01 CST-007, 02 §5, D-9), so it is an exclusion (B1) and not part of the totals above. Both designs call the same models through the same `jp.` profiles and In-Region models, so the tokens and prices are those of [LGW] §7 (Bedrock on-demand, [PL] AmazonBedrock and AmazonBedrockFoundationModels, ap-northeast-1, checked 2026-11-17), and the cost is the same.

### 8.1 Prices used (USD per 1 million tokens)

| Catalog ID | Model | How processed in Japan (01 §6.5) | Input | Cache write | Cache read | Output |
|---|---|---|---:|---:|---:|---:|
| MDL-001 | Claude Opus 5.5 | `jp.` profile | 4.4 | 5.5 | 0.22 | 22 |
| MDL-002 | Claude Haiku 5.5 | `jp.` profile | 0.11 | 0.1375 | 0.011 | 0.55 |
| MDL-003 | Claude Opus 4.8 | `jp.` profile | 5.5 | 6.875 | 0.55 | 27.5 |
| MDL-004 | Claude Sonnet 4.6 | `jp.` profile | 3.3 | 4.125 | 0.33 | 16.5 |
| MDL-005 | Claude Haiku 4.5 | `jp.` profile | 1.1 | 1.375 | 0.11 | 5.5 |
| MDL-006 | Amazon Nova 2 Lite | `jp.` profile | 0.396 | - | 0.099 | 3.311 |
| MDL-007 | Titan Text Embeddings V2 | In-Region Tokyo | 0.029 | - | - | - |
| MDL-008 | Cohere Embed v4 | In-Region Tokyo | 0.12 | - | - | - |
| MDL-009 | Mistral Large 3 | In-Region Tokyo | 0.61 | - | - | 1.82 |
| MDL-010 | gpt-oss-120b | In-Region Tokyo | 0.18 | - | - | 0.73 |

### 8.2 Scenario assumptions

| Driver | Low | Expected | High | Basis |
|---|---:|---:|---:|---|
| Active coding-agent users per month | 30 | 30 | 30 | 30 engineers, as [LGW] (A14); scenarios vary active days and workload volume only |
| Active days per user per month | 12 | 15 | 19 | As [LGW] §7.2 (Claude Code cost docs: about USD 13 per developer per active day, USD 150–250 a month) |
| Tokens per active user-day (M): input / cache write / cache read / output | 0.6 / 0.4 / 12 / 0.25 | 0.6 / 0.4 / 12 / 0.25 | 0.6 / 0.4 / 12 / 0.25 | Calibrated so a full day on Claude Opus 5.5 costs about USD 13 (USD 12.98) |
| Model mix for coding agents |  | Opus 5.5 60 %, Haiku 5.5 20 %, Sonnet 4.6 15 %, Opus 4.8 5 % |  | As [LGW]; 01 §6.5 UC-1 models (Q-4 open) |
| Workloads (UC-2), share of expected volume | 25 % | 100 % | 300 % | As [LGW]: Haiku 4.5 1.0 B in / 0.2 B out; Nova 2 Lite 1.0 / 0.2; gpt-oss-120b 0.3 / 0.06; Mistral Large 3 0.2 / 0.04; Titan V2 and Cohere v4 embeddings 0.5 B each (01 Q-4, Q-7) |

### 8.3 Monthly usage and cost by model

| Catalog ID | Model | Tokens/month Low (B) | Expected (B) | High (B) | JPY/month Low | Expected | High |
|---|---|---:|---:|---:|---:|---:|---:|
| MDL-001 | Claude Opus 5.5 | 2.9 | 3.6 | 4.5 | 448,589 | 560,736 | 710,266 |
| MDL-002 | Claude Haiku 5.5 | 1.0 | 1.2 | 1.5 | 4,499 | 5,623 | 7,123 |
| MDL-003 | Claude Opus 4.8 | 0.2 | 0.3 | 0.4 | 56,232 | 70,290 | 89,034 |
| MDL-004 | Claude Sonnet 4.6 | 0.7 | 0.9 | 1.1 | 101,218 | 126,522 | 160,261 |
| MDL-005 | Claude Haiku 4.5 | 0.3 | 1.2 | 3.6 | 88,000 | 352,000 | 1,056,000 |
| MDL-006 | Amazon Nova 2 Lite | 0.3 | 1.2 | 3.6 | 42,328 | 169,312 | 507,936 |
| MDL-007 | Titan Text Embeddings V2 | 0.1 | 0.5 | 1.5 | 580 | 2,320 | 6,960 |
| MDL-008 | Cohere Embed v4 | 0.1 | 0.5 | 1.5 | 2,400 | 9,600 | 28,800 |
| MDL-009 | Mistral Large 3 | 0.1 | 0.2 | 0.7 | 7,792 | 31,168 | 93,504 |
| MDL-010 | gpt-oss-120b | 0.1 | 0.4 | 1.1 | 3,912 | 15,648 | 46,944 |
|  | **Total** | **5.8** | **10.0** | **19.6** | **755,549** | **1,343,219** | **2,706,828** |
|  | Total per year (× 12) |  |  |  | 9,066,588 | 16,118,630 | 32,481,930 |
|  | Total over the 24-month operation period |  |  |  | 18,133,175 | 32,237,261 | 64,963,860 |

Tokens include cache reads, which are most of the coding-agent volume. Excl. tax. At the expected scenario, model usage (JPY 1,343,219 a month) is 0.96× this design's monthly running cost and 0.44× [LGW]'s: at 30 engineers it does not dominate either design yet [CMP §7.1], but its share of the total running cost is about twice as large here.

## 9. Optional items priced separately (not in the totals)

Route A is in the totals only at its expected value (contingency, 50 %). Its full cost, and the Private CA alternatives of finding F-1, are below at [PL] Tokyo rates and this estimate's traffic (about 168 GB a month through the endpoints). Azure OpenAI has no option: it cannot be reached without a proxy (01 NG-10).

| Option | Monthly AWS cost (USD) | Monthly (JPY) | One-time build | Not included |
|---|---:|---:|---|---|
| Route A for GA: interface endpoints over Direct Connect with Resolver inbound endpoint (D-6) | 6 interface endpoints × 3 AZs × 0.014/h 184.0; endpoint data 168 GB × 0.01 1.7; Route 53 Resolver inbound endpoint, 2 ENIs × 0.125/h 182.5; TGW attachment of the endpoint VPC 0.07/h 51.1; TGW processing 168 GB × 0.02 3.4; DX data out 27 GB × 0.041 1.1 = **424** | 67,794 | 15 pd Infra/DevOps ≈ JPY 825,000 | DX ports and circuits (AS-8), Osaka endpoints (finding F-6), Network team time |
| Corporate CA as the Roles Anywhere trust anchor instead of two Private CAs (02 §12) | −805.25 | −128,840 | Included in the IaC row; the PKI team issues and revokes | PKI team time; CRL publication to Roles Anywhere |
| Private CA in short-lived mode with 7-day workload certificates (TEN-006 changed) | −700.00 + certificates at 0.058 | −112,000 | Weekly renewal automation on every DC workload host | — |

## 10. Infrastructure sizing detail

Monthly AWS cost per environment in USD, before conversion. Production and DR are one row per component in §2; dev and staging are one row each in §2 with this breakdown.

| Environment | Component | USD / month |
|---|---|---:|
| Production (Tokyo) | Spend guard intake: SQS queue llm-meter-events | 1.07 |
| Production (Tokyo) | Spend guard compute: 7 Lambda functions (arm64, 256 MB) | 0.42 |
| Production (Tokyo) | Spend guard store: DynamoDB global table llm-spend (Tokyo) | 4.55 |
| Production (Tokyo) | Usage API: API Gateway REST API with IAM authorization | 0.04 |
| Production (Tokyo) | CloudTrail data events: bedrock-mantle inference (Codex CLI) | 0.02 |
| Production (Tokyo) | Chargeback: CUR 2.0 with IAM principal data, Athena, Quick Sight | 158.00 |
| Production (Tokyo) | S3: configuration, access inventory, CUR export share | 1.39 |
| Production (Tokyo) | KMS customer-managed keys | 5.50 |
| Production (Tokyo) | CloudWatch Logs, alarms, metrics and dashboards | 9.86 |
| Production (Tokyo) | AWS Private CA (general-purpose mode) for workload certificates | 403.75 |
| Production (Tokyo) | GuardDuty (CloudTrail management events, Lambda network activity) | 8.99 |
| Production (Tokyo) | Security Hub CSPM, AWS Config, Inspector (Lambda), IAM Access Analyzer (unused access) | 17.92 |
| Production (Tokyo) | Bedrock tokens for platform tests (gate re-runs, probe) | 75.00 |
| **Production (Tokyo)** | **Total** | **686.51** |
| DR (Osaka) | DynamoDB global table llm-spend (Osaka replica) | 4.41 |
| DR (Osaka) | Spend guard standby: SQS polling and Lambda (Osaka) | 0.31 |
| DR (Osaka) | KMS multi-Region replica keys (Osaka) | 2.00 |
| DR (Osaka) | CloudWatch alarms and logs (Osaka) | 1.15 |
| DR (Osaka) | GuardDuty, Security Hub, Config (Osaka) | 3.37 |
| **DR (Osaka)** | **Total** | **11.24** |
| Dev (Tokyo) | Spend guard, usage API and stores at test volume | 2.00 |
| Dev (Tokyo) | KMS (3 keys), S3, CloudWatch | 6.50 |
| Dev (Tokyo) | GuardDuty, Security Hub, Config, Access Analyzer | 8.00 |
| **Dev (Tokyo)** | **Total** | **16.50** |
| Staging (Tokyo) | AWS Private CA (general-purpose mode) for workload-certificate tests | 401.50 |
| Staging (Tokyo) | Spend guard, usage API and stores at gate-test volume | 3.00 |
| Staging (Tokyo) | Quick Sight: 1 author, 2 test readers (row-level security tests) | 30.00 |
| Staging (Tokyo) | KMS (4 keys), S3, CloudWatch | 10.50 |
| Staging (Tokyo) | GuardDuty, Security Hub, Config, Access Analyzer | 12.00 |
| **Staging (Tokyo)** | **Total** | **457.00** |

Comparison with 02 §12: every row of its table is priced here except model usage (§8) and Route A (contingency; full cost in §9). 02 §12 has no rows for threat detection and compliance services (finding F-4).

### 10.1 Per-call charges at higher volumes

The charges that grow with every model call: SQS, the llm-meter function, DynamoDB counter writes in both Regions (5 per call, not batched) and GuardDuty's analysis of the CloudTrail events. CloudWatch Logs and CloudTrail data events also grow, less. 02 §9 and §12 give 4.3–17 million calls a day at A-9 scale.

| Volume | Calls / month (M) | SQS | Lambda llm-meter | DynamoDB writes | GuardDuty events | Total USD / month | JPY / month |
|---|---:|---:|---:|---:|---:|---:|---:|
| This estimate (30 engineers) | 1.09 | 1 | 0 | 8 | 9 | **18** | 2,847 |
| 10 M | 10.00 | 8 | 1 | 72 | 74 | **153** | 24,544 |
| A-9 low: 4.3 M a day | 129.00 | 96 | 7 | 922 | 939 | **1,964** | 314,316 |
| A-9 high: 17 M a day | 510.00 | 378 | 28 | 3,646 | 3,711 | **7,763** | 1,242,075 |

At A-9 scale the per-call charges reach a few thousand USD a month, more than [LGW]'s whole production environment at 30 engineers; GuardDuty and the counter writes are most of it. Batching counter updates per key in llm-meter, as 02 §12 suggests, and a GuardDuty decision on Bedrock events are the levers (finding F-2). Model usage at that scale would be far larger still.

## 11. Open items that need a price or a decision, by owner

| Owner | Item | Where it is in the estimate | Due (from 01/02) |
|---|---|---|---|
| Product owner | Pilot and GA dates (01 Q-3); they set the project-period environment months | A3, Infrastructure one-time rows | 2026-12-18 |
| Product owner | Model list, usage forecast and growth (01 Q-4, Q-7); they set model usage and the per-call charges | §8, §10.1 | 2026-12-18 |
| Product owner | Support hours and DR drill interval (01 Q-6); AWS Support plan (01 Q-20) | Operation rows (A20), exclusion B7 | 2026-12-18 / 2027-01-29 |
| FinOps | Internal labor rates to replace the template sample rates | Rates sheet, all labor rows (A5) | — |
| FinOps | Budget exchange rate (JPY 160/USD assumed) | A10, all AWS rows | — |
| FinOps | Quick Sight reader count and allocation of fixed platform cost (01 Q-12, 02 R-17) | Chargeback row | 2026-12-18 |
| Security / SOC | Penetration-test vendor quote (template sample JPY 2,000,000 used) | Security row | 2027-01-29 |
| Security / SOC | Whether no guardrail in the path is accepted (01 Q-13) | Contingency R-5 | 2026-12-18 |
| Network | Whether Route A is adopted for GA (01 Q-24) and its Osaka side (F-6) | Contingency R-12, §9 | 2027-01-29 |
| Platform engineering | Private CA mode, or a corporate CA as trust anchor (R-24, F-1) | Private CA rows, §9 | 2027-01-29 |
| Platform engineering | Counter writes per call and batching in llm-meter; data-event selector for llm-spend (F-2, F-7) | Spend guard rows, §10.1 | 2027-01-29 |
| Identity | Number of teams and permission-set quotas (01 Q-22) | Contingency R-9 | 2026-12-18 |
| Legal / privacy | Whether per-team content logging is needed this phase (01 Q-10) | Contingency Q-10 / D-11 | 2026-12-18 |

## 12. Findings for the design documents (not edited)

docs/en/ was not changed. These are gaps or inconsistencies found while pricing the design; each should be resolved in 01/02 by its owner.

| ID | Finding | Owner |
|---|---|---|
| F-1 | 02 §12 says the short-lived certificate mode of AWS Private CA costs less, but that mode issues only certificates valid for 7 days or less, while D-4 and TEN-006 allow 90 days. A general-purpose CA is USD 400 a month; with one for staging, the two are USD 800 of this design's USD 1,171 a month. Decide between a corporate CA as trust anchor, 7-day certificates, or one shared CA (§9). | Platform engineering |
| F-2 | 02 §9 and §12 size the spend guard for 4.3–17 million calls a day (A-9). At that scale its per-call charges are about USD 1,964 a month at the low end (§10.1), mostly GuardDuty's analysis of Bedrock management events and unbatched counter writes in two Regions. 02 §12 should state the per-call cost, and 02 §5.2 how many counter writes a call makes after batching. | Platform engineering |
| F-3 | 02 §12 says no estimate has been made and leaves every row TBD; this estimate prices them, including R-17 (Quick Sight readers) and R-18 (bedrock-mantle data events). 02 §12 can point to it once reviewed. | Platform engineering |
| F-4 | 02 §12 has no rows for GuardDuty, Security Hub, Config, Inspector and IAM Access Analyzer, which 02 §2.2 and §8 require. GuardDuty charges per CloudTrail management event, and every Bedrock call is one (§10.1). | Security / SOC |
| F-5 | 02 §10 says staging has the same shapes as production, but not whether it has its own Private CA and Quick Sight, which T-084 and T-076 need. The estimate gives staging both. | Platform engineering |
| F-6 | 02 §2.2 lists Osaka for the Route A endpoints but does not say whether they run all the time or are created at failover; it affects RTO (AVL-M02) and cost. The estimate assumes they are created at failover. | Network |
| F-7 | 02 §4.3 logs DynamoDB data events for writes to llm-spend by any other principal. Unless an advanced event selector excludes the spend guard's own roles, every counter update is a paid data event: about USD 5.45 a month here, about USD 645 at the low end of A-9. | Platform engineering |
