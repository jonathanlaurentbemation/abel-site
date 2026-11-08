#!/usr/bin/env python3
"""Génère le site statique ABEL (dist/) depuis data/*.json.
Usage : python3 build/build.py   (depuis la racine du projet)
Les données references.json / actualites.json sont la future sortie des bases Airtable."""
import json, os, re, html, shutil, random, datetime, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
BASE = "https://www.abel.be"
def _v(f):
    return hashlib.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f), "rb").read()).hexdigest()[:8]
VCSS, VJS = _v("site.css"), _v("site.js")
refs = json.load(open(D("data", "references.json"), encoding="utf-8"))
news = json.load(open(D("data", "actualites.json"), encoding="utf-8"))
pages = json.load(open(D("data", "pages.json"), encoding="utf-8"))
news = [n for n in news if n.get("publie", True)]
esc = html.escape
MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
def fdate(s):
    y, m, d = map(int, s.split("-")); return f"{d} {MOIS[m-1]} {y}"
def strip(t): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()
def short(t, n=160):
    t = html.unescape(strip(t)); return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"
def wp(t):
    """wpautop minimal : lignes -> paragraphes si pas déjà du HTML bloc."""
    if re.search(r"<(p|ul|div|h\d|figure)\b", t): return t
    return "".join(f"<p>{l.strip()}</p>" for l in t.split("\n") if l.strip())

ICONS = {  # Font Awesome 4.7 -> classes
 "fa-thumbs-up":"fa-thumbs-up","fa-calendar":"fa-calendar","fa-eur":"fa-eur","fa-leaf":"fa-leaf","fa-home":"fa-home",
 "fa-fort-awesome":"fa-fort-awesome","fa-handshake-o":"fa-handshake-o","fa-industry":"fa-industry","fa-map":"fa-map",
 "fa-check-square":"fa-check-square"}
CATS = {"beton":"Béton","acier":"Acier","bois":"Bois","patrimoine":"Patrimoine","logements":"Logements","industrie":"Industrie",
        "equipements-collectifs":"Équipements collectifs","public":"Public","prive":"Privé"}

# ---------- gabarit ----------
NAV = [("Home","/"),("Je suis un particulier","/home-particuliers/"),("Je suis architecte","/home-architectes/"),("Je suis professionnel","/home-pro/")]
ANCH = [("Présentation","about"),("Actualités","news"),("Références","references"),("Contact","contact")]

def head(title, desc, path, og_img=None, extra="", body=""):
    url = BASE + path
    og = f'<meta property="og:image" content="{BASE}{og_img}">' if og_img else ""
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:locale" content="fr_BE">{og}
<link rel="icon" href="/wp-content/uploads/2017/02/abel_icon.png"><link rel="apple-touch-icon" href="/wp-content/uploads/2017/02/abel_icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<link rel="stylesheet" href="/assets/site.css?v={VCSS}">{extra}</head><body class="{body}">"""

def header(local=True, prefix="", cur=False):
    p = "" if local else "/"
    items = f'<div class="dd"><a href="/"{" class=\"cur\"" if cur else ""}><span class="t">Home</span></a><div class="sub">' + "".join(f'<a href="{u}">{t}</a>' for t, u in NAV[1:]) + '</div></div>'
    items += "".join(f'<a href="{prefix}#{a}"><span class="t">{t}</span></a>' for t, a in ANCH)
    return f"""<header class="hdr"><div class="top"><div class="wrap">
<span><i class="fa fa-phone"></i> +32 472 23 11 55</span><span><i class="fa fa-envelope"></i> <a href="mailto:info@abel.be">info@abel.be</a></span>
<span class="sp"></span><a class="soc fb" href="https://www.facebook.com/abel.stabilite/" target="_blank" rel="noopener" aria-label="Facebook"><i class="fa fa-facebook"></i></a>
<a class="soc pi" href="https://www.pinterest.com/abelsprl/" target="_blank" rel="noopener" aria-label="Pinterest"><i class="fa fa-pinterest"></i></a>
<a class="btn sm" href="#open-celia">Demander une offre</a></div></div>
<div class="mid"><div class="wrap"><a class="logo" href="/"><img src="/wp-content/uploads/2017/02/abel_web.png" alt="ABEL ingénierie et stabilité" width="234" height="80"></a>
<button class="burger" aria-label="Menu" onclick="document.body.classList.toggle('nav-open')"><i class="fa fa-bars"></i></button>
<nav>{items}</nav></div></div></header>"""

def contact_section():
    return """<section id="contact" class="sec dark"><div class="wrap two">
<div><p class="ic"><i class="fa fa-envelope"></i><a href="mailto:info@abel.be">info@abel.be</a></p>
<p class="ic"><i class="fa fa-phone"></i><a href="tel:+32472231155">+32 472 23 11 55</a></p>
<p class="ic"><i class="fa fa-map-marker"></i>Rue de la Roche 3/B<br>7061 THIEUSIES</p>
<div id="map" class="mapbox" data-lat="50.5147" data-lng="4.0513" role="img" aria-label="Plan d'accès : Rue de la Roche 3/B, 7061 Thieusies"></div></div>
<div><h4>Remplissez notre formulaire de demande de prix</h4><p>Nous y répondrons aussi vite que possible.</p>
<a class="btn" href="#open-celia">Demander une offre</a>
<p class="soc2"><a href="https://www.facebook.com/abel.stabilite/" target="_blank" rel="noopener">Facebook</a> · <a href="https://www.linkedin.com/company/abel-stabilite" target="_blank" rel="noopener">LinkedIn</a></p></div></div></section>"""

def footer():
    return f"""<footer class="sec orange foot"><div class="wrap"><a class="btn white" href="#open-celia">Demander une offre</a>
<p>© Copyright ABEL srl {datetime.date.today().year} · <a href="https://www.facebook.com/abel.stabilite/" target="_blank" rel="noopener">Facebook</a> · <a href="https://www.linkedin.com/company/abel-stabilite" target="_blank" rel="noopener">LinkedIn</a></p></div></footer>
<a href="#" class="totop" aria-label="Retour vers le haut"><i class="fa fa-chevron-up"></i></a>
<aside id="celia" aria-hidden="true"><div class="ch"><span>Célia · Demande de devis</span><button aria-label="Fermer" onclick="closeCelia()">×</button></div><iframe title="Célia" data-src="/chatbot/index.html?embed=1"></iframe></aside>
<script src="/assets/site.js?v={VJS}" defer></script></body></html>"""

def card_ref(r, big=False):
    cats = " ".join(r["categories"])
    return (f'<a class="rc" href="/portfolio/{r["slug"]}/" data-cats="{cats}"><img loading="lazy" src="{r["vignette"]}" alt="{esc(r["titre"])}">'
            f'<span class="ov"><b>{esc(r["titre"])}</b></span></a>')

def card_news(n, date=True):
    img = f'<img loading="lazy" src="{n["vignette"]}" alt="">' if n.get("vignette") else '<div class="noimg"></div>'
    return (f'<article class="nc"><a href="/{n["slug"]}/">{img}</a><div class="nb"><h3><a href="/{n["slug"]}/">{n["titre"]}</a></h3>'
            + (f'<time>{fdate(n["date"])}</time>' if date else '') + f'<p>{esc(short(n["contenu_html"], 140))}</p><a class="more" href="/{n["slug"]}/">Lire la suite</a></div></article>')

def refs_section(cats=None, n=12, sid="references"):
    pool = [r for r in refs if not cats or set(cats) & set(r["categories"])]
    rnd = random.Random(sid + str(cats)); sel = rnd.sample(pool, len(pool))  # toutes, tirage au hasard côté navigateur
    return f"""<section id="{sid}" class="sec orange"><div class="wrap"><p class="ctr"><a class="btn white big" href="#open-celia">Demander une offre</a></p>
<h2 class="ctr">QUELQUES REFERENCES</h2></div>
<div class="fullgrid shuffle" data-n="{n}">{"".join(card_ref(r) for r in sel)}</div>
<div class="wrap"><p class="ctr"><a class="btn light big" href="/allreferences/">Plus de références</a></p></div></section>"""

def news_section():
    return f"""<section id="news" class="sec"><div class="wrap"><h2>Nos dernières actualités</h2>
<div class="news4">{"".join(card_news(n, False) for n in news[:4])}</div>
<p class="ctr"><a class="btn big" href="/news/">Toutes les actualités</a></p>
<p class="ctr socl"><a href="https://www.facebook.com/abel.stabilite" target="_blank" rel="noopener" aria-label="Facebook"><i class="fa fa-facebook"></i></a>
<a href="https://www.linkedin.com/company/abel-stabilite" target="_blank" rel="noopener" aria-label="LinkedIn"><i class="fa fa-linkedin"></i></a></p></div></section>"""

ABOUT_P1 = "ABEL est un bureau d’ingénieurs conseils spécialisé dans la stabilité des constructions et des équipements, quels que soient les matériaux envisagés."
ABOUT_P2 = "Les activités actuelles du bureau touchent toujours aussi bien de nombreuses maisons individuelles que de vastes marchés publics, projets industriels, promotions immobilières ou équipements industriels ou de génie civil."
ABOUT_MORE = ("<p>Créé en 2004 par Jonathan Laurent, ingénieur civil de la Faculté Polytechnique de Mons, le bureau s’est développé au fil des ans. Inscrit dans une tradition familiale liée à la construction, ABEL a repris en 2008 les activités de bureau d’études en stabilité <a href=\"/desmons/\">Desmons</a>, bien connu dans la région Montoise.</p>"
"<p>Le bureau a conservé la confiance d’architectes et d’industriels qui lui ont permis de réaliser des projets de plus en plus ambitieux tant en taille qu’en difficulté et de développer le bureau jusqu’à l’activité actuelle.</p>"
"<p>Attentif aux attentes, nous veillons à accompagner l’architecte, le maître d’ouvrage ou l’entrepreneur dans le développement de son projet en tenant compte de ses contraintes propres et de l’étendue de la mission souhaitée quelle que soit la taille du projet en s’intégrant éventuellement dans des équipes multidisciplinaires.</p>"
"<p>La compréhension complète des tenants et aboutissants structurels d’un projet, l’intérêt pour les calculs détaillés et la mise au point de l’ensemble des détails constructifs sont les valeurs de notre bureau. Ces valeurs partagées permettent au bureau de continuer son partenariat avec des architectes ou maîtres d’ouvrages exigeants qui apprécient le service que notre équipe jeune et motivée peut offrir.</p>")

def about_block(extra_h2=None):
    h = f"<h2>{extra_h2}</h2>" if extra_h2 else ""
    return f'{h}<p>{ABOUT_P1}</p><p>{ABOUT_P2}</p><details class="acc"><summary>En savoir plus</summary>{ABOUT_MORE}</details>'

def iconbox(b, cls=""):
    ic = f'<span class="icc"><i class="fa {b["icon"]}"></i></span>' if b.get("icon") and not b.get("img") else ""
    im = f'<img class="ibimg" loading="lazy" src="{b["img"]}" alt="{esc(b["titre"])}">' if b.get("img") else ""
    return f'<div class="ib {cls}">{ic}{im}<h3>{esc(b["titre"])}</h3>{"".join("<p>"+l.strip()+"</p>" for l in b["texte"].split(chr(10)) if l.strip())}</div>'

def write(path, content):
    f = D("dist", path.strip("/"), "index.html") if not path.endswith(".html") else D("dist", path.strip("/"))
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w", encoding="utf-8").write(content)

def bg(url, ov=None):
    o = f"linear-gradient({ov},{ov})," if ov else ""
    return f'style="background-image:{o}url(\'{url}\')"'

SLIDES = json.load(open(D("data", "slider.json"), encoding="utf-8"))
TITLE = "ABEL sprl – ingénierie et stabilité"
DESC = "ABEL est un bureau d’ingénieurs conseils spécialisé dans la stabilité des constructions et des équipements, à Thieusies (Mons, Hainaut)."

# ---------- accueil ----------
def home():
    p = pages["home-4-2"]; av = p["boites"]
    def slide(i, s):
        lo = False
        im = (f'<img class="fg" src="{s["src"]}" alt="" style="max-width:{s["w"]}px">' if lo else
              f'<img class="cv" src="{s["src"]}" alt="">')
        return (f'<div class="sl{" on" if i==0 else ""}{" lo" if lo else ""}">'
                + (f'<div class="bgb" style="background-image:url(\'{s["src"]}\')"></div>' if lo else "") + im + '</div>')
    slides = "".join(slide(i, s) for i, s in enumerate(SLIDES))
    clients = [("Vous êtes un particulier", "/home-particuliers/", "/wp-content/uploads/2017/02/particuliers.jpg",
      "Vous souhaitez une expertise de votre bien suite à des problèmes de fissuration ou de désordres structurels, vous avez un projet de construction, vous cherchez un ingénieur pour le calcul des fondations, nous pouvons vous aider"),
     ("Vous êtes architecte", "/home-architectes/", "/wp-content/uploads/2017/02/architectes.jpg",
      "Nous proposons à nos partenaires une collaboration étroite, et ce dès la conception et tout au long de l'évolution du projet. Comprendre l'objectif et la philosophie de l'architecte, afin d'apporter les meilleures solutions constructives et techniques, sont nos objectifs."),
     ("Vous êtes professionnel", "/home-pro/", "/wp-content/uploads/2017/02/promoteur.jpg",
      "Que vous soyez promoteur à la recherche d'une équipe de confiance ou entrepreneur ayant une étude stabilité à votre charge, ou encore industriel devant gérer des équipements et leur génie civil, nous avons des solutions à vous proposer")]
    h = head(TITLE, DESC, "/", SLIDES[0]["src"], '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "ProfessionalService", "name": "ABEL sprl", "url": BASE + "/",
        "telephone": "+32472231155", "email": "info@abel.be", "logo": BASE + "/wp-content/uploads/2017/02/abel_web.png",
        "address": {"@type": "PostalAddress", "streetAddress": "Rue de la Roche 3/B", "postalCode": "7061", "addressLocality": "Thieusies", "addressCountry": "BE"},
        "sameAs": ["https://www.facebook.com/abel.stabilite/", "https://www.linkedin.com/company/abel-stabilite", "https://www.pinterest.com/abelsprl/"]},
        ensure_ascii=False) + "</script>", body="hashero")
    body = f"""{header(cur=True)}<main>
<section id="slider" class="slider" aria-label="Photos de projets">{slides}</section>
<section id="about" class="sec orange"><div class="wrap"><h1 class="ctr light">{TITLE}</h1></div></section>
<section id="about2" class="sec parallax" {bg("/wp-content/uploads/2017/02/BG-copy-1.jpg")}><div class="wrap narrow">{about_block()}</div></section>
<section id="avantages" class="parallax dim icosec" {bg("/wp-content/uploads/2017/02/backgroundB.jpg","rgba(30,30,30,.75)")}><div class="wrap grid4 ctrt">{"".join(iconbox(b,"onDark") for b in av if b["titre"])}</div></section>
<section id="typedeclient" class="triple">{"".join(f'<div class="col" {bg(i)}><div class="in"><h2>{t}</h2><p>{d}</p><a class="btn" href="{u}">En savoir plus</a></div></div>' for t,u,i,d in clients)}</section>
{refs_section(None,16)}
{news_section()}
{contact_section()}</main>{footer()}"""
    write("/", h + body)

# ---------- pages publics cibles ----------
def target(slug, path, hero_title, cats, ncards, key, intro_ibs=None):
    p = pages[slug]; hero, mid = p["fonds"][0], p["fonds"][1] if len(p["fonds"]) > 1 else p["fonds"][0]
    ibs = [b for b in p["boites"] if b["titre"]]
    title = f"{hero_title} | ABEL sprl"
    desc = short(" ".join(b["texte"] for b in ibs[:2]), 155)
    group1 = ibs[:3]; group2 = ibs[3:]
    pack = ""
    if slug == "home-particuliers":
        pack = '<section id="packfondation" class="sec"><div class="wrap cta"><div><h2>Découvrez notre pack fondations</h2><p>Ce pack comprend les essais de sol, l\'analyse et le choix des fondations ainsi que les documents d\'exécution.</p></div><a class="btn big" href="/packfondation/">Demandez une offre</a></div></section>'
    g2 = f'<section id="materiaux" class="sec large"><div class="wrap grid3 mat">{"".join(iconbox(b) for b in group2)}</div></section>' if group2 else ""
    body = f"""{head(title, desc, path, hero, body="hashero")}{header(cur=True)}<main>
<section id="slider" class="hero parallax" {bg(hero,"rgba(30,30,30,.75)")}><div class="wrap"><h1>{pages[slug].get('h1') or hero_title}</h1><a class="chev" href="#second" aria-label="Descendre"><i class="fa fa-chevron-down"></i></a></div></section>
<section id="second" class="sec small"><div class="wrap"><p class="ctr h1like">{TITLE}</p></div></section>
<section id="{key}" class="parallax dim icosec" {bg(mid if not group2 else mid,"rgba(30,30,30,.74)")}><div class="wrap grid3 ctrt">{"".join(iconbox(b,"onDark") for b in group1)}</div></section>
{g2}{pack}
{refs_section(cats,ncards)}{news_section()}
<section id="about" class="sec orange"><div class="wrap narrow">{about_block("Qui sommes nous")}</div></section>
{contact_section()}</main>{footer()}"""
    write(path, body)

# ---------- pack fondation ----------
def pack():
    p = pages["packfondation"]; ibs = [b for b in p["boites"] if b["titre"]]
    lead = html.unescape(strip(p["lead"] or ""))
    body = f"""{head("Pack fondation | ABEL sprl", short(lead,155), "/packfondation/", p["fonds"][0])}{header(prefix="/")}<main>
<section class="sec parallax dim pk" {bg(p["fonds"][0],"rgba(10,10,10,.7)")}><div class="wrap">
<h1 class="ctr">Démarrez sur une bonne base.</h1><h4 class="lead">{lead}</h4>
<div class="grid3 chk">{"".join(f'<div class="ib left"><span class="icc sm"><i class="fa fa-check-square"></i></span><h3>{esc(b["titre"][0].upper()+b["titre"][1:])}</h3><p>{b["texte"]}</p></div>' for b in ibs)}</div>
<p class="ctr"><a class="btn big" href="#open-celia">Demandez une offre</a></p></div></section>
{contact_section()}</main>{footer()}"""
    write("/packfondation/", body)

def desmons():
    p = pages["desmons"]; t = p["html"]
    t = re.sub(r"<h1>.*?</h1>", "", t, flags=re.S)
    body = f"""{head("Bureau d'études Desmons | ABEL sprl","Les activités du bureau d'études Desmons sont reprises depuis 2008 par ABEL sprl, sous la gérance de Jonathan Laurent, ingénieur civil.","/desmons/")}{header(prefix="/")}<main>
<section class="sec"><div class="wrap narrow"><h1>Bureau d'études Desmons</h1>{wp(t)}</div></section></main>{footer()}"""
    write("/desmons/", body)

# ---------- toutes les références / actualités / projets / articles ----------
def allrefs():
    cats = sorted({c for r in refs for c in r["categories"]}, key=lambda c: CATS.get(c, c))
    flt = '<button class="on" data-f="">Tout</button>' + "".join(f'<button data-f="{c}">{CATS.get(c,c)}</button>' for c in cats)
    body = f"""{head("Nos références | ABEL sprl","Projets réalisés par ABEL : logements, équipements publics, patrimoine, industrie, béton, acier et bois.","/allreferences/")}{header(prefix="/")}<main>
<section class="sec darkest"><div class="wrap"><h1 class="ctr light">Références</h1><div class="filters">{flt}</div></div><div class="nopad">
<div class="fullgrid shuffle" id="refgrid">{"".join(card_ref(r) for r in refs)}</div></div></section></main>{footer()}"""
    write("/allreferences/", body)

def allnews():
    body = f"""{head("Actualités | ABEL sprl","Les actualités du bureau d'ingénieurs ABEL : chantiers, inaugurations et projets.","/news/")}{header(prefix="/")}<main>
<section class="sec"><div class="wrap"><h1>Actualités</h1><div class="grid4">{"".join(card_news(n) for n in news)}</div></div></section></main>{footer()}"""
    write("/news/", body)

def project(r):
    cats = "".join(f'<span class="tag">{CATS.get(c,c)}</span>' for c in r["categories"])
    gal = "".join(f'<a href="{u}" class="gi"><img loading="lazy" src="{u}" alt="{esc(r["titre"])}"></a>' for u in r["galerie"])
    desc = short(r["description_html"], 155)
    body = f"""{head(r["titre"]+" | ABEL sprl", desc, f"/portfolio/{r['slug']}/", r["vignette"])}{header(prefix="/")}<main>
<section class="sec dark proj"><div class="wrap"><p class="back"><a href="/allreferences/">← Toutes les références</a></p>
<div class="pj"><div class="gal">{gal}</div><div class="pt">{wp(r["description_html"])}<p>{cats}</p></div></div></div></section></main>{footer()}"""
    write(f"/portfolio/{r['slug']}/", body)

def article(n):
    th = f'<img class="hero-img" src="{n["vignette"]}" alt="">' if n.get("vignette") else ""
    body = f"""{head(strip(html.unescape(n["titre"]))+" | ABEL sprl", short(n["contenu_html"],155), f"/{n['slug']}/", n.get("vignette"))}{header(prefix="/")}<main>
<article class="sec"><div class="wrap narrow"><p class="back"><a href="/news/">← Actualités</a></p><h1>{n["titre"]}</h1><time>{fdate(n["date"])}</time>{th}<div class="post">{wp(n["contenu_html"])}</div></div></article></main>{footer()}"""
    write(f"/{n['slug']}/", body)

def notfound():
    body = f"""{head("Page introuvable | ABEL sprl","Page introuvable","/404.html")}{header(prefix="/")}<main><section class="sec"><div class="wrap ctr"><h1>Page introuvable</h1><p>Cette page n'existe plus ou a changé d'adresse.</p><p><a class="btn" href="/">Retour à l'accueil</a></p></div></section></main>{footer()}"""
    write("/404.html", body)

def sitemap(urls):
    t = datetime.date.today().isoformat()
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{t}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    open(D("dist", "sitemap.xml"), "w").write(x)
    open(D("dist", "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

if __name__ == "__main__":
    # on garde les médias, assets et chatbot déjà copiés ; on régénère le HTML
    for d in ("portfolio",): shutil.rmtree(D("dist", d), ignore_errors=True)
    # fichiers fixes (images hors références, chatbot, _headers, _redirects)
    if os.path.isdir(D("static")): shutil.copytree(D("static"), D("dist"), dirs_exist_ok=True)
    os.makedirs(D("dist", "assets"), exist_ok=True)
    for f in ("site.css", "site.js"): shutil.copy(D("build", f), D("dist", "assets", f))
    home()
    target("home-particuliers", "/home-particuliers/", "Démarrez sur une base solide", ["logements"], 12, "particuliers")
    target("home-architectes", "/home-architectes/", "Des études collaboratives et durables", ["prive", "public"], 16, "architectes")
    target("home-pro", "/home-pro/", "Pour la stabilité de tous vos projets", ["industrie", "logements"], 12, "pro")
    pack(); desmons(); allrefs(); allnews(); notfound()
    for r in refs: project(r)
    for n in news: article(n)
    urls = ["/", "/home-particuliers/", "/home-architectes/", "/home-pro/", "/packfondation/", "/desmons/", "/allreferences/", "/news/"] + [f"/portfolio/{r['slug']}/" for r in refs] + [f"/{n['slug']}/" for n in news]
    sitemap(urls)
    print(len(urls), "URL générées")
