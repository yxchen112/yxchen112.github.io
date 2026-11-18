"""Minimal two-page theme (Home + Publications) in a plain jemdoc-like style.

Called by build.py when site.theme == "simple". Reads the same cv-data.json.
Writes index.html, publications.html (and uses simple.css).
"""
import html
import os

E = html.escape


def _link(label, url):
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (E(url, quote=True), E(label))


def _authors(text, me):
    out = E(text)
    for m in me:
        out = out.replace(E(m), "<b>%s</b>" % E(m))
    return out


def _page(d, title, current, body):
    menu = []
    for href, label in (("index.html", "Home"), ("publications.html", "Publications")):
        cls = ' class="current"' if href == current else ""
        menu.append('<div class="menu-item"><a href="%s"%s>%s</a></div>' % (href, cls, label))
    cv = (d.get("site") or {}).get("cv_file", "")
    if cv:
        menu.append('<div class="menu-item"><a href="%s" target="_blank">CV</a></div>' % E(cv, quote=True))
    icon_src = (d.get("simple") or {}).get("icon", "")
    icon = '<img src="%s" alt="">' % E(icon_src, quote=True) if icon_src else ""
    favicon = '<link rel="icon" href="%s">' % E(icon_src, quote=True) if icon_src else ""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="simple.css">
{favicon}
</head>
<body>
<header class="topbar">
  <a class="brand" href="index.html"><span class="brand-icon">{icon}</span><span>Homepage</span></a>
  <button class="menu-btn" aria-label="Menu" onclick="document.body.classList.toggle('menu-open')">&#9776;</button>
</header>
<div class="layout">
  <nav class="side">
    <div class="menu-category">Main</div>
    {menu}
  </nav>
  <main class="content">
{body}
    <footer>Last updated {updated}.</footer>
  </main>
</div>
</body>
</html>
""".format(title=E(title), desc=E((d.get("bio") or {}).get("short", "")), icon=icon, favicon=favicon,
           menu="\n    ".join(menu), body=body, updated=E(d.get("updated", "")))


def build_home(d):
    s = d.get("simple") or {}
    links = d.get("links") or {}
    parts = ['<div class="toptitle"><h1>%s</h1></div>' % E(d["name"])]

    info = []
    for line in s.get("info_lines", []):
        if line.get("url"):
            info.append(_link(line["text"], line["url"]))
        else:
            info.append(E(line["text"]))
    if d.get("email"):
        info.append('<b>E-mail</b>: <a href="mailto:%s">%s</a>' % (E(d["email"], quote=True), E(d["email"])))
    btns = []
    for key, label in (("scholar", "Google Scholar"), ("github", "GitHub"), ("orcid", "ORCID")):
        if links.get(key):
            btns.append("[%s]" % _link(label, links[key]))
    cv = (d.get("site") or {}).get("cv_file", "")
    if cv:
        btns.append('[<a href="%s" target="_blank">CV</a>]' % E(cv, quote=True))
    if btns:
        info.append(" ".join(btns))
    photo = (d.get("site") or {}).get("photo", "")
    parts.append('<div class="intro">%s<div class="intro-text"><p>%s</p></div></div>' % (
        '<img class="avatar" src="%s" alt="%s">' % (E(photo, quote=True), E(d["name"])) if photo else "",
        "<br>\n".join(info)))

    parts.append("<h2>About me</h2>")
    for para in s.get("about", []):
        parts.append("<p>%s</p>" % para)  # trusted, may contain links

    if s.get("interests"):
        parts.append('<p class="label">Research Interests</p><ul class="plain">%s</ul>' %
                     "".join("<li>%s</li>" % E(x) for x in s["interests"]))

    if s.get("news"):
        parts.append("<h2>News</h2><ul class=\"news\">%s</ul>" % "".join(
            '<li><span class="date">%s</span> %s</li>' % (E(n["date"]), n["text"]) for n in s["news"]))

    if d.get("education"):
        parts.append("<h2>Education</h2><ul class=\"plain\">%s</ul>" % "".join(
            "<li><b>%s</b>, %s, %s%s</li>" % (E(e["degree"]), E(e["institution"]), E(e["year"]),
                                              (" &middot; " + E(e["note"])) if e.get("note") else "")
            for e in d["education"]))

    if d.get("teaching"):
        parts.append("<h2>Research Experience</h2><ul class=\"plain\">%s</ul>" % "".join(
            "<li>%s <span class=\"muted\">(%s)</span></li>" % (E(t["course"]), E(t["terms"])) for t in d["teaching"]))

    if d.get("media"):
        parts.append("<h2>Talks</h2><ul class=\"plain\">%s</ul>" % "".join(
            "<li>%s. <i>%s</i>, %s.</li>" % (E(m["headline"]), E(m["outlet"]), E(m["date"])) for m in d["media"]))

    if d.get("advising"):
        parts.append("<h2>Honors &amp; Awards</h2><ul class=\"plain\">%s</ul>" % "".join(
            "<li>%s%s, %s</li>" % (E(a["name"]), (", " + E(a["detail"])) if a.get("detail") else "", E(a["note"]))
            for a in d["advising"]))

    return _page(d, "%s - Homepage" % d["name"], "index.html", "\n".join(parts))


def build_pubs(d):
    me = (d.get("simple") or {}).get("my_name_variants", ["Y. Chen"])
    groups = (("Preprints", "working_paper"), ("Journal &amp; Conference Papers", "peer_reviewed"),
              ("Under Review", "under_revision"), ("In Progress", "in_progress"))
    parts = ['<div class="toptitle"><h1>Publications</h1></div>']
    if (d.get("links") or {}).get("scholar"):
        parts.append("<p>See also my %s.</p>" % _link("Google Scholar profile", d["links"]["scholar"]))
    for label, t in groups:
        items = [p for p in d.get("publications", []) if p.get("type") == t]
        if not items:
            continue
        lis = []
        for p in items:
            venue = p.get("venue") or p.get("note") or ""
            extra = []
            for l in p.get("links", []):
                extra.append("[%s]" % _link(l["label"], l["url"]))
            tag = (' <span class="award">%s</span>' % E(p["tag"])) if p.get("tag") and p["tag"] != "First author" else ""
            lis.append("<li>%s<br>%s<br><i>%s</i> %s.%s%s</li>" % (
                E(p["title"]), _authors(p["authors"], me), E(venue), E(p.get("year") or p.get("marker", "")), tag,
                ("<br>" + " ".join(extra)) if extra else ""))
        parts.append("<h2>%s</h2><ul class=\"pubs\">%s</ul>" % (label, "".join(lis)))
    return _page(d, "%s - Publications" % d["name"], "publications.html", "\n".join(parts))


def build_simple(raw, out):
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_home(raw))
    with open(os.path.join(out, "publications.html"), "w", encoding="utf-8") as fh:
        fh.write(build_pubs(raw))
