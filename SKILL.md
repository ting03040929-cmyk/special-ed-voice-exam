---
name: special-ed-voice-exam
description: >-
  Generates fully self-contained, offline-compatible, voice-interactive adaptive web exams
  for special education and resource room students across subjects (Chinese, Mathematics, Daily Living).
  Trigger when the user requests "做成語音網頁版", "語音試卷", "互動試卷", "有語音的試卷",
  "特教語音測驗", "微軟語音網頁", or asks to convert Word (.docx) / JSON test papers into voice-interactive HTML apps.
  Features Microsoft Edge-TTS Taiwanese neural voice, Base64 embedded audio and images, prominent Question Voice Buttons,
  individual Option Voice Buttons, slow replay, high-contrast touch cards, and automated IEP scoring summaries.
---

# 特教無障礙語音互動適性試卷生成技能 (Special Ed Voice Exam)

本技能專為**特教班、資源班、識字量較低、聽覺學習或口語指認優先的學童**設計，可將任何現有試題（國語文、數學、生活常規等）轉化為 **100% 離線可用、自帶微軟 Edge-TTS 臺灣真人語音朗讀、具備大字體與獨立題目及選項語音按鈕** 的單一 HTML 互動試卷網頁。

---

## 🌟 核心特教無障礙規格與標準

1. **🎙️ 真人級語音合成 (Microsoft Edge-TTS)**：
   - 語音引擎：`zh-TW-HsiaoChenNeural`（溫暖、親切的臺灣國語女教師語音）。
   - 語速設定：`-5%`（適度放慢，咬字清晰，符合特教學童聽語辨識節奏）。
   - 數學科自動口語化：例如 `$5 + 3 = ?$` 轉為「五加三等於多少？」、`$25` 轉為「二十五元」、`08:30` 轉為「八點三十分」。
2. **🔊 雙層獨立語音按鈕機制**：
   - **題目區塊**：設置顯眼獨立的 **`🔊 聽題目`** 藍色大按鈕。
   - **情境公告**：設置 **`🔊 聽完整公告`** 琥珀色大按鈕。
   - **答案選項**：每一個選項卡片右側設置獨立的 **`🔊 聽選項`** 彩色按鈕（學生可單獨點擊按鈕反覆聆聽，不需擔心誤改選答案）。
   - **慢速重聽**：底部提供「📢 重聽題目」與「🐢 慢速重聽 (0.75x)」輔助按鈕。
3. **📦 100% 離線完全自包含 (Zero External Dependency)**：
   - 所有題目彩色圖卡、所有合成之 MP3 語音音訊，**全部以 Base64 數據格式內嵌於單一 `.html` 檔案中**。
   - 換電腦、複製到 USB 隨身碟、透過 LINE/雲端傳送至 iPad、Android 平板、教室大觸控白板，即使在**無網路環境**下皆可 100% 正常播放與顯示。
4. **👆 大字體與觸控友善排版**：
   - 純國字超大字體（20~24pt），免去注音符號干擾。
   - 超大觸控卡片，選取時帶有高對比藍色邊框與愉悅輕脆音效反饋。
5. **📝 自動計分與 IEP 檢核對照表**：
   - 作答完畢自動計算總分（滿分 100 分），並生成逐題對錯紀錄與標準答案對照表。
   - 提供「🖨️ 列印評量結果報告」，方便教師存檔作為個別化教育計畫 (IEP) 評量佐證。

---

## 🚀 觸發條件 (Triggers)

當使用者提及以下關鍵字或需求時，主動調用本技能：
- 「做成語音網頁版」、「語音試卷」、「互動試卷」、「有聲音的試卷」
- 「特教語音測驗」、「讓學生聽題目選答案」、「給不識字的學生考」
- 「用 edge-tts 做網頁試卷」、「題目有語音按鈕、選項也要語音按鈕」
- 「把這份試卷轉成網頁版」、「做數學科的語音網頁」

---

## 🛠️ 標準生成流程 (Execution Steps)

### 步驟 1：取得或解析試卷資料
支援以下輸入來源：
1. **現有 Word 檔 (`.docx`)**：讀取表格中之配對題、選擇題與情境素養題。
2. **對話中指定之課次**：直接讀取該課資料夾之 `generate_docs.py` 或題庫資料。
3. **數學科或其他科目題型**：由使用者提供或由 Agent 協助生成生活化數理題庫。

標準試卷結構（12 題，總分 100 分）：
- **第一大題：圖文／圖數配對題 (第 1~4 題，每題 8 分，共 32 分)**
- **第二大題：生活概念單選題 (第 5~10 題，每題 8 分，共 48 分)**
- **第三大題：生活素養應用與閱讀題 (第 11~12 題，每大題 10 分，共 20 分)**
  - 每大題拆為 `(1) 基礎識字認讀 (5分)` 與 `(2) 生活行動應用 (5分)`。

### 步驟 2：執行 Edge-TTS 語音合成快取
使用 Python 腳本調用 `edge_tts` 生成以下音訊檔（若已有快取則跳過合成）：
- 系統音效：`welcome`、`auto_on`、`auto_off`、`finish_praise`
- 題目朗讀：`q_{id}_prompt` 或 `q_{id}_scenario`
- 選項朗讀：`q_{id}_opt_{opt_id}`
- 子題朗讀：`sub_{id}_prompt` 與 `sub_{id}_opt_{opt_id}`

### 步驟 3：圖文音訊 Base64 封裝與 HTML 組裝
- 將所有圖片轉為 `data:image/png;base64,...`
- 將所有音訊轉為 `data:audio/mp3;base64,...`
- 組裝為單一 HTML 檔，寫入目標目錄。

### 步驟 4：檔案歸檔與說明更新
- 將檔案輸出至單元目錄（例如 `七上_L08_吃冰的滋味/吃冰的滋味_v1_語音互動試卷.html`）。
- 同步複製至總庫根目錄及 artifact 目錄方便使用者一鍵預覽。
- 自動更新該單元 `README.md` 及總庫 `README.md` 索引表。

---

## 💡 數學科（及其他學科）口語化朗讀轉換規則

當處理數學科或數理生活素養題時，需在前處理階段將算式與符號轉為自然教學口語：
- 加法：`3 + 2 = 5` ➡️ 朗讀為「三加二等於五」
- 減法：`10 - 4 = 6` ➡️ 朗讀為「十減四等於六」
- 找錢：`50 - 28 = 22` ➡️ 朗讀為「五十元減掉二十八元，找回二十二元」
- 乘法：`5 * 3` ➡️ 朗讀為「五乘以三」
- 錢幣：`$35` 或 `35元` ➡️ 朗讀為「三十五元」
- 時間：`08:30` ➡️ 朗讀為「八點三十分」；`14:00` ➡️ 朗讀為「下午兩點整」
- 單位：`150 cm` ➡️ 朗讀為「一百五十公分」；`2 kg` ➡️ 朗讀為「兩公斤」

---

## 📂 核心生成腳本模板與參考實現

技能目錄下附有通用生成引擎工具：
- `scripts/builder.py`：通用 Edge-TTS 合成與 HTML 封裝器，接收標準題型 JSON 即可一鍵輸出。
