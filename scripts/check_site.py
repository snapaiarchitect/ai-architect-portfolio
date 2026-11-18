#!/usr/bin/env python3
"""Offline site checker for the static portfolio (stdlib only).

Usage:
    python3 scripts/check_site.py [--root DIR]
    python3 scripts/check_site.py --selftest

Rules (the tag in brackets is printed with every failure):
  LOCAL_REF     every local href/src in every HTML file resolves to a file
  IFRAME_TITLE  every <iframe> has a non-empty title
  FORBIDDEN     no 'goaiarchitect.io', 'localhost', '127.0.0.1' in HTML
                (files under projects/ are excluded from this rule)
  CDN_VERSION   every external <script src> pins an exact version
                (no @latest, no /latest/, no major-only range like @3 or @3.5)
  CANONICAL     canonical and og:url, when present, start with
                https://goaiarchitect.com ; index.html must have a canonical
  SITEMAP       sitemap.xml exists and every <loc> maps to an existing file
  ROBOTS        robots.txt exists and references the sitemap

Exit code 0 = all rules pass, 1 = failures, 2 = usage error.
"""
import os
import re
import sys
import tempfile
import shutil
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

SITE = "https://goaiarchitect.com"
FORBIDDEN = ("goaiarchitect.io", "localhost", "127.0.0.1")
SKIP_DIRS = {".git", "node_modules", ".github"}
SKIP_SCHEMES = ("http:", "https:", "//", "mailto:", "tel:", "javascript:",
                "data:", "sms:", "blob:", "about:")
EXACT_VERSION = re.compile(r"(?<![\d.])\d+\.\d+\.\d+(?![\d])")
RANGE_PIN = re.compile(r"@(?:latest|next|\*|[\^~]?\d+(?:\.\d+)?(?:\.x)?)(?=[/?#]|$)")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []      # (tag, attr, value)
        self.iframes = []   # (line, title)
        self.scripts = []   # src
        self.canonical = None
        self.og_url = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        for attr in ("href", "src", "poster", "data"):
            if attr in a and tag in ("a", "link", "script", "img", "iframe",
                                     "source", "video", "audio", "embed",
                                     "object", "area", "track", "input"):
                self.refs.append((tag, attr, a[attr].strip()))
        if tag == "iframe":
            self.iframes.append((self.getpos()[0], a.get("title", "").strip()))
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"].strip())
        if tag == "link" and a.get("rel", "").lower() == "canonical":
            self.canonical = a.get("href", "").strip()
        if tag == "meta" and a.get("property", "").lower() == "og:url":
            self.og_url = a.get("content", "").strip()


def html_files(root):
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        out += [os.path.join(d, f) for f in files if f.lower().endswith((".html", ".htm"))]
    return sorted(out)


def rel(root, p):
    return os.path.relpath(p, root).replace(os.sep, "/")


def resolve_local(root, page, ref):
    """Return the filesystem path a local ref points at, or None to skip."""
    ref = ref.strip()
    if not ref or ref.startswith("#") or ref.lower().startswith(SKIP_SCHEMES):
        return None
    path = urllib.parse.unquote(re.split(r"[?#]", ref, maxsplit=1)[0])
    if not path:
        return None
    base = root if path.startswith("/") else os.path.dirname(page)
    full = os.path.normpath(os.path.join(base, path.lstrip("/") if path.startswith("/") else path))
    return full


def exists(full):
    if os.path.isdir(full):
        return os.path.isfile(os.path.join(full, "index.html"))
    return os.path.isfile(full)


def url_to_path(root, url):
    u = urllib.parse.urlparse(url.strip())
    p = urllib.parse.unquote(u.path)
    full = os.path.normpath(os.path.join(root, p.lstrip("/")))
    if p.endswith("/") or p == "":
        full = os.path.join(full, "index.html")
    return full


def check(root):
    fails = []

    def fail(rule, where, msg):
        fails.append((rule, where, msg))

    for page in html_files(root):
        name = rel(root, page)
        try:
            with open(page, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as e:
            fail("LOCAL_REF", name, "cannot read file: %s" % e)
            continue
        p = Page()
        p.feed(text)
        in_projects = name.startswith("projects/")

        seen = set()
        for tag, attr, val in p.refs:
            full = resolve_local(root, page, val)
            if full is None or (tag, val) in seen:
                continue
            seen.add((tag, val))
            if not exists(full):
                fail("LOCAL_REF", name, "<%s %s=\"%s\"> not found" % (tag, attr, val))

        for line, title in p.iframes:
            if not title:
                fail("IFRAME_TITLE", "%s:%d" % (name, line), "<iframe> has no title")

        if not in_projects:
            for bad in FORBIDDEN:
                if bad in text:
                    fail("FORBIDDEN", name, "contains '%s' (%d times)" % (bad, text.count(bad)))
            for label, val in (("canonical", p.canonical), ("og:url", p.og_url)):
                if val is not None and not (val == SITE or val.startswith(SITE + "/")):
                    fail("CANONICAL", name, "%s is '%s', expected %s/..." % (label, val, SITE))
            if name == "index.html" and p.canonical is None:
                fail("CANONICAL", name, "missing <link rel=\"canonical\">")

        for src in p.scripts:
            if not re.match(r"(https?:)?//", src):
                continue
            if RANGE_PIN.search(src) or re.search(r"/latest/", src) or not EXACT_VERSION.search(src):
                fail("CDN_VERSION", name, "script not pinned to an exact version: %s" % src)

    sm = os.path.join(root, "sitemap.xml")
    sitemap_ok = os.path.isfile(sm)
    if not sitemap_ok:
        fail("SITEMAP", "sitemap.xml", "file missing")
    else:
        try:
            tree = ET.parse(sm)
            locs = [e.text.strip() for e in tree.iter() if e.tag.endswith("}loc") or e.tag == "loc"]
            if not locs:
                fail("SITEMAP", "sitemap.xml", "no <loc> entries")
            for loc in locs:
                if not loc.startswith(SITE):
                    fail("SITEMAP", "sitemap.xml", "<loc> not on %s: %s" % (SITE, loc))
                elif not os.path.isfile(url_to_path(root, loc)):
                    fail("SITEMAP", "sitemap.xml", "<loc> has no file: %s" % loc)
        except ET.ParseError as e:
            fail("SITEMAP", "sitemap.xml", "invalid XML: %s" % e)

    rb = os.path.join(root, "robots.txt")
    if not os.path.isfile(rb):
        fail("ROBOTS", "robots.txt", "file missing")
    else:
        with open(rb, encoding="utf-8", errors="replace") as fh:
            if not re.search(r"^\s*sitemap:\s*\S*sitemap\.xml", fh.read(), re.I | re.M):
                fail("ROBOTS", "robots.txt", "no 'Sitemap: .../sitemap.xml' line")
    return fails


def report(fails):
    if not fails:
        print("check_site: OK (all rules pass)")
        return 0
    print("check_site: %d failure(s)" % len(fails))
    for rule in sorted({f[0] for f in fails}):
        print("\n[%s]" % rule)
        for r, where, msg in fails:
            if r == rule:
                print("  - %s: %s" % (where, msg))
    return 1


# ---------------------------------------------------------------- self test
CLEAN = {
    "index.html": ('<html><head><link rel="canonical" href="https://goaiarchitect.com/">'
                   '<meta property="og:url" content="https://goaiarchitect.com/">'
                   '<script src="https://cdn.plot.ly/plotly-3.5.0.min.js"></script></head>'
                   '<body><a href="about.html#x">a</a><a href="https://example.com">e</a>'
                   '<img src="img/a.png"><iframe src="c/x.html" title="Chart"></iframe></body></html>'),
    "about.html": "<html><body><a href='/'>home</a></body></html>",
    "c/x.html": "<html><body>chart</body></html>",
    "img/a.png": "x",
    "projects/p/index.html": "<html><body>localhost ok here</body></html>",
    "sitemap.xml": ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    '<url><loc>https://goaiarchitect.com/</loc></url>'
                    '<url><loc>https://goaiarchitect.com/about.html</loc></url></urlset>'),
    "robots.txt": "User-agent: *\nAllow: /\nSitemap: https://goaiarchitect.com/sitemap.xml\n",
}

BREAKS = {  # rule -> {file: new content}
    "LOCAL_REF": {"about.html": '<a href="nope.html">x</a>'},
    "IFRAME_TITLE": {"about.html": '<iframe src="c/x.html"></iframe>'},
    "FORBIDDEN": {"about.html": '<a href="https://goaiarchitect.io/">x</a> http://localhost:3000'},
    "CDN_VERSION": {"about.html": '<script src="https://cdn.jsdelivr.net/npm/foo@latest/a.js"></script>'
                                  '<script src="https://cdn.jsdelivr.net/npm/bar@3/a.js"></script>'},
    "CANONICAL": {"about.html": '<link rel="canonical" href="https://gosidehustlesisi.github.io/about.html">'},
    "SITEMAP": {"sitemap.xml": CLEAN["sitemap.xml"].replace("about.html", "missing.html")},
    "ROBOTS": {"robots.txt": "User-agent: *\nAllow: /\n"},
}


def write_tree(root, files):
    for name, content in files.items():
        p = os.path.join(root, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)


def selftest():
    ok = True
    tmp = tempfile.mkdtemp(prefix="check_site_")
    try:
        clean = os.path.join(tmp, "clean")
        write_tree(clean, CLEAN)
        got = check(clean)
        print("clean fixture:", "PASS" if not got else "FAIL %r" % got)
        ok &= not got
        # extra clean-side assertions: rule exclusions behave
        for rule, change in BREAKS.items():
            d = os.path.join(tmp, rule)
            write_tree(d, CLEAN)
            write_tree(d, change)
            rules = {f[0] for f in check(d)}
            hit = rule in rules and rules == {rule}
            print("break %-12s: %s (got %s)" % (rule, "PASS" if hit else "FAIL", sorted(rules)))
            ok &= hit
        d = os.path.join(tmp, "missing_sitemap")
        write_tree(d, CLEAN)
        os.remove(os.path.join(d, "sitemap.xml"))
        r = {f[0] for f in check(d)}
        print("break %-12s: %s" % ("SITEMAP(gone)", "PASS" if r == {"SITEMAP"} else "FAIL %s" % r))
        ok &= r == {"SITEMAP"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    if "--root" in argv:
        i = argv.index("--root")
        if i + 1 >= len(argv):
            print(__doc__)
            return 2
        root = argv[i + 1]
    elif len(argv) > 1:
        print(__doc__)
        return 2
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print("not a directory: %s" % root)
        return 2
    return report(check(root))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
