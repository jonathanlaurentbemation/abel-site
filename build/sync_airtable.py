#!/usr/bin/env python3
"""Lit les tables Airtable « Références » et « Actualités » et produit data/references.json,
data/actualites.json + les photos dans dist/refs/.

Variables d'environnement :
  AIRTABLE_TOKEN   jeton personnel Airtable (lecture seule sur la base ABEL Community Management)
  AIRTABLE_BASE    appFk8K08CAKtFvyF (par défaut)
  AIRTABLE_TABLE   tblSaDMHHxFwvxSAs (par défaut, Références)
  AIRTABLE_NEWS    tblQWkEn3inbgjBar (par défaut, Actualités)
Les photos déjà téléchargées sont gardées dans .cache/refs (cache GitHub Actions), seules les nouvelles sont récupérées.
"""
import json, os, re, sys, time, unicodedata, urllib.request, urllib.parse, html
from io import BytesIO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = os.environ.get("AIRTABLE_TOKEN")
BASE = os.environ.get("AIRTABLE_BASE", "appFk8K08CAKtFvyF")
TABLE = os.environ.get("AIRTABLE_TABLE", "tblSaDMHHxFwvxSAs")
NEWS = os.environ.get("AIRTABLE_NEWS", "tblQWkEn3inbgjBar")
CACHE = os.path.join(ROOT, ".cache", "refs")
OUT_IMG = os.path.join(ROOT, "dist", "refs")
MAX = 1600

CAT_SLUG = {"Béton": "beton", "Acier": "acier", "Bois": "bois", "Patrimoine": "patrimoine", "Logements": "logements",
            "Industrie": "industrie", "Équipements collectifs": "equipements-collectifs", "Public": "public", "Privé": "prive"}

def api(params, table=None):
    url = f"https://api.airtable.com/v0/{BASE}/{table or TABLE}?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(30); continue
            raise
    raise RuntimeError("Airtable indisponible")

def fetch_all(table=None):
    recs, offset = [], None
    while True:
        p = {"pageSize": 100, "filterByFormula": "{Publié}", "returnFieldsByFieldId": "false"}
        if offset: p["offset"] = offset
        d = api(p, table)
        recs += d["records"]
        offset = d.get("offset")
        if not offset: return recs

def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", t.lower())[:60] or "reference"

def image(att):
    """Télécharge (avec cache) et redimensionne une pièce jointe ; renvoie l'URL publique /refs/..."""
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = None
    ext = os.path.splitext(att.get("filename") or "")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = {"image/png": ".png", "image/webp": ".webp"}.get(att.get("type"), ".jpg")
    if ext in (".tif", ".tiff"): ext = ".jpg"
    name = att["id"] + ext
    cached = os.path.join(CACHE, name)
    if not os.path.exists(cached):
        os.makedirs(CACHE, exist_ok=True)
        try:
            req = urllib.request.Request(att["url"], headers={"User-Agent": "Mozilla/5.0 (abel-site build)"})
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
        except Exception as e:
            print("photo ignorée :", att.get("url"), e); return None
        im = Image.open(BytesIO(raw)); im = ImageOps.exif_transpose(im)
        if max(im.size) > MAX: im.thumbnail((MAX, MAX), Image.LANCZOS)
        if ext in (".jpg", ".jpeg"): im.convert("RGB").save(cached, "JPEG", quality=84, optimize=True, progressive=True)
        elif ext == ".webp": im.save(cached, "WEBP", quality=84)
        else: im.save(cached, "PNG", optimize=True)
    os.makedirs(OUT_IMG, exist_ok=True)
    dst = os.path.join(OUT_IMG, name)
    if not os.path.exists(dst):
        import shutil; shutil.copy(cached, dst)
    return "/refs/" + name

def para(t):
    return "".join(f"<p>{html.escape(p.strip()).replace(chr(10), '<br>')}</p>" for p in re.split(r"\n\s*\n", t or "") if p.strip())

def description_html(f):
    h = ""
    if f.get("Ville"): h += f"<h4>{html.escape(f['Ville'])}</h4>"
    if f.get("Projet"): h += f"<h5>{html.escape(f['Projet'])}</h5>"
    h += para(f.get("Description", ""))
    lis = []
    for k, lab in (("Maître d'ouvrage", "MO"), ("Architecte", "Architecte"), ("Entreprise", "Entreprise"), ("Budget", "Budget")):
        if f.get(k): lis.append(f"<li>{lab} : {html.escape(f[k])}</li>")
    for l in (f.get("Autres infos") or "").splitlines():
        if l.strip(): lis.append(f"<li>{html.escape(l.strip())}</li>")
    if lis: h += "<ul>" + "".join(lis) + "</ul>"
    return h

def main():
    if not TOKEN:
        sys.exit("AIRTABLE_TOKEN manquant")
    out, seen = [], set()
    for r in fetch_all():
        f = r["fields"]
        titre = (f.get("Titre") or "").strip()
        if not titre: continue
        slug = (f.get("Slug") or "").strip() or slugify(titre)
        while slug in seen: slug += "-2"
        seen.add(slug)
        vign = f.get("Vignette") or []; gal = f.get("Galerie") or []
        gal_urls = [u for u in (image(a) for a in gal if (a.get("type") or "image").startswith("image")) if u]
        v = image(vign[0]) if vign else (gal_urls[0] if gal_urls else None)
        if not v:
            print("ignorée (aucune photo) :", titre); continue
        out.append(dict(slug=slug, titre=titre, date=f.get("Date") or r["createdTime"][:10],
                        categories=[CAT_SLUG[c] for c in f.get("Catégories", []) if c in CAT_SLUG],
                        vignette=v, galerie=gal_urls or [v], description_html=description_html(f)))
    out.sort(key=lambda x: x["date"], reverse=True)
    json.dump(out, open(os.path.join(ROOT, "data", "references.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(out), "références publiées")

def news():
    """Table Actualités : Texte (texte enrichi, markdown) + Photos en galerie sous le texte."""
    import markdown
    out, seen = [], set()
    for r in fetch_all(NEWS):
        f = r["fields"]
        titre = (f.get("Titre") or "").strip()
        if not titre: continue
        slug = (f.get("Slug") or "").strip() or slugify(titre)
        while slug in seen: slug += "-2"
        seen.add(slug)
        vign = f.get("Vignette") or []
        v = image(vign[0]) if vign else None
        corps = markdown.markdown(f.get("Texte") or "", extensions=["nl2br", "sane_lists"])
        corps = re.sub(r'(?<![("=>])(https?://[^\s<]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', corps)
        photos = [u for u in (image(a) for a in (f.get("Photos") or []) if (a.get("type") or "image").startswith("image")) if u]
        if photos:
            corps += '<div class="gal">' + "".join(f'<a class="gi" href="{u}"><img loading="lazy" src="{u}" alt=""></a>' for u in photos) + "</div>"
        out.append(dict(slug=slug, titre=html.escape(titre, quote=False), date=f.get("Date") or r["createdTime"][:10],
                        vignette=v or (photos[0] if photos else None), contenu_html=corps, publie=True))
    out.sort(key=lambda x: x["date"], reverse=True)
    json.dump(out, open(os.path.join(ROOT, "data", "actualites.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(out), "actualités publiées")

if __name__ == "__main__":
    main()
    news()
