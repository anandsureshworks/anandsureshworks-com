# anandsureshworks-com

**anandsureshworks.com** — the AI-solutioning / widget-gallery leg of the three-leg
brand (build · secure · teach in public).

- **anandsureshworks.com** — interactive in-browser AI widgets (this site)
- [anandonsecurity.com](https://anandonsecurity.com) — security voice & analysis
- [anandsureshworks.dev](https://anandsureshworks.dev) — open-source reference lab

## Widgets

| Widget | Status | Stack |
|---|---|---|
| PII & Secret Redactor | live | rules (`redact.js`) + in-browser NER (Transformers.js) |
| Semantic Search | soon | in-browser embeddings over the OWASP reference |
| Prompt-Injection Sandbox | soon | in-browser LLM (WebLLM) |

Everything runs client-side — no server, no API key, no data leaves the browser.

## Develop / test

```sh
node redact.test.mjs        # unit tests for the deterministic redaction core
python3 -m http.server 8000 # then open http://localhost:8000 to test in a browser
```

Static site, zero build. Deploys on Vercel by pushing to `main`.
