
import ctypes
import math
import random
import sys
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

try:                 # 高 DPI 屏按物理像素渲染，否则系统拉伸会让图发糊
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    SCALE = ctypes.windll.user32.GetDpiForSystem() / 96.0
except Exception:
    SCALE = 1.0

KEY = "#ff00ff"      # 色键，图里不能出现这个颜色
HEIGHT = int(200 * SCALE)   # 修改这里的数值太改变小菲的大小
FRAMES = 7           # 呼吸动画帧数
TICK = 90            # 呼吸每帧间隔 (ms)
HERE = Path(__file__).resolve().parent
SRC = HERE / "pet.png"
if getattr(sys, "frozen", False):        # 打包后优先用 exe 同目录的图
    alt = Path(sys.executable).resolve().parent / "pet.png"
    if alt.exists():
        SRC = alt

root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes("-topmost", True)
root.wm_attributes("-transparentcolor", KEY)
root.configure(bg=KEY)

src = Image.open(SRC).convert("RGBA")
base_w = int(src.width * HEIGHT / src.height)
mid = src.resize((base_w * 2, HEIGHT * 2), Image.LANCZOS)

breath = []
for i in range(FRAMES):
    s = 1.0 + 0.025 * math.sin(i / FRAMES * 2 * math.pi)
    breath.append(mid.resize((int(base_w * s), int(HEIGHT * s)), Image.LANCZOS))


def to_tk(img):

    rgb = Image.new("RGB", img.size, (255, 0, 255))
    mask = img.split()[3].point(lambda v: 255 if v >= 128 else 0)
    rgb.paste(img.convert("RGB"), mask=mask)
    return ImageTk.PhotoImage(rgb)


right = [to_tk(f) for f in breath]
left = [to_tk(f.transpose(Image.FLIP_LEFT_RIGHT)) for f in breath]

W = max(f.width() for f in right) + 2
H = max(f.height() for f in right) + 2

cv = tk.Canvas(root, width=W, height=H, bg=KEY, highlightthickness=0)
cv.pack()
sprite = cv.create_image(W // 2, H // 2, image=right[0])

sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
x, y = sw / 2, sh / 2
vx, vy = 2.8, -1.6
fi = 0


def step():
    global x, y, vx, vy
    x, y = x + vx, y + vy
    if x <= 0 or x >= sw - W:
        vx, x = -vx, max(0, min(x, sw - W))
    if y <= 0 or y >= sh - H:
        vy, y = -vy, max(0, min(y, sh - H))
    root.geometry("+%d+%d" % (int(x), int(y)))
    root.after(30, step)


def breathe():
    global fi
    fi = (fi + 1) % FRAMES
    cv.itemconfig(sprite, image=(right if vx >= 0 else left)[fi])
    root.after(TICK, breathe)


def wander():
    global vx, vy
    if random.random() < 0.45:
        vx = random.choice((-1, 1)) * random.uniform(1.6, 3.4)
        vy = random.choice((-1, 1)) * random.uniform(1.0, 2.6)
    root.after(random.randint(1800, 4500), wander)


drag = [0, 0]


def press(e):
    drag[0], drag[1] = e.x, e.y


def move(e):
    global x, y
    x, y = e.x_root - drag[0], e.y_root - drag[1]
    root.geometry("+%d+%d" % (x, y))


cv.bind("<Button-1>", press)
cv.bind("<B1-Motion>", move)
cv.bind("<Button-3>", lambda e: root.destroy())

step()
breathe()
wander()
root.mainloop()
