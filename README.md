# Soundtrail — project site, privacy policy, and terms

Dependency-free GitHub Pages site for the Soundtrail Android app. It doubles as the project's
landing page: every outbound link points at the **active repository**,
[`mob5824m-wq/SoundTrail`](https://github.com/mob5824m-wq/SoundTrail), so the site funnels visitors,
issue reports, and license questions there.

- `/` — app overview: features, data flows, connections, install steps, FAQ, and the legal cards
- `/self-host/` — sync/audio server guide: native setup, TLS, limits, backups, operator duties
- `/privacy/` — Privacy Policy
- `/terms/` — Terms of Service
- `/404.html` — error page (GitHub Pages serves it for any unmatched path)
- `/assets/` — one stylesheet and the SVG app icon; `/sitemap.xml`, `/robots.txt`

Public operator: **Everett Grieve (egrie-tech), Ontario, Canada** · Contact: **mob5824@proton.me**

There is no build step, no bundler, and no third-party request: no JavaScript, no analytics, no
external fonts or CSS. The only permitted `<script>` is a JSON-LD block (checked by the test), which
carries `MobileApplication` and `WebSite` schema for the landing page. Dark mode, print layout,
reduced-motion, and small-screen behaviour are pure CSS.

## Repository move (October 13, 2026)

Development moved from `egrie-tech/Geotagged-Music-App` to `mob5824m-wq/SoundTrail`. The new
repository carries the same history up to `22d906f` and the tags `v1.0.1`–`v1.0.8`, but it has **no
GitHub Releases and no Actions runs yet**, so no prebuilt APKs are attached there; the release assets
still sit on the previous repository. The site is deliberately honest about that: it links the active
repository's Releases page (which shows the empty state) and gives the build-from-source command,
instead of sending visitors to the superseded repo.

Two follow-ups belong in the app repository, not here:

1. `app/src/main/java/tech/egrie/soundtrail/ui/PinMapView.kt` sends the map-tile `User-Agent`
   `Soundtrail/1.0 (https://github.com/egrie-tech/Geotagged-Music-App)`. Every tile request therefore
   advertises the **old** repo URL to CARTO. Update it to the new repository.
2. Publish Releases (with the debug APK) on `mob5824m-wq/SoundTrail`, then check the landing page's
   `#get` wording again; the site's notice paragraph about missing releases can be deleted once they
   exist. Consider adding the in-app links to `/privacy/` and `/terms/`, which the app does not yet
   expose.

## Policy basis

Technical review: [`mob5824m-wq/SoundTrail`](https://github.com/mob5824m-wq/SoundTrail), commit
`22d906f8ed2a939adce7c823beab2fe48f1f6346` (`main`), Android version **1.0.8** (`versionCode` 9),
reviewed October 13, 2026. Sources included the README, manifest, dependencies, network security
config, provider integrations, the unified in-app player, map tile loader, sync client, backup
code, and `server/` (README, API routes, rate limits, `run.py`).

The 1.0.8 review superseded four statements from the earlier 1.0.6 review, and they are now aligned:

- **Default server URL.** The app falls back to `https://soundtrail.duckdns.org` when the sync URL
  field is empty, so the policy names it. It previously said the URL had "not yet been assigned".
  The claim that the server is contacted only after sign-up/sign-in or enabled sync is backed by
  `MainViewModel` (`autoSyncEnabled && connected && hasRecoveryKey`).
- **YouTube sign-in.** Two mutually exclusive paths are disclosed: the Google-account path holds an
  access token in memory only; the Desktop-OAuth **Client ID** path persists access and refresh
  tokens, plus an expiry, in Keystore-encrypted storage — and playlist **auto-import is on by
  default** once connected, bounded at 200 playlists / 2,000 items, with search limited to the
  first 50 playlists × 50 items and matched on-device.
- **Google services.** `GoogleSignIn.getClient` backs the Google-account path, so that option needs
  Play services or a standard microG install under `com.google.android.gms`; `DeviceApps.systemGmsInstalled`
  and `microGReInstalled` show why MicroG RE is explicitly not enough, and the Client ID path is the
  no-Google-services route. The landing page therefore says "works on a de-Googled phone" with the
  exception named, not "no Google services required" — a claim that would have been about the app as a
  whole while the sign-in API is a compiled-in dependency. `tests/check_site.py` rejects that phrasing.
- **In-app playback.** The unified `MediaPlayer` player (Jellyfin streams, local files, Spotify
  `preview_url` previews, SoundCloud stream/transcoding URLs, and extracted YouTube audio) runs
  under a `mediaPlayback` foreground service, replacing the old "opens in an external app or
  browser" wording. Full-length Spotify tracks still open in Spotify's app.
- **Extraction internals.** The endpoint is named precisely: one video ID per request, `yt-dlp` plus
  FFmpeg, temporary per-request files, 250 MiB cap, no cookies, no Google token.

Operator-provided details carried forward unchanged: the operator self-hosts the default service in
Canada; AWS is a possible future provider only; the operator reports no server access logs and
Google authentication-related analytics only. Website hosting infrastructure (including GitHub Pages
or the preview platform) may independently generate request logs; the app's no-access-log disclosure
is not a claim about this website.

The reviewed source snapshot is not the distributed build. **Verify against the APK users actually
receive** before relying on: the default-server connection behaviour, whether sync's library upload
is limited to what the policy says, and any analytics/telemetry beyond Google sign-in. Source review
cannot verify hosting configuration, logging, or dashboard analytics. If "Google auth analytics"
actually means Firebase Analytics, Google Analytics, custom authentication-event logging, or another
SDK, name it and describe its fields and retention before shipping it.

## Policy choices made for the operator

- Ontario and applicable Canadian federal law, with mandatory consumer protections preserved.
- Services intended for adults (18+ and the age of majority where they live), without a claim of
  technical age verification. MIT software permissions remain separate.
- No payment obligation under these terms; any future paid service needs separate disclosed terms.
- Canadian privacy rights and PIPEDA language only where applicable, not a claim that every
  processing activity falls under that statute.
- No invented postal address, log-retention period, or AWS deployment.
- No promise that deleting an account erases independent hosts, other devices, or user-exported
  backups.

## Release checklist

1. Check the policies against the distributed APK and the actual default-server configuration.
   Confirm library sync is limited to what is disclosed, and that app/server analytics, logs,
   backups, and third-party services match these disclosures. The supplied server does not create
   database backups automatically; independently configured backup infrastructure needs additional
   retention disclosures.
2. Keep `https://soundtrail.duckdns.org` current in `privacy/` and `terms/` (and in the app) if the
   endpoint, its hosting country, or its subprocessors change. Material hosting changes require a
   policy revision first.
3. Add permanent policy links to the app, provider/OAuth consent setup, registration, and store
   listing, and provide a meaningful opportunity to review and accept the terms where required.
   Align store audience settings with the adult-service rule. These website files do not implement
   app-side changes.
4. Provide the prominent location disclosure and consent Android requires before collection, and
   make sure users can distinguish connecting to the default server from connecting a music
   provider: the former discloses IP address and timing even with no library upload.
5. Honour Google API Limited Use commitments and deletion/consent processes, and reconcile OAuth and
   app-store disclosures with runtime behaviour.
6. Obtain appropriate legal review. Keep the monitored email current, and verify a workable
   account-deletion assistance process for users who cannot sign in.
7. Deploy through the normal review process and configure GitHub Pages. Keep policy URLs stable.

### Values that go stale on purpose

The landing page and `sitemap.xml` state pinned facts reviewed by hand, so a new release means
touching them: the software version in the JSON-LD block and the `Reviewed at v1.0.8` pill, the
`lastmod` dates in `sitemap.xml`, and the "October 13, 2026" stamps. `tests/check_site.py` asserts
the sitemap dates, so update them together. `python3 tests/check_site.py` is the mechanical half of
that job; the policy text itself still needs a human against the source.

## Preview and checks

```sh
python3 tests/check_site.py                      # structure, links, policy invariants
python3 -m http.server 8000 --bind 0.0.0.0       # then open http://localhost:8000/
```

Relative local links work under a path prefix. The `canonical` tags, `og:url`, `robots.txt`, and
`sitemap.xml` hard-code `https://egrie-tech.github.io/`; if the site ever moves origin, update all
four together (or delete the canonicals and say so here).

`tests/check_site.py` enforces more than link health: no executable script, no inline event handler,
no iframe, no external stylesheet or font host, every external host inside a small allow-list, the
superseded repository linked nowhere, the contact address present on every page, one decorative logo
per page, and the four v1.0.8 disclosure statements. Keep it that way when adding pages — add them to
`PAGES` (and `INDEXED` plus the sitemap if they should be indexed).

## Hosting notes

This repository is published as a **user Pages site**: `Settings → Pages → Deploy from a branch`,
branch `main`, folder `/`. It therefore serves at `https://egrie-tech.github.io/`, with no path
prefix. The root `.nojekyll` file disables Jekyll processing so the HTML, CSS, `robots.txt`,
`sitemap.xml`, and `404.html` are published exactly as committed.

### Changing or removing the custom domain

A custom domain on a user site replaces the `<user>.github.io` hostname for **every** page on the
account. Two things are easy to get wrong:

1. **DNS must point at GitHub Pages.** For an apex domain use the four GitHub Pages `A` records
   (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`); for a subdomain use
   a `CNAME` to `egrie-tech.github.io`. A domain that resolves anywhere else (for example to a
   self-hosted server) cannot be verified by GitHub, and the site can then fail to serve — GitHub
   answers with its "Site not found" page for both the custom domain and the `github.io` URL.
2. **Removing the domain needs a new deployment.** Deleting the domain in `Settings → Pages` (or
   deleting the `CNAME` file, which sets the same value) does not always re-provision the default
   `github.io` hostname on its own. Push a new commit to `main` to force a fresh Pages build, then
   confirm `https://egrie-tech.github.io/privacy/` loads before treating the change as done.

### When the site returns "Site not found"

The published site, its Pages settings, and the build history are three separate things. Check them
in this order:

```sh
python3 tests/check_site.py
gh api repos/egrie-tech/egrie-tech.github.io/pages \
  --jq '{status,cname,source,html_url,pending_domain_unverified_at}'
gh api repos/egrie-tech/egrie-tech.github.io/pages/builds --jq '.[0] | {status,error,commit}'
```

A `PAGES/CNAME` value that is not `null` while the site should be on the default hostname means a
custom domain is still configured. `pending_domain_unverified_at` set to a timestamp means GitHub
could not verify the domain's DNS. If the settings are already clean and the newest build reports
`built` with no error but the URL still 404s, the edge has not picked up the change: push a new
commit to `main` (an empty commit is enough) and allow a few minutes for the deployment to finish.
