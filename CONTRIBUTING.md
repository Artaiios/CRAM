# Contributing to CRAM

Thanks for taking the time to look at contributing. This project is maintained by one person in their spare time, so I try to keep the contribution process simple and the expectations realistic.

## What's useful

- **Bug reports** — especially anything that breaks under real-world conditions: edge-case configurations, browser quirks, specific device behaviour during QR transfer.
- **Feature requests** that solve a concrete problem you're having. "It would be nice if..." with a short explanation of the situation is the most useful form.
- **Documentation fixes** — typos, unclear explanations, missing screenshots, broken links.
- **Translations** — the tool supports five languages today. If you can help with any of them, or want to add another, that's very welcome.
- **Pull requests** for clearly-scoped changes. Please open an issue first to discuss anything larger than a typo fix.

## What's probably not useful

- Large refactors that don't fix a real problem. The single-file architecture is deliberate and I want to keep it.
- Adding build tools, transpilers, bundlers, or npm dependencies. The tool is vanilla JavaScript so anyone can read and modify it with nothing but a text editor.
- Features that require a backend. The offline-first character is a hard constraint.

## How to file a bug report

Use the bug report issue template. The most important things to include:

1. What you were trying to do
2. What actually happened
3. Browser name and version
4. Whether you're opening CRAM via `file://`, `https://`, or localhost
5. Rough scale of your configuration (number of roles, persons) if it might be relevant
6. Screenshots if the problem is visual

Please avoid including real names, phone numbers, or email addresses. Sanitise your data before posting screenshots.

## How to submit a pull request

1. Open an issue first unless the change is genuinely tiny (typo, one-line fix).
2. Fork the repository.
3. Create a branch with a descriptive name — `fix/qr-scanner-firefox-fallback` or `add/swedish-translation`.
4. Keep the change focused. One concern per pull request.
5. Update the CHANGELOG under `[Unreleased]` if the change is user-visible.
6. The tool is a single HTML file. No build step. Please verify your change works by opening the file in a browser before submitting.

## Code style

The file is long but follows a few conventions:

- Module-level section headers marked with a banner comment
- State lives in a single `State` object near the top
- Event handling goes through a central dispatcher keyed on `data-action` attributes rather than inline handlers
- CSS uses variables defined in `:root` and `[data-theme="light"]` — stick to those rather than hardcoding colours
- Translations go in the five language blocks near the top. All five must be updated when adding a new key; English-only additions will be sent back for translation.

There is no linter configured. Try to match the surrounding code.

## Releases

Releases follow semantic versioning. Release candidates (`-rc1`, `-rc2`...) stay in circulation for at least two weeks before being promoted to a stable tag. Breaking changes bump the major version.

## Licence

By contributing, you agree that your contribution is licensed under the Apache License 2.0, matching the rest of the project. See [LICENSE](LICENSE).
