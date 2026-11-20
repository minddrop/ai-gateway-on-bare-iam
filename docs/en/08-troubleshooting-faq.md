# IAM-native LLM gateway: Troubleshooting and FAQ

<!--
Answers: the problems people actually hit, phrased the way they would describe them, and the questions they ask most.
Reader: users, integrators and support staff.
Owns: symptoms, likely causes and fixes; FAQ answers. Refers to: procedures (07), settings and limits (04), status codes (06 §4), contact details (11 §C).
Detail: one row per symptom, with a fix someone can act on and the role that can apply it. The rows below are likely problems for this design: confirm or remove them after the pilot. Add an entry every time a support question or incident repeats.
Status: stub written during design; the pilot fills it.
Fill it in using the writing conventions in ../../README.md. Delete this comment when done.
-->

> Owner: [fill: team] · Last reviewed: [fill: YYYY-MM-DD], for release [fill: version]

## 1. Common problems

| Symptom (as the user says it) | Likely cause | Fix | Who can fix it |
|---|---|---|---|
| "Claude Code says my token expired" or "UnrecognizedClient" | The portal session ended (8 h), or `llm login` was never run | Run `llm login`; check that Claude Code's `awsAuthRefresh` is set (04 §4.5) | User |
| "The browser sign-in is refused" | Device not compliant, Okta Verify not enrolled, or outside an office location (CA-GW-01) | Check Intune compliance; enrol in Okta Verify | User / Endpoint team |
| "AccessDenied" from home | Calls are allowed only from the corporate network [CMP A-13] | Use the office network | — |
| "AccessDenied" in the office | Model not in your team's tier, a non-Japan model ID, or a suspension | Run `llm models` and `llm usage`; it shows a suspension and its reason | User / Team lead |
| "My team has no access" or "llm says I have no team" | Not in an `llm-team-*` group, or provisioning has not run yet | Ask the team lead to add you; wait for the provisioning cycle | Team lead / Identity |
| "Connection reset / certificate error" | Secure web gateway is inspecting TLS for an AWS hostname [CMP A-15] | Check the exemption list in 02 §6 | Network team |
| "Request is cut off after about a minute" | A client or SDK read timeout is shorter than the request [CMP §2.7] | Set the timeouts in 04 §4.3 | User / Platform |
| "Why can't I use model X?" | Not processed in Japan, or not approved yet | See §3 | Product owner |
| "429 ThrottlingException" | The account quota for the model is reached | Retry; report if it persists | Platform |
| "My pasted key stopped working" | Short-term keys last only until your 1-hour session ends | Run `llm token` again (01 Q-27) | User |
| "My spend is charged to the wrong team" | Your tools use another of your teams | Run `llm team <name>` and restart your tools | User |
| "Codex CLI cannot find a model" | Codex CLI is approved only for some models and teams (04 §4.1, §5) | Check the approved list | Platform |
| "It stopped working after the Osaka switch" | Some models are not in Osaka; short-term keys are per Region | Use a model available in Osaka; run `llm token` again | User |

## 2. Diagnostic steps (when the cause is unclear)

1. Check the status channel: [fill: status page URL].
2. Note the time, the user, the tool, and the request ID (`x-amzn-RequestId`) from the error.
3. Check the identity the tool uses: `aws sts get-caller-identity --profile llm`.
4. Check suspensions and usage: `llm usage`.
5. Search CloudTrail for the request ID: [fill: example SIEM query].
6. Check recent deploys and `llm-guard-deny` versions: [fill: links].
7. Still stuck: escalate as in 07 §7, with the details from steps 2–6.

## 3. Frequently asked questions

- **Are my prompts stored or read by anyone?** No, by default. Nothing of ours ever receives your prompts: your tools call Bedrock directly, Bedrock does not store them, and request logging with content is turned off and locked. Only metadata is recorded. The exception is teams with their own content-logging account, approved by legal [CMP A-10, §2.8].
- **Does my data leave Japan?** Prompts, responses and everything derived from them stay in Tokyo and Osaka: the SCP denies any other model route or Region [CMP §2.5]. Sign-in data is handled by Entra ID, Okta, Intune and IAM Identity Center, which are outside this scope [CMP A-11].
- **Can I use GPT / Gemini / model X?** Only when it is on Bedrock, processed only in Japan, and approved. See the catalog in 01 §6.5 and the request process in 05 §5.3.
- **Can I get an API key?** Not a long-lived one (02 D-3). `llm token` gives a short-term key for tools that need one.
- **Who pays?** The team whose access your tools use. See 05 §1.
- **Can I use it from home?** Not in this phase.
- **Who can see my usage?** You, and others only as the privacy agreement allows (01 PRV-003); [fill: after 01 Q-9].

## 4. Getting help

Contact details are in 11 §C.

| Need | Go to |
|---|---|
| Help with the gateway or your tools | [default: help desk] |
| Integrating with Bedrock through the gateway | [default: platform engineering] |
| Bug or feature request | [fill: issue tracker and template (11 §B)] |
| Security concern | Security / SOC |
