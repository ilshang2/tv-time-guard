# AGENTS.md

本 repo 是 **TV Time Guard**（Android TV 每日額度，Home Assistant 計時＋電視端倒數 App）。

- 要幫使用者**安裝**：完整照 [docs/AI-ASSISTANT.md](docs/AI-ASSISTANT.md) 做（預檢 → 找實體 → 裝 App → 放 HA 設定 → 實測 → 回報）。
- 要**修改**專案：
  - HA 設定在 `ha/tv_time_guard.yaml`（單一 package），電視 App 在 `android/`（純 Java，沒有 AndroidX）。
  - 改 `tv_remaining_min` 的公式時要同步改 `tv_guard_cutoff` 裡的同一段公式。
  - 改完用 HA 的 `/api/template` 渲染樣板驗證，別只看語法。
- 機密（HA 權杖等）不進 repo、不貼對話。實測會關掉使用者的電視，先告知。
- 回覆使用者時用繁體中文，程式碼與指令維持原文。
