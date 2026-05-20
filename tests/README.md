# CRAM tests

Pre-release regression tests for CRAM. The suite is intentionally small —
CRAM is a single-file tool and only the security-critical paths warrant
automation today. Everything else is covered by the structured manual
release checklist in `ROADMAP.md`.

## Test IDs

| ID    | Name                          | Trigger                                                              |
|-------|-------------------------------|----------------------------------------------------------------------|
| S-02  | XSS pen-test                  | Every release tag. Mandatory if anything changed under any `innerHTML=` site, the CSP meta-tag, or any user-input field. |

`S-02` is the historical pen-test that validated `escapeHTML()` discipline
before V1.0. V2.0 introduces several new UI surfaces (toast, drift modal,
settings accordion, live countdown, auto-sync state badges) that touch
user-controlled strings, which is why S-02 now lives in the repo as an
automated regression rather than a one-shot audit.

## Running S-02

```bash
# one-time setup (local dev box or CI runner)
npm i --no-save playwright
npx playwright install chromium

# run
bash tests/run-pen-test.sh
```

Or directly, if you already have a static server in front of the repo:

```bash
BASE_URL=http://127.0.0.1:8000 node tests/pen-test-s02.js
```

Exit codes:

- `0` — all surfaces clean, release candidate is safe to tag
- `1` — at least one XSS payload survived. **Release blocker.** Inspect
        the `[FAIL]` block in stdout for the surface, payload, and the
        DOM finding that flagged it.
- `2` — tooling missing (Playwright/Chromium not installed). The test
        could not run; treat as "unverified" — do NOT tag a release on
        a code path that has never been pen-tested.

## What S-02 covers

The script injects nine XSS payloads (`<img src=x onerror=alert(1)>`,
`<script>alert(1)</script>`, `javascript:alert(1)`, `<svg onload=...>`,
URL-encoded variants, style-tag URL contexts, …) into every
user-controlled surface:

- `role.name`, `role.description`
- `person.name`, `person.phone`, `person.email`, `person.notes`
- `level.name`
- `meta.organizationName`, `meta.printTitle`
- Sync source `label` and `config.url`
- Synthetic audit-log entries

After each injection it forces a full re-render across chart, all
sidebar tabs, and the audit log, then asserts:

1. **No alert dialog fires** (script execution would trigger one).
2. **No foreign `<script>` tag** appears in the live DOM beyond the
   three the tool ships with (fflate, qrcode-generator, main).
3. **No inline event handlers** (`onerror=`, `onload=`, `onclick=`, …)
   anywhere in the rendered DOM. CRAM itself never emits those — it
   wires every listener via `addEventListener` — so even one is a
   smoking gun.
4. **No `javascript:` URL** in any `href` or `src` attribute.
5. **No CSP-violation console messages** during render.

## What S-02 does NOT cover

- File-upload paths (drag-and-drop, picker) — covered by manual QA.
- QR scanner path — covered by `cram-mobile-qa-engineer`.
- Sync-bundle decryption against tampered ciphertext — covered by
  `cram-sync-architect` unit tests.

## Pre-release gate

Before setting any `v*` tag, run S-02 and require a `0` exit code.
If the exit code is `2`, install Playwright and re-run — do not skip.
If the exit code is `1`, fix the finding and re-run; do not relax
the assertions.

## Manual repro (fallback)

If Playwright cannot be installed in your environment, the test logic
can be reproduced manually with Chrome DevTools:

1. Open `crisis-role-manager.html` in Chrome.
2. Load `demo/cram-demo-enterprise-en.json` via the import dialog.
3. Open DevTools → Console.
4. Paste one payload assignment per surface, e.g.:
   ```js
   State.config.persons[0].name = '<img src=x onerror=alert(1)>';
   render();
   ```
5. Confirm no `alert(1)` fires, no script runs, and the string
   appears as visible literal text in the chart cell.
6. Repeat for every payload × every surface listed in the table above.

That's nine payloads × twelve surfaces = 108 manual cases — which is
exactly why the automated version exists.

## File-permission note

`run-pen-test.sh` ships without the executable bit set on systems that
restrict `chmod` during automated commits. Run it explicitly as
`bash tests/run-pen-test.sh`, or `chmod +x tests/run-pen-test.sh` once
locally after the first checkout.
