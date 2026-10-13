"""Dependency-free checks for the static legal site; run from any directory."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / path for path in ("index.html", "privacy/index.html", "terms/index.html")]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.counts = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in ("a", "link") and "href" in attrs:
            self.links.append(attrs["href"])


def check():
    for path in PAGES:
        text = path.read_text()
        page = Page(text)
        label = path.relative_to(ROOT)
        assert page.counts.get("main") == 1, f"{label}: main landmark"
        assert page.counts.get("title") == 1, f"{label}: page title"
        assert page.counts.get("script", 0) == 0, f"{label}: unexpected script"
        assert len(page.ids) == len(set(page.ids)), f"{label}: duplicate IDs"
        assert 'class="placeholder"' not in text, f"{label}: unresolved placeholder"
        assert "Draft" not in text and "draft" not in text, f"{label}: stale draft notice"
        assert "mailto:mob5824@proton.me" in text, f"{label}: contact missing"
        for href in page.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / url.path).resolve() if url.path else path
            assert target.is_relative_to(ROOT), f"{label}: link leaves site"
            if target.is_dir():
                target /= "index.html"
            assert target.is_file(), f"{label}: missing local target {href}"
            if url.fragment:
                assert url.fragment in Page(target.read_text()).ids, f"{label}: missing anchor {href}"
        print(f"PASS {label}: structure, links, anchors, contact, and publication text")
    assert "@import" not in (ROOT / "assets/styles.css").read_text()
    assert "laws of Ontario" in (ROOT / "terms/index.html").read_text()
    assert "Everett Grieve" in (ROOT / "privacy/index.html").read_text()
    print("PASS Ontario governing law, operator identity, and no external CSS imports")


if __name__ == "__main__":
    check()
