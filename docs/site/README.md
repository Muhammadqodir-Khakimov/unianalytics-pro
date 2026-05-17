# UniAnalytics PRO — Documentation Site

This folder is the **Docusaurus**-compatible documentation source.

## Quick start (when you want to spin up Docusaurus)

```bash
npx create-docusaurus@latest unianalytics-docs classic
# Copy `docs/site/docs/*` into the new project's `docs/` folder
cd unianalytics-docs && npm run start
```

## Structure

- `docs/intro.md` — Welcome
- `docs/architecture.md` — System architecture
- `docs/getting-started.md` — Setup for new devs
- `docs/api/` — API reference (auto-gen-friendly)
- `docs/admin/` — Admin manual
- `docs/student/` — Student manual
- `docs/teacher/` — Teacher manual

## Why not commit the full Docusaurus tree?

We keep the docs as plain markdown so they render on GitHub *and* slot into Docusaurus when we deploy `docs.unianalytics.uz`. Avoids ~100MB of `node_modules` in the monorepo.
