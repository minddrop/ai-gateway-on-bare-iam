# IAM-native LLM gateway: API reference

<!--
Answers: everything an integrator needs to call models through the gateway: endpoints, authentication, errors, limits, and how the API changes over time.
Reader: developers integrating workloads, SDKs and tools.
Owns: the caller-facing contract: which Bedrock APIs are allowed and blocked, authentication, status codes and what callers should do about them. Refers to: request and response bodies (Bedrock's documentation), timeout and limit values (04), notice periods (10 §1).
Detail: document only what our policies add, remove or restrict, and link upstream for the rest. Every API style that differs from upstream gets a block from §3.4, with a working example request.
Status: stub written during design; [fill] markers are completed during the build.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last reviewed: [fill: YYYY-MM-DD], for release [fill: version]

## 1. Overview

| Item | Value |
|---|---|
| Base URL | No gateway URL: Bedrock's regional endpoints, `https://bedrock-runtime.ap-northeast-1.amazonaws.com` and `https://bedrock-mantle.ap-northeast-1.api.aws` (Osaka in DR, 02 §9) |
| Reachable from | Office and DC egress IPs, and our VPC endpoints on Route A; enforced by IAM, not by the network [CMP A-13, A-14] |
| Upstream reference | [Bedrock APIs](https://docs.aws.amazon.com/bedrock/latest/userguide/apis.html), [Bedrock endpoints](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html) |
| Format | Bedrock's: JSON over HTTPS (TLS 1.2+); streaming as Bedrock event streams or server-sent events, per API |
| Maximum request duration | 01 PRF-M03; client timeouts in 04 §4.3 |

## 2. Authentication

| Caller | Credential | Header | How to get it | Lifetime |
|---|---|---|---|---|
| Person (CLI, SDK, IDE plugin) | AWS credentials of their team's permission set | SigV4 (`Authorization: AWS4-HMAC-SHA256 …`), done by the SDK | `llm login`; AWS profile `llm` (05 §4) | 1 h, renewed by the SDK; sign-in every 8 h |
| Key-only tool | Short-term Bedrock API key | `Authorization: Bearer <key>` | `llm token` | The rest of the 1-hour session; one Region |
| DC workload | AWS credentials of the workload role | SigV4 | `aws_signing_helper` with the workload certificate (05 §5.2) | 1 h |
| Workload in an enrolled AWS account | Its own IAM role | SigV4 | The compute service | Temporary |
| Long-term API key | Not available (02 D-3) | — | — | — |

## 3. Endpoints

<!-- List only what is allowed. State explicitly what is denied, and why. -->

### 3.1 Model endpoints

| Method | Path | Purpose | Streaming | Notes |
|---|---|---|---|---|
| POST | `bedrock-runtime` `/model/{modelId}/invoke`, `/model/{modelId}/invoke-with-response-stream` | InvokeModel; Anthropic Messages body for Claude | Yes | Claude Code uses these |
| POST | `bedrock-runtime` `/model/{modelId}/converse`, `/model/{modelId}/converse-stream` | Converse, for every chat model | Yes | — |
| POST | `bedrock-runtime` `/anthropic/v1/messages` | Anthropic Messages API | Yes | Claude models |
| POST | `bedrock-runtime` `/openai/v1/chat/completions` | OpenAI Chat Completions | Yes | Only models Bedrock offers on it |
| POST | `bedrock-mantle` `/v1/responses`, or `bedrock-runtime` `/openai/v1/responses` | OpenAI Responses | Yes | Only for teams approved for Codex CLI; storage off (PRV-005) |
| GET | `bedrock` `/inference-profiles` | List inference profiles | No | Lists every profile, not only yours; use `llm models` |
| GET | Usage API `/usage/me`, `/usage/team/{team}` | Your usage, your team's | No | SigV4 with `execute-api` |

### 3.2 Management and health endpoints

| Method | Path | Who may call | Reachable through the ALB? | Purpose |
|---|---|---|---|---|
| — | None | — | n/a: there is no ALB and no management API of ours; changes go through CI (02 D-15) | — |

### 3.3 Not available

| Endpoint / feature | Reason |
|---|---|
| Batch and asynchronous invoke, agents, knowledge bases, flows, custom models, provisioned throughput, image and video models | Not in scope; denied by IAM and the SCP (01 NG-7) |
| `global.`, `apac.` and other non-`jp.` profiles; application inference profiles; any Region but Tokyo and Osaka | Not processed only in Japan; denied by the SCP (01 MDL-101) |
| The OpenAI chat format for models Bedrock does not offer on it, for example Claude | No translation (01 NG-10); use Converse or the Messages API |
| Long-term Bedrock API keys | Denied by the SCP (02 D-3) |
| Request metadata as a charging field | Recorded only in model invocation logs, which are off; never changes who pays (02 §5) |

### 3.4 Endpoint details

Add one block for each API style whose behaviour differs from upstream. Copy this template, and keep every field.

```markdown
#### <METHOD> <path>
- **Differences from upstream:** <what our policies add, remove or restrict>
- **Allowed `model` values:** <list, or "see llm models">
- **Request size limit:** <Bedrock's limit for this API, with a link>
- **Example request:** <command with placeholder credentials>
- **Example response:** <trimmed>
```

#### EXAMPLE: POST /model/{modelId}/converse
- **Differences from upstream:** only models of your team's tier; only from the corporate network; `jp.` profiles and Tokyo In-Region models only.
- **Allowed `model` values:** see `llm models`, for example `<main model ID from 04 §4.1>`.
- **Request size limit:** Bedrock's ([quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html)).
- **Example request:**
  ```sh
  aws bedrock-runtime converse --profile llm \
    --model-id <main model ID from 04 §4.1> \
    --messages '[{"role":"user","content":[{"text":"Say hello"}]}]' \
    --inference-config '{"maxTokens":64}'
  ```
- **Example response:** `{"output": {"message": {"role": "assistant", "content": [{"text": "Hello!"}]}}, "stopReason": "end_turn", "usage": {…}, …}`

## 4. Errors

<!-- The caller's view of the design decisions in 02 §3.2. -->

| HTTP status | When | What the caller should do |
|---|---|---|
| 400 | Invalid request (`ValidationException`) | Fix the request |
| 403 | Missing, wrong or expired signature or key (`UnrecognizedClientException`, `ExpiredTokenException`) | Run `llm login`; for a pasted key, run `llm token` again |
| 403 | `AccessDeniedException`: model outside your tier or the catalog, a non-Japan profile or Region, a call from outside the corporate network, or a suspension by the spend guard (budget, cap, runaway) | `llm usage` shows a suspension and its reason; otherwise see 08 §1 |
| 429 | `ThrottlingException`: the account quota for the model is reached | Retry with backoff (the SDK's adaptive mode); report if it persists |
| 5xx | Bedrock fault (`InternalServerException`, `ServiceUnavailableException`) | Retry with backoff; report the request ID |

Every response carries a request ID in the `x-amzn-RequestId` header, which is also the `requestID` in CloudTrail. Include it in support requests.

## 5. Limits and versioning

- **Budgets, caps and runaway stops:** 04 §4.4. There are no per-caller rate limits; Bedrock's account quotas apply (02 §9).
- **Request body size:** Bedrock's limits per API and model.
- **Versioning:** the APIs are Bedrock's and change only when AWS changes them. A gateway release can change which models, tiers or APIs are allowed; breaking changes are announced in 10 Release notes, with the notice period set in 10 §1.
- **Model names:** Bedrock's versioned IDs. A change of the default model in the managed client settings is announced in advance (MDL-105).
