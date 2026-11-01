"""Gera a animação 'terminal hacker azul' do README do Giovanni.

Uso:  python3 render.py            -> gera terminal.mp4 e terminal.gif
      python3 render.py --frame 9  -> salva só o quadro do segundo 9 (prévia)
Requer: Pillow e ffmpeg.
"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 900, 530, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
f_txt = ImageFont.truetype(FONT, 17)
f_bold = ImageFont.truetype(FONT_B, 17)
f_big = ImageFont.truetype(FONT_B, 30)
f_bar = ImageFont.truetype(FONT, 14)

# paleta (tudo em azul)
BG = (4, 9, 20)
WIN = (7, 16, 34)
BAR = (11, 26, 52)
EDGE = (31, 78, 150)
PROMPT = (77, 163, 255)
CMD = (200, 228, 255)
OUT = (140, 196, 255)
DIM = (62, 104, 160)
ACC = (0, 170, 255)
NAME = (225, 242, 255)

PROMPT_TXT = "giovanni@cyber:~$ "
CPS = 24  # caracteres digitados por segundo

# roteiro: (início em s, tipo, conteúdo)
#   cmd -> digita o comando depois do prompt
#   out -> lista de (texto, cor, fonte); aparece de uma vez
#   big -> nome em destaque, revelado letra a letra
#   bar -> barra de progresso
SCRIPT = [
    (0.6, "cmd", "whoami"),
    (1.4, "big", "Giovanni Benedetti"),
    (2.6, "out", [("  Desenvolvedor Full Stack Jr.", OUT, f_bold), ("  |  ", DIM, f_txt), ("Estudante de Cyber Security", ACC, f_txt)]),
    (3.6, "cmd", "cat stack.txt"),
    (4.5, "out", [("  front  ", DIM, f_txt), ("›  ", ACC, f_txt), ("React  ·  Next.js  ·  Tailwind CSS", OUT, f_txt)]),
    (4.8, "out", [("  back   ", DIM, f_txt), ("›  ", ACC, f_txt), ("Node.js  ·  Express  ·  JWT", OUT, f_txt)]),
    (5.1, "out", [("  dados  ", DIM, f_txt), ("›  ", ACC, f_txt), ("MySQL  ·  MongoDB", OUT, f_txt)]),
    (5.4, "out", [("  tools  ", DIM, f_txt), ("›  ", ACC, f_txt), ("Git  ·  Docker  ·  Figma  ·  VS Code", OUT, f_txt)]),
    (5.7, "out", [("  sec    ", DIM, f_txt), ("›  ", ACC, f_txt), ("Linux · Bash · Python · Kali · Nmap · Wireshark · Burp Suite", OUT, f_txt)]),
    (6.6, "cmd", "./github --stats giovannibenedetti"),
    (8.2, "bar", 2.0),
    (10.6, "cmd", "open https://giovannibenedetti.tech"),
    (12.3, "out", [("  ✔ ", ACC, f_bold), ("conexão segura estabelecida", OUT, f_txt)]),
    (13.0, "cmd", ""),
]
DURATION = 17.0

def line_h(kind):
    return 44 if kind == "big" else 27

def text(d, x, y, s, color, font):
    d.text((x, y), s, fill=color, font=font)
    return x + d.textlength(s, font=font)

def draw_frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # janela
    d.rounded_rectangle((18, 16, W - 18, H - 16), 14, fill=WIN, outline=EDGE, width=2)
    d.rounded_rectangle((19, 17, W - 19, 54), 13, fill=BAR)
    d.rectangle((19, 40, W - 19, 54), fill=BAR)
    for i, c in enumerate([(30, 90, 170), (45, 125, 220), (90, 175, 255)]):
        d.ellipse((38 + i * 22, 29, 50 + i * 22, 41), fill=c)
    title = "giovanni@cyber: ~  —  zsh"
    d.text(((W - d.textlength(title, font=f_bar)) / 2, 27), title, fill=DIM, font=f_bar)

    layer = Image.new("RGB", (W, H), (0, 0, 0))   # texto (recebe brilho)
    ld = ImageDraw.Draw(layer)
    x0, y = 44, 72
    cursor = None
    for start, kind, data in SCRIPT:
        if t < start:
            break
        el = t - start
        if kind == "cmd":
            x = text(ld, x0, y, PROMPT_TXT, PROMPT, f_bold)
            n = min(len(data), int(el * CPS))
            x = text(ld, x, y, data[:n], CMD, f_txt)
            cursor = (x, y)
        elif kind == "big":
            n = min(len(data), int(el * 30))
            x = text(ld, x0 + 14, y + 2, data[:n], NAME, f_big)
            if n < len(data):
                ld.rectangle((x + 2, y + 6, x + 16, y + 36), fill=ACC)
            cursor = None
        elif kind == "out":
            x = x0
            for s, c, f in data:
                x = text(ld, x, y, s, c, f)
            cursor = None
        elif kind == "bar":
            p = min(1.0, el / data)
            cells = 24
            full = int(p * cells)
            x = text(ld, x0, y, "  [", DIM, f_txt)
            x = text(ld, x, y, "█" * full, ACC, f_txt)
            x = text(ld, x, y, "░" * (cells - full), (24, 52, 92), f_txt)
            x = text(ld, x, y, f"] {int(p * 100):3d}%", OUT, f_txt)
            if p >= 1:
                text(ld, x + 18, y, "stats ao vivo logo abaixo ↓", ACC, f_bold)
            cursor = None
        y += line_h(kind)

    # cursor piscando
    if cursor and int(t * 2.2) % 2 == 0:
        cx, cy = cursor
        ld.rectangle((cx + 1, cy + 2, cx + 10, cy + 21), fill=ACC)

    glow = layer.filter(ImageFilter.GaussianBlur(6))
    glow = Image.eval(glow, lambda v: int(v * 0.55))
    img = Image.composite(img, img, Image.new("L", (W, H), 255))
    from PIL import ImageChops
    img = ImageChops.add(img, glow)
    img = ImageChops.lighter(img, layer)

    # linhas de varredura discretas
    sd = ImageDraw.Draw(img, "RGBA")
    for yy in range(18, H - 16, 3):
        sd.line((20, yy, W - 20, yy), fill=(0, 0, 0, 38))
    return img

def main():
    if "--frame" in sys.argv:
        s = float(sys.argv[sys.argv.index("--frame") + 1])
        draw_frame(s).save(f"preview_{s:g}s.png")
        return
    tmp = "terminal.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                          "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for i in range(int(DURATION * FPS)):
        p.stdin.write(draw_frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg falhou")
    import os
    os.replace(tmp, "terminal.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "terminal.mp4", "-vf",
                    "fps=15,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle",
                    "-loop", "0", "terminal.gif"], check=True)

if __name__ == "__main__":
    main()
