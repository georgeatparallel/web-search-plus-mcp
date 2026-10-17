# web-search-plus-mcp 5.1.1

Matches the engine of Hermes Web Search Plus [v5.1.1](https://github.com/robbyczgw-cla/hermes-web-search-plus/releases/tag/v5.1.1) (includes the engine parts of 5.1.0). Bug fixes for 5.0.1; no breaking changes, tool names, input schemas, routing defaults and config format stay the same.

## Fixed

- **No provider request after the request deadline.** The deadline now reaches every provider call, batch loop and retry. Pages already fetched are kept; the rest of a batch is marked `not tried: request ran out of time`. Octen, TinyFish and DonSeTch respect the per-attempt timeout cap, and `research` passes its deadline to its members and its source extraction.
- **Running out of time is not a provider failure.** It opens no circuit, records no latency sample and uses no budget unit when nothing was sent.
- **Brave's per-second 429 retry lives in the attempt engine**, so it respects the deadline and shows up as its own try in receipts.
- **Request budget without SQLite.** The per-request attempt limit is enforced even when the state store is unavailable; a daily limit fails closed when the ledger cannot be read; SQLite is probed again 30 s after an I/O error.
- **Half-open probes release their lease** when they end without a verdict on the provider or are blocked by a budget, so a provider is no longer blocked for 60 s by a probe that never ran.
- **One result per requested URL in `web_extract`,** in request order, also when several providers served the batch. Rewritten URLs (`http` → `https`, redirects, trailing slash, IDN) are matched to the URL you asked for; an item that cannot be matched leaves the URL open for fallback.
- **The search cache is keyed by the credentials that produced a result.** A new key or SearXNG instance no longer returns cached results of the old one.
- Brave queries are shortened only past 600 characters / 75 words.
- A `jev.api_key` in `config.json` is ignored with a warning instead of discarding the whole config file.
- Provider names given to `web_extract` are matched case-insensitively in the engine; unknown names return a clean error.

## Compatibility

- `web_search` and `web_extract` names and input schemas are unchanged.
- Additive: the `wsp.extract.partial` warning may carry `details.unmatched_count`, and extract payloads may carry `unmatched_results`; `details.failed_urls` stays.
- Provider SDK: `wsp_sdk` additionally exports `RequestDeadlineExceeded`, `deadline_passed`, `dispatch_timeout` and `remaining_seconds`.
- New module `web_search_plus_mcp.credentials`. No secret resolver is installed in this package, so keys still come from the MCP client `env` block, the process environment and the `.env` files the server loads.

## Not ported

Hermes plugin-only changes: profile-scoped provider keys (plugin catalog rule 11) and the removal of `.env` loading, the removal of `TYPESAFE_API_KEY_FILE`, `hermes web-search-plus` commands, Hermes Desktop settings, and the native backend with its keyless-rescue handling.
