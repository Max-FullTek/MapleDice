"""
auto_dice_hotkey.py  (修正版)
先點 → 等動畫 → 再 OCR；OCR 最多重試 3 次
F8 重新框選  |  F9 開始/暫停  |  Esc 退出
"""
import json, time, cv2, numpy as np, pytesseract, pyautogui as pg, keyboard
from mss import mss
from pathlib import Path

CONFIG = Path("roi.json")
TARGET = {"str":4,"dex":4,"int":13,"luk":4}
LABELS = ["str","dex","int","luk","dice"]
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESS_CFG = r"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"
ANIMATION_DELAY = 2.0

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
sct = mss()
running, need_reselect = False, False
ROI, DICE_POS = {}, (0,0)

def grab_desktop():
    mon = sct.monitors[0]
    return np.array(sct.grab(mon)), mon

def interactive_config():
    img, mon = grab_desktop()
    cv2.namedWindow("ROI", cv2.WINDOW_NORMAL)
    cv2.imshow("ROI", img)
    roi, dice_pos = {}, (0,0)
    for label in LABELS:
        tip = "骰子按鈕" if label=="dice" else label.upper()
        print(f"請框 {tip}，Enter 完成")
        x,y,w,h = cv2.selectROI("ROI", img, showCrosshair=True)
        if label=="dice":
            dice_pos = (x+w//2+mon["left"], y+h//2+mon["top"])
        else:
            roi[label]=(x+mon["left"],y+mon["top"],x+w+mon["left"],y+h+mon["top"])
    cv2.destroyWindow("ROI")
    CONFIG.write_text(json.dumps({"roi":roi,"dice_pos":dice_pos},indent=2,ensure_ascii=False))
    return roi, dice_pos

def load_config():
    if CONFIG.exists():
        d=json.loads(CONFIG.read_text())
        return d["roi"], tuple(d["dice_pos"])
    return interactive_config()

ROI, DICE_POS = load_config()

from datetime import datetime
DEBUG_DIR = Path("ocr_debug")
DEBUG_DIR.mkdir(exist_ok=True)

def get_stat(name, retries=2):
    x1, y1, x2, y2 = ROI[name]
    grab = sct.grab({"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1})
    img  = cv2.cvtColor(np.array(grab), cv2.COLOR_BGRA2GRAY)

    # 1️⃣ 放大 3 倍
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    # 2️⃣ 銳化
    blur = cv2.GaussianBlur(img, (0, 0), 1)
    sharp = cv2.addWeighted(img, 1.5, blur, -0.5, 0)

    # 3️⃣ 固定 threshold
    _, proc = cv2.threshold(sharp, 180, 255, cv2.THRESH_BINARY_INV)
    txt = pytesseract.image_to_string(proc, config=TESS_CFG).strip()
    if txt.isdigit():
        return int(txt)

    # 若失敗，再試一次 adaptive
    proc = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY_INV, 11, 2)
    txt = pytesseract.image_to_string(proc, config=TESS_CFG).strip()
    if txt.isdigit():
        return int(txt)

    # 兩次都失敗就回 -1 及存圖
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    cv2.imwrite(str(DEBUG_DIR / f"debug_{name}_{ts}.png"), img)
    print(f"[OCR FAIL] {name.upper()} → debug_{name}_{ts}.png")
    return -1



def all_ok(stats): return all(stats[k]>=TARGET[k] for k in TARGET)

def toggle_run():
    global running
    running = not running
    print("\n▶ 開始" if running else "\n⏸ 暫停")

def flag_reselect():
    global running, need_reselect
    running=False; need_reselect=True
    print("\n🔄 將在下一輪進入重新框選…")

keyboard.add_hotkey('f9', toggle_run)
keyboard.add_hotkey('f8', flag_reselect)
keyboard.add_hotkey('esc', lambda: exit(0))

print("F9 開始/暫停 | F8 重新框選 | Esc 結束")
print("程式已啟動，預設『暫停』，請按 F9 開始刷骰…")

while True:
    if need_reselect:
        ROI, DICE_POS = interactive_config()
        need_reselect = False
        print("請按 F9 開始 / 繼續")
        continue

    if not running:
        time.sleep(0.1)
        continue

    pg.click(DICE_POS)                 # ① 點骰子
    time.sleep(ANIMATION_DELAY)        # ② 等動畫

    stats = {k: get_stat(k) for k in TARGET}   # ③ OCR
    print(stats, end="\r")                      # ④ 立即顯示

    if all_ok(stats):                          # ⑤ 判斷目標
        print(f"\n🎉 命中：{stats}")
        break
