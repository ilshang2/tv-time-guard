"""產生「電視每日額度」示範動畫（約 28 秒，1080p）。
素材在 assets/：儀表板三個狀態的裁切圖與電視主畫面。
執行：python make_demo.py  →  tv-time-guard-demo.mp4
需要：pip install pillow imageio-ffmpeg
"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda n: os.path.join(HERE, "demo-assets", n)
OUT = os.path.join(HERE, "demo.mp4")
W, H, FPS = 1920, 1080, 30
BOLD, REG = r"C:\Windows\Fonts\msjhbd.ttc", r"C:\Windows\Fonts\msjh.ttc"
_f = {}
def font(sz, bold=True):
    k = (sz, bold)
    if k not in _f: _f[k] = ImageFont.truetype(BOLD if bold else REG, sz)
    return _f[k]

BG = (15, 23, 42); FG = (241, 245, 249); MUTED = (148, 163, 184)
ACC = (56, 189, 248); GOOD = (74, 222, 128); WARN = (251, 146, 60); RED = (200, 30, 30)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def seg(t, a, b): return clamp((t - a) / (b - a))

def text(img, xy, s, sz, fill=FG, bold=True, anchor="mm", alpha=1.0):
    if alpha <= 0: return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, s, font=font(sz, bold), fill=fill + (int(255 * alpha),), anchor=anchor)
    img.alpha_composite(layer)

def rrect(img, box, r, fill, outline=None, width=0, alpha=1.0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, r, fill=fill + (int(255 * alpha),),
                        outline=(outline + (int(255 * alpha),)) if outline else None, width=width)
    img.alpha_composite(layer)

def base(): return Image.new("RGBA", (W, H), BG + (255,))

def paste_a(img, im, xy, alpha=1.0):
    im = im.convert("RGBA")
    if alpha < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, xy)

DASH = {k: Image.open(A(f"dash_{k}.png")).convert("RGB") for k in ("normal", "bonus", "parent")}
TV = Image.open(A("tv_home.png")).convert("RGB").resize((W, H))

# ---------- 場景 1：標題 ----------
def s1(t):
    im = base()
    k = ease(seg(t, 0, .8)); k2 = ease(seg(t, .7, 1.5)); k3 = ease(seg(t, 1.6, 2.4))
    # 電視圖示
    cx, cy = W // 2, 300
    rrect(im, (cx - 150, cy - 95, cx + 150, cy + 95), 22, (30, 41, 59), ACC, 8, k)
    text(im, (cx, cy - 5), "⏳" if False else "90:00", 64, ACC, alpha=k)
    rrect(im, (cx - 50, cy + 105, cx + 50, cy + 118), 6, ACC, alpha=k)
    text(im, (W // 2, 560 + (1 - k) * 40), "電視也能設「每日額度」", 110, FG, alpha=k)
    text(im, (W // 2, 700), "時間到，自動關機", 64, WARN, alpha=k2)
    text(im, (W // 2, 820), "Home Assistant ＋ 100 行電視 App　·　純區網　免雲端", 40, MUTED, False, alpha=k3)
    return im

# ---------- 場景 2：手機儀表板 ----------
def s2(t):
    im = base()
    text(im, (W // 2, 90), "家長用手機掌控", 70, FG, alpha=ease(seg(t, 0, .5)))
    px, py, pw, ph = 150, 150, 820, 880
    slide = ease(seg(t, 0, .7))
    ox = int((1 - slide) * -500)
    rrect(im, (px + ox, py, px + pw + ox, py + ph), 56, (2, 6, 23), (71, 85, 105), 8)
    rrect(im, (px + 20 + ox, py + 70, px + pw - 20 + ox, py + ph - 40), 20, (250, 250, 250))
    # 狀態切換
    if t < 2.0: cur, nxt, m = "normal", "normal", 0
    elif t < 2.4: cur, nxt, m = "normal", "bonus", seg(t, 2.0, 2.4)
    elif t < 4.2: cur, nxt, m = "bonus", "bonus", 0
    elif t < 4.6: cur, nxt, m = "bonus", "parent", seg(t, 4.2, 4.6)
    else: cur, nxt, m = "parent", "parent", 0
    ds = 1.45
    sz = (int(520 * ds), int(360 * ds))
    a = DASH[cur].resize(sz, Image.LANCZOS); b = DASH[nxt].resize(sz, Image.LANCZOS)
    mix = Image.blend(a, b, m) if m else a
    im.paste(mix, (px + 33 + ox, py + 100))
    # 點擊動畫
    def tap(t0, x, y):
        k = seg(t, t0, t0 + .6)
        if 0 < k < 1:
            r = 20 + 60 * k
            layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(layer).ellipse((x - r, y - r, x + r, y + r), outline=ACC + (int(255 * (1 - k)),), width=8)
            im.alpha_composite(layer)
    tap(1.7, px + 33 + int(130 * ds), py + 100 + int(300 * ds))    # 加 15 分鐘
    tap(4.0, px + 33 + int(130 * ds), py + 100 + int(130 * ds))    # 家長模式
    # 右側說明
    items = [("看今日剩餘時間", .9, MUTED, FG), ("一鍵加時：加 15／30 分鐘", 2.0, ACC, FG), ("家長模式：不計時、不限制", 4.0, GOOD, FG)]
    for i, (s, t0, c, f) in enumerate(items):
        k = ease(seg(t, t0, t0 + .5))
        y = 360 + i * 170
        rrect(im, (1120, y - 55, 1800, y + 55), 24, (30, 41, 59), c, 4, k)
        text(im, (1460 + (1 - k) * 60, y), s, 44, f, alpha=k)
    text(im, (1460, 900), "家長手機的 HA 登入本身就是「密碼」", 36, MUTED, False, alpha=ease(seg(t, 5.2, 5.8)))
    return im

# ---------- 場景 3：電視倒數與關機 ----------
def pill(im, label, urgent, scale=1.0):
    f = font(int(54 * scale))
    d = ImageDraw.Draw(im)
    w = int(d.textlength(label, font=f)) + 72
    x1, y0 = W - 110, 70
    box = (x1 - w, y0, x1, y0 + int(96 * scale))
    rrect(im, box, 22, RED if urgent else (55, 55, 60), alpha=0.95)
    text(im, ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), label, int(54 * scale), (255, 255, 255))

def s3(t):
    # t: 0..10
    im = TV.copy().convert("RGBA")
    cap, capc = "", FG
    if t < 1.2:
        cap = "剩 10 分鐘，電視右上角自動出現倒數"
        k = ease(seg(t, .3, 1.0))
        if k > 0:
            sc = 0.6 + 0.4 * k
            pill(im, "剩餘 10:00", False, sc)
    elif t < 6.2:
        p = ease(seg(t, 1.2, 6.2))            # 把 10 分鐘壓縮成 5 秒
        left = int(600 * (1 - p))
        urgent = left <= 60
        cap = "最後 1 分鐘轉紅" if urgent else "剩 10 分鐘，電視右上角自動出現倒數"
        if urgent: capc = WARN
        pill(im, f"剩餘 {left // 60}:{left % 60:02d}", urgent)
    elif t < 7.8:
        cap, capc = "額度用完，自動關機", WARN
        pulse = 1 + 0.06 * math.sin((t - 6.2) * 12)
        pill(im, "時間到", True, pulse)
    elif t < 9.2:
        k = seg(t, 7.8, 9.2)
        # 類 CRT 關機：垂直收縮成線再收成點
        if k < .6:
            hh = max(4, int(H * (1 - ease(k / .6)) ))
            sub = TV.resize((W, hh)).convert("RGBA")
            im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            im.alpha_composite(sub, (0, (H - hh) // 2))
        else:
            im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            ww = int(W * (1 - ease((k - .6) / .4)))
            if ww > 6:
                ImageDraw.Draw(im).rectangle(((W - ww) // 2, H // 2 - 2, (W + ww) // 2, H // 2 + 2), fill=(255, 255, 255))
        cap, capc = "", FG
    else:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        text(im, (W // 2, H // 2), "之後再開機，也很快又被關掉", 56, MUTED, alpha=ease(seg(t, 9.3, 9.8)))
    if cap:
        rrect(im, (360, 930, 1560, 1030), 26, (0, 0, 0), alpha=0.7)
        text(im, (W // 2, 980), cap, 50, capc)
    return im

# ---------- 場景 4：運作流程 ----------
def s4(t):
    im = base()
    text(im, (W // 2, 110), "怎麼做到的？", 70, FG, alpha=ease(seg(t, 0, .4)))
    boxes = [("電視開著", "HA 偵測"), ("累計今日時間", "history_stats"), ("ADB 指令", "叫電視顯示倒數"), ("額度用完", "自動關機")]
    bw, bh, gap = 360, 190, 80
    x0 = (W - (4 * bw + 3 * gap)) // 2
    y = 400
    for i, (a, b) in enumerate(boxes):
        k = ease(seg(t, .5 + i * .8, 1.0 + i * .8))
        x = x0 + i * (bw + gap)
        rrect(im, (x, y + (1 - k) * 40, x + bw, y + bh + (1 - k) * 40), 28, (30, 41, 59), ACC if i < 3 else WARN, 5, k)
        text(im, (x + bw // 2, y + 70 + (1 - k) * 40), a, 46, FG, alpha=k)
        text(im, (x + bw // 2, y + 132 + (1 - k) * 40), b, 30, MUTED, False, alpha=k)
        if i < 3:
            ka = ease(seg(t, 1.0 + i * .8, 1.4 + i * .8))
            ax = x + bw + 12; ay = y + bh // 2
            d = ImageDraw.Draw(im)
            d.line((ax, ay, ax + (gap - 24) * ka, ay), fill=ACC + (255,), width=8)
            if ka > .9: d.polygon([(ax + gap - 24, ay - 14), (ax + gap - 24, ay + 14), (ax + gap - 4, ay)], fill=ACC + (255,))
    k = ease(seg(t, 4.0, 4.6))
    rrect(im, (x0 + 400, 720, x0 + 400 + 640, 830), 28, (30, 41, 59), GOOD, 5, k)
    text(im, (x0 + 720, 775), "家長手機：加時／家長模式", 42, FG, alpha=k)
    d = ImageDraw.Draw(im)
    if k > .5:
        d.line((x0 + 720, 720, x0 + 720, 625), fill=GOOD + (255,), width=8)
        d.polygon([(x0 + 706, 640), (x0 + 734, 640), (x0 + 720, 612)], fill=GOOD + (255,))
    return im

# ---------- 場景 5：結尾 ----------
def s5(t):
    im = base()
    for i, (s, c) in enumerate([("純區網", ACC), ("免雲端", GOOD), ("免帳號", WARN)]):
        k = ease(seg(t, .2 + i * .4, .8 + i * .4))
        text(im, (500 + i * 460, 430 + (1 - k) * 40), s, 100, c, alpha=k)
    text(im, (W // 2, 640), "Home Assistant ＋ ADB ＋ 100 行電視 App", 52, FG, alpha=ease(seg(t, 1.6, 2.2)))
    text(im, (W // 2, 740), "小米電視（Android TV）實測可用", 40, MUTED, False, alpha=ease(seg(t, 2.0, 2.6)))
    return im

SCENES = [(3.5, s1), (6.5, s2), (10.0, s3), (5.5, s4), (3.0, s5)]

def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    p = subprocess.Popen([ff, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", OUT],
                         stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    prev = None
    for dur, fn in SCENES:
        n = int(dur * FPS)
        for i in range(n):
            t = i / FPS
            fr = fn(t)
            if i < 6 and prev is not None:       # 場景間 0.2 秒淡入
                fr = Image.blend(prev.convert("RGBA"), fr.convert("RGBA"), (i + 1) / 7)
            p.stdin.write(fr.convert("RGB").tobytes())
        prev = fn(dur - 1 / FPS)
    p.stdin.close(); p.wait()
    print("完成：", OUT)

if __name__ == "__main__":
    main()
