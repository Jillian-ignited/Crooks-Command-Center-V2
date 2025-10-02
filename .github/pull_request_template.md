<!-- .github/pull_request_template.md -->

# Bugfix Title
[bugfix] <short, specific summary>  
Closes #<issue-id> (if applicable)

## Problem
- **Observed behavior:** <what’s broken, with error text or stack trace>
- **Expected behavior:** <what should happen>
- **User impact / severity:** <Critical | High | Medium | Low>

## Reproduction Steps
1) <step 1>
2) <step 2>
3) <actual result> vs <expected result>

## Root Cause (hypothesis or confirmed)
- <config mismatch / null check missing / race condition / bad route / etc.>
- Affected modules/files: `<paths>`

## Fix Summary
- <what you changed and why it resolves the bug>
- Alternatives considered: <optional>

## Tests & Verification
- [ ] Added/updated unit tests: `<files>`
- [ ] Manual verification steps:
  - Command(s): `<how to run app/tests>`
  - Endpoint(s)/Page(s): `<urls>`
  - Verified logs show `<signal>` and error no longer occurs
- [ ] Cross-env check (local → staging → prod)

## Risk & Rollback
- Risk level: <Low/Med/High> — why
- Feature flags or guarded paths: <if any>
- Rollback plan: `git revert <sha>` or `<toggle flag>`

## Diagnostics Artifacts
- Screenshot(s): <attach>
- Log/trace snippet(s):  
  ```text
  <paste minimal relevant log or stack trace>