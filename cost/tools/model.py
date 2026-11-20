"""Cost model for the IAM-native LLM gateway estimate (v0.1).

Single source of the numbers that go into the workbooks and the markdown.
Prices: AWS Price List API offer files for ap-northeast-1 / ap-northeast-3
(publications 2026-10-30 to 2026-11-19, downloaded and checked 2026-11-20),
cited as [PL]. Every English string is paired with its Japanese text through
tx.t(), so the Japanese outputs need no separate dictionary.

The usage basis, schedule, rates, exchange rate and template parameters are
those of the LiteLLM design's estimate ([LGW] cost/, commit 87ba355), so that
the two estimates can be compared line by line (md.py section 7).
"""
import datetime

from tx import t

CHECKED = "2026-11-20"
FX = 160            # JPY per USD, budget rate, as [LGW] (assumption A9)
H = 730             # hours per month
PL = f"[PL {CHECKED}]"

# ---------------------------------------------------------------- template
# Categories, roles, units and types come from the template (cost-estimate-template/tools/estimate.py).
import template_tools  # noqa: F401,E402  (puts the template's tools/ on sys.path)
from estimate import (Params, item,  # noqa: E402
                      R_ARCH, R_BA, R_SR, R_ENG, R_QA, R_INF, R_SEC, R_TW, R_OPS, R_HD, R_VEN,
                      SAMPLE_RATES, DAYS, U_PM, U_PD, U_MF, U_OT, T_OT, T_RC)

RATES = dict(SAMPLE_RATES)   # no internal rates yet: the template's sample rates are kept (A4, open item for FinOps)

# ---------------------------------------------------------------- schedule (same calendar as [LGW], A2)
MONTHS_DEV, MONTHS_STG, MONTHS_PRE_GA = 6, 4, 2
OPS_MONTHS = 24

PROJECT = dict(name=t("IAM-native LLM gateway on AWS (build and 24-month operation)",
                      "IAMネイティブLLMゲートウェイ（AWS）構築・24か月運用"),
               version="v0.1", date=datetime.datetime(2026, 11, 20),
               prepared_by=t("Claude (AI assistant), for platform engineering",
                             "Claude（AIアシスタント）、プラットフォームエンジニアリング向け"),
               status="Draft / 作成中")
t("Draft / 作成中", "作成中")
PARAMS = Params(pm=0.10, contingency=0.15, contingency_on_recurring=True, tax=0.10, months=OPS_MONTHS)

# ---------------------------------------------------------------- prices [PL], USD
P = dict(
    lambda_req=0.20, lambda_gbs=0.0000133334,          # per million requests; per GB-second, arm64 tier 1
    sqs_req=0.40,                                      # per million standard requests
    ddb_wru=0.715, ddb_rru=0.1425, ddb_gb=0.285, ddb_pitr=0.228,   # on-demand per million; per GB-month (Tokyo = Osaka)
    apigw_req=4.25,                                    # REST API, per million
    ct_data=0.10,                                      # CloudTrail data events, per 100,000
    pca_gp=400.0, pca_cert=0.75, pca_short=50.0,       # Private CA per month; per certificate (first 1,000)
    cw_ingest=0.76, cw_store=0.033, cw_alarm=0.10, cw_metric=0.30,
    athena_tb=5.0, qs_author=24.0, qs_reader=3.0,      # Quick Sight author: AWS pricing page as checked by [LGW] (not in [PL])
    s3_gb=0.025, s3_put=0.0047,                        # per GB-month; per 1,000 PUT
    kms_key=1.0, kms_req=0.03,                         # per key-month; per 10,000 requests
    gd_ct_m=4.72, gd_lambda_gb=1.18,                   # GuardDuty: per million CloudTrail events; per GB Lambda network logs
    shub_check=0.001, cfg_ci=0.003, cfg_eval=0.001, insp_lambda_h=0.0005, iaa_role=0.20,
    vpce_h=0.014, vpce_gb=0.01, resolver_eni=0.125, tgw_h=0.07, tgw_gb=0.02, dx_out_gb=0.041,
)


def usd(x):
    return f"USD {x:,.2f}"


def jpy(u):
    return int(round(u * FX))


# ---------------------------------------------------------------- usage basis (same as [LGW]; A13, A14)
ENGINEERS = 30                 # requester, 2026-11-17: "30 people for now" ([LGW] A12)
AGENT_CALLS_M = ENGINEERS * 15 * 200 / 1e6      # 30 users × 15 active days × 200 calls = 0.09 M calls/month
WL_CALLS_M = 1.0               # workload calls/month, million ([LGW] usage table: 2.5 B input tokens / ~2,500 per call)
CALLS_M = round(AGENT_CALLS_M + WL_CALLS_M, 2)  # 1.09 M model calls / month
REQ_KB, RESP_KB = 120, 20      # average request and response size, as [LGW]
# CloudTrail events per call: a streaming call has AwsApiCall + stream-completion; workloads assumed half streaming
EVENTS_M = round(AGENT_CALLS_M * 2 + WL_CALLS_M * 1.5, 2)   # 1.68 M events / month
COUNTERS = 5                   # counter updates per metered call: person-month, team-month, workload or person-day, model-month, 5-minute window
CODEX_SHARE = 0.2              # share of coding-agent calls made by Codex CLI on bedrock-mantle (data events)
TEAMS, WORKLOADS = 6, 10       # assumptions for 30 engineers (01 Q-22 open) and the [LGW] workload volume
ROLES = TEAMS + WORKLOADS + 8 + 4 + 2    # IAM roles in llm-prod: teams, workloads, spend guard, operator/admin, CI and break-glass


def comp(name, value, calc, basis):
    return dict(name=name, usd=round(value, 2), calc=calc, basis=basis)


def spend_guard_variable(calls_m, events_m):
    """Per-call charges of the spend guard and detection, USD per month (Tokyo + Osaka replica)."""
    sqs = (events_m * 1.2 + 0.66) * P["sqs_req"]
    lam = events_m * 1e6 / 100 * (P["lambda_req"] / 1e6 + 1.0 * 0.25 * P["lambda_gbs"])
    ddb = calls_m * COUNTERS * P["ddb_wru"] * 2          # global table: written in Tokyo and replicated to Osaka
    gd = (events_m + 0.2) * P["gd_ct_m"]
    return dict(sqs=sqs, lam=lam, ddb=ddb, gd=gd, total=sqs + lam + ddb + gd)


def prod_tokyo():
    c = []
    a = c.append
    req = EVENTS_M * 1.2 + 0.66
    a(comp(t("Spend guard intake: SQS queue llm-meter-events", "スペンドガード受信：SQSキュー llm-meter-events"),
           req * P["sqs_req"],
           f"({EVENTS_M} M events × 1.2 + 0.66 M polls) × 0.40/M",
           t(f"02 §5.2, D-8; {EVENTS_M} M CloudTrail events a month from {CALLS_M} M calls (2 per streaming call); send + batch receive/delete; Lambda long polling",
             f"02 §5.2、D-8。月{CALLS_M}百万回の呼び出しから月{EVENTS_M}百万件のCloudTrailイベント（ストリーミング1回につき2件）。送信＋一括受信・削除、Lambdaのロングポーリング")))
    inv = {"meter": EVENTS_M * 1e6 / 100, "enforce": 43800 + 100000, "lifecycle": 8760, "reconcile": 120, "other": 5000}
    gbs = (inv["meter"] * 1.0 + inv["enforce"] * 0.5 + inv["lifecycle"] * 2 + inv["reconcile"] * 60 + inv["other"] * 0.5) * 0.25
    n_inv = sum(inv.values())
    a(comp(t("Spend guard compute: 7 Lambda functions (arm64, 256 MB)", "スペンドガード処理：Lambda関数7個（arm64、256MB）"),
           n_inv / 1e6 * P["lambda_req"] + gbs * P["lambda_gbs"],
           f"{n_inv / 1e6:.2f} M invocations × 0.20/M + {gbs / 1000:,.1f}k GB-s × 0.0000133",
           t("02 §5.2: llm-meter (batches of 100), llm-enforce (stream + every minute), llm-lifecycle (5-minute poll), llm-reconcile (4 CUR deliveries a day), llm-admin, llm-usage, inventory job",
             "02 §5.2：llm-meter（100件単位）、llm-enforce（ストリーム＋毎分）、llm-lifecycle（5分ごとのポーリング）、llm-reconcile（CUR配信1日4回）、llm-admin、llm-usage、棚卸しジョブ")))
    w = CALLS_M * COUNTERS
    a(comp(t("Spend guard store: DynamoDB global table llm-spend (Tokyo)", "スペンドガードのストア：DynamoDBグローバルテーブル llm-spend（東京）"),
           w * P["ddb_wru"] + 1.0 * P["ddb_rru"] + 1 * P["ddb_gb"] + 1 * P["ddb_pitr"],
           f"{w:.2f} M writes × 0.715/M + 1 M reads × 0.1425/M + 1 GB × 0.285 + 1 GB PITR × 0.228",
           t(f"02 §5.2, §7.1; on-demand; {COUNTERS} counter updates per metered call, not batched (batching in llm-meter cuts this); stream reads by Lambda are free",
             f"02 §5.2、§7.1。オンデマンド。計測1回につきカウンター更新{COUNTERS}件（バッチ化なし。llm-meterでのバッチ化で削減可能）。Lambdaによるストリーム読み取りは無料")))
    a(comp(t("Usage API: API Gateway REST API with IAM authorization", "利用状況API：API Gateway REST API（IAM認可）"),
           0.01 * P["apigw_req"],
           "0.01 M requests × 4.25/M",
           t("02 §3.1, D-14; llm usage by 30 engineers and team leads", "02 §3.1、D-14。エンジニア30人とチームリードによる llm usage")))
    ev = AGENT_CALLS_M * CODEX_SHARE
    a(comp(t("CloudTrail data events: bedrock-mantle inference (Codex CLI)", "CloudTrailデータイベント：bedrock-mantle推論（Codex CLI）"),
           ev * 1e6 / 1e5 * P["ct_data"],
           f"{ev * 1e6:,.0f} events × 0.10/100k",
           t("02 §2.2, §7.4, R-18; Codex CLI assumed 20 % of coding-agent calls; management events are in the existing organization trail (first copy free)",
             "02 §2.2、§7.4、R-18。Codex CLIはコーディングエージェント呼び出しの20%と仮定。管理イベントは既存の組織証跡に記録（最初のコピーは無料）")))
    a(comp(t("Chargeback: CUR 2.0 with IAM principal data, Athena, Quick Sight", "配賦：IAMプリンシパル付きCUR 2.0、Athena、Quick Sight"),
           1 * P["athena_tb"] + 2 * P["qs_author"] + 35 * P["qs_reader"],
           "Athena 1 TB × 5 + 2 authors × 24 + 35 readers × 3 (CUR export and non-action Budgets free)",
           t("02 §5, D-9, D-14; readers = team leads and department contacts (30, as [LGW]) + 5 for the access inventory; Quick Sight reader [PL], author price as [LGW]",
             "02 §5、D-9、D-14。閲覧者＝チームリード・部門窓口（[LGW]と同じ30人）＋アクセス棚卸し用5人。Quick Sight閲覧者は[PL]、作成者の価格は[LGW]と同じ")))
    a(comp(t("S3: configuration, access inventory, CUR export share", "S3：構成、アクセス棚卸し、CURエクスポート（按分）"),
           30 * P["s3_gb"] + 50 * P["s3_put"] + 0.4,
           "avg 30 GB × 0.025 + 50k PUT × 0.0047/1k + GET 0.40",
           t("02 §7.1; daily inventory snapshot, versioned configuration, CUR rows per principal",
             "02 §7.1。日次の棚卸しスナップショット、バージョン管理された構成、プリンシパル別のCUR行")))
    a(comp(t("KMS customer-managed keys", "KMSカスタマー管理キー"),
           4 * P["kms_key"] + 0.5 * 1e6 / 1e4 * P["kms_req"],
           "4 CMKs × 1 + 0.5 M requests × 0.03/10k",
           t("02 §7.1: llm-spend (multi-Region primary), S3, CloudWatch Logs, CUR bucket",
             "02 §7.1：llm-spend（マルチリージョンのプライマリ）、S3、CloudWatch Logs、CURバケット")))
    a(comp(t("CloudWatch Logs, alarms, metrics and dashboards", "CloudWatch Logs、アラーム、メトリクス、ダッシュボード"),
           1.0 * P["cw_ingest"] + 3 * P["cw_store"] + 30 * P["cw_alarm"] + 20 * P["cw_metric"],
           "1.0 GB ingest × 0.76 + 3 GB stored × 0.033 + 30 alarms × 0.10 + 20 metrics × 0.30 (2 dashboards within the free 3)",
           t("02 §7.1, §9, OBS-006: function logs (metadata only), metering-delay and estimate-gap metrics, quota alarms at 80 %",
             "02 §7.1、§9、OBS-006：関数ログ（メタデータのみ）、計測遅延・見積差のメトリクス、80%のクォータアラーム")))
    a(comp(t("AWS Private CA (general-purpose mode) for workload certificates", "ワークロード証明書用AWS Private CA（汎用モード）"),
           P["pca_gp"] + 5 * P["pca_cert"],
           "1 CA × 400 + 5 certificates × 0.75",
           t(f"02 §2.2, D-4, R-24; {WORKLOADS} DC workloads, 90-day certificates renewed at 60 days; short-lived mode (USD 50) issues only certificates of 7 days or less (finding F-1); the Osaka trust anchor uses this CA's certificate",
             f"02 §2.2、D-4、R-24。DCワークロード{WORKLOADS}件、90日証明書を60日で更新。短期証明書モード（50USD）は7日以下の証明書しか発行できない（指摘F-1）。大阪のトラストアンカーはこのCAの証明書を使用")))
    a(comp(t("GuardDuty (CloudTrail management events, Lambda network activity)", "GuardDuty（CloudTrail管理イベント、Lambdaネットワーク活動）"),
           (EVENTS_M + 0.2) * P["gd_ct_m"] + 0.1 * P["gd_lambda_gb"],
           f"({EVENTS_M} + 0.2) M events × 4.72/M + 0.1 GB × 1.18",
           t("02 §2.2 threat detection, SEC-019; every Bedrock call is a management event; no ECS runtime monitoring",
             "02 §2.2 脅威検知、SEC-019。Bedrockの呼び出しはすべて管理イベント。ECSランタイム監視なし")))
    sec = 3000 * P["shub_check"] + 1000 * P["cfg_ci"] + 3000 * P["cfg_eval"] + 8 * P["insp_lambda_h"] * H + ROLES * P["iaa_role"]
    a(comp(t("Security Hub CSPM, AWS Config, Inspector (Lambda), IAM Access Analyzer (unused access)",
             "Security Hub CSPM、AWS Config、Inspector（Lambda）、IAM Access Analyzer（未使用アクセス）"),
           sec,
           f"3k checks × 0.001 + 1k CIs × 0.003 + 3k evals × 0.001 + 8 functions × 0.0005/h × 730 h + {ROLES} roles × 0.20",
           t("02 §8, §8.3: Config rules (invocation logging off, no IAM users with Bedrock access, SCP attached), Lambda scanning, unused workload roles",
             "02 §8、§8.3：Configルール（呼び出しログ無効、Bedrock権限を持つIAMユーザーなし、SCP適用）、Lambdaスキャン、未使用のワークロードロール")))
    a(comp(t("Bedrock tokens for platform tests (gate re-runs, probe)", "基盤テスト用Bedrockトークン（ゲート再実行、プローブ）"),
           75,
           "≈ USD 200 per full gate run × 1 run/quarter + probe on Haiku 5.5 (< USD 1)",
           t("OPS-001, AVL-M01; as [LGW]; platform's own usage, not charged back", "OPS-001、AVL-M01。[LGW]と同じ。基盤チーム自身の利用で配賦しない")))
    return c


def dr_osaka():
    c = []
    a = c.append
    w = CALLS_M * COUNTERS
    a(comp(t("DynamoDB global table llm-spend (Osaka replica)", "DynamoDBグローバルテーブル llm-spend（大阪レプリカ）"),
           w * P["ddb_wru"] + 1 * P["ddb_gb"] + 1 * P["ddb_pitr"],
           f"{w:.2f} M replicated writes × 0.715/M + 1 GB × 0.285 + 1 GB PITR × 0.228",
           t("02 §7.1, §9, D-13, AVL-M03", "02 §7.1、§9、D-13、AVL-M03")))
    a(comp(t("Spend guard standby: SQS polling and Lambda (Osaka)", "スペンドガード待機：SQSポーリングとLambda（大阪）"),
           0.66 * P["sqs_req"] + 0.05,
           "0.66 M polls × 0.40/M + Lambda 0.05",
           t("02 §9, D-13; deployed in both Regions, llm-enforce active in one", "02 §9、D-13。両リージョンに配置し、llm-enforceは片方のみ稼働")))
    a(comp(t("KMS multi-Region replica keys (Osaka)", "KMSマルチリージョンレプリカキー（大阪）"),
           2 * P["kms_key"], "2 replica keys × 1", t("02 §7.1", "02 §7.1")))
    a(comp(t("CloudWatch alarms and logs (Osaka)", "CloudWatchアラームとログ（大阪）"),
           10 * P["cw_alarm"] + 0.2 * P["cw_ingest"], "10 alarms × 0.10 + 0.2 GB × 0.76", t("02 §9, OBS-006", "02 §9、OBS-006")))
    a(comp(t("GuardDuty, Security Hub, Config (Osaka)", "GuardDuty、Security Hub、Config（大阪）"),
           0.1 * P["gd_ct_m"] + 1000 * P["shub_check"] + 300 * P["cfg_ci"] + 1000 * P["cfg_eval"],
           "0.1 M events × 4.72/M + 1k checks × 0.001 + 300 CIs × 0.003 + 1k evals × 0.001",
           t("02 §2.2 threat detection in both Regions; IAM Identity Center replica and Roles Anywhere have no charge",
             "02 §2.2 両リージョンで脅威検知。IAM Identity CenterのレプリカとRoles Anywhereは無料")))
    return c


def dev_env():
    return [
        comp(t("Spend guard, usage API and stores at test volume", "スペンドガード、利用状況API、ストア（テスト規模）"), 2.0, "", ""),
        comp(t("KMS (3 keys), S3, CloudWatch", "KMS（3キー）、S3、CloudWatch"), 3 * P["kms_key"] + 0.5 + 3.0, "", ""),
        comp(t("GuardDuty, Security Hub, Config, Access Analyzer", "GuardDuty、Security Hub、Config、Access Analyzer"), 8.0, "", ""),
    ]


def stg_env():
    return [
        comp(t("AWS Private CA (general-purpose mode) for workload-certificate tests", "ワークロード証明書テスト用AWS Private CA（汎用モード）"),
             P["pca_gp"] + 2 * P["pca_cert"], "", ""),
        comp(t("Spend guard, usage API and stores at gate-test volume", "スペンドガード、利用状況API、ストア（ゲート試験規模）"), 3.0, "", ""),
        comp(t("Quick Sight: 1 author, 2 test readers (row-level security tests)", "Quick Sight：作成者1、テスト閲覧者2（行レベルセキュリティの試験）"),
             P["qs_author"] + 2 * P["qs_reader"], "", ""),
        comp(t("KMS (4 keys), S3, CloudWatch", "KMS（4キー）、S3、CloudWatch"), 4 * P["kms_key"] + 0.5 + 6.0, "", ""),
        comp(t("GuardDuty, Security Hub, Config, Access Analyzer", "GuardDuty、Security Hub、Config、Access Analyzer"), 12.0, "", ""),
    ]


def tot(cs):
    return round(sum(x["usd"] for x in cs), 2)


def route_a():
    """Route A (02 D-6) in Tokyo with this estimate's traffic: interface endpoints over Direct Connect."""
    gb = CALLS_M * 1e6 * (REQ_KB + RESP_KB) / 1e6 * 1.1
    out = CALLS_M * 1e6 * RESP_KB / 1e6 * 1.25
    parts = [
        (t("6 interface endpoints × 3 AZs × 0.014/h", "インターフェースエンドポイント6個×3AZ×0.014/時"), 6 * 3 * P["vpce_h"] * H),
        (t(f"endpoint data {gb:,.0f} GB × 0.01", f"エンドポイント処理 {gb:,.0f} GB×0.01"), gb * P["vpce_gb"]),
        (t("Route 53 Resolver inbound endpoint, 2 ENIs × 0.125/h", "Route 53 Resolverインバウンドエンドポイント、ENI 2個×0.125/時"), 2 * P["resolver_eni"] * H),
        (t("TGW attachment of the endpoint VPC 0.07/h", "エンドポイントVPCのTGWアタッチメント 0.07/時"), P["tgw_h"] * H),
        (t(f"TGW processing {gb:,.0f} GB × 0.02", f"TGW処理 {gb:,.0f} GB×0.02"), gb * P["tgw_gb"]),
        (t(f"DX data out {out:,.0f} GB × 0.041", f"DXデータ送信 {out:,.0f} GB×0.041"), out * P["dx_out_gb"]),
    ]
    return dict(parts=parts, monthly_usd=round(sum(v for _, v in parts), 2), build_pd=15)


# ---------------------------------------------------------------- line items
def row(cat, desc, role, unit, qty, typ, notes, j=None, likelihood=None):
    return item(cat, desc, role, unit, qty, typ, notes, j, likelihood)


GATES = [  # (gate, description en, ja, role, person-days, requirement IDs)
    ("V-1", "No prompt content outside the approved stores: canary through every model, API style and endpoint, incl. refused and cancelled calls; search every store",
     "承認済みストア以外にプロンプト内容が残らない：全モデル・全API形式・全エンドポイントにカナリアを送信（拒否・キャンセルを含む）し、全ストアを検索", R_SR, 4, "PRV-001, PRV-002, RES-005, OBS-002"),
    ("V-2", "Credential issuance stays within its limits: no long-term keys or IAM-user calls, 1 h sessions, 90-day certificates",
     "認証情報の発行が上限内：長期キー・IAMユーザーの呼び出しなし、セッション1時間、証明書90日", R_QA, 2, "IAM-015, IAM-016, TEN-006"),
    ("V-4", "Spend correct per model (10 models, with and without prompt caching), estimate against CUR",
     "モデル別の費用が正しい（10モデル、プロンプトキャッシュあり・なし）、見積とCURの比較", R_ENG, 4, "CST-004"),
    ("V-5", "Cancelled requests are metered", "キャンセルされたリクエストも計測される", R_ENG, 3, "CST-006"),
    ("V-6", "Clients cannot skip tracking: every API, endpoint and auth mode in CloudTrail and CUR",
     "クライアントが追跡を回避できない：全API・全エンドポイント・全認証方式がCloudTrailとCURに記録される", R_QA, 2, "CST-005, OBS-002"),
    ("V-7", "Clients cannot choose who pays, incl. user in two teams", "クライアントが課金先を選べない（2チーム所属の利用者を含む）", R_QA, 2, "CST-001, TEN-009"),
    ("V-10", "Identity endpoints unavailable", "ID基盤のエンドポイント停止時の動作", R_INF, 2, "AVL-003"),
    ("V-11", "Unmanaged devices cannot use the office or DC egress IPs (with Network; CIDR list and owners)",
     "管理外端末がオフィス・DCの出口IPを使えない（ネットワーク部門と実施。CIDR一覧と所有者）", R_SEC, 3, "SEC-001–SEC-003, OPS-004"),
    ("V-12", "Authorization matrix: every principal type × action family × endpoint × auth mode × model class × network origin, automated",
     "認可マトリクス：プリンシパル種別×アクション群×エンドポイント×認証方式×モデル区分×接続元を自動化して検証", R_SR, 8, "TEN-001, TEN-008, MDL-101–MDL-103, SEC-001, SEC-020, FUN-006"),
    ("V-13", "Metering feed: events, tokens and delay per API and endpoint", "計測フィード：API・エンドポイント別のイベント・トークン数・遅延", R_ENG, 3, "OBS-002, CST-009"),
    ("V-14", "Spend guard enforcement and failure: budget, cap, runaway, leaver; each function stopped in turn",
     "スペンドガードの制御と障害時動作：予算・上限・暴走・退職者。各関数を順に停止", R_SR, 4, "CST-002, CST-012, CST-013, AVL-007, IAM-006"),
    ("V-15", "Cost allocation by principal in CUR 2.0, incl. Budgets tag filters", "CUR 2.0のプリンシパル別費用配分（Budgetsのタグフィルターを含む）", R_ENG, 3, "CST-001, CST-007, CST-014"),
    ("V-16", "No stored responses (Responses API on both endpoints)", "応答が保存されない（両エンドポイントのResponses API）", R_QA, 1, "PRV-005"),
]


def labor_rows():
    r = []
    a = r.append
    # 1-1 requirements
    a(row("req", t("Close the 26 open questions in 01 §9 and confirm assumptions AS-1–AS-27 with their owner teams; update 01 to v1.0",
                   "01 §9の未決事項26件を解決し、前提AS-1〜AS-27を各オーナー部門と確認。01をv1.0に更新"),
          R_BA, U_PD, 20, T_OT,
          t("01 §9 (Q-1–Q-27; Q-17 withdrawn), 01 §3. Sizing: ~0.75 pd per question incl. workshop and write-up",
            "01 §9（Q-1〜Q-27、Q-17は取り下げ）、01 §3。見積根拠：1件あたり約0.75人日（ワークショップ・記録を含む）")))
    a(row("req", t("Requirements review and approval (security, legal/privacy, network, FinOps, platform lead)",
                   "要件レビューと承認（セキュリティ、法務・プライバシー、ネットワーク、FinOps、プラットフォームリード）"),
          R_ARCH, U_PD, 4, T_OT,
          t("01 header Approvers, 01 §11, REG-003. Sizing: 2 review rounds × 2 pd", "01ヘッダーの承認者、01 §11、REG-003。見積根拠：レビュー2回×2人日")))
    # 1-2 design
    a(row("des", t("Design v0.2: close uncovered requirements and open decisions — guardrail position (SEC-008, R-5), content-logging accounts (PRV-002, D-11), Codex CLI models (FUN-002, R-4), Route A for GA (SEC-014, D-6), sign-in DR (R-35), budget overshoot bound (CST-009, R-1), Private CA or corporate CA (R-24)",
                   "設計v0.2：未対応の要件と未決の判断を解消 — ガードレールの方針（SEC-008、R-5）、内容記録用アカウント（PRV-002、D-11）、Codex CLIのモデル（FUN-002、R-4）、GAでのRoute A（SEC-014、D-6）、サインインのDR（R-35）、予算超過の上限（CST-009、R-1）、Private CAか社内CAか（R-24）"),
          R_ARCH, U_PM, 1.0, T_OT,
          t("02 §1.2, §12, §14 (target 2027-01-29). Sizing: ~7 design topics × ~3 pd", "02 §1.2、§12、§14（期限2027-01-29）。見積根拠：設計論点約7件×約3人日")))
    a(row("des", t("Detailed design of remaining TBDs: IaC tool and CI federation (R-24), SCP size and landing-zone fit (R-23), team count and permission-set quotas (R-9), llm-guard-deny size (R-15), Lambda concurrency, Bedrock quota plan for Tokyo and Osaka (R-28), enrolment checklist (R-32), alert thresholds (OBS-006)",
                   "残りのTBDの詳細設計：IaCツールとCI連携（R-24）、SCPのサイズとランディングゾーンとの整合（R-23）、チーム数と権限セットのクォータ（R-9）、llm-guard-denyのサイズ（R-15）、Lambdaの同時実行数、東京・大阪のBedrockクォータ計画（R-28）、登録チェックリスト（R-32）、アラートのしきい値（OBS-006）"),
          R_INF, U_PM, 1.0, T_OT,
          t("02 §1.3, §9, §10, §14. Sizing: ~8 topics × ~2.5 pd", "02 §1.3、§9、§10、§14。見積根拠：論点約8件×約2.5人日")))
    a(row("des", t("Early spikes on a sandbox for the AWS behaviours the design rests on: CUR attribution by principal and Budgets tag filters (R-2), stream-completion events on EventBridge and their delay (R-30), network condition with jp. routing, bedrock-mantle and short-term keys (R-25), IAM model control on bedrock-mantle (R-29), Responses API storage (R-3), Codex CLI provider (R-4), SCIM deprovisioning event (R-33), device-code flow (R-7)",
                   "設計の前提となるAWSの挙動をサンドボックスで早期検証：CURのプリンシパル別配分とBudgetsのタグフィルター（R-2）、EventBridgeでのストリーム完了イベントと遅延（R-30）、jp.ルーティング・bedrock-mantle・短期キーでのネットワーク条件（R-25）、bedrock-mantleでのIAMによるモデル制御（R-29）、Responses APIの保存（R-3）、Codex CLIのプロバイダー（R-4）、SCIMによる無効化イベント（R-33）、デバイスコードフロー（R-7）"),
          R_SR, U_PD, 20, T_OT,
          t("02 §14 mitigations 'V-n before launch'; 01 AS-24, AS-25. Sizing: 8 spikes × 2.5 pd; CUR results arrive a day later, so elapsed time is longer than effort",
            "02 §14の対策（ローンチ前のV-n）、01 AS-24、AS-25。見積根拠：検証8件×2.5人日。CURの結果は翌日に出るため、期間は工数より長い")))
    a(row("des", t("Guardrail decision support for 01 Q-13: test the Classic-tier Bedrock guardrail option (regex filters, Japanese samples) enforced through a Bedrock policy on a test OU",
                   "01 Q-13の判断材料：Classic tierのBedrockガードレール（正規表現フィルター、日本語サンプル）をテスト用OUにBedrockポリシーで適用して検証"),
          R_SR, U_PD, 3, T_OT,
          t("02 §8, D-10, R-5; 01 SEC-008, Q-13. Sizing: 1 test setup + report; [LGW] spent 10 pd selecting a classifier",
            "02 §8、D-10、R-5、01 SEC-008、Q-13。見積根拠：検証環境1式＋報告。[LGW]は分類器の選定に10人日")))
    a(row("des", t("Design review and approval (security, network, platform lead, FinOps, SRE), incl. Security sign-off of R-34 parameters",
                   "設計レビューと承認（セキュリティ、ネットワーク、プラットフォームリード、FinOps、SRE）。R-34のパラメータのセキュリティ承認を含む"),
          R_ARCH, U_PD, 5, T_OT,
          t("02 header Approvers, R-34. Sizing: 2 rounds + 1 pd follow-up", "02ヘッダーの承認者、R-34。見積根拠：2回＋フォロー1人日")))
    # 1-3 implementation
    a(row("imp", t("IaC for the accounts and both Regions: SCP baseline and resource control policies, Config rules, permission-set and operator roles, Roles Anywhere trust anchors and profiles, Private CA with certificate template and CRL, KMS, S3 buckets, AWS Budgets with actions, IAM Identity Center replication to Osaka",
                   "アカウントと両リージョンのIaC：SCPベースラインとリソースコントロールポリシー、Configルール、権限セットと運用者ロール、Roles Anywhereのトラストアンカーとプロファイル、証明書テンプレートとCRLを含むPrivate CA、KMS、S3バケット、アクション付きAWS Budgets、IAM Identity Centerの大阪へのレプリケーション"),
          R_INF, U_PM, 1.5, T_OT,
          t("02 §2.2, §4.3, §4.7, §7.1, §9; D-4, D-7, D-13, D-15; OPS-002. Sizing: ~15 components, mostly IAM and organization level; no VPC, cluster or database ([LGW]: 3.0 pm)",
            "02 §2.2、§4.3、§4.7、§7.1、§9、D-4、D-7、D-13、D-15、OPS-002。見積根拠：約15コンポーネント、大半はIAM・組織レベル。VPC・クラスター・DBなし（[LGW]は3.0人月）")))
    a(row("imp", t("Policy generator and model catalog: models.yaml and teams.yaml to permission policies per tier with network conditions, short-term key and bedrock-mantle permissions, workload-role policies bound to CIDRs, client defaults; policy tests with the IAM policy simulator",
                   "ポリシー生成とモデルカタログ：models.yaml・teams.yamlからティア別の権限ポリシー（ネットワーク条件、短期キー・bedrock-mantleの権限）、CIDRに限定したワークロードロールのポリシー、クライアント既定値を生成。IAMポリシーシミュレーターによるポリシーテスト"),
          R_SR, U_PM, 1.0, T_OT,
          t("02 §4.2, §4.7, §5, §5.1; D-5, D-15; 01 MDL-101–MDL-105, OPS-009, SEC-020. Takes the place of [LGW]'s LiteLLM configuration (1.0 pm)",
            "02 §4.2、§4.7、§5、§5.1、D-5、D-15、01 MDL-101〜MDL-105、OPS-009、SEC-020。[LGW]のLiteLLM設定（1.0人月）に相当")))
    a(row("imp", t("Spend guard core: llm-meter (CloudTrail events to estimated cost; counters per person, team, workload and 5-minute window), llm-enforce (budgets, caps, runaway stop, llm-guard-deny policy versions and size limit), DynamoDB global table, active Region switch, failure behaviour",
                   "スペンドガードの中核：llm-meter（CloudTrailイベントから推定費用を算出し、個人・チーム・ワークロード・5分間のカウンターに加算）、llm-enforce（予算・上限・暴走停止、llm-guard-denyのポリシーバージョンとサイズ上限）、DynamoDBグローバルテーブル、稼働リージョンの切替、障害時動作"),
          R_SR, U_PM, 2.0, T_OT,
          t("02 §5.2, D-8, R-13, R-15, R-16; 01 CST-002, CST-004, CST-009, CST-010, CST-012, CST-013, AVL-007. Sizing: our only security-critical code; it can deny everyone",
            "02 §5.2、D-8、R-13、R-15、R-16、01 CST-002、CST-004、CST-009、CST-010、CST-012、CST-013、AVL-007。見積根拠：唯一のセキュリティ上重要な自社コードで、全員を拒否し得る")))
    a(row("imp", t("llm-reconcile and chargeback: CUR 2.0 export with IAM principal data, cost allocation tags, Athena views per principal, team and department, reconciliation of estimates with billed cost, Quick Sight chargeback with unattributed line",
                   "llm-reconcileと配賦：IAMプリンシパル付きCUR 2.0エクスポート、コスト配分タグ、プリンシパル・チーム・部門別のAthenaビュー、推定と請求額の照合、帰属不明行を含むQuick Sightの配賦レポート"),
          R_ENG, U_PM, 1.0, T_OT,
          t("02 §5, §7.1, D-9, D-14; 01 CST-007, CST-008, CST-011 [CMP §4.5]", "02 §5、§7.1、D-9、D-14、01 CST-007、CST-008、CST-011 [CMP §4.5]")))
    a(row("imp", t("llm-lifecycle and llm-admin: leaver denial from SCIM events with a 5-minute Identity Store poll; operator suspend and restore with reason, expiry and Security alert",
                   "llm-lifecycleとllm-admin：SCIMイベントと5分ごとのIdentity Storeポーリングによる退職者の拒否。理由・期限・セキュリティ通知付きの運用者による停止と復旧"),
          R_ENG, U_PD, 10, T_OT,
          t("02 §4.5, §5.2 (R-33); 01 IAM-006, TEN-007, UC-12", "02 §4.5、§5.2（R-33）、01 IAM-006、TEN-007、UC-12")))
    a(row("imp", t("Usage API: API Gateway with IAM authorization and llm-usage; own and team usage as PRV-003 allows",
                   "利用状況API：IAM認可のAPI Gatewayとllm-usage。PRV-003の範囲で本人とチームの利用状況を返す"),
          R_ENG, U_PD, 5, T_OT,
          t("02 §3.1, §5.2, D-14; 01 FUN-008, IAM-010", "02 §3.1、§5.2、D-14、01 FUN-008、IAM-010")))
    a(row("imp", t("IAM Identity Center integration: Entra enterprise app (SAML, SCIM), llm-team-* and operator group assignments by CI, session lengths, Conditional Access requirements handed to Identity",
                   "IAM Identity Center連携：Entraのエンタープライズアプリ（SAML、SCIM）、CIによるllm-team-*・運用者グループの割り当て、セッション長、条件付きアクセスの要件をID管理部門に引き渡し"),
          R_ENG, U_PD, 10, T_OT,
          t("02 §4.2–§4.4, D-2, D-16; 01 IAM-001, IAM-003, IAM-004, IAM-011, TEN-004. One app instead of [LGW]'s three; Conditional Access itself is Identity's (B5)",
            "02 §4.2〜§4.4、D-2、D-16、01 IAM-001、IAM-003、IAM-004、IAM-011、TEN-004。[LGW]の3アプリに対し1アプリ。条件付きアクセスの設定はID管理部門（B5）")))
    a(row("imp", t("Configuration pipeline: CI with OIDC to llm-platform-deploy; pull requests for teams, budgets, tiers, workload roles, certificates and enrolments; plan, review, apply",
                   "構成パイプライン：OIDCでllm-platform-deployに連携するCI。チーム・予算・ティア・ワークロードロール・証明書・登録のプルリクエスト、計画・レビュー・適用"),
          R_ENG, U_PM, 1.0, T_OT,
          t("02 §4.5, §10, D-15; 01 OPS-002, OPS-003, TEN-002, SEC-012, SEC-021", "02 §4.5、§10、D-15、01 OPS-002、OPS-003、TEN-002、SEC-012、SEC-021")))
    a(row("imp", t("Client package: llm helper (login with PKCE, team choice, profile, Region switch, usage, short-term keys) for Windows and macOS; Claude Code managed settings with awsAuthRefresh; Codex CLI config.toml (deployed by Intune team)",
                   "クライアントパッケージ：Windows・macOS向けllmヘルパー（PKCEでのログイン、チーム選択、プロファイル、リージョン切替、利用状況、短期キー）、awsAuthRefresh付きのClaude Code管理設定、Codex CLIのconfig.toml（配布はIntune担当）"),
          R_ENG, U_PM, 1.0, T_OT,
          t("02 §2.2, §4.1, §4.5, D-12; 01 FUN-005, FUN-008, FUN-009, TEN-009. Larger than [LGW]'s key helper (10 pd): sign-in, team and Region logic. Intune deployment itself excluded (B5)",
            "02 §2.2、§4.1、§4.5、D-12、01 FUN-005、FUN-008、FUN-009、TEN-009。[LGW]のキーヘルパー（10人日）より大きい：サインイン・チーム・リージョンの処理。Intuneでの配布作業は対象外（B5）")))
    a(row("imp", t("DC workload onboarding kit: aws_signing_helper profile, certificate request and renewal guide, workload role request template",
                   "DCワークロードの導入キット：aws_signing_helperのプロファイル、証明書の申請・更新手順、ワークロードロールの申請テンプレート"),
          R_ENG, U_PD, 5, T_OT,
          t("02 §2.3.3, §4.5, D-4; 01 TEN-002, TEN-006, OBS-008", "02 §2.3.3、§4.5、D-4、01 TEN-002、TEN-006、OBS-008")))
    a(row("imp", t("Logging and audit: bedrock-mantle data-event selector on the organization trail, EventBridge rules in both Regions, log groups with KMS and retention, subscription to the SIEM, alerts on llm-guard-deny changes and break-glass use",
                   "ログと監査：組織証跡へのbedrock-mantleデータイベントのセレクター追加、両リージョンのEventBridgeルール、KMS・保持期間付きのロググループ、SIEMへのサブスクリプション、llm-guard-denyの変更と緊急用アカウント利用の通知"),
          R_INF, U_PD, 10, T_OT,
          t("02 §4.3, §7.1, §7.4; 01 OBS-001, OBS-002, OBS-004, OBS-007, OPS-010. SIEM-side ingestion and correlation rules excluded (B6)",
            "02 §4.3、§7.1、§7.4、01 OBS-001、OBS-002、OBS-004、OBS-007、OPS-010。SIEM側の取り込みと相関ルールは対象外（B6）")))
    a(row("imp", t("Dashboards and alarms: CloudWatch operations dashboards and alarms (no events for 15 min, function errors, quota use at 80 %, CUR late 36 h), daily access-inventory snapshot job, Quick Sight spend and access-inventory dashboards with row-level security, synthetic availability probe",
                   "ダッシュボードとアラーム：CloudWatchの運用ダッシュボードとアラーム（15分間イベントなし、関数エラー、クォータ使用率80%、CURの36時間遅延）、日次のアクセス棚卸しスナップショットジョブ、行レベルセキュリティ付きのQuick Sight費用・アクセス棚卸しダッシュボード、可用性の合成監視プローブ"),
          R_ENG, U_PM, 1.0, T_OT,
          t("02 §2.2, §7.1, §9, D-14; 01 OBS-003, OBS-006, OBS-010, AVL-M01", "02 §2.2、§7.1、§9、D-14、01 OBS-003、OBS-006、OBS-010、AVL-M01")))
    # 1-4 testing
    a(row("tst", t("Unit tests for custom code (spend guard, usage API, inventory job, policy generator, llm helper)",
                   "自社コードの単体テスト（スペンドガード、利用状況API、棚卸しジョブ、ポリシー生成、llmヘルパー）"),
          R_ENG, U_PD, 18, T_OT,
          t("Sizing: ≈15 % of custom-code build effort (≈6 pm)", "見積根拠：自社コード構築工数（約6人月）の約15%")))
    a(row("tst", t("Integration, security and inspection tests T-001–T-086 on staging: automate, run, retest",
                   "ステージングでの結合・セキュリティ・点検テスト T-001〜T-086：自動化、実施、再テスト"),
          R_QA, U_PM, 2.8, T_OT,
          t("02 §11.1 (86 tests; [LGW] 75). Sizing: avg 0.65 pd per test incl. automation + 1 retest cycle",
            "02 §11.1（86件、[LGW]は75件）。見積根拠：1件平均0.65人日（自動化と再テスト1回を含む）")))
    a(row("tst", t("Load and long-stream tests: spend guard at the A-9 event rate (replayed CloudTrail events), long streams (T-055), Bedrock quota checks (T-056)",
                   "負荷・長時間ストリームのテスト：A-9相当のイベント量でのスペンドガード（CloudTrailイベントの再生）、長時間ストリーム（T-055）、Bedrockクォータの確認（T-056）"),
          R_INF, U_PD, 5, T_OT,
          t("02 §9, §11.1; 01 PRF-M02, PRF-M04, PRF-001 (sizing basis A-9). Replayed events need no Bedrock tokens; no task sizing ([LGW]: 8 pd)",
            "02 §9、§11.1、01 PRF-M02、PRF-M04、PRF-001（規模の前提A-9）。再生イベントはBedrockトークン不要。タスクのサイジングなし（[LGW]は8人日）")))
    for g, en, ja, role, pd, req in GATES:
        a(row("tst", t(f"Launch gate {g}: {en}", f"ローンチゲート {g}：{ja}"), role, U_PD, pd, T_OT,
              t(f"02 §11.2 [CMP {g}, §2.10]; 01 {req}; must pass before first pilot user (01 §1.4)",
                f"02 §11.2 [CMP {g}, §2.10]、01 {req}。最初のパイロット利用者の受け入れ前に合格が必要（01 §1.4）")))
    a(row("tst", t("DR drill before launch: sign in through Osaka (Identity Center replica), switch clients with llm region, move llm-enforce, call each model available in Osaka, fail back",
                   "ローンチ前のDR訓練：大阪経由でサインイン（Identity Centerのレプリカ）、llm regionでクライアントを切替、llm-enforceを移動、大阪で利用可能な各モデルを呼び出し、切り戻し"),
          R_INF, U_PD, 4, T_OT,
          t("02 §9, §11.1 T-052, D-13, R-11, R-35; 01 OPS-007, AVL-M02, AVL-M03, GA exit (01 §1.4). No AZ-loss test: regional services only ([LGW]: 6 pd)",
            "02 §9、§11.1 T-052、D-13、R-11、R-35、01 OPS-007、AVL-M02、AVL-M03、GA移行条件（01 §1.4）。リージョンサービスのみのためAZ障害試験なし（[LGW]は6人日）")))
    # 1-5 data migration: none
    # 1-6 setup
    a(row("set", t("AWS accounts and landing-zone onboarding: llm-dev, llm-staging, llm-prod; SCP attachment, IAM Identity Center instance settings, CUR 2.0 export with IAM principal data and cost allocation tags in the management account, break-glass users and vault",
                   "AWSアカウントとランディングゾーンへの登録：llm-dev、llm-staging、llm-prod。SCPの適用、IAM Identity Centerインスタンスの設定、管理アカウントでのIAMプリンシパル付きCUR 2.0エクスポートとコスト配分タグ、緊急用ユーザーと保管庫"),
          R_INF, U_PD, 10, T_OT,
          t("02 §4.3, §10, D-18; 01 IAM-007–IAM-009, RES-003, CST-007", "02 §4.3、§10、D-18、01 IAM-007〜IAM-009、RES-003、CST-007")))
    a(row("set", t("CI/CD: OIDC federation, IaC plan/apply with drift check, Lambda code signing with AWS Signer, promotion dev → staging → prod, configuration deploy",
                   "CI/CD：OIDC連携、ドリフト検出付きのIaCの計画・適用、AWS SignerによるLambdaのコード署名、開発→ステージング→本番の昇格、構成のデプロイ"),
          R_INF, U_PD, 10, T_OT,
          t("02 §8, §10, D-15; 01 SEC-016, OPS-002. No image mirror ([LGW]: 15 pd)", "02 §8、§10、D-15、01 SEC-016、OPS-002。イメージのミラーなし（[LGW]は15人日）")))
    a(row("set", t("Bedrock setup in both Regions: model access, quota requests for jp. profiles in Tokyo and Osaka and for bedrock-mantle, GetInferenceProfile records, invocation logging off and locked",
                   "両リージョンのBedrock設定：モデルアクセス、東京・大阪のjp.プロファイルとbedrock-mantleのクォータ申請、GetInferenceProfileの記録、呼び出しログの無効化とロック"),
          R_ENG, U_PD, 4, T_OT,
          t("02 §5.1, §9 (R-28), D-5, D-11; 01 MDL-104, RES-008", "02 §5.1、§9（R-28）、D-5、D-11、01 MDL-104、RES-008")))
    a(row("set", t("Production and DR deployment and release", "本番・DRのデプロイとリリース"), R_INF, U_PD, 3, T_OT,
          t("02 §10 (no restart; Lambda alias shift)", "02 §10（再起動なし、Lambdaエイリアスの切替）")))
    # 1-7 training & docs
    a(row("trn", t("Technical docs 03, 04, 06, 07, 09 written to the design, incl. the policy text in 04 §4.2",
                   "技術文書03・04・06・07・09を設計に沿って作成（04 §4.2のポリシー本文を含む）"),
          R_SR, U_PM, 1.0, T_OT, t("README doc set, 02 R-21. Sizing: 5 docs × 4 pd", "READMEの文書体系、02 R-21。見積根拠：5文書×4人日")))
    a(row("trn", t("User-facing docs 05, 08, 10 and editing of the set to the 11 §D checklist",
                   "利用者向け文書05・08・10の作成と、11 §Dのチェックリストに沿った全体の編集"),
          R_TW, U_PD, 12, T_OT, t("README doc set, 11 §D", "READMEの文書体系、11 §D")))
    a(row("trn", t("User onboarding: guide and short video (Okta Verify enrolment, llm login, team choice), 2 live sessions for pilot and GA cohorts, team-lead training (budget and workload-role pull requests)",
                   "利用者のオンボーディング：ガイドと短い動画（Okta Verifyの登録、llm login、チーム選択）、パイロット・GA向けのライブ説明会2回、チームリード研修（予算・ワークロードロールのプルリクエスト）"),
          R_TW, U_PD, 6, T_OT,
          t("01 §1.4, AS-21; 30 engineers (A14). Sizing: 2 sessions × 1 pd + 4 pd material", "01 §1.4、AS-21。エンジニア30人（A14）。見積根拠：説明会2回×1人日＋資料4人日")))
    a(row("trn", t("Operations handover to on-call: 07 runbook walk-through and alert drills", "オンコールへの運用引き継ぎ：07ランブックの読み合わせとアラート訓練"),
          R_SR, U_PD, 3, T_OT, t("02 §10 on-call; 01 OPS-006", "02 §10 オンコール、01 OPS-006")))
    # 1-8 cutover
    a(row("cut", t("Pilot (1 month): onboard pilot teams, triage, fixes, findings into 08", "パイロット（1か月）：パイロットチームの受け入れ、切り分け、修正、知見を08に記録"),
          R_ENG, U_PM, 1.0, T_OT, t("01 §1.4 (pilot teams Q-3)", "01 §1.4（パイロットチームはQ-3）")))
    a(row("cut", t("GA readiness: re-run launch gates on the release that goes live", "GA準備：本番に出すリリースでローンチゲートを再実行"),
          R_QA, U_PD, 6, T_OT, t("01 §1.4 GA exit, OPS-001; 13 applicable gates ([LGW]: 11, 5 pd)", "01 §1.4 GA移行条件、OPS-001。対象ゲート13件（[LGW]は11件・5人日）")))
    a(row("cut", t("Hypercare 2 weeks after GA", "GA後2週間のハイパーケア"), R_ENG, U_PD, 15, T_OT,
          t("Sizing: 1.5 engineers × 10 days", "見積根拠：1.5人×10日")))
    # 1-9 operation (per month)
    a(row("ops", t("On-call and incident response in support hours (business hours assumed): sign-in, wrong suspensions, quota throttling",
                   "サポート時間内のオンコール・障害対応（業務時間帯を想定）：サインイン、誤った停止、クォータによるスロットリング"),
          R_OPS, U_PM, 0.25, T_RC,
          t("Per month. 01 OPS-006 (hours open, Q-6); 00 §1.4. Half of [LGW]: no servers, database or proxy of ours",
            "月額。01 OPS-006（時間帯は未定、Q-6）、00 §1.4。サーバー・DB・プロキシを持たないため[LGW]の半分")))
    a(row("ops", t("Monitoring, alert triage and pull requests for teams, budgets, tiers, workload roles and certificates",
                   "監視、アラートの切り分け、チーム・予算・ティア・ワークロードロール・証明書のプルリクエスト対応"),
          R_OPS, U_PM, 0.25, T_RC, t("Per month. 01 OPS-003, OBS-006; 02 §10", "月額。01 OPS-003、OBS-006、02 §10")))
    a(row("ops", t("First-line help desk: sign-in and Okta Verify issues, team choice, Region switch, onboarding questions",
                   "一次ヘルプデスク：サインイン・Okta Verifyの問題、チーム選択、リージョン切替、利用開始の質問"),
          R_HD, U_PD, 2, T_RC,
          t("Per month. 01 Q-20; 30 engineers (A14). No keys to renew", "月額。01 Q-20。エンジニア30人（A14）。更新するキーはない")))
    a(row("ops", t("Monthly chargeback run, estimate-to-bill gap check and unattributed-cost investigation",
                   "月次の配賦処理、推定と請求の差の確認、帰属不明の費用の調査"),
          R_ENG, U_PD, 1.5, T_RC,
          t("Per month. 01 CST-007, CST-008; 02 §5, D-9. CUR names the caller, so no share model ([LGW]: 2 pd)",
            "月額。01 CST-007、CST-008、02 §5、D-9。CURに呼び出し元が載るため按分モデルなし（[LGW]は2人日）")))
    a(row("ops", t("Periodic reviews: operator and break-glass activity, access inventory, unused workload roles",
                   "定期レビュー：運用者・緊急用アカウントの操作、アクセス棚卸し、未使用のワークロードロール"),
          R_SEC, U_PD, 1, T_RC, t("Per month. 01 OBS-007, OBS-010 (frequency Q-8)", "月額。01 OBS-007、OBS-010（頻度はQ-8）")))
    a(row("ops", t("Recurring DR drill (assumed every 6 months × 4 pd)", "定期DR訓練（6か月ごと×4人日と想定）"), R_INF, U_PD, 0.67, T_RC,
          t("Per month equivalent. 01 OPS-007 (interval Q-6)", "月額換算。01 OPS-007（間隔はQ-6）")))
    # 1-10 maintenance (per month)
    a(row("mnt", t("Quarterly re-run of every launch gate on staging, and on each AWS change a gate depends on (assumed 6 pd per quarter)",
                   "四半期ごと、およびゲートが依存するAWSの変更ごとに、ステージングで全ローンチゲートを再実行（四半期あたり6人日と想定）"),
          R_SR, U_PD, 2, T_RC,
          t("Per month. 01 OPS-001; 02 §10 change gate [CMP §2.10]. Takes the place of [LGW]'s LiteLLM upgrade cycle (12 pd per quarter)",
            "月額。01 OPS-001、02 §10 変更ゲート [CMP §2.10]。[LGW]のLiteLLM更新サイクル（四半期12人日）に相当")))
    a(row("mnt", t("Policy upkeep for new Bedrock operations, endpoints and condition keys; SCP and permission-policy updates",
                   "Bedrockの新しい操作・エンドポイント・条件キーへのポリシー追随、SCPと権限ポリシーの更新"),
          R_SR, U_PD, 1, T_RC, t("Per month. 02 R-14, R-23; 01 SEC-020", "月額。02 R-14、R-23、01 SEC-020")))
    a(row("mnt", t("Quarterly Japan model snapshot re-check of every catalog model and catalog updates (≈3 pd per quarter)",
                   "全カタログモデルの国内処理の四半期再確認とカタログ更新（四半期約3人日）"),
          R_ENG, U_PD, 1, T_RC, t("Per month. 01 MDL-104, AS-17; 02 §5.1 (R-19)", "月額。01 MDL-104、AS-17、02 §5.1（R-19）")))
    a(row("mnt", t("Client package upkeep for new Claude Code, Codex CLI and AWS CLI releases", "Claude Code・Codex CLI・AWS CLIの新リリースに合わせたクライアントパッケージの保守"),
          R_ENG, U_PD, 1, T_RC, t("Per month. 02 §1.3 pinned versions, D-12", "月額。02 §1.3 固定バージョン、D-12")))
    a(row("mnt", t("Patching: Lambda runtimes and dependencies, Inspector findings, advisories", "パッチ適用：Lambdaランタイムと依存ライブラリ、Inspectorの検出事項、アドバイザリ"),
          R_INF, U_PD, 1, T_RC, t("Per month. 02 §8.3, SEC-016 ([LGW]: 2 pd for images, Aurora and Valkey)", "月額。02 §8.3、SEC-016（[LGW]はイメージ・Aurora・Valkeyで2人日）")))
    a(row("mnt", t("Bug fixes and minor changes to the spend guard, usage API, inventory job and llm helper",
                   "スペンドガード、利用状況API、棚卸しジョブ、llmヘルパーの不具合修正と軽微な変更"),
          R_ENG, U_PD, 2, T_RC, t("Per month. 02 R-13", "月額。02 R-13")))
    # 2-2 QA
    a(row("qa", t("Independent review of IaC and security-critical configuration (SCP, permission and trust policies, llm-guard-deny logic, bucket and resource control policies) before launch",
                  "ローンチ前のIaCとセキュリティ上重要な設定の独立レビュー（SCP、権限・信頼ポリシー、llm-guard-denyのロジック、バケット・リソースコントロールポリシー）"),
          R_ARCH, U_PD, 5, T_OT, t("02 §4.7, §8, 04 §4.2, D-7", "02 §4.7、§8、04 §4.2、D-7")))
    a(row("qa", t("Phase-gate reviews: design, build complete, launch readiness, GA", "フェーズゲートレビュー：設計、構築完了、ローンチ準備、GA"),
          R_QA, U_PD, 4, T_OT, t("01 §1.4 exit criteria. 4 gates × 1 pd", "01 §1.4 移行条件。4ゲート×1人日")))
    # 2-5 security
    a(row("sec", t("Security design review: threat model and residual-risk acceptance (R-34), SCP and policy layers, spend guard failure modes, break-glass",
                   "セキュリティ設計レビュー：脅威モデルと残存リスクの受容（R-34）、SCPとポリシー階層、スペンドガードの障害モード、緊急用アクセス"),
          R_SEC, U_PD, 8, T_OT,
          t("02 §4.7, §8, §8.1, R-34. No guardrail service or proxy to review ([LGW]: 10 pd)", "02 §4.7、§8、§8.1、R-34。レビュー対象のガードレールサービス・プロキシなし（[LGW]は10人日）")))
    a(row("sec", t("Third-party penetration test before launch, focused on the policy layers", "ローンチ前の第三者ペネトレーションテスト（ポリシー階層が中心）"),
          R_VEN, U_OT, 1, T_OT,
          t("02 §8.3 (R-34). Price = template sample value, as [LGW], placeholder until a vendor quote (Security); no web application is in scope, so a quote may be lower",
            "02 §8.3（R-34）。価格はテンプレートのサンプル値（[LGW]と同じ）で、ベンダー見積までの仮置き（セキュリティ）。Webアプリケーションが対象外のため見積は下がる可能性"),
          j=2000000))
    return r


def infra_rows(pt, dr, dev, stg):
    r = []
    a = r.append
    pt_t, dr_t, dev_t, stg_t = tot(pt), tot(dr), tot(dev), tot(stg)
    lst = lambda cs, sep: sep.join(f"{c['name']} {usd(c['usd'])}" for c in cs)
    lst_ja = lambda cs: "、".join(f"{t_ja(c['name'])} {usd(c['usd'])}" for c in cs)
    a(row("inf", t("Dev environment during the project (Tokyo)", "プロジェクト期間中の開発環境（東京）"), R_VEN, U_MF, MONTHS_DEV, T_OT,
          t(f"Quantity = {MONTHS_DEV} months (2027-02 to 2027-07). {usd(dev_t)}/month × {FX} = J. {lst(dev, '; ')}. 02 §10, 03 §2. {PL}",
            f"数量＝{MONTHS_DEV}か月（2027年2月〜7月）。月額{usd(dev_t)}×{FX}円＝J列。内訳：{lst_ja(dev)}。02 §10、03 §2。{PL}"),
          j=jpy(dev_t)))
    a(row("inf", t("Staging environment during the project (Tokyo, same policies and spend guard as production)", "プロジェクト期間中のステージング環境（東京、本番と同じポリシー・スペンドガード）"),
          R_VEN, U_MF, MONTHS_STG, T_OT,
          t(f"Quantity = {MONTHS_STG} months (2027-04 to 2027-07). {usd(stg_t)}/month. {lst(stg, '; ')}. 02 §10 (valid launch gates). {PL}",
            f"数量＝{MONTHS_STG}か月（2027年4月〜7月）。月額{usd(stg_t)}。内訳：{lst_ja(stg)}。02 §10（ローンチゲートの有効性のため）。{PL}"),
          j=jpy(stg_t)))
    a(row("inf", t("Production Tokyo before GA (build and pilot)", "GA前の本番（東京）（構築とパイロット）"), R_VEN, U_MF, MONTHS_PRE_GA, T_OT,
          t(f"Quantity = {MONTHS_PRE_GA} months (2027-06 to 2027-07). Same components as the recurring production rows below: {usd(pt_t)}/month. {PL}",
            f"数量＝{MONTHS_PRE_GA}か月（2027年6月〜7月）。下記の本番の継続費用の行と同じ構成要素：月額{usd(pt_t)}。{PL}"),
          j=jpy(pt_t)))
    a(row("inf", t("DR Osaka before GA (build and DR drill)", "GA前のDR（大阪）（構築とDR訓練）"), R_VEN, U_MF, MONTHS_PRE_GA, T_OT,
          t(f"Quantity = {MONTHS_PRE_GA} months. Same components as the recurring DR rows below: {usd(dr_t)}/month. {PL}",
            f"数量＝{MONTHS_PRE_GA}か月。下記のDRの継続費用の行と同じ構成要素：月額{usd(dr_t)}。{PL}"),
          j=jpy(dr_t)))
    a(row("inf", t("Bedrock tokens used by the platform team during the project (development, tests, launch gates, DR drill)",
                   "プロジェクト期間中に基盤チームが使うBedrockトークン（開発、テスト、ローンチゲート、DR訓練）"),
          R_VEN, U_OT, 1, T_OT,
          t("Sizing: dev use ≈ USD 300/month × 6 + functional and gate tests ≈ USD 300 + quota checks ≈ USD 30 → ≈ USD 2,130 (as [LGW]; the spend guard load test replays events). Not charged back",
            "見積根拠：開発利用 月約300USD×6＋機能・ゲート試験 約300USD＋クォータ確認 約30USD → 約2,130USD（[LGW]と同額。スペンドガードの負荷試験はイベントの再生）。配賦しない"),
          j=jpy(2130)))
    for c in pt:
        a(row("inf", t(f"Production Tokyo: {c['name']}", f"本番（東京）：{t_ja(c['name'])}"), R_VEN, U_MF, 1, T_RC,
              t(f"Per month from GA. {c['calc']} = {usd(c['usd'])}. {c['basis']}. {PL}",
                f"GA以降の月額。{calc_ja(c['calc'])} = {usd(c['usd'])}。{t_ja(c['basis'])}。{PL}"),
              j=jpy(c["usd"])))
    for c in dr:
        a(row("inf", t(f"DR Osaka: {c['name']}", f"DR（大阪）：{t_ja(c['name'])}"), R_VEN, U_MF, 1, T_RC,
              t(f"Per month from GA. {c['calc']} = {usd(c['usd'])}. {c['basis']}. {PL} (ap-northeast-3)",
                f"GA以降の月額。{calc_ja(c['calc'])} = {usd(c['usd'])}。{t_ja(c['basis'])}。{PL}（ap-northeast-3）"),
              j=jpy(c["usd"])))
    a(row("inf", t("Dev environment after GA (Tokyo)", "GA後の開発環境（東京）"), R_VEN, U_MF, 1, T_RC,
          t(f"Per month. Same sizing as the project-period row: {usd(dev_t)}. Kept for maintenance (02 §10). {PL}",
            f"月額。プロジェクト期間の行と同じサイジング：{usd(dev_t)}。保守のため維持（02 §10）。{PL}"),
          j=jpy(dev_t)))
    a(row("inf", t("Staging environment after GA (Tokyo)", "GA後のステージング環境（東京）"), R_VEN, U_MF, 1, T_RC,
          t(f"Per month. Same sizing as the project-period row: {usd(stg_t)}, of which the Private CA is USD 401.50 (finding F-1). Needed for gate re-runs (OPS-001). {PL}",
            f"月額。プロジェクト期間の行と同じサイジング：{usd(stg_t)}（うちPrivate CAが401.50USD、指摘F-1）。ゲート再実行に必要（OPS-001）。{PL}"),
          j=jpy(stg_t)))
    return r


LIK = {"Low": 0.25, "Medium": 0.5, "High": 0.75}
LIK_JA = {"Low": "低", "Medium": "中", "High": "高"}


def risk_rows():
    r = []
    a = r.append

    def risk(rid, lik, desc_en, desc_ja, role, unit, qty, typ, impact_en, impact_ja, j=None, src="02 §14"):
        notes = t(f"{src} {rid} (likelihood {lik} = {int(LIK[lik] * 100)} %, column K). {impact_en}",
                  f"{src} {rid}（発生可能性：{LIK_JA[lik]}＝{int(LIK[lik] * 100)}%、K列）。{impact_ja}")
        a(row("con", t(f"Risk {rid}: {desc_en}", f"リスク {rid}：{desc_ja}"), role, unit, qty, typ, notes, j=j, likelihood=LIK[lik]))

    ra = route_a()
    risk("R-12 / Q-24", "Medium", "Route A adopted for GA (D-6) — endpoint VPC, endpoints, Resolver, DNS forwarding, endpoint policies",
         "GAでRoute Aを採用（D-6）— エンドポイントVPC、エンドポイント、Resolver、DNS転送、エンドポイントポリシー",
         R_INF, U_PD, ra["build_pd"], T_OT, "Impact 15 pd, as [LGW]'s Route A option. 01 SEC-014, RES-007", "影響額15人日（[LGW]のRoute Aオプションと同じ）。01 SEC-014、RES-007")
    risk("R-12 / Q-24", "Medium", "Route A recurring part — interface endpoints over Direct Connect (Tokyo)",
         "Route Aの継続費用 — Direct Connect経由のインターフェースエンドポイント（東京）",
         R_VEN, U_MF, 1, T_RC, f"Impact {usd(ra['monthly_usd'])}/month (§9). Osaka endpoints created at failover, not priced. {PL}",
         f"影響額 月{usd(ra['monthly_usd'])}（§9）。大阪のエンドポイントは切替時に作成するため計上しない。{PL}", j=jpy(ra["monthly_usd"]))
    risk("R-2", "Medium", "CUR lacks the session name, bedrock-mantle or short-term-key attribution — per-person attribution from CloudTrail joined to CUR",
         "CURにセッション名・bedrock-mantle・短期キーの帰属がない — CloudTrailとCURを結合して個人別に配分",
         R_ENG, U_PM, 1.0, T_OT, "Impact 1.0 pm. 01 AS-24, CST-007; V-15", "影響額1.0人月。01 AS-24、CST-007、V-15")
    risk("R-30 / AS-25", "Medium", "stream-completion events do not reach EventBridge — meter from the trail's S3 delivery instead (longer delay)",
         "ストリーム完了イベントがEventBridgeに届かない — 証跡のS3配信から計測（遅延が長くなる）",
         R_SR, U_PM, 1.0, T_OT, "Impact 1.0 pm. 01 CST-009; V-13", "影響額1.0人月。01 CST-009、V-13")
    risk("R-9", "Medium", "one permission set per team exceeds the Identity Center quotas — team from an Entra attribute (ABAC, ADR D-2 option 2)",
         "チームごとの権限セットがIdentity Centerのクォータを超える — Entra属性によるチーム判定（ABAC、ADR D-2の案2）",
         R_SR, U_PM, 1.0, T_OT, "Impact 1.0 pm: policies, spend guard, CUR views. 01 Q-22, AS-26", "影響額1.0人月：ポリシー、スペンドガード、CURのビュー。01 Q-22、AS-26")
    risk("R-35", "Medium", "Identity Center replication not available for our instance — another sign-in path for DR",
         "当社インスタンスでIdentity Centerのレプリケーションが使えない — DR用の別のサインイン経路",
         R_SR, U_PD, 10, T_OT, "Impact 10 pd. 01 AVL-001, AS-23", "影響額10人日。01 AVL-001、AS-23")
    risk("R-5 / Q-13", "Medium", "Security requires screening for some OUs — Classic-tier Bedrock guardrail with regex filters through a Bedrock policy",
         "セキュリティが一部OUでの検査を要求 — BedrockポリシーによるClassic tierのガードレール（正規表現フィルター）",
         R_SR, U_PD, 10, T_OT, "Impact 10 pd; regex sensitive-information filters have no charge [PL AmazonBedrock 2026-11-11]. 01 SEC-008, D-10",
         "影響額10人日。正規表現の機密情報フィルターは無料 [PL AmazonBedrock 2026-11-11]。01 SEC-008、D-10")
    risk("Q-10 / D-11", "Medium", "per-team content logging required this phase — content-logging account, invocation logging, Macie, V-1 re-run",
         "今期にチーム単位の内容記録が必要 — 内容記録用アカウント、呼び出しログ、Macie、V-1の再実行",
         R_SR, U_PM, 0.5, T_OT, "Impact 0.5 pm: account-level configuration ([LGW] R-6: 1.0 pm). 01 PRV-002",
         "影響額0.5人月：アカウント単位の設定（[LGW]のR-6は1.0人月）。01 PRV-002", src="01")
    risk("R-8", "Medium", "AWS CLI caches credentials in files — llm helper keeps the cache in the OS credential store",
         "AWS CLIが認証情報をファイルにキャッシュする — llmヘルパーがOSの資格情報ストアに保持",
         R_ENG, U_PD, 10, T_OT, "Impact 10 pd. 02 §8.1", "影響額10人日。02 §8.1")
    risk("R-4", "High", "Codex CLI's model choice in Japan is unclear — workaround or limited approval",
         "Codex CLIで国内処理のモデルが選べるか不明 — 回避策または限定承認",
         R_ENG, U_PD, 10, T_OT, "Impact 10 pd. 01 FUN-002; T-002", "影響額10人日。01 FUN-002、T-002")
    risk("R-1 / R-6", "High", "heavy or non-streaming workloads need their own enrolled accounts — enrolment, quotas, budgets",
         "大量・非ストリーミングのワークロードに専用の登録アカウントが必要 — 登録、クォータ、予算",
         R_INF, U_PD, 5, T_OT, "Impact 5 pd. D-18; 01 CST-009, CST-014", "影響額5人日。D-18、01 CST-009、CST-014")
    return r


def estimate_rows():
    """All Estimate rows and the four environments they are priced from."""
    envs = (prod_tokyo(), dr_osaka(), dev_env(), stg_env())
    return labor_rows() + infra_rows(*envs) + risk_rows(), envs


def t_ja(en):
    from tx import JA
    return JA[en]


CALC_JA = [("M events", "百万件"), ("M polls", "百万回のポーリング"), ("M invocations", "百万回の起動"),
           ("M writes", "百万件の書き込み"), ("M replicated writes", "百万件の複製書き込み"), ("M reads", "百万件の読み取り"),
           ("M requests", "百万リクエスト"), ("events", "件"), ("authors", "作成者"), ("readers", "閲覧者"),
           ("CMKs", "CMK"), ("certificates", "証明書"), ("checks", "チェック"), ("CIs", "構成項目"), ("evals", "評価"),
           ("functions", "関数"), ("roles", "ロール"), ("alarms", "アラーム"), ("metrics", "メトリクス"),
           ("replica keys", "レプリカキー"), ("ingest", "取り込み"), ("stored", "保存"), ("avg", "平均"),
           ("(2 dashboards within the free 3)", "（ダッシュボード2個は無料枠3個以内）"),
           ("(CUR export and non-action Budgets free)", "（CURエクスポートとアクションなしのBudgetsは無料）"),
           ("per full gate run", "（全ゲート1回あたり）"), ("run/quarter", "回／四半期"), ("probe on", "プローブ"),
           ("Lambda", "Lambda")]


def calc_ja(s):
    for a, b in sorted(CALC_JA, key=lambda x: -len(x[0])):
        s = s.replace(a, b)
    return s


# ---------------------------------------------------------------- assumptions & exclusions
ASSUMPTIONS = [
    ("Scope / 範囲",
     "Build and 24-month operation of the IAM-native LLM gateway as designed in 01 and 02 v0.1 (Draft, 2026-11-20): no gateway server; IAM Identity Center, IAM policies and SCPs, CUR 2.0 by IAM principal and a serverless spend guard; Tokyo with DR in Osaka; the Bedrock catalog in 01 §6.5; Route B for the pilot and GA, with Route A as a contingency row (02 D-6, 01 Q-24).",
     "01・02 v0.1（作成中、2026-11-20）で設計されたIAMネイティブLLMゲートウェイの構築と24か月の運用を対象とする。ゲートウェイサーバーなし。IAM Identity Center、IAMポリシーとSCP、IAMプリンシパル別のCUR 2.0、サーバーレスのスペンドガード。東京、DRは大阪。01 §6.5のBedrockモデル。パイロット・GAともRoute Bとし、Route Aは予備費の行として計上（02 D-6、01 Q-24）。"),
    ("Comparability / 比較の前提",
     "To compare with the LiteLLM design's estimate ([LGW] cost/, commit 87ba355), this estimate keeps its schedule, usage basis, rates, exchange rate, template parameters, penetration-test placeholder and platform Bedrock usage. Differences come only from the design.",
     "LiteLLM設計の見積（[LGW]のcost/、コミット87ba355）と比較するため、スケジュール、利用量の前提、単価、為替レート、テンプレートのパラメータ、ペネトレーションテストの仮価格、基盤のBedrock利用量は同じとする。差は設計の違いからのみ生じる。"),
    ("Schedule / スケジュール",
     "Project 2027-01 to 2027-07 (7 months), as [LGW]: M1 remaining requirements, design and spikes; M2–M5 build; M4–M6 tests and launch gates; M6 production and DR build, penetration test; M7 pilot and DR drill. GA 2027-08. Recurring costs start at GA; operation period 24 months (2027-08 to 2029-07). Dates are open (01 Q-3); the smaller build may allow an earlier GA.",
     "プロジェクト期間 2027年1月〜7月（7か月、[LGW]と同じ）：1か月目 残りの要件・設計・早期検証、2〜5か月目 構築、4〜6か月目 テスト・ローンチゲート、6か月目 本番・DR構築とペネトレーションテスト、7か月目 パイロットとDR訓練。2027年8月GA。継続費用はGAから発生し、運用期間は24か月（2027年8月〜2029年7月）。日程は未確定（01 Q-3）。構築規模が小さいためGAを早められる可能性がある。"),
    ("Effort unit / 工数単位",
     "1 person-month = 20 person-days = 160 hours (Rates sheet). Rates are blended and exclude tax.",
     "1人月＝20人日＝160時間（Ratesシート）。単価は平均単価・税抜。"),
    ("Rates / 単価",
     "OPEN ITEM (FinOps): no internal rates exist yet. The template's sample rates (indicative FY2026 market rates) are kept unchanged, as in [LGW], and are not quotes. Replace them on the Rates sheet; every labor row updates.",
     "【未決事項・FinOps】社内単価が未設定のため、[LGW]と同じくテンプレートのサンプル単価（2026年度の参考相場）をそのまま使用しており、見積回答ではない。Ratesシートで置き換えると全工数行が更新される。"),
    ("Recurring costs / 継続費用",
     "Recurring lines are monthly amounts; annual = monthly x 12. The grand total includes 24 recurring months (the operation period). The markdown output also gives 12- and 36-month views.",
     "継続費用は月額で計上し、年額＝月額×12。総額には運用期間の24か月分の継続費用を含む。Markdown出力には12か月・36か月の試算も記載。"),
    ("Project management / PM費",
     "Project management = PM % (10 %, template default) x development cost (one-time phase-based costs). PM effort is not included in phase rows.",
     "PM費＝PM費率（10%、テンプレート既定値）×開発費（工程別の初期費用）。工程別の行にはPM工数を含めない。"),
    ("Contingency / 予備費",
     "Contingency = 15 % (template default) of initial cost excluding contingency, plus 15 % of monthly recurring cost. Identified risks from 02 §14 and 01 §9 are line items with their impact as Quantity x Unit cost and their likelihood in column K (Low 25 %, Medium 50 %, High 75 %), so Subtotal = impact x likelihood. Tax is never included in the base.",
     "予備費＝予備費を除く初期費用×15%（既定値）＋継続月額×15%。02 §14・01 §9の特定済みリスクは、影響額を数量×単価、発生確率をK列（低25%、中50%、高75%）に入力した明細とし、小計＝影響額×発生確率。消費税は算定基礎に含めない。"),
    ("Tax / 消費税",
     "Consumption tax is calculated once on each total at the rate on Summary; amounts below JPY 1 are rounded down.",
     "消費税はSummaryの税率で各合計に対して1回計算し、1円未満は切り捨て。"),
    ("Cloud / クラウド",
     "AWS On-Demand list prices from the AWS Price List API offer files for ap-northeast-1 and ap-northeast-3 (publications 2026-10-30 to 2026-11-19, checked 2026-11-20), cited as [PL]; the Quick Sight author price is [LGW]'s (pricing page, 2026-11-17). 730 h per month; no Savings Plans or EDP discounts; free tiers are not applied. Budget exchange rate JPY 160 / USD, as [LGW]. OPEN ITEM (FinOps): confirm the budget rate.",
     "AWSの価格はAWS Price List API（ap-northeast-1／ap-northeast-3、2026-10-30〜2026-11-19公開版、2026-11-20確認）のオンデマンド定価（[PL]と表記）。Quick Sightの作成者の価格は[LGW]の値（料金ページ、2026-11-17）。1か月730時間、Savings Plans・EDP割引は考慮せず、無料枠も適用しない。予算レートは[LGW]と同じ1USD＝160円。【未決事項・FinOps】予算レートの確認。"),
    ("No-charge services / 無料のサービス",
     "IAM, IAM Identity Center (incl. its Osaka replica), AWS Organizations and SCPs, IAM Roles Anywhere, AWS Signer for Lambda, CUR 2.0 data exports, AWS Budgets without actions, and AWS service events on the EventBridge default bus have no charge (AWS pricing pages; not in [PL]). Organization trail management events are its first copy.",
     "IAM、IAM Identity Center（大阪のレプリカを含む）、AWS OrganizationsとSCP、IAM Roles Anywhere、Lambda向けAWS Signer、CUR 2.0のデータエクスポート、アクションなしのAWS Budgets、EventBridgeのデフォルトバス上のAWSサービスイベントは無料（AWSの料金ページ。[PL]には含まれない）。組織証跡の管理イベントは最初のコピー。"),
    ("Environments / 環境",
     "Accounts llm-dev, llm-staging and llm-prod (Tokyo, with DR in Osaka in the same account), as 02 §10 and D-18. Staging has the same SCP, policy shapes, catalog and spend guard as production, so that launch gates are valid, and a Private CA of its own. Dev and staging remain after GA.",
     "アカウントはllm-dev、llm-staging、llm-prod（東京、DRは同一アカウントの大阪）（02 §10、D-18）。ステージングは、ローンチゲートが有効となるよう本番と同じSCP・ポリシーの形・カタログ・スペンドガードを持ち、専用のPrivate CAを持つ。開発・ステージングはGA後も維持する。"),
    ("Sizing / サイジング",
     "No fixed capacity: every component is serverless or a regional AWS service. Per-call charges use [LGW]'s expected usage: about 1.09 million model calls a month (30 engineers plus workloads), 1.68 million CloudTrail events (2 per streaming call; workloads half streaming), 5 counter updates per metered call, 6 teams, 10 DC workloads. §10 shows the per-call charges at higher volumes.",
     "固定容量なし：全コンポーネントがサーバーレスまたはリージョンのAWSサービス。従量部分は[LGW]の想定利用量による：モデル呼び出し月約109万回（エンジニア30人とワークロード）、CloudTrailイベント月168万件（ストリーミング1回につき2件、ワークロードは半数がストリーミング）、計測1回につきカウンター更新5件、6チーム、DCワークロード10件。§10に利用量が多い場合の従量費用を示す。"),
    ("Users / 利用者",
     "30 engineers use the gateway with coding agents (set by the requester on 2026-11-17 for [LGW], kept here). CMP A-9 (about 5,000 employees, about 300 concurrent users) is not used for sizing. Workload volume (UC-2) is as in the markdown usage table.",
     "コーディングエージェントでゲートウェイを利用するエンジニアは30人（2026-11-17に依頼者が[LGW]用に設定した値を踏襲）。CMP A-9（従業員約5,000人、同時約300人）はサイジングに使わない。ワークロード（UC-2）の利用量はMarkdownの利用試算表のとおり。"),
    ("Model usage / モデル利用料",
     "Bedrock token charges for teams are not in the totals: CUR 2.0 charges them to the calling principal (01 CST-007). The markdown output gives the same low / expected / high usage table as [LGW]. Bedrock tokens used by the platform team itself (development, tests, gates, probe) are included.",
     "チームのBedrockトークン料金は合計に含めない（CUR 2.0で呼び出し元のプリンシパルに配賦、01 CST-007）。Markdown出力に[LGW]と同じ低・想定・高の利用試算を記載。基盤チーム自身の利用（開発・テスト・ゲート・監視プローブ）は計上する。"),
    ("Licences / ライセンス",
     "No licensed software: no LiteLLM (01 AS-6 and Q-17 withdrawn). The Bedrock guardrail option uses regex filters, which have no charge.",
     "ライセンスが必要なソフトウェアなし：LiteLLMを使わない（01 AS-6・Q-17は取り下げ）。Bedrockガードレールの選択肢は無料の正規表現フィルターを使う。"),
    ("Certificates / 証明書",
     "AWS Private CA in general-purpose mode, one in llm-prod and one in llm-staging, because workload certificates last up to 90 days (02 D-4) and short-lived mode issues only certificates of 7 days or less. Using an existing corporate CA as the trust anchor would remove both (finding F-1).",
     "ワークロード証明書の有効期間は最大90日（02 D-4）で、短期証明書モードは7日以下の証明書しか発行できないため、汎用モードのAWS Private CAをllm-prodとllm-stagingに1つずつ置く。既存の社内CAをトラストアンカーにすれば両方とも不要になる（指摘F-1）。"),
    ("Delivery team / 実施体制",
     "Platform engineering does all build and run work estimated here, using the template roles. Penetration test is by a third party; its price is the template sample value until a vendor quote (OPEN ITEM, Security).",
     "本見積の構築・運用作業はプラットフォームエンジニアリングがテンプレートの役割で実施する。ペネトレーションテストは外部委託で、ベンダー見積までテンプレートのサンプル価格を使用（【未決事項・セキュリティ】）。"),
    ("Data migration / データ移行",
     "No data migration: 01 and 02 define none, and what the gateway replaces is still open (01 Q-2).",
     "データ移行なし：01・02に定義がなく、置き換え対象も未確定（01 Q-2）。"),
    ("Support hours / サポート時間",
     "On-call covers business hours (01 OPS-006, Q-6 open). 24x7 on-call would increase the Operation rows.",
     "オンコールは業務時間帯を前提（01 OPS-006、Q-6未確定）。24時間365日対応の場合、運用の行が増える。"),
]

EXCLUSIONS = [
    ("Model inference / モデル利用料",
     "Bedrock token charges for teams' usage (charged to the calling principal through CUR 2.0, 01 CST-007). See the separate usage table in the markdown output.",
     "各チームの利用によるBedrockトークン料金（CUR 2.0で呼び出し元のプリンシパルに配賦、01 CST-007）。Markdown出力の別表を参照。"),
    ("Route A at full cost / Route Aの全額",
     "Route A is in the totals only at its expected value (contingency, 50 %). Its full cost is in §9 of the markdown output.",
     "Route Aは期待値（予備費、50%）でのみ合計に含める。全額はMarkdown出力の§9に記載。"),
    ("Azure OpenAI / Azure OpenAI",
     "Azure OpenAI is not reachable without a proxy (01 NG-10, MDL-011), so it has no option here.",
     "Azure OpenAIはプロキシなしでは利用できないため（01 NG-10、MDL-011）、本見積に選択肢はない。"),
    ("Remote access / リモートアクセス",
     "Remote and home access (01 NG-1, R-27).",
     "リモート・在宅アクセス（01 NG-1、R-27）。"),
    ("Internal staff / 社内要員",
     "Time of other internal teams for their own deliverables: Network (egress list, secure web gateway rules, V-11 data), Identity (Entra app, Conditional Access, groups), Endpoint/Intune (client deployment), Cloud platform (SCP attachment, Identity Center, CUR), Legal/privacy and FinOps approvals, users attending training.",
     "他部門の要員工数：ネットワーク（出口IP一覧、セキュアWebゲートウェイのルール、V-11の情報）、ID管理（Entraアプリ、条件付きアクセス、グループ）、端末/Intune（クライアント配布）、クラウド基盤（SCPの適用、Identity Center、CUR）、法務・FinOpsの承認、研修受講者。"),
    ("Shared platforms / 共有基盤",
     "Costs of shared platforms already paid elsewhere: the organization CloudTrail trail and log-archive account, SIEM licence, ingestion and correlation rules (02 R-34), Direct Connect circuits, corporate Git/CI, Entra ID P1/P2, Okta and Intune licences.",
     "他で負担済みの共有基盤費用：組織のCloudTrail証跡とログアーカイブアカウント、SIEMのライセンス・取り込み・相関ルール（02 R-34）、Direct Connect回線、社内Git/CI、Entra ID P1/P2・Okta・Intuneのライセンス。"),
    ("Support contracts / サポート契約",
     "AWS Support plan (01 Q-20).",
     "AWSサポートプラン（01 Q-20）。"),
    ("Enhancements / 機能追加",
     "New endpoint families (01 NG-7), response caching, API translation for tools that speak only the OpenAI format (NG-10), per-caller rate limits (NG-12), and features beyond the maintenance allowance.",
     "新しいエンドポイント種別（01 NG-7）、レスポンスキャッシュ、OpenAI形式のみのツール向けのAPI変換（NG-10）、呼び出し元ごとのレート制限（NG-12）、保守範囲を超える機能追加。"),
    ("Enrolled accounts / 登録アカウント",
     "AWS charges in enrolled workload accounts (D-18) other than their Bedrock tokens; their VPC endpoints and budgets belong to their owners (R-32).",
     "登録されたワークロードアカウント（D-18）のBedrockトークン以外のAWS料金。そのVPCエンドポイントと予算は各所有者が負担（R-32）。"),
    ("Expenses / 経費",
     "Travel, accommodation and on-site expenses.",
     "出張・宿泊・現地作業に伴う経費。"),
    ("Unlisted purchases / 記載外の購入",
     "Hardware or software not listed on the Estimate sheet; end-user devices and office network changes.",
     "Estimateシートに記載のないハードウェア・ソフトウェア、利用者端末および社内ネットワークの変更。"),
    ("Price changes / 価格変動",
     "Exchange-rate movements beyond JPY 160 / USD and AWS price changes after 2026-11-20.",
     "1USD＝160円を超える為替変動、および2026-11-20以降のAWSの価格改定。"),
    ("Legal & audit / 法務・監査",
     "Legal, regulatory or external audit fees, incl. any ISO 27001 / SOC 2 work (01 Q-19).",
     "法務・規制対応・外部監査の費用（ISO 27001／SOC 2対応を含む、01 Q-19）。"),
    ("Decommissioning / 旧システム廃止",
     "Decommissioning of anything the gateway replaces (01 Q-2 open).",
     "ゲートウェイが置き換えるものの廃止作業（01 Q-2未確定）。"),
]

# ---------------------------------------------------------------- Bedrock usage (not in totals): same as [LGW] §7
# jp. (geographic CRIS, 'Standard' non-global) and In-Region prices, USD per 1M tokens, [PL Tokyo] as checked by [LGW]
BR = {
    "Claude Opus 5.5":   dict(inp=4.40, cw=5.50, cr=0.22, out=22.00),
    "Claude Haiku 5.5":  dict(inp=0.11, cw=0.1375, cr=0.011, out=0.55),
    "Claude Opus 4.8":   dict(inp=5.50, cw=6.875, cr=0.55, out=27.50),
    "Claude Sonnet 4.6": dict(inp=3.30, cw=4.125, cr=0.33, out=16.50),
    "Claude Haiku 4.5":  dict(inp=1.10, cw=1.375, cr=0.11, out=5.50),
    "Amazon Nova 2 Lite": dict(inp=0.396, cw=0.0, cr=0.099, out=3.311),
    "Titan Text Embeddings V2": dict(inp=0.029, cw=0, cr=0, out=0),
    "Cohere Embed v4":   dict(inp=0.12, cw=0, cr=0, out=0),
    "Mistral Large 3":   dict(inp=0.61, cw=0, cr=0, out=1.82),
    "gpt-oss-120b":      dict(inp=0.18, cw=0, cr=0, out=0.73),
}
MDL = {"Claude Opus 5.5": "MDL-001", "Claude Haiku 5.5": "MDL-002", "Claude Opus 4.8": "MDL-003",
       "Claude Sonnet 4.6": "MDL-004", "Claude Haiku 4.5": "MDL-005", "Amazon Nova 2 Lite": "MDL-006",
       "Titan Text Embeddings V2": "MDL-007", "Cohere Embed v4": "MDL-008", "Mistral Large 3": "MDL-009",
       "gpt-oss-120b": "MDL-010"}
DAY = dict(inp=0.6, cw=0.4, cr=12.0, out=0.25)    # coding-agent tokens per active user-day (M); Opus 5.5 day ≈ USD 13
MIX = {"Claude Opus 5.5": 0.60, "Claude Sonnet 4.6": 0.15, "Claude Opus 4.8": 0.05, "Claude Haiku 5.5": 0.20}
SCEN = {"Low": dict(users=ENGINEERS, days=12, wl=0.25), "Expected": dict(users=ENGINEERS, days=15, wl=1.0),
        "High": dict(users=ENGINEERS, days=19, wl=3.0)}
WL = {"Claude Haiku 4.5": dict(inp=1.0, out=0.2), "Amazon Nova 2 Lite": dict(inp=1.0, out=0.2),
      "gpt-oss-120b": dict(inp=0.3, out=0.06), "Mistral Large 3": dict(inp=0.2, out=0.04),
      "Titan Text Embeddings V2": dict(inp=0.5, out=0), "Cohere Embed v4": dict(inp=0.5, out=0)}


def usage():
    res = {}
    for s, p in SCEN.items():
        rows = {}
        for m in BR:
            tk = dict(inp=0.0, cw=0.0, cr=0.0, out=0.0)
            if m in MIX:
                k = p["users"] * p["days"] * MIX[m]
                for f in tk:
                    tk[f] += DAY[f] * k
            if m in WL:
                tk["inp"] += WL[m]["inp"] * 1000 * p["wl"]
                tk["out"] += WL[m]["out"] * 1000 * p["wl"]
            rows[m] = dict(total_b=sum(tk.values()) / 1000, usd=sum(tk[f] * BR[m][f] for f in tk))
        res[s] = rows
    return res


def day_cost(m):
    return sum(DAY[f] * BR[m][f] for f in DAY)


# ---------------------------------------------------------------- the LiteLLM design's estimate, for section 7
# From ai-gateway-on-aws cost/ at commit 87ba355 (cost_estimate_InternalLLMGateway_v0.1.md, the same
# template, parameters and rates). make.py recomputes them from that repository when it is checked out next
# to this one and fails if they differ.
LGW = dict(
    commit="87ba355",
    initial=43820838, monthly=3019657.25, effort=30.05, effort_excl_con=27.55, dev=26620000, pm=2662000,
    ot=dict(req=1180000, des=3825000, imp=11312500, tst=4900000, mig=0, set=1820000, trn=1895000, cut=1687500,
            ops=0, mnt=0, pm=0, qa=510000, inf=3257642, lic=0, sec=2800000, con=2593750),
    rc=dict(req=0, des=0, imp=0, tst=0, mig=0, set=0, trn=0, cut=0, ops=837500, mnt=512500, pm=0, qa=0,
            inf=963892, lic=0, sec=0, con=358681.25),
    cont_ot=5377446, cont_rc=347084,
    env_usd=dict(prod=2480.32, dr=955.05, dev=501.86, stg=2087.09),
    usage_expected=1343219.2,
)
