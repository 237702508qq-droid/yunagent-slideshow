#!/usr/bin/env python3
"""生成《云桌面 AI Agent 记忆增强方案》演示配图 — 商务深蓝风格，纯 PIL 绘制。"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)

# ---- palette (business deep-blue) ----
NAVY = (11, 31, 59)        # deep navy background
NAVY2 = (17, 42, 78)
CARD = (23, 52, 92)
LINE = (47, 82, 128)
WHITE = (244, 249, 255)
GREY = (166, 186, 212)
SKY = (94, 168, 255)       # light blue accent
SKY_DIM = (94, 168, 255, 36)
GOLD = (240, 180, 60)

FONT_PATH = "/home/song/screenpipe-deck/slideshow/assets/NotoSansCJK-Bold.ttc"


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def canvas(w, h, bg=NAVY):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img, "RGBA")
    return img, d


def glow(d, cx, cy, r, color, alpha=40):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))


def arrow(d, x1, y1, x2, y2, color=SKY, w=4):
    d.line([x1, y1, x2, y2], fill=color, width=w)
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 18
    for s in (-1, 1):
        a = ang + math.pi + s * 0.45
        d.line([x2, y2, x2 + L * math.cos(a), y2 + L * math.sin(a)], fill=color, width=w)


def rounded(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)


# =====================================================================
# 1. cover.png — 封面：抽象"记忆 + 云桌面"概念图
#    一排屏幕 + 从屏幕升起的信息流汇入大脑/记忆节点
# =====================================================================
def cover():
    W, H = 1100, 1240
    img, d = canvas(W, H)
    # ambient glow
    glow(d, 550, 380, 420, SKY, 26)
    glow(d, 550, 900, 380, (40, 90, 170), 30)

    # --- cloud/desktop frame at bottom: 3 screens ---
    sw, sh = 250, 158
    xs = [95, 425, 755]
    ys = 880
    labels = ["文档", "沟通", "浏览"]
    for i, x in enumerate(xs):
        rounded(d, [x, ys, x + sw, ys + sh], 18, fill=CARD, outline=LINE, width=3)
        d.rectangle([x + 14, ys + 14, x + sw - 14, ys + 44], fill=NAVY2)
        for r in range(3):
            d.rounded_rectangle(
                [x + 18, ys + 62 + r * 30, x + sw - 30 - (r % 3) * 55, ys + 62 + r * 30 + 14],
                7, fill=(LINE[0], LINE[1], LINE[2], 150),
            )
        d.rectangle([x + 105, ys + sh, x + 145, ys + sh + 22], fill=LINE)
        d.rectangle([x + 70, ys + sh + 22, x + 180, ys + sh + 30], fill=LINE)
        d.text((x + sw // 2, ys + 28), labels[i], font=font(22), fill=GREY, anchor="mm")

    # --- memory core (brain-ish concentric rings) ---
    cx, cy = 550, 360
    for rr, a in [(220, 26), (165, 40), (110, 60)]:
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=SKY + (a,), width=3)
    glow(d, cx, cy, 78, SKY, 90)
    d.ellipse([cx - 72, cy - 72, cx + 72, cy + 72], fill=(18, 52, 98), outline=SKY, width=4)
    d.text((cx, cy - 20), "桌面", font=font(44), fill=WHITE, anchor="mm")
    d.text((cx, cy + 34), "记忆", font=font(44), fill=WHITE, anchor="mm")

    # --- data streams from screens to core ---
    for x in xs:
        sx = x + sw // 2
        sy = ys - 6
        # dotted stream
        steps = 26
        for k in range(steps):
            t = k / (steps - 1)
            px = sx + (cx - sx) * t + math.sin(t * 5.2) * 46 * math.sin(t * math.pi)
            py = sy + (cy + 60 - sy) * t
            d.ellipse([px - 3.4, py - 3.4, px + 3.4, py + 3.4], fill=SKY + (int(150 * (1 - t * 0.4)),))
    # small chips floating (记忆条目)
    chips = ["张三 的文件", "周一 周会", "方案.docx", "PPT 模板", "客户 A", "周五 周报"]
    pos = [(150, 620), (860, 600), (260, 500), (800, 470), (120, 760), (880, 740)]
    for (tx, ty), label in zip(pos, chips):
        tw = d.textlength(label, font=font(24))
        rounded(d, [tx - tw / 2 - 18, ty - 22, tx + tw / 2 + 18, ty + 22], 22,
                fill=(23, 52, 92, 235), outline=SKY + (110,), width=2)
        d.text((tx, ty), label, font=font(24), fill=WHITE, anchor="mm")

    # VDI badge
    rounded(d, [W // 2 - 130, H - 92, W // 2 + 130, H - 40], 26, fill=(16, 40, 74), outline=LINE, width=2)
    d.text((W // 2, H - 66), "VDI 云桌面 · 本地闭环", font=font(26), fill=SKY, anchor="mm")

    img = img.filter(ImageFilter.GaussianBlur(0.4))
    img.save(os.path.join(OUT, "cover.png"))
    print("cover.png", img.size)


# =====================================================================
# 2. arch.png — P4 三层架构：采集层 → 记忆层 → 增强层
# =====================================================================
def arch():
    W, H = 1160, 1060
    img, d = canvas(W, H)
    d.text((W // 2, 46), "三层架构 · 数据全程留在云桌面内", font=font(34), fill=GREY, anchor="mm")

    layers = [
        ("采集层", "无障碍树 + 智能截图", "不录屏 · 内容哈希脱敏 · 密码框自动排除", 170),
        ("记忆层", "工作上下文数据库 · 滚动记录", "文件往来 · 沟通对象 · 文档习惯 · 应用图谱", 470),
        ("增强层", "Agent 调用记忆 → 自动补全 5W", "谁 · 何时 · 什么文件 · 什么格式 · 什么目标", 770),
    ]
    for i, (t, m, s, y) in enumerate(layers):
        hl = i == 1
        bc = SKY if hl else LINE
        rounded(d, [80, y, W - 80, y + 220], 22,
                fill=(20, 48, 88) if not hl else (24, 60, 110), outline=bc, width=4)
        d.text((150, y + 74), t, font=font(46), fill=SKY if hl else WHITE, anchor="lm")
        d.text((150, y + 140), m, font=font(30), fill=WHITE, anchor="lm")
        d.text((150, y + 182), s, font=font(24), fill=GREY, anchor="lm")
        # icon chip
        rounded(d, [W - 250, y + 60, W - 110, y + 160], 18, fill=(13, 33, 62), outline=bc, width=2)
        ic = ["⌨", "🗄", "✦"][i]
        d.text((W - 180, y + 108), ic, font=font(52), fill=SKY, anchor="mm")
        if i < 2:
            arrow(d, W // 2 - 60, y + 224, W // 2 - 60, y + 300, SKY, 5)
            d.text((W // 2 - 20, y + 262), "整理 / 调用", font=font(22), fill=GREY, anchor="lm")

    # side loop: 用户 ←→ 增强
    d.text((W // 2, H - 44), "用户照常办公，无感知 · Agent 输出贴合岗位与习惯", font=font(26), fill=SKY, anchor="mm")
    img.save(os.path.join(OUT, "arch.png"))
    print("arch.png", img.size)


# =====================================================================
# 3. flow-compare.png — P5 前后对比流程（30 秒 vs 5 分钟）
# =====================================================================
def flow_compare():
    W, H = 1160, 1000
    img, d = canvas(W, H)
    # two columns
    colw = 510
    # ---- left: 改造前 ----
    lx = 60
    rounded(d, [lx, 60, lx + colw, H - 60], 24, fill=(18, 34, 56), outline=(90, 110, 140), width=3)
    d.text((lx + colw // 2, 116), "改造前 · 5 分钟起步", font=font(38), fill=(210, 140, 140), anchor="mm")
    steps_b = [
        "Agent 反问：哪个文件？",
        "张三是谁？什么格式？",
        "用户手动翻找文件",
        "手动上传 + 说明要求",
    ]
    y = 210
    for s in steps_b:
        rounded(d, [lx + 50, y, lx + colw - 50, y + 110], 16, fill=(26, 44, 68), outline=(80, 100, 130), width=2)
        d.text((lx + colw // 2, y + 54), s, font=font(27), fill=GREY, anchor="mm")
        if s != steps_b[-1]:
            arrow(d, lx + colw // 2, y + 112, lx + colw // 2, y + 158, (150, 120, 120), 4)
        y += 158
    d.text((lx + colw // 2, H - 120), "人工纠偏 · 反复打断", font=font(28), fill=(210, 140, 140), anchor="mm")

    # ---- right: 改造后 ----
    rx = W - 60 - colw
    rounded(d, [rx, 60, rx + colw, H - 60], 24, fill=(16, 44, 78), outline=SKY, width=3)
    d.text((rx + colw // 2, 116), "改造后 · 30 秒内", font=font(38), fill=SKY, anchor="mm")
    steps_a = [
        "记忆定位：昨天 + 张三 + 方案.docx",
        "自动打开 · 按既往习惯转换",
        "输出即用的 PPT",
    ]
    y = 230
    for i, s in enumerate(steps_a):
        rounded(d, [rx + 50, y, rx + colw - 50, y + 120], 16,
                fill=(22, 60, 108), outline=SKY, width=3)
        d.text((rx + colw // 2, y + 60), s, font=font(28), fill=WHITE, anchor="mm")
        if i < len(steps_a) - 1:
            arrow(d, rx + colw // 2, y + 122, rx + colw // 2, y + 178, SKY, 5)
        y += 178
    d.text((rx + colw // 2, H - 120), "一次说清 · 直接交付", font=font(28), fill=SKY, anchor="mm")

    # center vs
    cx = W // 2
    d.ellipse([cx - 44, H // 2 - 44, cx + 44, H // 2 + 44], fill=NAVY, outline=LINE, width=3)
    d.text((cx, H // 2), "VS", font=font(40), fill=WHITE, anchor="mm")
    # 指令 chip on top
    rounded(d, [cx - 250, -6, cx + 250, 52], 26, fill=(13, 33, 62), outline=GOLD + (200,), width=3)
    d.text((cx, 22), "“把昨天张三发我的方案改成 PPT”", font=font(27), fill=GOLD, anchor="mm")

    img.save(os.path.join(OUT, "flow-compare.png"))
    print("flow-compare.png", img.size)


# =====================================================================
# 4. shield.png — P9 四道防线盾牌图
# =====================================================================
def shield():
    W, H = 1000, 1120
    img, d = canvas(W, H)
    cx = W // 2
    # shield body
    pts = [(cx, 90), (cx + 300, 200), (cx + 300, 560),
           (cx + 170, 830), (cx, 960), (cx - 170, 830), (cx - 300, 560), (cx - 300, 200)]
    d.polygon(pts, fill=(17, 44, 82), outline=SKY)
    d.line(pts + [pts[0]], fill=SKY, width=6)
    inner = [(cx, 150), (cx + 245, 245), (cx + 245, 545), (cx + 135, 775), (cx, 890),
             (cx - 135, 775), (cx - 245, 545), (cx - 245, 245)]
    d.line(inner + [inner[0]], fill=SKY + (120,), width=2)
    d.text((cx, 420), "数据", font=font(56), fill=WHITE, anchor="mm")
    d.text((cx, 500), "不出云桌面", font=font(44), fill=SKY, anchor="mm")

    # four defense labels around
    items = [
        ("本地闭环", "记忆只在云桌面内处理存储", 60, 1040),
        ("企业主权", "开关 / 保留时长 / 排除名单", 500, 1040),
        ("用户知情", "记忆可视化 · 可查看可删除", 60, 780),
        ("脱敏处理", "密码框 / 支付页不采集", 500, 780),
    ]
    for t, s, x, y in items:
        pass
    # better: 2x2 grid below
    gy = 960
    for i, (t, s, _, _) in enumerate(items):
        gx = 60 + (i % 2) * 470
        gyy = gy + (i // 2) * 0  # unused
    img.save(os.path.join(OUT, "shield.png"))
    print("shield.png (base)")


def shield2():
    W, H = 1160, 1060
    img, d = canvas(W, H)
    cx = W // 2
    # shield
    pts = [(cx, 60), (cx + 240, 150), (cx + 240, 440), (cx + 130, 650), (cx, 740),
           (cx - 130, 650), (cx - 240, 440), (cx - 240, 150)]
    d.polygon(pts, fill=(17, 44, 82), outline=SKY)
    d.line(pts + [pts[0]], fill=SKY, width=6)
    for k, lab in enumerate(["盾"]):
        pass
    d.text((cx, 330), "数据", font=font(52), fill=WHITE, anchor="mm")
    d.text((cx, 400), "不出云桌面", font=font(40), fill=SKY, anchor="mm")
    d.text((cx, 530), "本地闭环 · 企业主权", font=font(24), fill=GREY, anchor="mm")
    d.text((cx, 570), "用户知情 · 全程脱敏", font=font(24), fill=GREY, anchor="mm")

    # four cards below
    cards = [
        ("① 本地闭环", "记忆数据只在云桌面内处理与存储，不外传"),
        ("② 企业主权", "管理员控制开关 / 保留时长 / 敏感应用排除名单"),
        ("③ 用户知情", "记忆可视化，员工可查看并删除自己的记忆"),
        ("④ 脱敏处理", "密码框、支付页等敏感界面自动排除采集"),
    ]
    gy = 800
    for i, (t, s) in enumerate(cards):
        gx = 40 + (i % 2) * 560
        gyy = gy + (i // 2) * 120
        rounded(d, [gx, gyy, gx + 540, gyy + 106], 16, fill=(20, 48, 88), outline=LINE, width=2)
        d.text((gx + 26, gyy + 34), t, font=font(28), fill=SKY, anchor="lm")
        d.text((gx + 26, gyy + 76), s, font=font(22), fill=WHITE, anchor="lm")
    img.save(os.path.join(OUT, "shield.png"))
    print("shield.png", img.size)


# =====================================================================
# 5. profiles.png — P6 四类工作画像
# =====================================================================
def profiles():
    W, H = 1160, 1000
    img, d = canvas(W, H)
    d.text((W // 2, 50), "越用越懂你 · 四类工作画像持续沉淀", font=font(34), fill=GREY, anchor="mm")

    cards = [
        ("人际图谱", "谁给你发过什么", "和谁的协作最多", 100, 130),
        ("文档习惯", "PPT 结构偏好", "周报格式 · 命名规范", 640, 130),
        ("工作边界", "岗位职责关键词", "常用系统与工具", 100, 600),
        ("时间规律", "周一开周会", "周五交周报 · 主动提醒", 640, 600),
    ]
    for i, (t, l1, l2, x, y) in enumerate(cards):
        rounded(d, [x, y, x + 420, y + 320], 22, fill=(20, 48, 88), outline=SKY, width=3)
        # icon ring
        icx, icy = x + 210, y + 92
        d.ellipse([icx - 46, icy - 46, icx + 46, icy + 46], fill=(13, 33, 62), outline=SKY, width=3)
        ic = ["👥", "📄", "🧭", "🕐"][i]
        d.text((icx, icy), ic, font=font(44), fill=SKY, anchor="mm")
        d.text((x + 210, y + 180), t, font=font(36), fill=WHITE, anchor="mm")
        d.text((x + 210, y + 234), l1, font=font(24), fill=GREY, anchor="mm")
        d.text((x + 210, y + 272), l2, font=font(24), fill=GREY, anchor="mm")

    # connecting memory hub in middle
    cx, cy = W // 2, 525
    d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=(16, 40, 74), outline=SKY, width=4)
    d.text((cx, cy), "个人", font=font(28), fill=WHITE, anchor="mm")
    d.text((cx, cy + 32), "上下文", font=font(28), fill=WHITE, anchor="mm")
    for (hx, hy) in [(310, 450), (850, 450), (310, 600), (850, 600)]:
        arrow(d, hx, hy, cx, cy, SKY + (130,), 3)
    d.text((W // 2, H - 50), "全部在云桌面本地处理 · 记忆只服务这一个用户", font=font(26), fill=SKY, anchor="mm")
    img.save(os.path.join(OUT, "profiles.png"))
    print("profiles.png", img.size)


# =====================================================================
# 6. bridge.png — P2/P3 问题页：断桥概念图（Agent 与工作环境之间）
# =====================================================================
def bridge():
    W, H = 1160, 560
    img, d = canvas(W, H)
    # left island: Agent
    rounded(d, [70, 200, 360, 360], 24, fill=(22, 52, 94), outline=LINE, width=3)
    d.text((215, 258), "AI Agent", font=font(36), fill=WHITE, anchor="mm")
    d.text((215, 312), "只有对话框上下文", font=font(23), fill=GREY, anchor="mm")
    # right island: 真实工作环境
    rounded(d, [800, 200, 1090, 360], 24, fill=(22, 52, 94), outline=LINE, width=3)
    d.text((945, 258), "真实工作环境", font=font(36), fill=WHITE, anchor="mm")
    d.text((945, 312), "文件 · 沟通 · 岗位 · 习惯", font=font(23), fill=GREY, anchor="mm")
    # broken bridge
    d.line([380, 280, 540, 280], fill=(200, 120, 120), width=8)
    d.line([620, 280, 780, 280], fill=(200, 120, 120), width=8)
    # gap + question marks
    for i, (qx, qy, fs) in enumerate([(580, 250, 44), (545, 300, 30), (615, 320, 26)]):
        d.text((qx, qy), "?", font=font(fs), fill=(220, 140, 140), anchor="mm")
    d.text((580, 400), "上下文断层", font=font(34), fill=(220, 150, 150), anchor="mm")
    d.text((580, 452), "每一次反问与纠偏，都在消耗用户耐心", font=font(24), fill=GREY, anchor="mm")
    # question rain top
    qs = [("这是哪个文件？", 120), ("周报什么格式？", 420), ("“usual”是什么？", 720), ("张三是谁？", 960)]
    for t, x in qs:
        tw = d.textlength(t, font=font(23))
        rounded(d, [x - tw / 2 - 16, 60, x + tw / 2 + 16, 106], 23, fill=(30, 44, 66), outline=(120, 100, 110), width=2)
        d.text((x, 82), t, font=font(23), fill=(215, 180, 180), anchor="mm")
    img.save(os.path.join(OUT, "bridge.png"))
    print("bridge.png", img.size)


# =====================================================================
# 7. gacha.png — 问题1 配图："抽卡"比喻（Agent 猜你要什么）
# =====================================================================
def gacha():
    W, H = 1160, 560
    img, d = canvas(W, H)
    # machine body
    rounded(d, [430, 90, 730, 470], 28, fill=(22, 52, 94), outline=LINE, width=3)
    # glass globe
    d.ellipse([470, 120, 690, 340], fill=(13, 33, 62), outline=SKY, width=3)
    # balls inside
    balls = [(530, 240, (120, 140, 170)), (620, 220, (90, 120, 160)), (575, 285, (140, 160, 190)),
             (635, 285, (110, 130, 165)), (525, 300, (100, 125, 160))]
    for bx, by, c in balls:
        d.ellipse([bx - 26, by - 26, bx + 26, by + 26], fill=c + (255,) if len(c) == 3 else c, outline=(30, 60, 100))
    # question marks on balls
    for bx, by, _ in balls:
        d.text((bx, by), "?", font=font(26), fill=(25, 45, 75), anchor="mm")
    # slot
    rounded(d, [535, 370, 625, 470], 14, fill=(13, 33, 62), outline=LINE, width=2)
    d.text((580, 400), "输出", font=font(22), fill=GREY, anchor="mm")
    d.text((580, 445), "▼", font=font(22), fill=GREY, anchor="mm")

    d.text((580, 510), "不「懂你」的 Agent，只能靠抽卡猜你要什么", font=font(32), fill=(230, 190, 150), anchor="mm")

    # left annotation
    rounded(d, [60, 150, 360, 250], 18, fill=(24, 46, 76), outline=(120, 110, 100), width=2)
    d.text((210, 180), "很多提示词", font=font(28), fill=GREY, anchor="mm")
    d.text((210, 218), "也拦不住随机性", font=font(23), fill=(210, 170, 150), anchor="mm")
    arrow(d, 366, 200, 452, 210, (170, 150, 130), 4)
    # right annotation
    rounded(d, [800, 150, 1100, 250], 18, fill=(24, 46, 76), outline=(120, 110, 100), width=2)
    d.text((950, 180), "输出看运气", font=font(28), fill=GREY, anchor="mm")
    d.text((950, 218), "成功率高时低", font=font(23), fill=(210, 170, 150), anchor="mm")
    arrow(d, 708, 210, 794, 200, (170, 150, 130), 4)
    img.save(os.path.join(OUT, "gacha.png"))
    print("gacha.png", img.size)


# =====================================================================
# 8. dual.png — 方案核心：记忆双用途（桌面记忆 + 个人上下文）
# =====================================================================
def dual():
    W, H = 1160, 1020
    img, d = canvas(W, H)
    d.text((W // 2, 48), "一套操作数据 · 两种增强产出", font=font(34), fill=GREY, anchor="mm")

    # top: VDI 桌面
    rounded(d, [W // 2 - 330, 100, W // 2 + 330, 210], 20, fill=(16, 40, 74), outline=SKY, width=3)
    d.text((W // 2, 136), "VDI 云桌面 · 用户正常办公", font=font(32), fill=WHITE, anchor="mm")
    d.text((W // 2, 182), "启用桌面记忆：操作信息以数据库滚动记录", font=font(23), fill=GREY, anchor="mm")

    arrow(d, W // 2, 214, W // 2, 300, SKY, 5)
    d.text((W // 2 + 120, 258), "滚动记录", font=font(22), fill=GREY, anchor="lm")

    # middle: memory DB
    rounded(d, [W // 2 - 250, 306, W // 2 + 250, 430], 20, fill=(24, 60, 110), outline=SKY, width=4)
    d.text((W // 2, 348), "桌面记忆数据库", font=font(34), fill=WHITE, anchor="mm")
    d.text((W // 2, 396), "文件往来 · 沟通对象 · 操作轨迹 · 文档习惯", font=font(23), fill=GREY, anchor="mm")

    # two branches
    ly, ry = 330, 830
    arrow(d, W // 2 - 250, 368, 300, 520, SKY + (150,), 4)
    arrow(d, W // 2 + 250, 368, 860, 520, SKY + (150,), 4)

    # left output: Agent 桌面记忆
    rounded(d, [70, 526, 530, 760], 22, fill=(20, 48, 88), outline=SKY, width=3)
    d.text((300, 572), "① Agent 的「桌面记忆」", font=font(30), fill=SKY, anchor="mm")
    d.text((300, 626), "Agent 直接调用", font=font(25), fill=WHITE, anchor="mm")
    d.text((300, 666), "昨天和张三的沟通内容", font=font(25), fill=WHITE, anchor="mm")
    d.text((300, 706), "桌面上的数据 · 随时可回溯", font=font(25), fill=WHITE, anchor="mm")

    # right output: 个人上下文
    rounded(d, [630, 526, 1090, 760], 22, fill=(20, 48, 88), outline=SKY, width=3)
    d.text((860, 572), "② 模型整理为「个人上下文」", font=font(30), fill=SKY, anchor="mm")
    d.text((860, 626), "当前用户的岗位", font=font(25), fill=WHITE, anchor="mm")
    d.text((860, 666), "工作边界", font=font(25), fill=WHITE, anchor="mm")
    d.text((860, 706), "写作偏好", font=font(25), fill=WHITE, anchor="mm")

    # bottom value bar
    rounded(d, [70, 820, 1090, 940], 20, fill=(13, 33, 62), outline=SKY, width=2)
    d.text((580, 866), "Agent 回答成功率大幅提升（不再抽卡）", font=font(29), fill=WHITE, anchor="mm")
    d.text((580, 906), "模糊指令也能达成目标", font=font(29), fill=WHITE, anchor="mm")
    d.text((580, 988), "全程在云桌面内完成 · 数据不出域", font=font(24), fill=SKY, anchor="mm")
    img.save(os.path.join(OUT, "dual.png"))
    print("dual.png", img.size)


# =====================================================================
# 9. admin.png — 管理员文件分发 → 企业个性化 AI 服务
# =====================================================================
def admin():
    W, H = 1160, 620
    img, d = canvas(W, H)
    # admin console
    rounded(d, [70, 200, 380, 380], 22, fill=(20, 48, 88), outline=SKY, width=3)
    d.text((225, 256), "企业管理员", font=font(32), fill=WHITE, anchor="mm")
    d.text((225, 312), "统一控制台", font=font(23), fill=GREY, anchor="mm")
    # files
    fx = [470, 590, 710]
    labels = ["制度模板", "部门规范", "业务知识"]
    for x, lab in zip(fx, labels):
        rounded(d, [x, 240, x + 90, 320], 12, fill=(16, 40, 74), outline=GOLD, width=2)
        d.text((x + 45, 272), "📄", font=font(30), fill=WHITE, anchor="mm")
        d.text((x + 45, 352), lab, font=font(20), fill=GREY, anchor="mm")
        arrow(d, x + 45, 330, x + 45, 352, GOLD, 0)
    arrow(d, 386, 290, 452, 280, GOLD, 4)
    arrow(d, 806, 280, 872, 290, GOLD, 4)
    # VDI
    rounded(d, [880, 200, 1090, 380], 22, fill=(20, 48, 88), outline=SKY, width=3)
    d.text((985, 250), "全员 VDI", font=font(30), fill=WHITE, anchor="mm")
    d.text((985, 300), "桌面记忆", font=font(30), fill=SKY, anchor="mm")
    d.text((985, 344), "按部门自动注入", font=font(21), fill=GREY, anchor="mm")
    # title & bottom
    d.text((W // 2, 90), "管理员通过文件分发，实现企业个性化 AI 服务", font=font(34), fill=WHITE, anchor="mm")
    d.text((W // 2, 140), "一次分发 · 全员生效 · 记忆与上下文自动对齐企业规范", font=font(24), fill=GREY, anchor="mm")
    d.text((W // 2, 470), "例：销售部自动获得客户汇报模板，研发部自动对齐代码与文档规范", font=font(26), fill=SKY, anchor="mm")
    d.text((W // 2, 530), "新员工入职即继承团队协作上下文 · 人员流动不断档", font=font(24), fill=GREY, anchor="mm")
    img.save(os.path.join(OUT, "admin.png"))
    print("admin.png", img.size)


# =====================================================================
# 10. road.png — P10 三步落地路径
# =====================================================================
def road():
    W, H = 1160, 560
    img, d = canvas(W, H)
    d.text((W // 2, 70), "三步落地路径", font=font(36), fill=WHITE, anchor="mm")
    steps = [
        ("1", "试点验证", "20–50 人部门级 PoC", "验证采纳率与效率收益"),
        ("2", "场景深化", "按部门定制记忆模板", "管理员文件分发 · 对齐企业规范"),
        ("3", "全员推广", "统一部署全员生效", "习惯沉淀为企业数字资产"),
    ]
    x0 = 80
    for i, (no, t, l1, l2) in enumerate(steps):
        x = x0 + i * 360
        rounded(d, [x, 170, x + 300, 420], 22, fill=(20, 48, 88), outline=SKY, width=3)
        d.ellipse([x + 118, 130, x + 182, 194], fill=(13, 33, 62), outline=SKY, width=3)
        d.text((x + 150, 162), no, font=font(34), fill=SKY, anchor="mm")
        d.text((x + 150, 250), t, font=font(34), fill=WHITE, anchor="mm")
        d.text((x + 150, 310), l1, font=font(23), fill=GREY, anchor="mm")
        d.text((x + 150, 356), l2, font=font(21), fill=GREY, anchor="mm")
        if i < 2:
            arrow(d, x + 306, 295, x + 354, 295, SKY, 5)
    d.text((W // 2, 490), "让云桌面里的每一个 AI Agent，都成为懂你的数字同事", font=font(28), fill=SKY, anchor="mm")
    img.save(os.path.join(OUT, "road.png"))
    print("road.png", img.size)


if __name__ == "__main__":
    cover()
    bridge()
    gacha()
    dual()
    arch()
    flow_compare()
    profiles()
    shield2()
    admin()
    road()
    print("ALL DONE ->", OUT)
