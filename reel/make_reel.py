"""Colliery Parc Building 5 - Crane Day comic reel renderer.
Builds a 1080x1920 30fps reel by moving a virtual camera over the comic pages,
plus a synthesized 120 BPM soundtrack with whooshes/impacts on the cuts."""
import subprocess, sys, math, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

U = sys.argv[1] if len(sys.argv) > 1 else "src"
OUT = sys.argv[2] if len(sys.argv) > 2 else "out"
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
BEAT = 0.5  # 120 BPM
SAFE = (40, 270, 1000, 1210)  # card box inside Instagram safe zone
FULL = (0, 0, W, H)
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"

IMG = {k: Image.open(f"{U}/{v}-image.png").convert("RGB") for k, v in dict(
    p1="bd792af5", peter="ece3a294", colin="175c01f3", ron="aea4dc48", eion="66c2f79a",
    akogun="9bf553f4", p2="1dd33b49", p3="1cda8757", p4="7cf4c33e", p5="8f948dc4",
    snap="3d3923ef", credits="920a78a1").items()}

def bg_for(im):
    s = max(W / im.width, H / im.height) * 1.15
    b = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
    b = b.crop(((b.width - W) // 2, (b.height - H) // 2, (b.width - W) // 2 + W, (b.height - H) // 2 + H))
    b = b.filter(ImageFilter.GaussianBlur(28))
    return ImageEnhance.Brightness(b).enhance(0.42)
BG = {k: bg_for(v) for k, v in IMG.items()}

def r(x0, y0, x1, y1):
    return (x0, y0, x1 - x0, y1 - y0)

def cam(im, cx, cy, w):
    """9:16 camera rect centred at cx,cy with width w, clamped inside the image."""
    h = w * 16 / 9
    if h > IMG[im].height:
        h = IMG[im].height; w = h * 9 / 16
    x = min(max(cx - w / 2, 0), IMG[im].width - w)
    y = min(max(cy - h / 2, 0), IMG[im].height - h)
    return (x, y, w, h)

def full(im):
    return (0, 0, IMG[im].width, IMG[im].height)

# Shot: (image, beats, [(t, src_rect, box)], opts)
#   keyframes at normalized t in [0,1]; box = output rect the source is fitted into.
S = []
def shot(im, beats, keys, **o):
    S.append(dict(im=im, dur=beats * BEAT, keys=keys, **o))
def push(im, beats, a, b, box=SAFE, **o):
    shot(im, beats, [(0, a, box), (1, b, box)], **o)
def grow(rect, k):
    x, y, w, h = rect; return (x - w * k / 2, y - h * k / 2, w * (1 + k), h * (1 + k))

# --- helpers for the edit
PANBOX = (40, 470, 1000, 800)
def pan(im, rect, beats, rev=False, **o):
    x, y, w, h = rect
    cw = h * PANBOX[2] / PANBOX[3]
    a, b = (x, y, cw, h), (x + w - cw, y, cw, h)
    if rev: a, b = b, a
    shot(im, beats, [(0, a, PANBOX), (1, b, PANBOX)], **o)
def panel(im, rect, beats, **o):
    if rect[2] / rect[3] > 1.8: pan(im, rect, beats, **o)
    else: push(im, beats, rect, grow(rect, -0.1), **o)
def title(im, rect, beats=3, sfx="whoosh"):
    shot(im, beats, [(0, full(im), SAFE), (0.35, full(im), SAFE), (1, rect, SAFE)], sfx=sfx, flash=True)
def card(im, beats, blocks, **o):
    shot(im, beats, [(0, full(im), SAFE), (1, full(im), SAFE)], text=blocks, nopanel=True, **o)

# --- Cold open hook: the Snap splash, pushing out from Eion
shot("snap", 5, [(0, cam("snap", 830, 560, 420), FULL), (1, cam("snap", 830, 520, 529), FULL)],
     hook=True, sfx="impact", pop=False)
# --- Page 1: Team Assemble
title("p1", r(80, 0, 960, 125))
panel("p1", r(8, 128, 1016, 540), 5)
panel("p1", r(8, 548, 1016, 955), 5, sfx="swoosh")
for rr in [r(8, 965, 508, 1248), r(514, 965, 1016, 1248), r(8, 1252, 508, 1532), r(514, 1252, 1016, 1532)]:
    panel("p1", rr, 1.5, sfx="tick")
# --- Character cards: tight on the face, pull back to the full card with nameplate
faces = dict(peter=(500, 190), colin=(495, 190), ron=(470, 170), eion=(480, 170), akogun=(470, 220))
for k in ["peter", "colin", "ron", "eion", "akogun"]:
    fx, fy = faces[k]
    shot(k, 4, [(0, cam(k, fx, 320, 360), FULL), (0.35, cam(k, fx, 340, 384), FULL),
                (1, full(k), SAFE)], sfx="impact", flash=(k == "peter"))
# --- Page 2: The Journey to Canmore
title("p2", r(150, 0, 870, 82))
panel("p2", r(8, 88, 1016, 400), 5)
panel("p2", r(8, 410, 584, 803), 3, sfx="tick")
panel("p2", r(592, 410, 1016, 803), 3, sfx="tick")
shot("p2", 5, [(0, cam("p2", 180, 990, 330), FULL), (1, cam("p2", 845, 990, 330), FULL)], sfx="tick")
panel("p2", r(8, 1160, 494, 1532), 3, sfx="tick")
panel("p2", r(502, 1160, 1016, 1532), 3, sfx="tick")
# --- Page 3: Foundation preparation
title("p3", r(10, 0, 1016, 100))
panel("p3", r(4, 90, 1020, 515), 5)
for rr in [r(4, 525, 508, 1020), r(516, 525, 1020, 1020), r(4, 1030, 508, 1468), r(516, 1030, 1020, 1468)]:
    panel("p3", rr, 3, sfx="tick")
card("p3", 6, [(0.0, "Michael worked too!", "head"),
               (0.9, "No photo this time — apparently his superpower is invisibility.", "body")], sfx="tick")
# --- Page 4: The night before crane day
title("p4", r(140, 0, 840, 80))
panel("p4", r(8, 85, 972, 535), 5)
panel("p4", r(8, 545, 448, 978), 4, sfx="tick")
panel("p4", r(456, 545, 972, 978), 3, sfx="tick")
panel("p4", r(8, 985, 972, 1285), 4, sfx="tick")
card("p4", 11, [(0.0, "RUMOUR HAS IT...", "head"),
                (0.7, "Cpt. Jack Sparrow met the Virgin Mary at the bar that night.", "body"),
                (2.0, "Dr. Akogun's pool skills are still under construction.", "body"),
                (3.2, "Colin delivered a Grammy-worthy karaoke performance.", "body"),
                (4.3, "Eyewitness accounts may vary.", "small")], sfx="tick")
card("p4", 7, [(0.0, "Meanwhile, as the team made merry, an alien force from outer space attacked their crane in Calgary...", "body"),
               (2.0, "NEXT PAGE: CRANE UNDER ATTACK!", "head")], sfx="riser")
# --- Page 5: Crane under attack
title("p5", r(100, 0, 920, 82), sfx="impact")
panel("p5", r(4, 85, 1020, 400), 5, shake=True)
panel("p5", r(4, 408, 476, 790), 2, sfx="tick")
panel("p5", r(484, 408, 1020, 790), 5, sfx="tick")
panel("p5", r(4, 800, 1020, 1100), 5, sfx="tick")
panel("p5", r(4, 1108, 446, 1490), 3, sfx="tick")
panel("p5", r(452, 1108, 1020, 1490), 4, sfx="impact", shake=True)
card("p5", 4, [(0.0, "The crane was ready.", "body"), (0.8, "The clock had other ideas.", "head")], sfx="tick")
# --- Page 6: Hold the wind. Snap it into reality!
shot("snap", 3, [(0, full("snap"), SAFE), (1, grow(full("snap"), -0.05), SAFE)], sfx="whoosh", flash=True)
shot("snap", 9, [(0, cam("snap", 180, 470, 529), FULL), (1, cam("snap", 1490, 470, 529), FULL)], sfx="snap")
shot("snap", 3, [(0, full("snap"), SAFE), (1, grow(full("snap"), -0.06), SAFE)], sfx="impact")
# --- Credits
card("credits", 14, [(0.0, "EVERY HERO DESERVES A CREDIT", "head"),
                     (0.8, "Apologies to everyone on site who didn't feature — I couldn't take photos or record videos on crane day.", "body"),
                     (2.6, "A huge shout-out to Dave, Devon, and Mike, and everyone who helped make it happen.", "body"),
                     (4.4, "You may be missing from the panels, but you're a big part of the story!", "head")],
     sfx="whoosh", flash=True)
shot("credits", 6, [(0, full("credits"), SAFE), (1, grow(full("credits"), -0.05), SAFE)], end=True, sfx="impact")

# --- caption-box text cards
CREAM, INK = (250, 238, 205), (15, 15, 25)
STY = {"head": (F_BLACK, 66, (190, 20, 20)), "body": ("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 52, INK),
       "small": ("/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf", 38, (90, 70, 40))}
def wrap(text, font, maxw):
    out, cur = [], ""
    for w_ in text.split():
        t_ = (cur + " " + w_).strip()
        if font.getlength(t_) <= maxw or not cur: cur = t_
        else: out.append(cur); cur = w_
    out.append(cur)
    # never end a line on a tiny word
    for i in range(len(out) - 1):
        last = out[i].split()[-1]
        if last.lower() in ("a", "the", "an", "to", "of", "and") and len(out[i].split()) > 1:
            out[i] = out[i][: -len(last) - 1]; out[i + 1] = last + " " + out[i + 1]
    return out
_BOX = {}
def box_img(text, style):
    k = (text, style)
    if k in _BOX: return _BOX[k]
    fp, size, col = STY[style]; f = ImageFont.truetype(fp, size)
    lines = wrap(text, f, 860)
    lh = size * 1.22; pw, ph = 36, 30
    bw = int(max(f.getlength(l) for l in lines) + pw * 2); bh = int(lh * len(lines) + ph * 2)
    im = Image.new("RGBA", (bw + 14, bh + 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([12, 12, bw + 12, bh + 12], fill=(0, 0, 0, 170))
    d.rectangle([0, 0, bw, bh], fill=CREAM + (255,), outline=INK + (255,), width=6)
    for i, l in enumerate(lines):
        x = (bw - f.getlength(l)) / 2
        d.text((x, ph + i * lh - size * 0.08), l, font=f, fill=col)
    _BOX[k] = im; return im
def layout(blocks):
    ims = [box_img(t, s) for _, t, s in blocks]
    gap = 34; tot = sum(i.height for i in ims) + gap * (len(ims) - 1)
    y = 880 - tot / 2; pos = []
    for i in ims: pos.append(y + i.height / 2); y += i.height + gap
    return ims, pos

def ease(t):
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))

def state(sh, t):
    ks = sh["keys"]
    for (t0, s0, b0), (t1, s1, b1) in zip(ks, ks[1:]):
        if t <= t1:
            u = (t - t0) / max(t1 - t0, 1e-6)
            u = ease(u) if len(ks) > 2 else u * 0.35 + ease(u) * 0.65
            return lerp(s0, s1, u), lerp(b0, b1, u)
    return ks[-1][1], ks[-1][2]

def fit(src, box):
    sx, sy, sw, sh = src; bx, by, bw, bh = box
    s = min(bw / sw, bh / sh)
    dw, dh = sw * s, sh * s
    return bx + (bw - dw) / 2, by + (bh - dh) / 2, dw, dh

def text_img(lines, size, fill=(255, 214, 64)):
    f = ImageFont.truetype(F_BLACK, size)
    pad = 30
    bbs = [f.getbbox(l) for l in lines]
    lw = max(b[2] - b[0] for b in bbs) + pad * 2
    lh = size * 1.12
    im = Image.new("RGBA", (int(lw), int(lh * len(lines) + pad * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = (lw - (bbs[i][2] - bbs[i][0])) / 2 - bbs[i][0]; y = pad + i * lh
        d.text((x + 6, y + 8), l, font=f, fill=(0, 0, 0, 200))
        d.text((x, y), l, font=f, fill=fill, stroke_width=7, stroke_fill=(15, 15, 30))
    return im
HOOK1 = text_img(["CRANE DAY"], 150)
HOOK2 = text_img(["COLLIERY PARC", "BUILDING 5"], 78, fill=(255, 255, 255))
HOOK3 = text_img(["THE COMIC"], 64, fill=(255, 214, 64))
END = text_img(["TEAM ASSEMBLED."], 82)

def paste_pop(fr, im, cx, cy, t0, t):
    if t < t0: return
    u = min((t - t0) / 0.25, 1)
    sc = 0.6 + 0.4 * (1 + 2.2 * (u - 1) ** 3 + 1.2 * (u - 1) ** 2)  # back-out
    w, h = int(im.width * sc), int(im.height * sc)
    if w < 2: return
    fr.paste(im.resize((w, h), Image.BICUBIC), (int(cx - w / 2), int(cy - h / 2)), im.resize((w, h), Image.BICUBIC))

def render_frame(sh, lt):
    t = lt / sh["dur"]
    src, box = state(sh, t)
    im = IMG[sh["im"]]
    fr = BG[sh["im"]].copy()
    dx, dy, dw, dh = fit(src, box)
    if sh.get("pop", True) and box != FULL:  # panel pops in at shot start
        u = min(lt / 0.22, 1)
        sc = 0.88 + 0.12 * (1 + 2.0 * (u - 1) ** 3 + 1.0 * (u - 1) ** 2)
        cx, cy = dx + dw / 2, dy + dh / 2
        dw, dh = dw * sc, dh * sc; dx, dy = cx - dw / 2, cy - dh / 2
    if sh.get("shake") and lt < 0.5:
        a = 14 * (1 - lt / 0.5); dx += a * math.sin(lt * 90); dy += a * math.cos(lt * 70)
    if sh.get("nopanel"):
        ims, pos = layout(sh["text"])
        for (t0, _, _), bim, cy in zip(sh["text"], ims, pos):
            paste_pop(fr, bim, W / 2, cy, t0, lt)
        if sh.get("flash") and lt < 0.18:
            fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), (1 - lt / 0.18) * 0.85)
        return fr
    iw, ih = max(int(round(dw)), 1), max(int(round(dh)), 1)
    sx, sy, sw, shh = src
    panel = im.resize((iw, ih), Image.BICUBIC, box=(sx, sy, sx + sw, sy + shh))
    ix, iy = int(round(dx)), int(round(dy))
    if iw < W or ih < H:
        d = ImageDraw.Draw(fr)
        d.rectangle([ix - 4, iy + 18, ix + iw + 22, iy + ih + 26], fill=(0, 0, 0))
        d.rectangle([ix - 9, iy - 9, ix + iw + 8, iy + ih + 8], fill=(255, 255, 255))
        d.rectangle([ix - 4, iy - 4, ix + iw + 3, iy + ih + 3], fill=(10, 10, 20))
    fr.paste(panel, (ix, iy))
    if sh.get("hook"):
        paste_pop(fr, HOOK2, W / 2, 330, 0.0, lt)
        paste_pop(fr, HOOK1, W / 2, 470, 0.0, lt)
        paste_pop(fr, HOOK3, W / 2, 1380, 0.9, lt)
    if sh.get("end"):
        paste_pop(fr, END, W / 2, 1620 - 140, 0.0, lt)
    if sh.get("flash") and lt < 0.18:
        a = 1 - lt / 0.18
        fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), a * 0.85)
    if sh.get("end"):  # fade to black over the last second
        rem = sh["dur"] - lt
        if rem < 1.0: fr = Image.blend(Image.new("RGB", (W, H)), fr, max(rem, 0))
    return fr

def render_video(path_noaudio):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p", path_noaudio],
                         stdin=subprocess.PIPE)
    n = 0
    for sh in S:
        nf = int(round(sh["dur"] * FPS))
        for i in range(nf):
            p.stdin.write(render_frame(sh, i / FPS).tobytes()); n += 1
    p.stdin.close(); p.wait()
    return n

# ---------------- audio ----------------
SR = 48000
def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)

def music(total):
    n = int(total * SR); out = np.zeros(n)
    rng = np.random.default_rng(1)
    def add(sig, t):
        i = int(t * SR); j = min(n, i + len(sig))
        if i < n: out[i:j] += sig[:j - i]
    kick_n = int(0.35 * SR); tt = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * (45 + 110 * np.exp(-tt * 30)) * tt) * env(kick_n, 0.002, 0.12)
    sn_n = int(0.25 * SR); snare = (rng.standard_normal(sn_n) * 0.6 + np.sin(2 * np.pi * 190 * np.arange(sn_n) / SR) * 0.5) * env(sn_n, 0.001, 0.07)
    hat_n = int(0.06 * SR); hat = np.diff(rng.standard_normal(hat_n + 1)) * env(hat_n, 0.001, 0.015) * 0.35
    roots = [57, 53, 48, 55]  # A F C G (midi)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    bar = 4 * BEAT
    nb = int(math.ceil(total / bar))
    for b in range(nb):
        t0 = b * bar; ci = b % 4
        intro = b < 1
        for k in range(4):
            if not intro: add(kick * 0.9, t0 + k * BEAT)
            if k in (1, 3) and not intro: add(snare * 0.5, t0 + k * BEAT)
        for k in range(8): add(hat * (0.9 if k % 2 else 0.5), t0 + k * BEAT / 2)
        # bass: eighth-note pulse
        bn = int(BEAT / 2 * SR); bt = np.arange(bn) / SR
        f = hz(roots[ci] - 24)
        bass = (2 * ((bt * f) % 1) - 1)
        bass = np.convolve(bass, np.ones(24) / 24, mode="same") * env(bn, 0.004, 0.18) * 0.45
        if not intro:
            for k in range(8): add(bass, t0 + k * BEAT / 2)
        # pad chord stabs
        pn = int(bar * SR); pt = np.arange(pn) / SR
        pad = sum((2 / np.pi) * np.arcsin(np.sin(2 * np.pi * hz(m) * pt)) * 0.6 + np.sin(2 * np.pi * hz(m + 12) * pt) for m in chords[ci])
        pad = np.convolve(pad, np.ones(40) / 40, mode="same") * np.minimum(pt / 0.05, 1) * np.exp(-pt / 1.2) * 0.06
        add(pad, t0)
    fade = np.ones(n); fl = int(2.0 * SR); fade[-fl:] = np.linspace(1, 0, fl)
    return out * fade

def sfx(kind):
    rng = np.random.default_rng(hash(kind) % 1000)
    if kind == "whoosh" or kind == "swoosh":
        n = int(0.45 * SR); x = rng.standard_normal(n); t = np.arange(n) / SR
        out = np.zeros(n); y = 0; 
        cut = 0.02 + 0.25 * np.sin(np.pi * t / t[-1]) ** 2
        for i in range(n): y += cut[i] * (x[i] - y); out[i] = y
        return out * np.sin(np.pi * t / t[-1]) ** 2 * (0.9 if kind == "whoosh" else 0.5)
    if kind == "impact":
        n = int(0.9 * SR); t = np.arange(n) / SR
        boom = np.sin(2 * np.pi * (38 + 80 * np.exp(-t * 18)) * t) * np.exp(-t / 0.35)
        crack = rng.standard_normal(n) * np.exp(-t / 0.03) * 0.5
        return (boom + crack) * 0.9
    if kind == "tick":
        n = int(0.08 * SR); t = np.arange(n) / SR
        return np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.012) * 0.25
    if kind == "snap":
        n = int(0.15 * SR); t = np.arange(n) / SR
        return (rng.standard_normal(n) * np.exp(-t / 0.008) + np.sin(2 * np.pi * 2500 * t) * np.exp(-t / 0.01)) * 0.7
    if kind == "riser":
        n = int(3.0 * SR); t = np.arange(n) / SR
        return np.sin(2 * np.pi * (200 * t + 300 * t ** 2)) * (t / t[-1]) ** 2 * 0.25
    return np.zeros(1)

def build_audio(path, with_music=True):
    total = sum(s["dur"] for s in S)
    n = int(total * SR)
    a = music(total) * 0.55 if with_music else np.zeros(n)
    t = 0
    for sh in S:
        k = sh.get("sfx")
        if k:
            s = sfx(k); i = max(int((t - (0.12 if k in ("whoosh", "swoosh") else 0)) * SR), 0)
            j = min(n, i + len(s)); a[i:j] += s[:j - i] * 0.7
            if k == "snap":  # five snaps, one per hero
                for q in range(1, 5):
                    i2 = int((t + q * sh["dur"] / 5) * SR); j2 = min(n, i2 + len(s)); a[i2:j2] += s[:j2 - i2] * 0.7
        t += sh["dur"]
    a = a / (np.abs(a).max() + 1e-9)
    a = np.tanh(a * 2.5) / np.tanh(2.5) * 0.9  # soft limiter so loudness can reach -14 LUFS
    st = np.stack([a, a], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
    return total

if __name__ == "__main__":
    mode = sys.argv[3] if len(sys.argv) > 3 else "all"
    total = sum(s["dur"] for s in S)
    print(f"{len(S)} shots, {total:.1f}s")
    if mode == "sheet":
        t = 0; frames = []
        for sh in S:
            frames.append(render_frame(sh, sh["dur"] * (0.95 if sh.get("nopanel") else 0.6)).resize((180, 320)))
        cols = 10; rows = math.ceil(len(frames) / cols)
        sheet = Image.new("RGB", (cols * 180, rows * 320))
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * 180, (i // cols) * 320))
        sheet.save(f"{OUT}/sheet.jpg", quality=85); sys.exit()
    build_audio(f"{OUT}/music.wav", True)
    build_audio(f"{OUT}/sfx_only.wav", False)
    if mode != "audio": render_video(f"{OUT}/video.mp4")
    for name, wav in [("final", "music.wav"), ("final_sfx_only", "sfx_only.wav")]:
        import json, re
        def lufs(af):
            e = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{OUT}/{wav}", "-af", af + ",ebur128", "-f", "null", "-"],
                               capture_output=True, text=True).stderr
            return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1])
        g = 0.0
        for _ in range(3):  # gain + true-peak limiter, iterate to -14 LUFS
            ln = f"lowpass=f=15000,volume={g:.2f}dB,aresample=192000,alimiter=limit=0.6:level=false:attack=1:release=60,aresample=48000"
            g += -14.0 - lufs(ln)
        ln = f"lowpass=f=15000,volume={g:.2f}dB,aresample=192000,alimiter=limit=0.6:level=false:attack=1:release=60,aresample=48000"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/video.mp4", "-i", f"{OUT}/{wav}",
                        "-af", ln, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-movflags", "+faststart", "-shortest", f"{OUT}/{name}.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/video.mp4", "-c:v", "copy", "-an",
                    "-movflags", "+faststart", f"{OUT}/final_no_audio.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", f"{OUT}/video.mp4", "-frames:v", "1",
                    f"{OUT}/cover.jpg"], check=True)
