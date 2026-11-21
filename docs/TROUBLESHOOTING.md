# 疑難排解

| 症狀 | 原因與處理 |
|---|---|
| 電視沒出現倒數 | ① `adb shell appops get io.github.ilshang2.tvcountdown SYSTEM_ALERT_WINDOW` 要是 `allow`，不是就重跑 `tools/install-overlay.sh`。② 螢幕保護程式在跑：先喚醒電視。③ 手動送 `SHOW` 指令（見 INSTALL.md）看 App 本身有沒有問題。 |
| HA 沒送指令到電視 | 確認 ADB 整合的 media_player 是 `on`（不是 `unavailable`）。電視關機或待機時 ADB 會離線。第一次連線電視會跳「允許偵錯」要選「一律允許」。 |
| `adb_command` 報錯 | 指令字串含中文 label 時，確認整合與 adb 版本支援 UTF-8；可先把 `--es label 即將關機` 拿掉測試。 |
| 倒數往回跳或時間不準 | 不要改掉 `tv_remaining_min` 裡「距離上次更新」的補償（`history_stats` 約每分鐘才更新）。 |
| 時間到但電視沒關 | 看 `automation.tv_guard_cutoff` 的追蹤（設定 → 自動化 → 追蹤）。常見：Remote 整合的 `remote.*` 是 `unavailable`；或家長模式開著（`tv_counting` 是 `off`）。 |
| 關機後 HA 開不了電視 | 電視進深度待機，區網喚不醒；用遙控器開，或在電視設定裡把「網路喚醒／WoL」打開（依機型）。 |
| 重啟 HA 後額度變回預設 | 輔助工具 `input_number` 不要設 `initial`（本設定包已經沒設）。 |
| 要停用某天的限制 | 打開 `TV parent mode`（2 小時後自動關），或把 `TV bonus today` 加到夠大。 |
| 小孩用別的裝置看電視 | 本專案只計「這台電視開著」。其他裝置請在路由器層管制。 |
| 倒數字太小／位置要改 | 改 `android/.../OverlayService.java` 的 `setTextSize(30)` 與 `p.x / p.y`，重新編譯安裝。 |
