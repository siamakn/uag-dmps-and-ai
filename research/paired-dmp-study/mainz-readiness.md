# Information needed before the first Mainz model run

Prepared 2026-11-04. This is a small infrastructure handoff, not an access request
already sent, a model recommendation or an execution commitment. No model calls
are made. The human pilot remains deferred.

The draft experiment in [experiment-protocol-draft.md](experiment-protocol-draft.md)
uses one fixed model first, compares overall versus one-criterion-at-a-time prompts,
and adds another model only after that comparison is specified. We should choose
actual model IDs from the available Mainz service, rather than infer availability
from public model releases or DMP-EVA's example configuration.

## Small information request to forward when useful

We are preparing a six-project/twelve-document DMP evaluation pilot. Could you
provide the service documentation or confirm the following?

1. **Connection and model identity:** UI/API documentation; exact available model
   IDs/checkpoint revisions; serving software/revision; authentication method.
   Credentials can be configured separately rather than included in this note.
2. **Input capacity:** supported context and output limits, the actual tokenizer or
   token-counting facility, and any service-level input-size cap. We need to count
   the complete request, rubric, instructions and reserved output together.
3. **Request controls:** which temperature, sampling, seed, structured-output and
   reasoning/thinking parameters are accepted, and how to identify parameters
   actually used or rejected. Does the response identify the served model revision?
4. **Run accounting:** request/token usage and finish-reason fields, request IDs,
   practical concurrency/rate limits, retry guidance and available test allocation.
5. **Data handling:** where submitted text and outputs are processed/retained, and
   the intended-use terms relevant to the source documents. AGRICORE's blanket
   document reuse licence has not been identified; public access is not being
   treated as a universal permission statement.

Documentation answering several items is enough; there is no need to research or
read the DMP evaluation publication to answer these infrastructure questions.

## Why these facts matter

The native DMP-EVA parser limits text before submission. The separately configured
full-document conditions in the proposal need an identified input path and a backend
that can accept the **whole** frozen request. The candidate page packets preserve
page/line references and extracted words, but their 24,000 UTF-16-unit chunk budget
is not a provider token limit and does not establish model suitability.

The native request builder also omits some configurable parameters. The experiment
must log the actual request and accepted settings, not merely values shown in a UI.
No automatic averaging of chunk scores is proposed. If full-document input does not
fit, the design must explicitly address that rather than silently reduce content.

## Local readiness contract

[mainz-profile-template.json](mainz-profile-template.json) is an unfilled information
template. Null values mean unknown, not unsupported or approved. The matrix's
proposed request counts describe future logical requests and exclude retries; they
are not charges, API calls or an estimate of the user's OpenAI subscription budget.
Before a run, resolve the profile, input/rights conditions, exact prompt/schema and
analysis decisions. Technical smoke tests can remain separate from substantive
human/tool agreement claims, which need actual human reference assessments.

No message has been sent to Andrej, IT or another person. This note is ready for the
user to reuse whenever the infrastructure discussion is timely; it is not a task
that must be completed now for the other preparation work to continue.
