# TV Time Guard｜電視每日額度

> 小孩一天只能看多久電視？用 **Home Assistant 計時**，加一個 **100 行的電視 App 在畫面角落顯示倒數**，時間到自動關機。
> 全程在區網內，**免雲端、免帳號、免訂閱**。家長用手機的 HA 一鍵加時或解除限制。

**English summary:** A local-only parental time limit for Android TV. Home Assistant tracks daily TV-on time (`history_stats`), a tiny Android app draws a countdown overlay in the last 10 minutes (triggered over ADB), and HA turns the TV off when the quota is used up. Parents add time or switch on "parent mode" from the HA mobile app. No cloud, no account.

<video src="docs/demo.mp4" controls width="720"></video>

示範影片：[docs/demo.mp4](docs/demo.mp4)（約 28 秒）

## 它做什麼

| 時間點 | 電視 | 家長手機 |
|---|---|---|
| 電視開著、家長模式關 | 開始累計今日時間 | 儀表板看「今日剩餘」 |
| 剩 10 分鐘 | 右上角出現倒數 | — |
| 剩 5 分鐘 | 暫停播放一次 | 收到通知 |
| 最後 1 分鐘 | 倒數轉紅 | — |
| 時間到 | 顯示「即將關機」，回首頁，關機；再開機很快又被關 | 收到通知 |
| 任何時候 | — | 「加 15／30 分鐘」、「家長模式」（不計時，2 小時後自動關） |

## 需要什麼

- 一台 **Android TV／Google TV**（已用小米電視實測，Android 14）。
- **Home Assistant**（2024.10 以上，需要新式 `triggers:`／`actions:` 語法；已用 2026.11 實測）。
- HA 的兩個整合都要加到同一台電視：
  - **Android TV Remote**（開關機、按鍵、判斷電視是否開著）
  - **Android Debug Bridge**（叫電視顯示倒數）
- 電視開啟 ADB 偵錯，並給電視固定 IP。
- 家長手機裝 HA Companion App（收通知用，可省略）。

## 快速安裝（約 20 分鐘）

1. **電視端**：編譯或下載 APK，用 `tools/install-overlay.sh <電視IP>` 安裝並授權，電視右上角會出現 5 秒測試倒數。
2. **HA 端**：把 [`ha/tv_time_guard.yaml`](ha/tv_time_guard.yaml) 放到 `/config/packages/`，替換檔頭的四個實體名稱，重啟。
3. **設定額度**：輔助工具「TV daily limit」設成分鐘數（例如 90）。
4. **儀表板**：貼上 [`ha/dashboard_card.yaml`](ha/dashboard_card.yaml)。
5. **測試**：先把額度調成「已看時間＋2 分鐘」，確認倒數與自動關機，再調回正常值。

詳細步驟見 [docs/INSTALL.md](docs/INSTALL.md)。**想讓 AI 助理幫你裝**：把 [docs/AI-ASSISTANT.md](docs/AI-ASSISTANT.md) 貼給它（Claude Code、Codex 等都適用）。

## 運作原理

```
電視開著 ──► template 感測器「計時中」 ──► history_stats 累計今日時間
                                              │
              家長加時／家長模式 ──► 剩餘分鐘 = 額度 + 加時 − 已看
                                              │
        剩 ≤10 分 ──► HA 透過 ADB 叫電視上的 App 畫倒數（每分鐘校正，App 自己每秒走）
        剩 ≤ 5 分 ──► 暫停播放 + 通知家長
        剩 ≤ 0   ──► HOME 鍵 → 關機
```

- `history_stats` 約每分鐘才更新，所以剩餘時間加上「距離上次更新過了多久」，倒數才不會往回跳。
- 家長「密碼」就是家長手機的 HA 登入；電視端沒有 PIN。若你需要電視上輸入 PIN，請改用 TVGuard、tvusage 等現成 App。

## 限制與誠實說明

- **小孩能繞過嗎？** 能。這是「家庭約定的輔助」，不是防破解的系統：小孩若會用 Wi-Fi 或 HDMI 接別的裝置（遊戲機、機上盒）就不會被計時；若能操作 HA 就能自己開家長模式。要更強的管制請在路由器層做（排程斷網）。
- 電視進入深度待機後，區網指令有時喚不醒，要用遙控器或 HA 手機開機。
- 電視沒有內建 Chromecast 時，倒數的疊層仍可運作（它只靠 ADB）。
- 計時依據是「電視開著」，不分看什麼、也不分誰在看。
- APK 以 debug 金鑰簽署，自用即可；不建議發佈到商店。

## 授權

MIT，見 [LICENSE](LICENSE)。歡迎 issue 與 PR。
