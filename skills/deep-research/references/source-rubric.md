# Source Reliability & Conflict Resolution Rubric

Use this rubric when two search waves return conflicting numbers, benchmarks, or claims:

1. **Primary over secondary**: Official vendor docs, specification sheets, peer-reviewed papers, regulatory filings, and canonical GitHub repositories outrank aggregator blogs or reposted summaries.
2. **Recency check**: Check publication/commit dates. Pricing, API limits, model names, and OS requirements older than 12 months must be re-verified with `web_search` (`mode="news"`).
3. **Independent corroboration**: Two sites quoting the same press release count as **one** source, not two.
4. **Explicit ranges when unresolved**: When credible sources still disagree (e.g. real-world battery life or street pricing), report the range (`"11–14 hours across independent reviews"`) and name both sources rather than picking one silently.
