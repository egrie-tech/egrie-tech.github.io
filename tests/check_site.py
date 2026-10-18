"""Dependency-free checks for the static Soundtrail site; run from any directory.

Guards, in addition to structure and links:
  * no executable JavaScript anywhere (only a JSON-LD block is tolerated);
  * no third-party stylesheets, fonts, frames, or trackers;
  * every absolute URL points at an allow-listed host, and no link anywhere on
    the site still points at the superseded egrie-tech/Geotagged-Music-App repo;
  * the legal disclosures that must stay in step with the app source.
"""
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "privacy/index.html", "terms/index.html", "self-host/index.html", "404.html"]
INDEXED = ["index.html", "privacy/index.html", "terms/index.html", "self-host/index.html"]
ACTIVE_REPO = "mob5824m-wq/SoundTrail"
ACTIVE_REPO_URL = "https://github.com/" + ACTIVE_REPO
STALE_REPO = "egrie-tech/Geotagged-Music-App"
ORIGIN = "egrie-tech.github.io"
# Outbound service hosts are explicitly allow-listed; add each new destination deliberately.
ALLOWED_DOMAINS = {
    ORIGIN, "github.com", "google.com", "google.dev", "youtube.com", "priv.gc.ca", "ffmpeg.org",
    "discord.gg", "spotify.com", "soundcloud.com", "jellyfin.org", "ollama.com", "openai.com",
    "openrouter.ai", "arena.ai", "anthropic.com",
}
LD_JSON = 'type="application/ld+json"'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.counts = {}
        self.script_attrs = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "script":
            self.script_attrs.append(attrs)
        if tag in ("a", "link") and "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
            if "src" in attrs:
                self.links.append(attrs["src"])
        if tag == "style" or (tag == "link" and "stylesheet" in str(attrs.get("rel", ""))):
            self.links.append(attrs.get("href", ""))


def local_target(path, href):
    """Resolve a local href, treating a leading / as the site root (404.html is served anywhere)."""
    url = urlsplit(href)
    if not url.path:
        return path, url
    if url.path.startswith("/"):
        return (ROOT / url.path.lstrip("/")).resolve(), url
    return (path.parent / url.path).resolve(), url


def check():
    for rel in PAGES:
        path = ROOT / rel
        text = path.read_text()
        page = Page(text)
        label = path.relative_to(ROOT)
        assert page.counts.get("main") == 1, f"{label}: main landmark"
        assert page.counts.get("title") == 1, f"{label}: page title"
        assert len(page.images) == 1, f"{label}: expected one site logo image"
        assert page.images[0].get("alt") == "", f"{label}: decorative logo should not duplicate brand text"
        assert "soundtrail-logo.svg" in page.images[0].get("src", ""), f"{label}: incorrect site logo"
        # Only a JSON-LD block may use a <script> tag; no event handlers, no iframes, no trackers.
        assert all(a.get("type") == "application/ld+json" and "src" not in a for a in page.script_attrs), \
            f"{label}: executable or external script found"
        assert page.counts.get("iframe", 0) == 0, f"{label}: unexpected iframe"
        assert not re.search(r"\son[a-z]+\s*=\s*\"", text), f"{label}: inline event handler"
        external = [h for h in page.links if h.startswith(("http:", "https:", "//"))]
        assert not [h for h in external if "cdn." in h or "googleapis.com" in h and "youtube" in h], \
            f"{label}: third-party asset or font host in a link ({external})"
        assert len(page.ids) == len(set(page.ids)), f"{label}: duplicate IDs"
        assert 'class="placeholder"' not in text, f"{label}: unresolved placeholder"
        assert "Draft" not in text and "draft" not in text, f"{label}: stale draft notice"
        assert "mailto:mob5824@proton.me" in text, f"{label}: contact missing"
        assert "https://discord.gg/rZzbuEjXrg" in text, f"{label}: community help link missing"
        for href in page.links:
            url = urlsplit(href)
            if url.scheme == "mailto":
                continue
            if url.scheme or url.netloc:
                host = url.netloc.split(":")[0]
                assert any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS), \
                    f"{label}: unexpected external host {href}"
                # The active app repository may be linked; the superseded repository must never be linked.
                assert STALE_REPO not in url.path, f"{label}: link still points at the superseded repo ({href})"
                continue
            target, parsed = local_target(path, href)
            assert target.is_relative_to(ROOT), f"{label}: link leaves site"
            if target.is_dir():
                target /= "index.html"
            assert target.is_file(), f"{label}: missing local target {href}"
            if parsed.fragment:
                assert parsed.fragment in Page(target.read_text()).ids, f"{label}: missing anchor {href}"
        if rel != "404.html":
            assert f'href="/' not in text, f"{label}: root-relative link breaks under a path prefix"
        if ACTIVE_REPO in text:
            assert ACTIVE_REPO_URL in text, f"{label}: no link to the active repository"
        print(f"PASS {label}: structure, links, anchors, contact, and publication text")


def check_seo():
    sitemap = (ROOT / "sitemap.xml").read_text()
    robots = (ROOT / "robots.txt").read_text()
    base = "https://egrie-tech.github.io/"
    for rel in INDEXED:
        url = base + ("" if rel == "index.html" else rel.replace("index.html", ""))
        assert f"<loc>{url}</loc>" in sitemap, f"sitemap.xml: missing {url}"
        assert f'rel="canonical" href="{url}"' in (ROOT / rel).read_text(), f"{rel}: canonical URL mismatch"
    assert "404.html" not in sitemap, "the error page does not belong in the sitemap"
    dates = set(re.findall(r"<lastmod>([^<]+)</lastmod>", sitemap))
    assert dates == {"2026-10-18"}, f"sitemap lastmod dates must match the review date: {sorted(dates)}"
    assert "Sitemap: " + base + "sitemap.xml" in robots, "robots.txt: sitemap line missing"
    assert not (ROOT / "privacy" / "index.html").read_text().count("noindex"), "legal pages must stay indexable"
    assert 'name="robots" content="noindex"' in (ROOT / "404.html").read_text(), "404 must stay out of the index"
    print("PASS sitemap, robots, and canonical URLs agree with the published pages")


def check_site_css():
    css = (ROOT / "assets/styles.css").read_text()
    packed = "".join(css.split())  # the stylesheet is minified; compare without whitespace
    assert "@import" not in css, "external CSS import"
    assert "url(http" not in css, "external CSS asset"
    assert "prefers-color-scheme:dark" in packed, "dark mode is missing"
    assert "(prefers-reduced-motion:reduce)" in packed, "reduced-motion guard"
    assert packed.count("scroll-behavior") <= 1, "smooth scrolling must stay opt-in"
    assert "--ink:" in packed and "var(--ink)" in packed, "colours must run through the token set"
    print("PASS stylesheet: self-contained, dark mode, reduced motion")


def check_disclosures():
    privacy = (ROOT / "privacy/index.html").read_text()
    terms = (ROOT / "terms/index.html").read_text()
    app = (ROOT / "index.html").read_text()
    assert "laws of Ontario" in terms, "Ontario governing law"
    assert "Everett Grieve" in privacy, "operator identity"
    egrie_link = '<a href="https://github.com/egrie-tech">egrie-tech</a>'
    mob_link = '<a href="https://github.com/mob5824m-wq">mob5824m-wq</a>'
    for name, text in (("index", app), ("privacy", privacy), ("terms", terms),
                       ("404", (ROOT / "404.html").read_text())):
        assert "Everett Grieve (" in text and "also known as " in text and egrie_link in text and mob_link in text, \
            f"{name}: maintainer attribution must link both handles to the same person"
    readme = (ROOT / "README.md").read_text()
    assert "[egrie-tech](https://github.com/egrie-tech)" in readme and \
        "[mob5824m-wq](https://github.com/mob5824m-wq)" in readme, \
        "README: maintainer attribution must link both GitHub profiles"
    # Current version facts: the site pins the reviewed release on every legal page.
    assert "1.0.14" in app, "landing page must name the reviewed app version"
    assert '\"softwareVersion\":\"1.0.14\"' in app, "JSON-LD softwareVersion is stale"
    assert "37b4413" in privacy and "37b4413" in terms, "legal pages must name the reviewed commit"
    assert "v1.0.9" in app and "v1.0.14" in app, "release history is stale"
    assert "Once Releases are published" not in app, "releases now exist; remove the old caveat"
    assert "soundtrail-1.0.14-debug.apk" in app, "install step must name the current APK"
    # Claims that were stale against app v1.0.8 and must not regress:
    assert "soundtrail.duckdns.org" in privacy, "default sync server must be named in the policy"
    assert "soundtrail.duckdns.org" in terms, "default sync server must be named in the terms"
    assert "Its public URL has not yet been assigned" not in privacy, "stale: server URL is now assigned"
    assert "has not yet been assigned" not in terms, "stale: server URL is now assigned"
    assert "refresh token" in privacy, "Client-ID YouTube path must disclose persisted refresh tokens"
    assert "250 MiB" in privacy, "download caps are a material disclosure"
    assert "yt-dlp" in privacy and "yt-dlp" in terms, "the third-party extractor must be named"
    assert "advertising ID" in privacy, "no-advertising-ID statement"
    # The Google-services caveat must stay visible: only the Google-account YouTube
    # sign-in wants Play services or standard microG, and "no Google services needed"
    # as a blanket claim about the app is wrong.
    assert "Play services" in app and "standard microG" in app, \
        "landing page must state which YouTube path needs Google services"
    assert "MicroG RE" in app, "the MicroG RE limitation must be stated, not hidden in the app README"
    for text, name in (("index", app), ("privacy", privacy)):
        assert "No Google services required" not in text, f"{name}: overbroad Google-services claim"
    assert "requires Google Play services" in privacy, \
        "the policy must name the Play services dependency of the Google-account path"
    # Voice, speech, and optional model readings, added at app 1.0.14:
    assert "RECORD_AUDIO" in privacy, "the microphone permission must be disclosed"
    assert "speech" in privacy and "text-to-speech" in privacy, "speech recognition and replies must be disclosed"
    assert "does not record" in privacy, "the policy must say the app does not record audio"
    assert "Ollama" in privacy and "OpenAI-compatible" in privacy, "model providers must be named"
    assert "Google AI Studio" in privacy and "Arena" in privacy, "hosted model providers must be named"
    assert "off by default" in privacy, "the model reading must be disclosed as opt-in"
    assert "TheAudioDB" in privacy, "tag lookups must be disclosed"
    assert "Android Auto" in privacy and "Android Auto" in app, "the car path must be disclosed"
    assert "MEDIA_CONTENT_CONTROL" in privacy, "the Android Auto caller allowlist must be stated"
    assert "Discord help group" in privacy and "third-party platform" in privacy, \
        "the privacy policy must identify Discord as a third-party support channel"
    assert "Discord help group" in terms, "the terms must cover the Discord support channel"
    assert "Android Auto" in terms and "Ollama" in terms and "Arena" in terms, \
        "the terms must cover car, speech, and model providers"
    assert "which you must follow" in terms and "Privacy Policy before sending a mood request" in terms, \
        "AI Mood users must follow provider terms and review its privacy policy"
    assert "which you must follow" in app and "review its Privacy Policy before sending a mood request" in app, \
        "the landing page must disclose the model-provider requirements"
    provider_policy_urls = (
        "https://policies.google.com/terms",
        "https://policies.google.com/privacy",
        "https://developers.google.com/terms",
        "https://ai.google.dev/gemini-api/terms",
        "https://www.spotify.com/legal/end-user-agreement/",
        "https://developer.spotify.com/terms",
        "https://www.spotify.com/legal/privacy-policy/",
        "https://pages.soundcloud.com/legal/terms-of-use.html",
        "https://developers.soundcloud.com/docs/api/terms-of-use",
        "https://pages.soundcloud.com/legal/privacy-policy.html",
        "https://jellyfin.org/",
        "https://jellyfin.org/docs/general/community-standards/servers/",
        "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
        "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement",
        "https://ollama.com/terms",
        "https://ollama.com/privacy",
        "https://www.anthropic.com/legal/consumer-terms",
        "https://www.anthropic.com/legal/commercial-terms",
        "https://www.anthropic.com/legal/privacy",
        "https://www.anthropic.com/legal/data-processing-addendum",
        "https://openai.com/policies/row-terms-of-use/",
        "https://openai.com/policies/",
        "https://openai.com/policies/service-terms/",
        "https://openai.com/policies/services-agreement/",
        "https://openai.com/policies/row-privacy-policy/",
        "https://openai.com/policies/api-data-usage-policies/",
        "https://openrouter.ai/terms",
        "https://openrouter.ai/privacy",
        "https://help.arena.ai/articles/5629909088-terms-of-use",
        "https://help.arena.ai/articles/3765052346-privacy-policy",
    )
    for url in provider_policy_urls:
        assert f'href="{url}"' in terms, f"terms: missing official provider policy link {url}"
    assert "Jellyfin is self-hosted software, not one hosted service" in terms, \
        "Jellyfin must not be described as one centrally hosted service"
    assert "individual-services privacy policy does not cover API content" in terms, \
        "OpenAI API data handling must not be conflated with its individual-services privacy policy"
    assert "The Privacy Policy does not cover customer business/API content" in terms, "Anthropic API handling must be distinguished from its consumer privacy policy"
    assert '../terms/#provider-policy-links' in privacy, "privacy policy should link to the provider policy list"
    assert "Before enabling AI Mood" in app and "changing the provider or endpoint URL" in app, \
        "the landing page must advise users to re-check provider changes"
    assert "Soundtrail cannot verify who operates a custom endpoint" in app, \
        "custom endpoint limitations must be disclosed"
    assert "follow its applicable terms and usage policies" in privacy, \
        "the privacy policy must direct AI Mood users to provider terms and policies"
    assert "Changing the provider or endpoint URL can change who receives the request" in privacy, \
        "the privacy policy must disclose provider changes"
    assert "Before enabling or changing an endpoint" in terms and "confirm you trust the destination" in terms, \
        "the terms must advise users to verify endpoints before use"
    for name, text in (("index", app), ("privacy", privacy), ("terms", terms)):
        assert "not medical or mental-health advice, diagnosis, or crisis support" in text, \
            f"{name}: AI Mood must be limited to music discovery, not health or crisis support"
    assert "Avoid including sensitive or identifying details in mood descriptions" in app and privacy, \
        "the landing page and privacy policy must warn against sensitive mood prompts"
    assert "Do not include sensitive or identifying details in a mood prompt" in terms, \
        "the terms must warn against sensitive mood prompts"
    assert "Keystore" in privacy, "stored secrets must be described"
    for name, text in (("index", app), ("privacy", privacy), ("terms", terms),
                       ("self-host", (ROOT / "self-host/index.html").read_text())):
        assert ACTIVE_REPO in text, f"{name}: must link the active repository"
    assert STALE_REPO not in "".join(
        href for href in Page(privacy).links + Page(terms).links + Page(app).links if "http" in href
    ), "a legal page links the superseded repository"
    print("PASS active-repo links, release facts, and the v1.0.14 disclosure set")


def check_self_host_guide():
    guide = (ROOT / "self-host/index.html").read_text()
    for text in (
        "python3 run.py --setup", "python3 run.py --test",
        "curl -fsS http://127.0.0.1:8080/health",
        "Invoke-RestMethod http://127.0.0.1:8080/health",
        "TCP ports", "443", "sudo caddy validate --config /etc/caddy/Caddyfile",
        "systemctl enable --now soundtrail-sync",
        "SOUNDTRAIL_DB=/var/lib/soundtrail/data/soundtrail.sqlite3",
        "journalctl -u soundtrail-sync", "X-Forwarded-For", "python3-venv",
        "tar -czf /secure-backups/soundtrail-data-$(date +%F).tar.gz",
    ):
        assert text in guide, f"self-host guide missing setup instruction: {text}"
    assert "WantedBy=multi-user.target" in guide, "systemd unit needs an install target"
    assert "stop the service" in guide, "backup instructions must stop SQLite before archiving"
    print("PASS self-host guide: local smoke test, HTTPS proxy, systemd, updates, and backups")


if __name__ == "__main__":
    check()
    check_seo()
    check_site_css()
    check_disclosures()
    check_self_host_guide()
