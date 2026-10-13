# Soundtrail privacy and terms

Dependency-free GitHub Pages site:

- `/` — legal landing page
- `/privacy/` — Privacy Policy
- `/terms/` — Terms of Service

Public operator: **Everett Grieve (egrie-tech), Ontario, Canada**

Contact: **mob5824@proton.me**

The documents have no remaining placeholders and take effect upon first publication. They are not a legal compliance certification. Creating these files does **not** deploy them, configure GitHub Pages, add links to the Android app, or implement acceptance of the terms.

## Policy basis

Technical review: [Geotagged-Music-App](https://github.com/egrie-tech/Geotagged-Music-App), commit `861de3258c8e946db10f6d0fff71e31ccf2e489a`, Android version 1.0.6, reviewed October 13, 2026. Sources included the README, manifest, dependencies, provider integrations, map tile loader, local data/backup implementation, cloud sync/account deletion, server documentation, and MIT license.

Operator-provided details:

- The distributed app connects to the operator’s default server, with a self-hosting option.
- The operator self-hosts in Canada; no public server URL has been assigned yet.
- AWS is a possible future provider, not a current server host.
- The operator reports no server logs, and authentication-related Google analytics only. The policy distinguishes those from account/session records, encrypted sync data, and Google’s own processing.

The reviewed source snapshot had an empty default server setting, so the released/default-connection behavior must be verified against the build users actually receive. Source review cannot independently verify hosting configuration, logging, or dashboard analytics. If “Google auth analytics” actually means Firebase Analytics, Google Analytics, custom authentication-event logging, or a different SDK/dashboard with additional data collection, update the policy to name it and describe actual fields and retention before using that integration. The present wording describes Google authentication-related service metadata, not a verified separate telemetry system.

## Policy choices made for the operator

- Ontario and applicable Canadian federal law, with mandatory consumer protections preserved.
- Services intended for adults (18+ and the age of majority where they live), without a claim of technical age verification. MIT software permissions remain separate.
- No payment obligation under these terms; any future paid services require separate disclosed terms.
- Canadian privacy rights and PIPEDA language only where applicable, not an assertion that every processing activity falls under that statute.
- No invented public URL, postal address, log-retention period, or AWS deployment.
- No promise that deleting an account erases independent hosts, other devices, or user-exported backups.

## Release checklist

1. Check the policies against the distributed APK and actual default-server configuration. Confirm that library sync is enabled only as described, and verify that app/server analytics, logs, backups, and third-party services match these disclosures. The supplied server does not create database backups automatically; independently configured backup infrastructure requires additional retention disclosures.
2. Set a public HTTPS server endpoint before releasing hosted features and identify it in the app. Update the hosting description before switching to AWS or another provider; disclose actual processing countries and any material subprocessors.
3. Add permanent policy links to the app, provider/OAuth consent setup, registration, and store listing. Provide a meaningful opportunity to review and accept terms where required. Align store audience settings with the adult-service rule. These website files do not implement app-side changes.
4. Provide any required prominent location disclosure and consent before collection. Ensure users can distinguish default-server connection from library sync; the former can disclose IP address and timing even without a library upload.
5. Honor Google API Limited Use commitments and deletion/consent processes, and reconcile OAuth/app-store disclosures with actual runtime behavior. Additional regional disclosures may be needed depending on distribution.
6. Obtain appropriate legal review. Keep the monitored email current and verify a workable account-deletion assistance process when sign-in is unavailable.
7. Deploy through the normal review process and configure GitHub Pages. Keep policy URLs stable and update them as practices change.

If this repository uses its default GitHub Pages domain, the intended URLs are:

- https://egrie-tech.github.io/privacy/
- https://egrie-tech.github.io/terms/

## Preview and checks

```sh
python3 tests/check_site.py
python3 -m http.server 8000 --bind 0.0.0.0
```

No JavaScript, tracking scripts, external fonts, cookies, or build tools are used by these pages. Website hosting infrastructure (including GitHub Pages or the preview platform) may independently generate request logs; the default app server’s no-access-log disclosure is not a claim about website hosting. Relative local links work under a path prefix.
