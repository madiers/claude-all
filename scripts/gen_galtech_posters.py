#!/usr/bin/env python3
import os, html as H
REPO = "/Users/madiyarismagulov/Library/CloudStorage/GoogleDrive-info@verstack.design/My Drive/Verstack Projects/Marketing/Galtech/claude-all-1"
A = REPO + "/Assets/galtech-posters"
def furl(p):
    import urllib.parse
    return "file://" + urllib.parse.quote(p)
GAL = furl(REPO + "/Assets/galtech-newsletter/galtech-logo.png")

BR = {
 "stormaudio": dict(
   name="StormAudio", accent="#00A6E2", logo=furl(A+"/logos/stormaudio.png"), logoh=46,
   product=furl(A+"/products/storm_stack.jpg"), mode="photo",
   title="REFERENCE-GRADE<br>CINEMA SOUND",
   body="Reference-grade AV processors and amplifiers engineered for the world's most demanding home cinemas. With immersive audio up to Dolby&nbsp;Atmos, DTS:X and Auro-3D across dozens of channels, plus Dirac&nbsp;Live room correction, StormAudio delivers studio-accurate sound for the ultimate private theater.",
   tag="Cinema, engineered without compromise."),
 "lea": dict(
   name="LEA Professional", accent="#009CC2", logo=furl(A+"/logos/lea.png"), logoh=40,
   product=furl(A+"/products/lea_amp.png"), mode="cutout",
   title="SMART, CONNECTED<br>AMPLIFICATION",
   body="Smart, network-connected amplifiers that bring IoT control to commercial and residential installations. With built-in DSP, web-based management and Dante connectivity, LEA's Connect Series simplifies multi-zone audio while delivering clean, reliable power for any space.",
   tag="Smart amplification, cloud connected."),
 "krix": dict(
   name="Krix", accent="#F14320", logo=furl(A+"/logos/krix.png"), logoh=40,
   product=furl(A+"/products/krix_speaker.png"), mode="cutout",
   title="AUSTRALIAN SOUND,<br>CINEMA SOUL",
   body="Australian-made loudspeakers crafted for home cinema and high-fidelity listening since 1974. From in-wall and in-ceiling installation speakers to flagship cinema systems, Krix combines precision engineering with a heritage of powering commercial theatres worldwide.",
   tag="Crafted in Australia since 1974."),
 "nice": dict(
   name="Nice", accent="#1E73C8", logo=furl(A+"/logos/nice.png"), logoh=52,
   product=furl(A+"/products/nice_robus.jpg"), mode="photobg",
   title="AUTOMATION,<br>MADE EFFORTLESS",
   body="Italian-engineered home and building automation — smart gates, motors, access control and integrated control systems. Nice makes everyday living seamless and secure, automating entrances, shading and connected devices for the modern smart home.",
   tag="Seamless, secure, smart living."),
}

CHEV = lambda accent, sw: f'''<svg class="chev" viewBox="0 0 460 640" preserveAspectRatio="none">
<g stroke="{accent}" stroke-width="{sw}" fill="none" stroke-linejoin="miter">
<polyline points="60,30 330,320 60,610"/><polyline points="220,30 490,320 220,610"/></g></svg>'''

BASECSS = '''
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#0a0b0d}
.ff{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif}
.poster{position:relative;overflow:hidden;background:
  radial-gradient(120% 90% at 78% 8%, #1b1f25 0%, #0d0f12 46%, #08090b 100%);}
.tex{position:absolute;inset:0;opacity:.5;background:
  radial-gradient(60% 50% at 80% 12%, rgba(255,255,255,.045), transparent 70%);}
.title{color:#fff;font-weight:800;text-transform:uppercase;letter-spacing:-1px;
  line-height:.93;transform:scaleX(.91);transform-origin:left center}
.eyebrow{color:var(--ac);text-transform:uppercase;font-weight:700}
.body{color:#aab0b8;font-weight:400}
.rule{background:var(--ac);height:5px;border:0}
.chev{position:absolute;opacity:.95}
.foot-l{color:#6f757c;text-transform:uppercase;letter-spacing:3px;font-weight:600}
.tag{color:#fff;font-weight:600}
.prodshadow{filter:drop-shadow(0 30px 60px rgba(0,0,0,.6))}
'''

def landscape(slug, c):
    W,Hh=1920,1080
    accent=c["accent"]
    # product block
    if c["mode"]=="cutout":
        prod=f'<img src="{c["product"]}" class="prodshadow" style="position:absolute;right:60px;top:50%;transform:translateY(-50%);max-width:920px;max-height:840px;object-fit:contain">'
        overlay=""
    elif c["mode"]=="photo":
        prod=f'<div style="position:absolute;right:0;top:0;width:50%;height:100%;background:url({c["product"]}) center/cover no-repeat"></div>'
        overlay=f'<div style="position:absolute;right:0;top:0;width:58%;height:100%;background:linear-gradient(to right,#0a0b0d 0%,rgba(10,11,13,.25) 28%,transparent 60%),linear-gradient(to top,#0a0b0d,transparent 30%)"></div>'
    else: # photobg
        prod=f'<div style="position:absolute;inset:0;background:url({c["product"]}) center/cover no-repeat"></div>'
        overlay=f'<div style="position:absolute;inset:0;background:linear-gradient(to right,rgba(7,8,10,.97) 0%,rgba(7,8,10,.82) 34%,rgba(7,8,10,.30) 70%,rgba(7,8,10,.12) 100%)"></div>'
    chev = f'<div style="position:absolute;top:-70px;right:-40px;width:440px;height:620px">{CHEV(accent,52)}</div>' if c["mode"]!="photobg" else ""
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>{BASECSS}
.poster{{width:{W}px;height:{Hh}px;--ac:{accent}}}</style></head><body>
<div class="poster ff">
 <div class="tex"></div>{prod}{overlay}{chev}
 <img src="{c['logo']}" style="position:absolute;left:90px;top:80px;height:{c['logoh']}px">
 <div style="position:absolute;left:90px;top:50%;transform:translateY(-50%);width:880px">
   <div class="eyebrow" style="font-size:17px;letter-spacing:5px;margin-bottom:22px">{H.escape(c['name'])}</div>
   <div class="title" style="font-size:88px">{c['title']}</div>
   <hr class="rule" style="width:84px;margin:30px 0 28px">
   <div class="body" style="font-size:21px;line-height:1.55;max-width:760px">{c['body']}</div>
   <div class="tag" style="font-size:19px;margin-top:26px;font-style:italic;color:#dfe3e8">{H.escape(c['tag'])}</div>
 </div>
 <div style="position:absolute;left:90px;bottom:60px;display:flex;align-items:center;gap:18px">
   <img src="{GAL}" style="height:30px"><span style="width:1px;height:26px;background:#2c2f34"></span>
   <span class="foot-l" style="font-size:12px">Your Technical Partner</span>
 </div>
</div></body></html>'''

def portrait(slug, c):
    W,Hh=1080,1920
    accent=c["accent"]
    if c["mode"]=="cutout":
        prod=f'<img src="{c["product"]}" class="prodshadow" style="position:absolute;left:50%;top:560px;transform:translate(-50%,-50%);max-width:860px;max-height:760px;object-fit:contain">'
        overlay=""
        chev=f'<div style="position:absolute;top:-40px;right:-60px;width:380px;height:540px">{CHEV(accent,48)}</div>'
    elif c["mode"]=="photo":
        prod=f'<div style="position:absolute;left:0;top:0;width:100%;height:62%;background:url({c["product"]}) center 28%/cover no-repeat"></div>'
        overlay=f'<div style="position:absolute;left:0;top:0;width:100%;height:70%;background:linear-gradient(to bottom,rgba(10,11,13,.25) 0%,rgba(10,11,13,.15) 40%,#0a0b0d 96%)"></div>'
        chev=f'<div style="position:absolute;top:-30px;right:-50px;width:300px;height:430px">{CHEV(accent,46)}</div>'
    else:
        prod=f'<div style="position:absolute;left:0;top:0;width:100%;height:58%;background:url({c["product"]}) center/cover no-repeat"></div>'
        overlay=f'<div style="position:absolute;left:0;top:0;width:100%;height:66%;background:linear-gradient(to bottom,rgba(7,8,10,.35) 0%,rgba(7,8,10,.1) 38%,#0a0b0d 95%)"></div>'
        chev=""
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>{BASECSS}
.poster{{width:{W}px;height:{Hh}px;--ac:{accent}}}</style></head><body>
<div class="poster ff">
 <div class="tex"></div>{prod}{overlay}{chev}
 <img src="{c['logo']}" style="position:absolute;left:80px;top:70px;height:{int(c['logoh']*1.05)}px;z-index:5">
 <div style="position:absolute;left:80px;right:80px;top:1080px">
   <div class="eyebrow" style="font-size:18px;letter-spacing:5px;margin-bottom:24px">{H.escape(c['name'])}</div>
   <div class="title" style="font-size:104px">{c['title']}</div>
   <hr class="rule" style="width:90px;margin:34px 0 30px">
   <div class="body" style="font-size:27px;line-height:1.55">{c['body']}</div>
   <div class="tag" style="font-size:25px;margin-top:30px;font-style:italic;color:#dfe3e8">{H.escape(c['tag'])}</div>
 </div>
 <div style="position:absolute;left:80px;bottom:70px;display:flex;align-items:center;gap:20px">
   <img src="{GAL}" style="height:36px"><span style="width:1px;height:30px;background:#2c2f34"></span>
   <span class="foot-l" style="font-size:13px">Your Technical Partner</span>
 </div>
</div></body></html>'''

os.makedirs("/tmp/posters", exist_ok=True)
for slug,c in BR.items():
    open(f"/tmp/posters/{slug}_16x9.html","w").write(landscape(slug,c))
    open(f"/tmp/posters/{slug}_9x16.html","w").write(portrait(slug,c))
print("generated", len(BR)*2, "html files")
