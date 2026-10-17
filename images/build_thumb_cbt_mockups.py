#!/usr/bin/env python3
"""
CBTアプリの4タブスクショをスマホモックに収め、WORKS用サムネ（1600×1200）へ横一列で配置する。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
SOURCES = (
    ROOT / "cbt-thumb-tab1-home.png",
    ROOT / "cbt-thumb-tab2-chat.png",
    ROOT / "cbt-thumb-tab3-memory.png",
    ROOT / "cbt-thumb-tab4-progress.png",
)
OUT = ROOT / "thumb-cbt-mindful-path.jpg"

CANVAS_W, CANVAS_H = 1600, 1200
GAP = 28
SIDE = 48
BG = (233, 236, 241)

BODY_FILL = (26, 28, 40, 255)
NOTCH_FILL = (8, 9, 12, 240)
HOME_BAR = (230, 230, 238, 200)
SCREEN_BG = (244, 247, 250)


def draw_rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255
    )
    return mask


def resize_cover_top(im: Image.Image, tw: int, th: int) -> Image.Image:
    """画面領域いっぱいに覆う。上端基準でクロップ（UIヘッダーが切れにくい）。"""
    rgb = im.convert("RGB")
    w, h = rgb.size
    scale = max(tw / w, th / h)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    resized = rgb.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = 0
    return resized.crop((left, top, left + tw, top + th))


def phone_mock(screen: Image.Image, pw: int, ph: int) -> Image.Image:
    """外寸 pw×ph の端末フレーム。画面はベゼル内に上寄せでフィット。"""
    bezel = max(8, pw // 28)
    notch_h = max(12, ph // 72)
    top_band = bezel + notch_h + max(8, ph // 150)
    bottom_band = bezel + max(14, ph // 56)

    sx0, sy0 = bezel, top_band
    sw = pw - bezel * 2
    sh = ph - top_band - bottom_band
    screen_r = max(14, pw // 14)
    outer_r = max(24, min(pw, ph) // 10)

    out = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))

    body_mask = draw_rounded_mask((pw, ph), outer_r)
    body = Image.new("RGBA", (pw, ph), BODY_FILL)
    body.putalpha(body_mask)
    out.alpha_composite(body)

    # ノッチ
    nw = int(pw * 0.36)
    nx = (pw - nw) // 2
    ny = max(2, bezel // 2)
    notch = Image.new("RGBA", (nw, notch_h), (0, 0, 0, 0))
    ImageDraw.Draw(notch).rounded_rectangle(
        (0, 0, nw - 1, notch_h - 1), radius=notch_h // 2, fill=NOTCH_FILL
    )
    out.alpha_composite(notch, (nx, ny))

    # 画面（角丸クリップ）
    content = resize_cover_top(screen, sw, sh)
    screen_layer = Image.new("RGBA", (sw, sh), SCREEN_BG + (255,))
    screen_layer.paste(content, (0, 0))
    r_scr = min(screen_r, sw // 4, sh // 12)
    screen_layer.putalpha(draw_rounded_mask((sw, sh), r_scr))
    out.alpha_composite(screen_layer, (sx0, sy0))

    # ホームインジケータ
    bw = max(28, pw // 3)
    bh = max(4, ph // 150)
    bx = (pw - bw) // 2
    by = ph - bottom_band // 2 - bh // 2
    home = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(home).rounded_rectangle(
        (0, 0, bw - 1, bh - 1), radius=bh // 2, fill=HOME_BAR
    )
    out.alpha_composite(home, (bx, by))

    return out


def drop_shadow(im: Image.Image, blur: int = 14, offset: tuple[int, int] = (0, 8)) -> Image.Image:
    w, h = im.size
    pad = blur * 2 + max(offset) + 8
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (w, h), (40, 48, 62, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    ox, oy = pad + offset[0], pad + offset[1]
    canvas.alpha_composite(shadow, (ox, oy))
    canvas.alpha_composite(im, (pad, pad))
    return canvas


def main() -> None:
    for p in SOURCES:
        if not p.is_file():
            raise FileNotFoundError(p)

    screens = [Image.open(p).convert("RGB") for p in SOURCES]

    content_w = CANVAS_W - SIDE * 2
    content_h = CANVAS_H - SIDE * 2
    cols = len(screens)
    total_gap = (cols - 1) * GAP

    ar_phone = 2.08
    pw = min(
        (content_w - total_gap) // cols,
        int(content_h / ar_phone),
    )
    ph = int(pw * ar_phone)
    if ph > content_h:
        ph = content_h
        pw = int(ph / ar_phone)

    handsets = [phone_mock(s, pw, ph) for s in screens]
    row_w = cols * pw + total_gap

    base = Image.new("RGBA", (CANVAS_W, CANVAS_H), BG + (255,))
    start_x = SIDE + (content_w - row_w) // 2
    start_y = SIDE + (content_h - ph) // 2

    x = start_x
    for handset in handsets:
        framed = drop_shadow(handset)
        pad = (framed.size[0] - pw) // 2
        base.alpha_composite(framed, (x - pad, start_y - pad))
        x += pw + GAP

    base.convert("RGB").save(OUT, format="JPEG", quality=92, optimize=True)
    print(f"Wrote {OUT} (mock {pw}×{ph}, row {row_w}px)")


if __name__ == "__main__":
    main()
