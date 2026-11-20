"""Markdown snapshot of the IAM-native LLM gateway estimate, in English or Japanese.

Sections 1-6 (Summary, Estimate details, Rates, Assumptions, Lists, Calculation
rules) come from the template's snapshot.py, with this estimate's notes.
Sections 7-12 are this estimate's own: the comparison with the LiteLLM design's
estimate, model usage, options, sizing detail, open items and findings.
Numbers are computed from model.py with the workbook's formulas
(estimate.compute), so the markdown matches the workbook.

Run make.py to write it; render(lang) returns (text, untranslated strings).
"""
import model as M
import template_tools  # noqa: F401  (puts the template's tools/ on sys.path)
from estimate import CATEGORIES, CAT_ORDER, PHASE, R_VEN, T_OT, T_RC, U_PD, U_PM, compute
from snapshot import Notes, Snapshot, Translator, n
from tx import JA, t

XLSX = "CostEstimate_IAMNativeLLMGateway_v0.1.xlsx"
XLSX_JP = "CostEstimate_IAMNativeLLMGateway_v0.1_jp.xlsx"
MD, MD_JP = "cost_estimate_IAMNativeLLMGateway_v0.1.md", "cost_estimate_IAMNativeLLMGateway_v0.1_jp.md"
t("Total", "合計")

NOTES = Notes(
    parameters=[
        t("Template default kept, as [LGW]; the design docs give no reason to change it.", "[LGW]と同じくテンプレート既定値を維持。設計文書に変更する根拠がない。"),
        t("Template default kept, as [LGW]. Identified risks from 02 §14 and 01 §9 are line items with a likelihood (§2, Contingency).",
          "[LGW]と同じくテンプレート既定値を維持。02 §14・01 §9の特定済みリスクは発生確率付きの明細（§2 予備費）。"),
        t("Template default, as [LGW].", "テンプレート既定値（[LGW]と同じ）。"),
        t("Calculated once on each total and rounded down to JPY 1.", "各合計に対して1回計算し、1円未満切り捨て。"),
        t("Operation period of 2 years (2027-08 to 2029-07), as [LGW]. 12- and 36-month views are in the multi-year table below.",
          "運用期間2年（2027年8月〜2029年7月、[LGW]と同じ）。12か月・36か月の試算は下の複数年試算表を参照。"),
    ],
    views=[(t("Initial + first year", "初期費用＋初年度"), 12),
           (t("Initial + operation period (grand total)", "初期費用＋運用期間（総額）"), 24),
           (t("Initial + 3 years", "初期費用＋3年"), 36)],
    views_intro=t("The same initial cost with 12, 24 (the grand total above) and 36 months of recurring cost. Model inference is excluded in every view.",
                  "同じ初期費用に、継続費用12か月・24か月（上記の総額）・36か月分を加えた試算。いずれもモデル利用料は含まない。"),
    checks_footer=t("The workbook could not be recalculated with LibreOffice in this environment (not installed). The Summary values above were computed independently in Python with the workbook's formulas (unit cost lookup, likelihood, ROUND for PM and contingency, ROUNDDOWN for tax), from the filled workbook and from the model, and the two agree; Excel recalculates the workbook when it is opened.",
                    "この環境ではLibreOfficeがないためブックを再計算できなかった。上記のSummaryの値は、ブックの数式（単価参照、発生確率、PM費・予備費のROUND、消費税のROUNDDOWN）をPythonで再現し、記入済みブックとモデルの両方から計算して一致を確認したもの。Excelではブックを開くと再計算される。"),
    category_notes={
        "mig": t("No rows: no data migration in 01/02 (A19)", "明細なし：01・02にデータ移行の定義なし（A19）"),
        "pm": t("No bottom-up PM rows", "積み上げのPM明細なし"),
        "lic": t("No licensed software (A16)", "ライセンスが必要なソフトウェアなし（A16）"),
        "con": t("Identified risks at expected value (02 §14, 01 §9)", "特定済みリスクの期待値（02 §14、01 §9）"),
    },
    empty_categories={
        "mig": t("*No line items: 01 and 02 define no data migration; what the gateway replaces is open (01 Q-2).*",
                 "*明細なし：01・02にデータ移行の定義がなく、置き換え対象も未確定（01 Q-2）。*"),
        "lic": t("*No line items: no licensed software (01 AS-6 and Q-17 withdrawn; no LiteLLM).*",
                 "*明細なし：ライセンスが必要なソフトウェアなし（01 AS-6・Q-17は取り下げ、LiteLLMなし）。*"),
    },
    details_note=t("[PL] = AWS Price List API offer file for the region, checked 2026-11-20; USD amounts are converted at JPY 160/USD. [LGW] = the LiteLLM design's estimate.",
                   "[PL]＝リージョン別のAWS Price List APIのオファーファイル（2026-11-20確認）。USDは1USD＝160円で換算。[LGW]＝LiteLLM設計の見積。"),
    rates_note=t("**OPEN ITEM (FinOps): there are no internal rates yet. These are the template's sample rates (indicative blended market rates, excl. tax), kept unchanged as in [LGW]; replace them on the Rates sheet.**",
                 "**【未決事項・FinOps】社内単価が未設定のため、[LGW]と同じくテンプレートのサンプル単価（参考の平均相場、税抜）をそのまま使用している。Ratesシートで置き換えること。**"),
)


def estimate(lang, T):
    """The estimate as snapshot.py and fill.py take it, with Japanese row text for jp."""
    rows, envs = M.estimate_rows()
    if lang == "jp":
        rows = [dict(r, desc=T(r["desc"]), notes=T(r["notes"])) for r in rows]
    est = dict(project=M.PROJECT, params=M.PARAMS, rates=M.RATES, days=M.DAYS, items=rows,
               assumptions=M.ASSUMPTIONS, exclusions=M.EXCLUSIONS)
    return est, envs


def effort_excl_con(res):
    return (sum(i["qty"] for i in res.items if i["type"] == T_OT and i["key"] != "con" and i["unit"] == U_PM) +
            sum(i["qty"] for i in res.items if i["type"] == T_OT and i["key"] != "con" and i["unit"] == U_PD) / M.DAYS)


def signed(x):
    if abs(x) < 0.5:
        return "-"
    return ("+" if x > 0 else "−") + f"{abs(round(x)):,}"


def ratio(a, b):
    return f"{a / b * 100:.0f}%" if b else "-"


def render(lang):
    LANG = lang
    T = Translator(lang, JA)
    L = lambda en, jp: en if LANG == "en" else jp
    est, (PT, DR, DEV, STG) = estimate(lang, T)
    res = compute(est["items"], M.RATES, M.DAYS, M.PARAMS)
    monthly, MON = res.monthly, M.PARAMS.months
    doc = Snapshot(est, res, lang, T, NOTES)
    w, table = doc.w, doc.table
    G = M.LGW
    lgw_grand = G["initial"] + G["monthly"] * MON
    grand = res.grand()

    # ------------------------------------------------------------------ header
    if LANG == "en":
        w("# Cost Estimate — IAM-native LLM gateway on AWS, v0.1")
        w("")
        w(f"> **Generated, read-only snapshot of the estimate model.** The master is the Excel workbook built from the cost estimate template (`{XLSX}`; Japanese workbook: `{XLSX_JP}`); it holds the formulas, dropdowns, rate lookups and checks. Numbers here do not recalculate — change the workbook instead. A Japanese version is in `{MD_JP}`.")
        w("")
        w(f"> Purpose: internal budget approval in the design phase — **a budget estimate, not a quote** · Currency: JPY (line items excl. tax) · Prices: AWS list prices checked {M.CHECKED}, JPY {M.FX}/USD · Parameters: PM 10%, contingency 15% (applied to recurring: Yes), tax 10%, **{MON} recurring months in grand total** (24-month operation period). Model inference (Bedrock tokens charged to the calling principal) is **not** in the totals; see §8. Schedule, usage basis, rates and parameters are those of the LiteLLM design's estimate `[LGW]`, so that §7 compares the two like for like.")
        w("")
        w("Sections 1–6 mirror the workbook sheets (Summary · Estimate · Rates · Assumptions · Lists · Calculation rules). Sections 7–12 are additions for this estimate: the comparison with `[LGW]`, model usage, separately priced options, infrastructure sizing detail, open pricing items by owner, and findings for the design documents.")
    else:
        w("# 費用見積 — IAMネイティブLLMゲートウェイ（AWS） v0.1")
        w("")
        w(f"> **本ファイルは見積モデルから自動生成した参照用スナップショットです。** 正本は費用見積テンプレートから作成したExcelブック（`{XLSX_JP}`。英語版のブックは`{XLSX}`）で、数式・プルダウン・単価参照・チェックを持ちます。本ファイルの数値は再計算されないため、変更はExcel側で行ってください。英語版は `{MD}` です。")
        w("")
        w(f"> 目的：設計フェーズにおける社内予算承認用 — **予算見積であり見積回答ではない** · 通貨：円（明細は税抜） · 価格：AWS定価（{M.CHECKED}確認）、1USD＝{M.FX}円 · パラメータ：PM費率10%、予備費率15%（継続費用にも適用：Yes）、消費税10%、**総額に含める継続月数{MON}か月**（運用期間24か月）。モデル利用料（呼び出し元のプリンシパルに配賦するBedrockトークン料金）は合計に**含めない**（§8参照）。スケジュール・利用量の前提・単価・パラメータはLiteLLM設計の見積`[LGW]`と同じとし、§7で同じ条件で比較する。")
        w("")
        w("1〜6章はExcelのシート構成（Summary・Estimate・Rates・Assumptions・Lists・計算ルール）に対応します。7〜12章は本見積の追加情報：`[LGW]`との比較、モデル利用料の試算、別途試算のオプション、インフラのサイジング明細、オーナー別の価格未決事項、設計文書への指摘事項です。")
    w("")

    # ------------------------------------------------------------------ 1-6: the workbook sheets
    doc.sections()

    # ------------------------------------------------------------------ 7 Comparison with [LGW]
    w(L("## 7. Comparison with the LiteLLM design's estimate [LGW]", "## 7. LiteLLM設計の見積[LGW]との比較"))
    w("")
    w(T(t(f"[LGW] is the estimate in ai-gateway-on-aws cost/ (commit {G['commit']}): the same template, schedule, usage basis (30 engineers, about 1.1 million calls a month), rates, exchange rate and parameters. Both exclude model inference, which is the same in both designs (§8). Amounts in JPY, excl. tax.",
          f"[LGW]はai-gateway-on-awsのcost/（コミット{G['commit']}）の見積で、テンプレート・スケジュール・利用量の前提（エンジニア30人、月約110万回の呼び出し）・単価・為替レート・パラメータは同じ。両者ともモデル利用料を含まず、それは両設計で同じ（§8）。金額は円・税抜。")))
    w("")
    w(L("### 7.1 Totals", "### 7.1 合計"))
    w("")
    tax = res.tax
    ee, lee = effort_excl_con(res), G["effort_excl_con"]
    body = [
        (T(t("Total initial cost (one-time)", "初期費用合計")), n(res.initial), n(G["initial"]), signed(res.initial - G["initial"]), ratio(res.initial, G["initial"])),
        (T(t("Total recurring cost – monthly", "継続費用（月額）")), n(monthly), n(G["monthly"]), signed(monthly - G["monthly"]), ratio(monthly, G["monthly"])),
        (T(t("Total recurring cost – annual", "継続費用（年額）")), n(res.annual), n(G["monthly"] * 12), signed(res.annual - G["monthly"] * 12), ratio(monthly, G["monthly"])),
        (f"**{T(t('Grand total (initial + 24 months), excl. tax', '総額（初期費用＋24か月）、税抜'))}**", f"**{n(grand)}**", f"**{n(lgw_grand)}**",
         f"**{signed(grand - lgw_grand)}**", f"**{ratio(grand, lgw_grand)}**"),
        (T(t("Grand total, incl. tax", "総額、税込")), n(grand + tax(grand)), n(lgw_grand + tax(lgw_grand)),
         signed(grand + tax(grand) - lgw_grand - tax(lgw_grand)), ratio(grand, lgw_grand)),
        (T(t("Development cost (base for PM %)", "開発費（PM費の算定基礎）")), n(res.dev), n(G["dev"]), signed(res.dev - G["dev"]), ratio(res.dev, G["dev"])),
        (T(t("One-time effort excl. contingency rows (person-months)", "予備費の行を除く初期工数（人月）")), f"{ee:.1f}", f"{lee:.1f}", f"{ee - lee:+.1f}".replace("-", "−"), ratio(ee, lee)),
    ]
    table(L(["Item", "This design", "[LGW]", "Difference", "This / [LGW]"], ["項目", "本設計", "[LGW]", "差", "本設計／[LGW]"]), body, "lrrrr")
    w(T(t("The template's own indicator 'Total one-time effort' (§1) counts risk rows at their full impact when the likelihood is in column K, as here; [LGW] put the expected value into Quantity instead. The row above leaves contingency rows out of both, so the two are comparable.",
        "テンプレートの指標「初期工数合計」（§1）は、本見積のようにK列に発生確率を入れると予備費の行を影響額で数える。[LGW]は期待値を数量に入れている。上の行は両者とも予備費の行を除いているため比較できる。")))
    w("")

    w(L("### 7.2 By category", "### 7.2 費目別"))
    w("")
    body = []
    for k in CAT_ORDER:
        label = doc.side(CATEGORIES[k])
        o, lo, r_, lr = res.ot[k], G["ot"][k], res.rc[k], G["rc"][k]
        body.append((label, n(o), n(lo), signed(o - lo), n(r_), n(lr), signed(r_ - lr)))
        if k == "pm":
            body.append((L("Project management (PM % of development cost)", "PM費（開発費×PM費率）"), n(res.pm), n(G["pm"]), signed(res.pm - G["pm"]), "", "", ""))
    body.append((L("Contingency buffer (15 %)", "予備費（15%、自動計算）"), n(res.cont_ot), n(G["cont_ot"]), signed(res.cont_ot - G["cont_ot"]),
                 n(res.cont_rc), n(G["cont_rc"]), signed(res.cont_rc - G["cont_rc"])))
    body.append((f"**{L('Total (excl. tax)', '合計（税抜）')}**", f"**{n(res.initial)}**", f"**{n(G['initial'])}**", f"**{signed(res.initial - G['initial'])}**",
                 f"**{n(monthly)}**", f"**{n(G['monthly'])}**", f"**{signed(monthly - G['monthly'])}**"))
    table(L(["Category", "One-time: this", "One-time: [LGW]", "Difference", "Monthly: this", "Monthly: [LGW]", "Difference"],
            ["費目", "初期：本設計", "初期：[LGW]", "差", "月額：本設計", "月額：[LGW]", "差"]), body, "lrrrrrr")

    w(L("### 7.3 Monthly AWS cost by environment (USD, before conversion)", "### 7.3 環境別のAWS月額（USD、換算前）"))
    w("")
    envs = [(T(t("Production (Tokyo)", "本番（東京）")), M.tot(PT), G["env_usd"]["prod"]),
            (T(t("DR (Osaka)", "DR（大阪）")), M.tot(DR), G["env_usd"]["dr"]),
            (T(t("Dev (Tokyo)", "開発（東京）")), M.tot(DEV), G["env_usd"]["dev"]),
            (T(t("Staging (Tokyo)", "ステージング（東京）")), M.tot(STG), G["env_usd"]["stg"])]
    body = [(e, f"{a:,.2f}", f"{b:,.2f}", f"{a - b:+,.2f}".replace("-", "−")) for e, a, b in envs]
    sa, sb = sum(e[1] for e in envs), sum(e[2] for e in envs)
    body.append((f"**{T('Total')}**", f"**{sa:,.2f}**", f"**{sb:,.2f}**", f"**{sa - sb:+,.2f}**".replace("-", "−")))
    table(L(["Environment", "This design", "[LGW]", "Difference"], ["環境", "本設計", "[LGW]", "差"]), body, "lrrr")
    pca = M.P["pca_gp"] * 2
    w(T(t(f"Two general-purpose Private CAs (production and staging) are USD {pca:,.0f} of this design's USD {sa:,.0f} a month (finding F-1). [LGW] also had no Private CA in its base (only in contingency row R-3).",
        f"本設計の月{sa:,.0f}USDのうち、汎用モードのPrivate CA 2つ（本番・ステージング）が{pca:,.0f}USD（指摘F-1）。[LGW]はPrivate CAを基本見積に含めていない（予備費R-3のみ）。")))
    w("")

    w(L("### 7.4 Where the difference comes from", "### 7.4 差の要因"))
    w("")
    d = {k: (res.ot[k] - G["ot"][k], res.rc[k] - G["rc"][k]) for k in CAT_ORDER}
    lab_ot = lambda r: sum(i["G"] for i in r.items if i["type"] == T_OT and i["role"] != R_VEN and i["key"] != "con")
    DRV = [
        (t("No servers, database, cache, load balancer, WAF or VPC endpoints to run (02 §2.2, 00 §1.6)", "稼働させるサーバー・DB・キャッシュ・ロードバランサー・WAF・VPCエンドポイントがない（02 §2.2、00 §1.6）"),
         t("Infrastructure", "インフラ"), signed(d["inf"][0]), signed(d["inf"][1])),
        (t("Less to build: no guardrail service (D-10), no LiteLLM configuration or images; new: the spend guard, policy generator and a larger llm helper",
           "構築が少ない：ガードレールサービス（D-10）・LiteLLMの設定・イメージなし。新規：スペンドガード、ポリシー生成、より大きなllmヘルパー"),
         t("Implementation", "実装"), signed(d["imp"][0]), "-"),
        (t("More open questions (26 vs 20) and early spikes: the design rests on AWS behaviours not yet checked (R-2, R-25, R-29, R-30, AS-24, AS-25); a smaller guardrail decision",
           "未決事項（26件対20件）と早期検証が多い：設計が未確認のAWSの挙動（R-2、R-25、R-29、R-30、AS-24、AS-25）に依存。ガードレールの判断は小さい"),
         t("Design, requirements", "設計・要件定義"), signed(d["des"][0] + d["req"][0]), "-"),
        (t("More tests (86 vs 75) and project gates V-12 to V-16; V-3, V-8, V-9 are n/a; no AZ-loss or task-sizing tests",
           "テストが多い（86件対75件）、プロジェクトゲートV-12〜V-16。V-3・V-8・V-9は対象外。AZ障害・タスクサイジングの試験なし"),
         t("Testing", "テスト"), signed(d["tst"][0]), "-"),
        (t("No LiteLLM upgrades or guardrail upkeep; quarterly gate re-runs and policy upkeep instead; half the on-call load",
           "LiteLLMの更新・ガードレールの保守なし。代わりに四半期のゲート再実行とポリシーの追随。オンコール負荷は半分"),
         t("Operation, maintenance", "運用・保守"), "-", signed(d["ops"][1] + d["mnt"][1])),
        (t("Setup, training, cutover, QA, security: smaller CI/CD, fewer components to review", "構築・教育・移行・品質保証・セキュリティ：CI/CDが小さく、レビュー対象が少ない"),
         t("Other phases", "その他の工程"), signed(sum(d[k][0] for k in ("set", "trn", "cut", "qa", "sec"))), "-"),
        (t("Identified risks: Route A for GA at 50 % (D-6), AWS-behaviour fallbacks; [LGW]'s GPU guardrail, mTLS and egress risks do not apply",
           "特定済みリスク：GAでのRoute A（50%、D-6）、AWSの挙動に対する代替策。[LGW]のGPUガードレール・mTLS・出口経路のリスクは該当しない"),
         t("Contingency (identified risks)", "予備費（特定済みリスク）"), signed(d["con"][0]), signed(d["con"][1])),
        (t("PM % and the 15 % buffer follow the base", "PM費と15%の予備費は基礎額に連動"),
         t("PM, contingency buffer", "PM費、予備費（自動計算）"), signed(res.pm - G["pm"] + res.cont_ot - G["cont_ot"]), signed(res.cont_rc - G["cont_rc"])),
    ]
    DRV.append((f"**{L('Total difference', '差の合計')}**", "", f"**{signed(res.initial - G['initial'])}**", f"**{signed(monthly - G['monthly'])}**"))
    table(L(["Driver", "Category", "One-time (JPY)", "Monthly (JPY)"], ["要因", "費目", "初期（円）", "月額（円）"]),
          [(T(a) if b else a, T(b) if b else b, c, e) for a, b, c, e in DRV], "llrr")
    pc = monthly / G["monthly"] * 100
    w(T(t(f"The build costs about the same as [LGW]'s: what this design saves in components it spends on custom code, spikes and tests. The saving is in running it: {pc:.0f} % of [LGW]'s monthly cost.",
          f"構築費は[LGW]とほぼ同じ：コンポーネントが減った分を、自社コード・早期検証・テストに使う。削減は運用にあり、月額は[LGW]の{pc:.0f}%。")))
    w("")
    w(T(t(f"Labor is most of both estimates: one-time labor excl. contingency is JPY {n(lab_ot(res))} here; in [LGW] it is JPY 27,930,000.",
        f"両見積とも大半は人件費：予備費を除く初期の人件費は本設計で{n(lab_ot(res))}円、[LGW]で27,930,000円。")))
    w("")

    w(L("### 7.5 What the totals do not show", "### 7.5 合計に現れないこと"))
    w("")
    for en, ja in [
        ("**[LGW] is understated by its licence.** Its LiteLLM Enterprise licence row has no price (its check 'Rows with quantity but no amount' = 1), so its totals exclude a recurring licence fee that this design does not pay.",
         "**[LGW]はライセンス分だけ過小。** LiteLLM Enterpriseライセンスの行に価格がなく（チェック「単価未設定の行数」＝1）、本設計では発生しない継続のライセンス費が[LGW]の合計に含まれていない。"),
        ("**Capabilities differ.** This design gives up in-path guardrails for Japanese text (SEC-008 deferred, D-10), per-caller rate limits (NG-12), API translation (NG-10) and Azure OpenAI; budgets act within minutes instead of in real time (CST-009). ADR D-1 §5 lists every difference. The estimate prices the design as it is, not these gaps.",
         "**機能が異なる。** 本設計では日本語テキストのインラインガードレール（SEC-008は延期、D-10）、呼び出し元ごとのレート制限（NG-12）、API変換（NG-10）、Azure OpenAIを諦め、予算の制御はリアルタイムではなく数分以内（CST-009）。差異の一覧はADR D-1 §5。本見積は設計どおりに価格を付けており、これらの差は価格に含まない。"),
        ("**Per-call charges scale with use.** [LGW]'s AWS cost is mostly fixed capacity; this design's is mostly fixed (Private CA, Quick Sight) at 30 engineers, but its per-call charges grow linearly with calls (§10).",
         "**従量部分は利用量に比例する。** [LGW]のAWS費用は大半が固定容量。本設計は30人規模では大半が固定費（Private CA、Quick Sight）だが、従量部分は呼び出し回数に比例して増える（§10）。"),
        ("**Route A is counted differently.** [LGW] kept Route B for GA and priced Route A outside its totals; this design proposes Route A for GA (D-6), so it is in contingency at 50 % here and at full cost in §9.",
         "**Route Aの扱いが異なる。** [LGW]はGAもRoute Bとし、Route Aを合計外で試算した。本設計はGAでRoute Aを提案している（D-6）ため、予備費に50%で計上し、全額を§9に示す。"),
    ]:
        w("- " + t(en, ja) if LANG == "en" else "- " + ja)
    w("")

    # ------------------------------------------------------------------ 8 Model usage
    U = M.usage()
    S = M.SCEN
    w("## 8. Model usage (Bedrock tokens) — not in the totals" if LANG == "en" else "## 8. モデル利用料（Bedrockトークン） — 合計に含めない")
    w("")
    w(T(t("Model inference is a variable cost charged to the principal that makes each call (01 CST-007, 02 §5, D-9), so it is an exclusion (B1) and not part of the totals above. Both designs call the same models through the same `jp.` profiles and In-Region models, so the tokens and prices are those of [LGW] §7 (Bedrock on-demand, [PL] AmazonBedrock and AmazonBedrockFoundationModels, ap-northeast-1, checked 2026-11-17), and the cost is the same.",
          "モデル利用料は呼び出しごとにそのプリンシパルに課金される変動費（01 CST-007、02 §5、D-9）のため対象外（B1）とし、上記の合計に含めない。両設計とも同じ`jp.`プロファイルとリージョン内モデルで同じモデルを呼び出すため、トークン数と単価は[LGW] §7と同じ（Bedrockオンデマンド、[PL] AmazonBedrock・AmazonBedrockFoundationModels、ap-northeast-1、2026-11-17確認）で、費用も同じ。")))
    w("")
    w("### 8.1 Prices used (USD per 1 million tokens)" if LANG == "en" else "### 8.1 使用した単価（USD／100万トークン）")
    w("")
    hd = ["Catalog ID", "Model", "How processed in Japan (01 §6.5)", "Input", "Cache write", "Cache read", "Output"] if LANG == "en" else \
         ["カタログID", "モデル", "日本国内での処理（01 §6.5）", "入力", "キャッシュ書込", "キャッシュ読込", "出力"]
    proc = {m: (L("`jp.` profile", "`jp.` プロファイル") if m.startswith(("Claude", "Amazon")) else L("In-Region Tokyo", "東京リージョン内")) for m in M.BR}
    f = lambda v: f"{v:g}" if v else "-"
    table(hd, [(M.MDL[m], m, proc[m], f(p["inp"]), f(p["cw"]), f(p["cr"]), f(p["out"])) for m, p in M.BR.items()], "lllrrrr")
    w("### 8.2 Scenario assumptions" if LANG == "en" else "### 8.2 シナリオの前提")
    w("")
    hd = ["Driver", "Low", "Expected", "High", "Basis"] if LANG == "en" else ["要素", "低", "想定", "高", "根拠"]
    tok = "0.6 / 0.4 / 12 / 0.25"
    table(hd, [
        (T(t("Active coding-agent users per month", "月間のコーディングエージェント利用者数")), S["Low"]["users"], S["Expected"]["users"], S["High"]["users"],
         T(t("30 engineers, as [LGW] (A14); scenarios vary active days and workload volume only", "エンジニア30人（[LGW]と同じ、A14）。シナリオは稼働日数とワークロード量のみ変える"))),
        (T(t("Active days per user per month", "利用者1人あたりの月間稼働日数")), S["Low"]["days"], S["Expected"]["days"], S["High"]["days"],
         T(t("As [LGW] §7.2 (Claude Code cost docs: about USD 13 per developer per active day, USD 150–250 a month)", "[LGW] §7.2と同じ（Claude Codeのコスト資料：開発者1人1日約13USD、月150〜250USD）"))),
        (T(t("Tokens per active user-day (M): input / cache write / cache read / output", "稼働1日あたりのトークン（百万）：入力／キャッシュ書込／キャッシュ読込／出力")), tok, tok, tok,
         T(t("Calibrated so a full day on Claude Opus 5.5 costs about USD 13 (", "Claude Opus 5.5で1日利用した場合に約13USDとなるよう調整（")) + f"USD {M.day_cost('Claude Opus 5.5'):.2f}" + L(")", "）")),
        (T(t("Model mix for coding agents", "コーディングエージェントのモデル構成")), "", T(t("Opus 5.5 60 %, Haiku 5.5 20 %, Sonnet 4.6 15 %, Opus 4.8 5 %", "Opus 5.5 60%、Haiku 5.5 20%、Sonnet 4.6 15%、Opus 4.8 5%")), "",
         T(t("As [LGW]; 01 §6.5 UC-1 models (Q-4 open)", "[LGW]と同じ。01 §6.5 UC-1のモデル（Q-4未確定）"))),
        (T(t("Workloads (UC-2), share of expected volume", "ワークロード（UC-2）、想定量に対する比率")), "25 %", "100 %", "300 %",
         T(t("As [LGW]: Haiku 4.5 1.0 B in / 0.2 B out; Nova 2 Lite 1.0 / 0.2; gpt-oss-120b 0.3 / 0.06; Mistral Large 3 0.2 / 0.04; Titan V2 and Cohere v4 embeddings 0.5 B each (01 Q-4, Q-7)",
             "[LGW]と同じ：Haiku 4.5 入力10億・出力2億、Nova 2 Lite 10億・2億、gpt-oss-120b 3億・6千万、Mistral Large 3 2億・4千万、Titan V2・Cohere v4の埋め込み各5億（01 Q-4、Q-7）"))),
    ], "lrrrl")
    w("### 8.3 Monthly usage and cost by model" if LANG == "en" else "### 8.3 モデル別の月間利用量と費用")
    w("")
    hd = ["Catalog ID", "Model", "Tokens/month Low (B)", "Expected (B)", "High (B)", "JPY/month Low", "Expected", "High"] if LANG == "en" else \
         ["カタログID", "モデル", "月間トークン 低（10億）", "想定（10億）", "高（10億）", "月額（円）低", "想定", "高"]
    body = [(M.MDL[m], m, *(f"{U[s][m]['total_b']:,.1f}" for s in S), *(n(U[s][m]["usd"] * M.FX) for s in S)) for m in M.BR]
    tb = {s: sum(x["total_b"] for x in U[s].values()) for s in S}
    tu = {s: sum(x["usd"] for x in U[s].values()) for s in S}
    body.append(("", f"**{T('Total')}**", *(f"**{tb[s]:,.1f}**" for s in S), *(f"**{n(tu[s] * M.FX)}**" for s in S)))
    body.append(("", T(t("Total per year (× 12)", "年額（×12）")), "", "", "", *(n(tu[s] * M.FX * 12) for s in S)))
    body.append(("", T(t("Total over the 24-month operation period", "24か月の運用期間の合計")), "", "", "", *(n(tu[s] * M.FX * 24) for s in S)))
    table(hd, body, "llrrrrrr")
    ue = tu["Expected"] * M.FX
    w(T(t(f"Tokens include cache reads, which are most of the coding-agent volume. Excl. tax. At the expected scenario, model usage (JPY {n(ue)} a month) is {ue / monthly:.2f}× this design's monthly running cost and {ue / G['monthly']:.2f}× [LGW]'s: at 30 engineers it does not dominate either design yet [CMP §7.1], but its share of the total running cost is about twice as large here.",
        f"トークン数はキャッシュ読込を含み、コーディングエージェントの大半を占める。税抜。想定シナリオでは、モデル利用料（月{n(ue)}円）は本設計の月額運用費の{ue / monthly:.2f}倍、[LGW]の{ue / G['monthly']:.2f}倍。エンジニア30人の規模ではどちらの設計でもまだ支配的ではない [CMP §7.1] が、運用費全体に占める割合は本設計の方が約2倍大きい。")))
    w("")

    # ------------------------------------------------------------------ 9 Options
    ra = M.route_a()
    w("## 9. Optional items priced separately (not in the totals)" if LANG == "en" else "## 9. 別途試算のオプション（合計に含めない）")
    w("")
    w(T(t("Route A is in the totals only at its expected value (contingency, 50 %). Its full cost, and the Private CA alternatives of finding F-1, are below at [PL] Tokyo rates and this estimate's traffic (about 168 GB a month through the endpoints). Azure OpenAI has no option: it cannot be reached without a proxy (01 NG-10).",
          "Route Aは期待値（予備費、50%）でのみ合計に含める。全額と、指摘F-1のPrivate CAの代替案を、[PL]の東京料金と本見積の通信量（エンドポイント経由で月約168GB）で以下に示す。Azure OpenAIはプロキシなしでは利用できないため選択肢がない（01 NG-10）。")))
    w("")
    hd = ["Option", "Monthly AWS cost (USD)", "Monthly (JPY)", "One-time build", "Not included"] if LANG == "en" else \
         ["オプション", "AWS月額（USD）", "月額（円）", "初期構築", "含まないもの"]
    pca_save = -(2 * M.P["pca_gp"] + 7 * M.P["pca_cert"])
    short = 2 * M.P["pca_short"] - 2 * M.P["pca_gp"]
    table(hd, [
        (T(t("Route A for GA: interface endpoints over Direct Connect with Resolver inbound endpoint (D-6)", "GAでのRoute A：Direct Connect経由のインターフェースエンドポイントとResolverインバウンドエンドポイント（D-6）")),
         "; ".join(f"{T(a)} {v:,.1f}" for a, v in ra["parts"]) + f" = **{ra['monthly_usd']:,.0f}**",
         n(ra["monthly_usd"] * M.FX), f"{ra['build_pd']} " + T(t("pd Infra/DevOps ≈ JPY", "人日（インフラ）≈")) + f" {n(ra['build_pd'] * 55000)}" + L("", "円"),
         T(t("DX ports and circuits (AS-8), Osaka endpoints (finding F-6), Network team time", "DXのポート・回線（AS-8）、大阪のエンドポイント（指摘F-6）、ネットワーク部門の工数"))),
        (T(t("Corporate CA as the Roles Anywhere trust anchor instead of two Private CAs (02 §12)", "2つのPrivate CAの代わりに社内CAをRoles Anywhereのトラストアンカーにする（02 §12）")),
         f"{pca_save:,.2f}".replace("-", "−"), signed(pca_save * M.FX), T(t("Included in the IaC row; the PKI team issues and revokes", "IaCの行に含む。発行・失効はPKI担当")),
         T(t("PKI team time; CRL publication to Roles Anywhere", "PKI担当の工数、Roles AnywhereへのCRL公開"))),
        (T(t("Private CA in short-lived mode with 7-day workload certificates (TEN-006 changed)", "短期証明書モードのPrivate CAで7日のワークロード証明書（TEN-006を変更）")),
         f"{short:,.2f}".replace("-", "−") + L(" + certificates at 0.058", "＋証明書1枚0.058"), signed(short * M.FX),
         T(t("Weekly renewal automation on every DC workload host", "全DCワークロードのホストで週次更新の自動化")), "—"),
    ], "lrrll")

    # ------------------------------------------------------------------ 10 Sizing detail
    w("## 10. Infrastructure sizing detail" if LANG == "en" else "## 10. インフラのサイジング明細")
    w("")
    w(T(t("Monthly AWS cost per environment in USD, before conversion. Production and DR are one row per component in §2; dev and staging are one row each in §2 with this breakdown.",
          "環境別のAWS月額（USD、換算前）。本番とDRは§2で構成要素ごとに1行、開発とステージングは§2で各1行（内訳は下表）。")))
    w("")
    hd = ["Environment", "Component", "USD / month"] if LANG == "en" else ["環境", "構成要素", "USD／月"]
    body = []
    for env, cs in ((T("Production (Tokyo)"), PT), (T("DR (Osaka)"), DR), (T("Dev (Tokyo)"), DEV), (T("Staging (Tokyo)"), STG)):
        for c in cs:
            body.append((env, T(c["name"]), f"{c['usd']:,.2f}"))
        body.append((f"**{env}**", f"**{T('Total')}**", f"**{M.tot(cs):,.2f}**"))
    table(hd, body, "llr")
    w(T(t("Comparison with 02 §12: every row of its table is priced here except model usage (§8) and Route A (contingency; full cost in §9). 02 §12 has no rows for threat detection and compliance services (finding F-4).",
          "02 §12との比較：モデル利用料（§8）とRoute A（予備費、全額は§9）を除き、02 §12の表のすべての行に価格を付けた。02 §12には脅威検知・コンプライアンスのサービスの行がない（指摘F-4）。")))
    w("")
    w(L("### 10.1 Per-call charges at higher volumes", "### 10.1 利用量が多い場合の従量費用"))
    w("")
    w(T(t("The charges that grow with every model call: SQS, the llm-meter function, DynamoDB counter writes in both Regions (5 per call, not batched) and GuardDuty's analysis of the CloudTrail events. CloudWatch Logs and CloudTrail data events also grow, less. 02 §9 and §12 give 4.3–17 million calls a day at A-9 scale.",
          "モデルの呼び出しごとに増える料金：SQS、llm-meter関数、両リージョンのDynamoDBカウンター書き込み（1回につき5件、バッチ化なし）、GuardDutyによるCloudTrailイベントの分析。CloudWatch LogsとCloudTrailデータイベントも増えるが小さい。02 §9・§12ではA-9規模で1日430万〜1,700万回。")))
    w("")
    ratio_ev = M.EVENTS_M / M.CALLS_M
    vols = [(T(t("This estimate (30 engineers)", "本見積（エンジニア30人）")), M.CALLS_M), ("10 M", 10.0),
            (T(t("A-9 low: 4.3 M a day", "A-9下限：1日430万回")), 4.3 * 30), (T(t("A-9 high: 17 M a day", "A-9上限：1日1,700万回")), 17 * 30)]
    body = []
    for lbl, c in vols:
        v = M.spend_guard_variable(c, c * ratio_ev)
        body.append((lbl, f"{c:,.2f}", f"{v['sqs']:,.0f}", f"{v['lam']:,.0f}", f"{v['ddb']:,.0f}", f"{v['gd']:,.0f}", f"**{v['total']:,.0f}**", n(v["total"] * M.FX)))
    table(L(["Volume", "Calls / month (M)", "SQS", "Lambda llm-meter", "DynamoDB writes", "GuardDuty events", "Total USD / month", "JPY / month"],
            ["利用量", "月間呼び出し（百万）", "SQS", "Lambda llm-meter", "DynamoDB書き込み", "GuardDutyイベント", "合計 USD／月", "円／月"]), body, "lrrrrrrr")
    w(T(t("At A-9 scale the per-call charges reach a few thousand USD a month, more than [LGW]'s whole production environment at 30 engineers; GuardDuty and the counter writes are most of it. Batching counter updates per key in llm-meter, as 02 §12 suggests, and a GuardDuty decision on Bedrock events are the levers (finding F-2). Model usage at that scale would be far larger still.",
          "A-9規模では従量部分が月数千USDに達し、30人規模の[LGW]の本番環境全体を上回る。大半はGuardDutyとカウンター書き込み。02 §12が示すllm-meterでのキー単位のバッチ化と、BedrockイベントについてのGuardDutyの判断が削減策（指摘F-2）。その規模ではモデル利用料はさらに桁違いに大きい。")))
    w("")

    # ------------------------------------------------------------------ 11 Open items
    w("## 11. Open items that need a price or a decision, by owner" if LANG == "en" else "## 11. 価格・判断が必要な未決事項（オーナー別）")
    w("")
    hd = ["Owner", "Item", "Where it is in the estimate", "Due (from 01/02)"] if LANG == "en" else ["オーナー", "項目", "見積上の箇所", "期限（01/02より）"]
    OPEN = [
        (("Product owner", "プロダクトオーナー"), ("Pilot and GA dates (01 Q-3); they set the project-period environment months", "パイロットとGAの日程（01 Q-3）。プロジェクト期間の環境の月数が決まる"),
         ("A3, Infrastructure one-time rows", "A3、インフラの初期費用の行"), "2026-12-18"),
        (("Product owner", "プロダクトオーナー"), ("Model list, usage forecast and growth (01 Q-4, Q-7); they set model usage and the per-call charges", "モデル一覧、利用量の予測と伸び（01 Q-4、Q-7）。モデル利用料と従量費用が決まる"),
         ("§8, §10.1", "§8、§10.1"), "2026-12-18"),
        (("Product owner", "プロダクトオーナー"), ("Support hours and DR drill interval (01 Q-6); AWS Support plan (01 Q-20)", "サポート時間とDR訓練の間隔（01 Q-6）、AWSサポートプラン（01 Q-20）"),
         ("Operation rows (A20), exclusion B7", "運用の行（A20）、対象外B7"), "2026-12-18 / 2027-01-29"),
        (("FinOps", "FinOps"), ("Internal labor rates to replace the template sample rates", "テンプレートのサンプル単価を置き換える社内単価"), ("Rates sheet, all labor rows (A5)", "Ratesシート、全工数行（A5）"), "—"),
        (("FinOps", "FinOps"), ("Budget exchange rate (JPY 160/USD assumed)", "予算レート（1USD＝160円と仮定）"), ("A10, all AWS rows", "A10、全AWSの行"), "—"),
        (("FinOps", "FinOps"), ("Quick Sight reader count and allocation of fixed platform cost (01 Q-12, 02 R-17)", "Quick Sightの閲覧者数と基盤の固定費の配賦（01 Q-12、02 R-17）"),
         ("Chargeback row", "配賦の行"), "2026-12-18"),
        (("Security / SOC", "セキュリティ／SOC"), ("Penetration-test vendor quote (template sample JPY 2,000,000 used)", "ペネトレーションテストのベンダー見積（テンプレートのサンプル2,000,000円を使用）"),
         ("Security row", "セキュリティの行"), "2027-01-29"),
        (("Security / SOC", "セキュリティ／SOC"), ("Whether no guardrail in the path is accepted (01 Q-13)", "経路上にガードレールを置かないことを受容するか（01 Q-13）"),
         ("Contingency R-5", "予備費R-5"), "2026-12-18"),
        (("Network", "ネットワーク"), ("Whether Route A is adopted for GA (01 Q-24) and its Osaka side (F-6)", "GAでRoute Aを採用するか（01 Q-24）、その大阪側（F-6）"),
         ("Contingency R-12, §9", "予備費R-12、§9"), "2027-01-29"),
        (("Platform engineering", "プラットフォームエンジニアリング"), ("Private CA mode, or a corporate CA as trust anchor (R-24, F-1)", "Private CAのモード、または社内CAをトラストアンカーにするか（R-24、F-1）"),
         ("Private CA rows, §9", "Private CAの行、§9"), "2027-01-29"),
        (("Platform engineering", "プラットフォームエンジニアリング"), ("Counter writes per call and batching in llm-meter; data-event selector for llm-spend (F-2, F-7)", "1回あたりのカウンター書き込みとllm-meterでのバッチ化、llm-spendのデータイベントのセレクター（F-2、F-7）"),
         ("Spend guard rows, §10.1", "スペンドガードの行、§10.1"), "2027-01-29"),
        (("Identity", "ID管理"), ("Number of teams and permission-set quotas (01 Q-22)", "チーム数と権限セットのクォータ（01 Q-22）"), ("Contingency R-9", "予備費R-9"), "2026-12-18"),
        (("Legal / privacy", "法務／プライバシー"), ("Whether per-team content logging is needed this phase (01 Q-10)", "今期にチーム単位の内容記録が必要か（01 Q-10）"),
         ("Contingency Q-10 / D-11", "予備費Q-10／D-11"), "2026-12-18"),
    ]
    table(hd, [(L(*a), L(*b), L(*c), dd) for a, b, c, dd in OPEN], "llll")

    # ------------------------------------------------------------------ 12 Findings
    w("## 12. Findings for the design documents (not edited)" if LANG == "en" else "## 12. 設計文書への指摘事項（文書は未修正）")
    w("")
    w(T(t("docs/en/ was not changed. These are gaps or inconsistencies found while pricing the design; each should be resolved in 01/02 by its owner.",
          "docs/en/は変更していない。以下は設計に価格を付ける中で見つかった不足・不整合で、各オーナーが01/02で解消すべきもの。")))
    w("")
    v_hi = M.spend_guard_variable(4.3 * 30, 4.3 * 30 * ratio_ev)
    FIND = [
        ("F-1", (f"02 §12 says the short-lived certificate mode of AWS Private CA costs less, but that mode issues only certificates valid for 7 days or less, while D-4 and TEN-006 allow 90 days. A general-purpose CA is USD 400 a month; with one for staging, the two are USD {pca:,.0f} of this design's USD {sa:,.0f} a month. Decide between a corporate CA as trust anchor, 7-day certificates, or one shared CA (§9).",
                 f"02 §12は短期証明書モードの方が安いとしているが、このモードは有効期間7日以下の証明書しか発行できず、D-4とTEN-006は90日を許容している。汎用モードのCAは月400USDで、ステージング用と合わせると本設計の月{sa:,.0f}USDのうち{pca:,.0f}USDを占める。社内CAをトラストアンカーにする、7日証明書にする、1つのCAを共有する、のいずれかを決める（§9）。"),
         ("Platform engineering", "プラットフォームエンジニアリング")),
        ("F-2", (f"02 §9 and §12 size the spend guard for 4.3–17 million calls a day (A-9). At that scale its per-call charges are about USD {v_hi['total']:,.0f} a month at the low end (§10.1), mostly GuardDuty's analysis of Bedrock management events and unbatched counter writes in two Regions. 02 §12 should state the per-call cost, and 02 §5.2 how many counter writes a call makes after batching.",
                 f"02 §9・§12はスペンドガードを1日430万〜1,700万回（A-9）で想定している。その規模では従量費用が下限でも月約{v_hi['total']:,.0f}USD（§10.1）となり、大半はGuardDutyによるBedrock管理イベントの分析と、2リージョンでのバッチ化しないカウンター書き込み。02 §12に1回あたりの費用を、02 §5.2にバッチ化後の1回あたりのカウンター書き込み数を記載すべき。"),
         ("Platform engineering", "プラットフォームエンジニアリング")),
        ("F-3", ("02 §12 says no estimate has been made and leaves every row TBD; this estimate prices them, including R-17 (Quick Sight readers) and R-18 (bedrock-mantle data events). 02 §12 can point to it once reviewed.",
                 "02 §12は見積未作成として全行をTBDにしている。本見積はR-17（Quick Sightの閲覧者）とR-18（bedrock-mantleのデータイベント）を含めて価格を付けた。レビュー後は02 §12から本見積を参照できる。"),
         ("Platform engineering", "プラットフォームエンジニアリング")),
        ("F-4", ("02 §12 has no rows for GuardDuty, Security Hub, Config, Inspector and IAM Access Analyzer, which 02 §2.2 and §8 require. GuardDuty charges per CloudTrail management event, and every Bedrock call is one (§10.1).",
                 "02 §12には、02 §2.2・§8で必要としているGuardDuty、Security Hub、Config、Inspector、IAM Access Analyzerの行がない。GuardDutyはCloudTrail管理イベントごとに課金され、Bedrockの呼び出しはすべて管理イベント（§10.1）。"),
         ("Security / SOC", "セキュリティ／SOC")),
        ("F-5", ("02 §10 says staging has the same shapes as production, but not whether it has its own Private CA and Quick Sight, which T-084 and T-076 need. The estimate gives staging both.",
                 "02 §10はステージングが本番と同じ形を持つとしているが、T-084・T-076に必要なPrivate CAとQuick Sightを専用に持つかは記載がない。本見積では両方を持つとした。"),
         ("Platform engineering", "プラットフォームエンジニアリング")),
        ("F-6", ("02 §2.2 lists Osaka for the Route A endpoints but does not say whether they run all the time or are created at failover; it affects RTO (AVL-M02) and cost. The estimate assumes they are created at failover.",
                 "02 §2.2はRoute Aのエンドポイントに大阪を挙げているが、常時稼働か切替時に作成するかの記載がない。RTO（AVL-M02）と費用に影響する。本見積では切替時に作成するとした。"),
         ("Network", "ネットワーク")),
        ("F-7", (f"02 §4.3 logs DynamoDB data events for writes to llm-spend by any other principal. Unless an advanced event selector excludes the spend guard's own roles, every counter update is a paid data event: about USD {M.CALLS_M * M.COUNTERS * M.P['ct_data'] * 10:,.2f} a month here, about USD {4.3 * 30 * M.COUNTERS * M.P['ct_data'] * 10:,.0f} at the low end of A-9.",
                 f"02 §4.3はllm-spendへの他のプリンシパルによる書き込みをDynamoDBのデータイベントとして記録する。高度なイベントセレクターでスペンドガード自身のロールを除外しないと、すべてのカウンター更新が有料のデータイベントとなる：本見積で月約{M.CALLS_M * M.COUNTERS * M.P['ct_data'] * 10:,.2f}USD、A-9下限で月約{4.3 * 30 * M.COUNTERS * M.P['ct_data'] * 10:,.0f}USD。"),
         ("Platform engineering", "プラットフォームエンジニアリング")),
    ]
    hd = ["ID", "Finding", "Owner"] if LANG == "en" else ["ID", "指摘事項", "オーナー"]
    table(hd, [(i, L(*b), L(*c)) for i, b, c in FIND], "lll")

    return doc.text(), T.missing
