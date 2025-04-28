# 楓之谷自動擲骰工具 (Maple Dice)

這是一個適用於楓之谷遊戲的自動擲骰工具，能夠自動點擊骰子按鈕並使用OCR技術識別屬性值，當屬性達到目標值時自動停止。

## 🔧 系統需求

- Windows 作業系統
- Python 3.6 或更高版本
- Tesseract OCR 引擎

## 📦 依賴套件

```
numpy
opencv-python
pytesseract
pyautogui
keyboard
mss
```

## 📥 安裝步驟

1. 安裝 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)（預設安裝路徑：`C:\Program Files\Tesseract-OCR\`）

2. 安裝所需的 Python 套件：

```bash
pip install numpy opencv-python pytesseract pyautogui keyboard mss
```

3. 下載本項目文件

## 🚀 使用方法

1. 執行程式：

```bash
python maple-dice.py
```

2. 首次執行時，程式會要求您框選以下區域：
   - STR 屬性值
   - DEX 屬性值
   - INT 屬性值
   - LUK 屬性值
   - 骰子按鈕

3. 使用熱鍵控制程式：
   - `F9`: 開始/暫停自動擲骰
   - `F8`: 重新框選區域
   - `Esc`: 退出程式

4. 程式會自動執行直到所有屬性達到目標值

## ⚙️ 配置

在程式碼中，您可以修改 `TARGET` 變數來調整目標屬性值：

```python
TARGET = {"str":4, "dex":4, "int":13, "luk":4}
```

您也可以調整 `ANIMATION_DELAY` 變數來配置點擊後等待的動畫時間（單位：秒）。

## 🔍 除錯

若 OCR 識別失敗，程式會自動將截圖保存到 `ocr_debug` 資料夾中，以便您檢查和調整。

## 📝 注意事項

- 請確保遊戲視窗在執行程式時處於前景
- 使用此工具時請遵守遊戲規則
- 此工具僅供學習和研究用途