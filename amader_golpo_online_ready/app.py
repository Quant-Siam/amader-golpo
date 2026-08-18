import os, uuid
from datetime import datetime
from flask import Flask, request, redirect, url_for, session, render_template_string, flash
from werkzeug.security import check_password_hash, generate_password_hash
from supabase import create_client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-render")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET = os.environ.get("SUPABASE_BUCKET", "love-photos")
ADMIN_USER = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASS_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH",
    generate_password_hash("ChaduSiam")
)

sb = create_client(SUPABASE_URL, SUPABASE_KEY)


def admin_ok():
    return session.get("admin") is True


def rows(table, order="id", ascending=False):
    q = sb.table(table).select("*").order(order, desc=not ascending)
    return q.execute().data or []


def setting(key, default=""):
    data = sb.table("settings").select("value").eq("key", key).limit(1).execute().data
    return data[0]["value"] if data else default


def set_setting(key, value):
    sb.table("settings").upsert({"key": key, "value": value}).execute()


@app.template_filter("pretty_date")
def pretty_date(v):
    if not v:
        return ""
    try:
        d = datetime.strptime(v, "%Y-%m-%d")
        months = ["","জানুয়ারি","ফেব্রুয়ারি","মার্চ","এপ্রিল","মে","জুন",
                  "জুলাই","আগস্ট","সেপ্টেম্বর","অক্টোবর","নভেম্বর","ডিসেম্বর"]
        return f"{d.day} {months[d.month]} {d.year}"
    except Exception:
        return v


HOME = r"""
<!doctype html><html lang="bn"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>আমাদের গল্প ❤️</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root{--bg:#fff8fb;--ink:#351e2b;--muted:#856c79;--rose:#d84f7b;--line:#efd9e3;--shadow:0 18px 55px #5d263c1c}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 8% 8%,#ffeaf2,transparent 28%),radial-gradient(circle at 92% 30%,#ffeaf0,transparent 25%),var(--bg);color:var(--ink);font-family:'Hind Siliguri',sans-serif}a{text-decoration:none;color:inherit}
nav{max-width:1180px;margin:auto;padding:24px;display:flex;justify-content:space-between}.logo{font-weight:700;font-size:1.35rem}.links{display:flex;gap:20px;color:var(--muted)}.links a:hover{color:var(--rose)}
.hero{min-height:92vh;background:linear-gradient(135deg,#ffffffdd,#ffe2edc7);position:relative}.hero:after{content:"";position:absolute;width:500px;height:500px;right:-160px;bottom:-190px;border-radius:50%;background:#fff;opacity:.65}.hero-content{position:relative;z-index:2;text-align:center;max-width:900px;margin:16vh auto 0;padding:0 20px}.eyebrow{color:var(--rose);font-weight:700;letter-spacing:.12em;font-size:.78rem}.hero h1{font-family:'Playfair Display',serif;font-size:clamp(4rem,11vw,8.5rem);line-height:.95;margin:18px 0}.hero p{color:var(--muted);font-size:1.2rem;max-width:650px;margin:0 auto 30px}.btn{display:inline-block;padding:13px 22px;border-radius:999px;background:var(--rose);color:white;box-shadow:0 12px 28px #d84f7b40}
.section{max-width:1180px;margin:auto;padding:90px 24px}.title{display:flex;gap:20px;margin-bottom:40px}.title>span{color:var(--rose);font-weight:700}.title h2{font-family:'Playfair Display',serif;font-size:3rem;margin:0}.title p{color:var(--muted);margin:5px 0}.card{background:#fffffff0;border:1px solid var(--line);box-shadow:var(--shadow);border-radius:25px;padding:28px}.story{font-size:1.18rem;line-height:1.9;white-space:pre-wrap}
.cube-area{height:460px;display:grid;place-items:center;perspective:1100px;cursor:grab;touch-action:none}.cube-area:active{cursor:grabbing}.cube{width:270px;height:270px;position:relative;transform-style:preserve-3d;transform:rotateX(-14deg) rotateY(28deg)}.face{position:absolute;width:270px;height:270px;overflow:hidden;border:2px solid white;background:#f8d8e4;backface-visibility:hidden}.face img{width:100%;height:100%;object-fit:cover}.front{transform:translateZ(135px)}.back{transform:rotateY(180deg) translateZ(135px)}.right{transform:rotateY(90deg) translateZ(135px)}.left{transform:rotateY(-90deg) translateZ(135px)}.top{transform:rotateX(90deg) translateZ(135px)}.bottom{transform:rotateX(-90deg) translateZ(135px)}
.center{text-align:center}.dots{text-align:center}.dot{width:9px;height:9px;border:0;border-radius:50%;background:#e2bdcb;margin:4px}.dot.active{background:var(--rose);transform:scale(1.3)}
.wall{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.photo{padding:0;overflow:hidden}.photo img{width:100%;aspect-ratio:1;object-fit:cover}.photo div{padding:17px}.date,.label{color:var(--rose);font-weight:700;font-size:.84rem}.muted{color:var(--muted);line-height:1.7}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}.promise:before{content:'“';float:right;font:5rem Georgia;color:#f6c5d5}.count{font-weight:700;margin:14px 0}
footer{text-align:center;padding:55px;color:var(--muted);border-top:1px solid var(--line)}
@media(max-width:800px){.links a{display:none}.section{padding:65px 18px}.title h2{font-size:2.25rem}.wall,.grid{grid-template-columns:1fr}.cube{width:220px;height:220px}.face{width:220px;height:220px}.front{transform:translateZ(110px)}.back{transform:rotateY(180deg) translateZ(110px)}.right{transform:rotateY(90deg) translateZ(110px)}.left{transform:rotateY(-90deg) translateZ(110px)}.top{transform:rotateX(90deg) translateZ(110px)}.bottom{transform:rotateX(-90deg) translateZ(110px)}}
</style></head><body>
<header class="hero"><nav><div class="logo">আমাদের গল্প ❤️</div><div class="links"><a href="#story">গল্প</a><a href="#best">Best Photos</a><a href="#wall">Photo Wall</a><a href="#oviman">অভিমান</a><a href="#promise">Promise</a><a href="#meetup">Meetup Date</a></div></nav>
<div class="hero-content"><div class="eyebrow">তুমি + আমি = আমাদের গল্প</div><h1>আমাদের গল্প</h1><p>ছোট ছোট মুহূর্ত, কিছু অভিমান, অনেক ভালোবাসা—সবকিছু এক জায়গায়।</p><a class="btn" href="#best">আমাদের Best Photos ✨</a></div></header>

<section id="story" class="section"><div class="title"><span>01</span><div><h2>আমাদের গল্প</h2><p>যে গল্পটা শুধু আমাদের।</p></div></div><div class="card story">{{ story }}</div></section>

<section id="best" class="section"><div class="title"><span>02</span><div><h2>Our Best Photos</h2><p>Admin থেকে select করা প্রিয় ছবিগুলো।</p></div></div>
{% if cube %}<div class="cube-area" id="area"><div class="cube" id="cube">
{% for cls in ['front','back','right','left','top','bottom'] %}<div class="face {{cls}}"><img src="{{cube[loop.index0 % cube|length].url}}"></div>{% endfor %}
</div></div><div class="center"><h3 id="ct">{{cube[0].description}}</h3><p class="muted" id="cd">{{cube[0].photo_date|pretty_date}}</p></div><div class="dots">{% for p in cube %}<button class="dot {% if loop.first %}active{% endif %}" onclick="pick({{loop.index0}})"></button>{% endfor %}</div>
{% else %}<div class="card center"><h3>এখনো Best Photo যোগ করা হয়নি ❤️</h3></div>{% endif %}</section>

<section id="wall" class="section"><div class="title"><span>03</span><div><h2>Our Photo Wall</h2><p>আমাদের সব ছবি—তারিখ ও description সহ।</p></div></div>
{% if photos %}<div class="wall">{% for p in photos %}<article class="card photo"><img src="{{p.url}}" alt=""><div><div class="date">{{p.photo_date|pretty_date}}</div><h3>{{p.description}}</h3>{% if p.is_cube %}<small class="date">⭐ Best Photo</small>{% endif %}</div></article>{% endfor %}</div>{% else %}<div class="card center">এখনো কোনো ছবি নেই 📸</div>{% endif %}</section>

<section id="oviman" class="section"><div class="title"><span>04</span><div><h2>অভিমান</h2><p>অভিমান থাকবে, কিন্তু দূরত্ব নয়।</p></div></div><div class="grid">
{% for x in oviman %}<article class="card"><div class="date">{{x.oviman_date|pretty_date}}</div><h3>💭 অভিমানের কারণ</h3><p class="muted">{{x.reason}}</p><div class="label">অভিমান ভাঙানোর উপায়</div><p class="muted">{{x.solution}}</p></article>{% else %}<div class="card">এখনো কোনো অভিমান জমা হয়নি ❤️</div>{% endfor %}</div></section>

<section id="promise" class="section"><div class="title"><span>05</span><div><h2>Our Promises</h2><p>আমাদের একে অপরকে দেওয়া প্রতিশ্রুতি।</p></div></div><div class="grid">
{% for p in promises %}<article class="card promise"><div class="label">❤️ Promise</div><h3>{{p.promise_text}}</h3>{% if p.promise_date %}<div class="date">{{p.promise_date|pretty_date}}</div>{% endif %}</article>{% else %}<div class="card">আমাদের Promise এখনো লেখা হয়নি ❤️</div>{% endfor %}</div></section>

<section id="meetup" class="section"><div class="title"><span>06</span><div><h2>Meetup Date</h2><p>কখন দেখা হবে, কোথায় ঘুরবো আর কী খাবো।</p></div></div><div class="grid">
{% for m in meetups %}<article class="card"><div class="label">📅 Meetup Date</div><h3>{{m.meetup_date|pretty_date}}</h3><div class="count countdown" data-date="{{m.meetup_date}}"></div><div class="label">📍 কোথায় ঘুরবো</div><ul class="muted">{% for x in m.places.splitlines() %}{% if x.strip() %}<li>{{x}}</li>{% endif %}{% endfor %}</ul><div class="label">🍜 কী খাবো</div><ul class="muted">{% for x in m.foods.splitlines() %}{% if x.strip() %}<li>{{x}}</li>{% endif %}{% endfor %}</ul></article>{% else %}<div class="card">এখনো কোনো Meetup Date ঠিক হয়নি 🌸</div>{% endfor %}</div></section>
<footer>আমাদের গল্প • শুধু আমাদের জন্য ❤️</footer>
<script>
const cp={{cube|tojson}}, cube=document.getElementById('cube'), area=document.getElementById('area'); let ci=0,rx=-14,ry=28;
function pick(i){ci=i;let p=cp[i];document.querySelectorAll('.face img').forEach(x=>x.src=p.url);document.getElementById('ct').textContent=p.description;document.getElementById('cd').textContent=p.photo_date;document.querySelectorAll('.dot').forEach((x,j)=>x.classList.toggle('active',j===i))}
if(area){let down=false,lx=0,ly=0;area.onpointerdown=e=>{down=true;lx=e.clientX;ly=e.clientY;area.setPointerCapture(e.pointerId)};area.onpointermove=e=>{if(!down)return;ry+=(e.clientX-lx)*.55;rx-=(e.clientY-ly)*.55;lx=e.clientX;ly=e.clientY;cube.style.transform=`rotateX(${rx}deg) rotateY(${ry}deg)`};area.onpointerup=()=>down=false;area.onpointercancel=()=>down=false}
function countdown(){document.querySelectorAll('.countdown').forEach(e=>{let d=new Date(e.dataset.date+'T00:00:00')-new Date();if(d<=0)e.textContent='আজ আমাদের Meetup Date ❤️';else e.textContent=`${Math.floor(d/86400000)} দিন ${Math.floor(d%86400000/3600000)} ঘণ্টা ${Math.floor(d%3600000/60000)} মিনিট বাকি ❤️`})} countdown();setInterval(countdown,60000);
</script></body></html>
"""


ADMIN = r"""
<!doctype html><html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin — আমাদের গল্প</title><style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
*{box-sizing:border-box}body{margin:0;background:#fff7fa;color:#351e2b;font-family:'Hind Siliguri',sans-serif}.wrap{max-width:1100px;margin:auto;padding:30px 20px 70px}.top{display:flex;justify-content:space-between;gap:15px;align-items:center}.panel{background:white;border:1px solid #efd9e3;border-radius:22px;padding:25px;margin:20px 0;box-shadow:0 15px 45px #5d263c12}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}.tab,button,.btn{border:0;background:#d84f7b;color:white;padding:10px 16px;border-radius:999px;cursor:pointer;font:inherit;text-decoration:none;display:inline-block}.tab{background:#ffe8f0;color:#704e5d}.tab.active{background:#d84f7b;color:white}.tabcontent{display:none}.tabcontent.active{display:block}label{display:block;font-weight:600;margin:14px 0}input,textarea{width:100%;margin-top:6px;padding:11px;border:1px solid #e9d2dc;border-radius:11px;font:inherit}textarea{min-height:110px}.item{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:13px;margin:10px 0;background:#fff9fb;border:1px solid #efd9e3;border-radius:14px}.thumb{width:70px;height:70px;object-fit:cover;border-radius:10px}.itemmain{display:flex;gap:12px;align-items:center}.danger{background:#ffe0e9;color:#9e244a}.green{background:#e5f8ec;color:#237642}.muted{color:#856c79}.flash{padding:12px;background:#e6f7ed;color:#226d3a;border-radius:10px;margin:10px 0}.login{max-width:430px;margin:15vh auto}.actions{display:flex;gap:7px;flex-wrap:wrap}@media(max-width:700px){.item{flex-direction:column;align-items:flex-start}}
</style></head><body><div class="wrap">
{% if not auth %}<div class="panel login"><h1>Admin Login ❤️</h1>{% with ms=get_flashed_messages() %}{% for m in ms %}<div class="flash">{{m}}</div>{% endfor %}{% endwith %}<form method="post"><label>Username<input name="username" required></label><label>Password<input type="password" name="password" required></label><button>Login</button></form><p><a href="/">← Website</a></p></div>
{% else %}
<div class="top"><div><h1>আমাদের গল্প — Admin</h1><span class="muted">Private control panel</span></div><div class="actions"><a class="btn" href="/">Website</a><a class="btn danger" href="/logout">Logout</a></div></div>
{% with ms=get_flashed_messages() %}{% for m in ms %}<div class="flash">{{m}}</div>{% endfor %}{% endwith %}
<div class="panel"><div class="tabs"><button class="tab active" onclick="tab('story',this)">গল্প</button><button class="tab" onclick="tab('photos',this)">ছবি</button><button class="tab" onclick="tab('oviman',this)">অভিমান</button><button class="tab" onclick="tab('promise',this)">Promise</button><button class="tab" onclick="tab('meetup',this)">Meetup Date</button></div>

<div id="story" class="tabcontent active"><h2>আমাদের গল্প</h2><form method="post" action="/admin/story"><textarea name="story" required>{{story}}</textarea><br><button>Save Story ❤️</button></form></div>

<div id="photos" class="tabcontent"><h2>Photos</h2><form method="post" action="/admin/photos/add" enctype="multipart/form-data"><label>ছবি<input type="file" name="photo" accept="image/*" required></label><label>Description<input name="description" required></label><label>তারিখ<input type="date" name="photo_date" required></label><button>Upload 📸</button></form><hr>
{% for p in photos %}<div class="item"><div class="itemmain"><img class="thumb" src="{{p.url}}"><div><b>{{p.description}}</b><br><span class="muted">{{p.photo_date|pretty_date}}</span><br>{% if p.is_cube %}<b style="color:#d84f7b">⭐ Cube-এ আছে</b>{% endif %}</div></div><div class="actions">{% if p.is_cube %}<form method="post" action="/admin/photos/{{p.id}}/cube"><button class="tab">Remove from Cube</button></form>{% else %}<form method="post" action="/admin/photos/{{p.id}}/cube"><button class="green">Make Best Photo</button></form>{% endif %}<form method="post" action="/admin/photos/{{p.id}}/delete" onsubmit="return confirm('Delete করবে?')"><button class="danger">Delete</button></form></div></div>{% endfor %}</div>

<div id="oviman" class="tabcontent"><h2>অভিমান</h2><form method="post" action="/admin/oviman/add"><label>তারিখ<input type="date" name="oviman_date" required></label><label>কারণ<textarea name="reason" required></textarea></label><label>ভাঙানোর উপায়<textarea name="solution" required></textarea></label><button>Save 💭</button></form>{% for x in oviman %}<div class="item"><div><b>{{x.oviman_date|pretty_date}}</b><br><span class="muted">{{x.reason}}</span></div><form method="post" action="/admin/oviman/{{x.id}}/delete"><button class="danger">Delete</button></form></div>{% endfor %}</div>

<div id="promise" class="tabcontent"><h2>Our Promises ❤️</h2><form method="post" action="/admin/promise/add"><label>Promise<textarea name="promise_text" required></textarea></label><label>Date — optional<input type="date" name="promise_date"></label><button>Save Promise</button></form>{% for p in promises %}<div class="item"><div><b>{{p.promise_text}}</b>{% if p.promise_date %}<br><span class="muted">{{p.promise_date|pretty_date}}</span>{% endif %}</div><form method="post" action="/admin/promise/{{p.id}}/delete"><button class="danger">Delete</button></form></div>{% endfor %}</div>

<div id="meetup" class="tabcontent"><h2>Meetup Date 📅</h2><form method="post" action="/admin/meetup/add"><label>Date<input type="date" name="meetup_date" required></label><label>কোথায় ঘুরবো<textarea name="places" placeholder="এক লাইনে একটি জায়গা" required></textarea></label><label>কী খাবো<textarea name="foods" placeholder="এক লাইনে একটি খাবার" required></textarea></label><button>Save Meetup</button></form>{% for m in meetups %}<div class="item"><div><b>{{m.meetup_date|pretty_date}}</b><br><span class="muted">{{m.places.splitlines()[0] if m.places else ''}}</span></div><form method="post" action="/admin/meetup/{{m.id}}/delete"><button class="danger">Delete</button></form></div>{% endfor %}</div>

</div>{% endif %}</div><script>function tab(id,b){document.querySelectorAll('.tabcontent').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');b.classList.add('active')}</script></body></html>
"""


def prepare(items, image=False):
    out = []
    for x in items:
        x = dict(x)
        if image:
            x["url"] = sb.storage.from_(BUCKET).get_public_url(x["storage_path"])
        out.append(x)
    return out


@app.get("/")
def home():
    photos = prepare(rows("photos", "photo_date"))
    cube = [p for p in photos if p["is_cube"]]
    return render_template_string(
        HOME,
        story=setting("story", "এখানে আমাদের গল্প লিখে রাখো ❤️"),
        photos=photos,
        cube=cube,
        oviman=rows("oviman", "oviman_date"),
        promises=rows("promises", "id"),
        meetups=rows("meetups", "meetup_date", True)
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == ADMIN_USER and check_password_hash(ADMIN_PASS_HASH, p):
            session["admin"] = True
            return redirect("/admin")
        flash("Username অথবা password ভুল।")
    if not admin_ok():
        return render_template_string(ADMIN, auth=False)
    return render_template_string(
        ADMIN,
        auth=True,
        story=setting("story", ""),
        photos=prepare(rows("photos", "id")),
        oviman=rows("oviman", "oviman_date"),
        promises=rows("promises", "id"),
        meetups=rows("meetups", "meetup_date", True)
    )


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/admin")


@app.post("/admin/story")
def save_story():
    if not admin_ok(): return redirect("/admin")
    set_setting("story", request.form["story"].strip())
    flash("গল্প Save হয়েছে ❤️")
    return redirect("/admin")


@app.post("/admin/photos/add")
def add_photo():
    if not admin_ok(): return redirect("/admin")
    f = request.files.get("photo")
    desc = request.form.get("description", "").strip()
    pdate = request.form.get("photo_date", "").strip()
    if not f or not f.filename or not desc or not pdate:
        flash("ছবি, description ও date সব দিতে হবে।"); return redirect("/admin")
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"jpg","jpeg","png","webp","gif"}:
        flash("শুধু JPG/JPEG/PNG/WEBP/GIF দেওয়া যাবে।"); return redirect("/admin")
    path = f"photos/{uuid.uuid4().hex}.{ext}"
    data = f.read()
    sb.storage.from_(BUCKET).upload(
        path=path, file=data,
        file_options={"content-type": f.mimetype or "image/jpeg", "upsert": "false"}
    )
    sb.table("photos").insert({
        "storage_path": path, "description": desc,
        "photo_date": pdate, "is_cube": False
    }).execute()
    flash("ছবি যোগ হয়েছে 📸")
    return redirect("/admin")


@app.post("/admin/photos/<int:pid>/cube")
def toggle_cube(pid):
    if not admin_ok(): return redirect("/admin")
    r = sb.table("photos").select("is_cube").eq("id", pid).single().execute().data
    if r:
        sb.table("photos").update({"is_cube": not bool(r["is_cube"])}).eq("id", pid).execute()
    return redirect("/admin")


@app.post("/admin/photos/<int:pid>/delete")
def delete_photo(pid):
    if not admin_ok(): return redirect("/admin")
    r = sb.table("photos").select("storage_path").eq("id", pid).single().execute().data
    if r:
        try: sb.storage.from_(BUCKET).remove([r["storage_path"]])
        except Exception: pass
        sb.table("photos").delete().eq("id", pid).execute()
    return redirect("/admin")


@app.post("/admin/oviman/add")
def add_oviman():
    if not admin_ok(): return redirect("/admin")
    sb.table("oviman").insert({
        "oviman_date": request.form["oviman_date"],
        "reason": request.form["reason"].strip(),
        "solution": request.form["solution"].strip()
    }).execute()
    return redirect("/admin")


@app.post("/admin/oviman/<int:i>/delete")
def del_oviman(i):
    if not admin_ok(): return redirect("/admin")
    sb.table("oviman").delete().eq("id", i).execute()
    return redirect("/admin")


@app.post("/admin/promise/add")
def add_promise():
    if not admin_ok(): return redirect("/admin")
    sb.table("promises").insert({
        "promise_text": request.form["promise_text"].strip(),
        "promise_date": request.form.get("promise_date") or None
    }).execute()
    return redirect("/admin")


@app.post("/admin/promise/<int:i>/delete")
def del_promise(i):
    if not admin_ok(): return redirect("/admin")
    sb.table("promises").delete().eq("id", i).execute()
    return redirect("/admin")


@app.post("/admin/meetup/add")
def add_meetup():
    if not admin_ok(): return redirect("/admin")
    sb.table("meetups").insert({
        "meetup_date": request.form["meetup_date"],
        "places": request.form["places"].strip(),
        "foods": request.form["foods"].strip()
    }).execute()
    return redirect("/admin")


@app.post("/admin/meetup/<int:i>/delete")
def del_meetup(i):
    if not admin_ok(): return redirect("/admin")
    sb.table("meetups").delete().eq("id", i).execute()
    return redirect("/admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
