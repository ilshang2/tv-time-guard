# 安裝步驟（給人看）

預計 20～30 分鐘。每一步都有「怎麼確認成功」。

## 0. 先決條件

| 項目 | 怎麼確認 |
|---|---|
| 電視是 Android TV／Google TV | 設定裡有「開發人員選項」 |
| 電視有固定 IP | 路由器 DHCP 保留，或電視網路設定改靜態 |
| HA 版本 ≥ 2024.10 | 設定 → 關於 |
| 電腦有 `adb` | `adb version`（[platform-tools](https://developer.android.com/tools/releases/platform-tools)） |

## 1. 電視：開啟 ADB 偵錯

設定 → 關於 → 連點「版本號碼」7 次 → 回上一層進「開發人員選項」→ 開 **USB 偵錯／網路偵錯**。
電腦執行 `adb connect <電視IP>:5555`，電視會跳「允許偵錯？」，勾**一律允許**。

確認：`adb devices` 看到 `<電視IP>:5555  device`。

## 2. HA：加入兩個整合到同一台電視

1. **Android TV Remote**：設定 → 裝置與服務 → 新增整合 → 輸入電視 IP → 電視螢幕顯示配對碼，輸入到 HA。
2. **Android Debug Bridge**：新增整合 → IP、埠 5555、裝置類型選 *Android TV*。

確認：HA 出現兩組實體——一組 `media_player.*`＋`remote.*`（Remote 整合）、一組 `media_player.*`（ADB 整合）。**記下三個實體名稱**，第 4 步要用。

## 3. 電視：安裝倒數 App

### 方法 A：自己編譯

需要 JDK 17 與 Android SDK（compileSdk 35）。

```bash
cd android
export JAVA_HOME=/path/to/jdk-17 ANDROID_HOME=/path/to/android-sdk
./gradlew assembleRelease          # Windows 用 gradlew.bat
cd ..
tools/install-overlay.sh <電視IP>
```

### 方法 B：用 Release 的 APK

下載 Releases 內的 `tv-countdown.apk`，再執行
`tools/install-overlay.sh <電視IP> tv-countdown.apk`。

確認：電視右上角出現約 5 秒的「剩餘 0:05」倒數。
手動指令：

```bash
adb -s <電視IP>:5555 shell am start-foreground-service -n io.github.ilshang2.tvcountdown/.OverlayService -a SHOW --ei seconds 120
adb -s <電視IP>:5555 shell am start-foreground-service -n io.github.ilshang2.tvcountdown/.OverlayService -a HIDE
```

## 4. HA：放入設定包

1. `configuration.yaml` 加上（若已有就略過）：
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
2. 複製 `ha/tv_time_guard.yaml` 到 `/config/packages/tv_time_guard.yaml`。
3. 用編輯器**全部取代**這四個名稱：

   | 範例名稱 | 換成 |
   |---|---|
   | `media_player.living_room_tv` | Android TV Remote 整合的 media_player |
   | `remote.living_room_tv` | 同一個整合的 remote |
   | `media_player.living_room_tv_adb` | ADB 整合的 media_player |
   | `notify.mobile_app_parent_phone` | 家長手機的通知服務（開發者工具 → 動作，搜尋 `notify.mobile_app`）；不要通知就刪掉那兩段 |

4. 開發者工具 → YAML → **檢查設定** 通過後，重新啟動 HA。

確認：實體 `sensor.tv_remaining_min` 出現；電視開著時 `binary_sensor.tv_counting` 是 `on`。

## 5. 設定額度與儀表板

- 設定 → 裝置與服務 → 輔助工具 → **TV daily limit** 設為 90（或你要的分鐘數）。
- 儀表板 → 編輯 → 原始設定編輯器，把 `ha/dashboard_card.yaml` 貼進某個 view 的 `sections:`。

## 6. 測試（家長在場時做）

1. 記下「TV remaining min」目前數值 R。
2. 把 TV daily limit 暫時改成「目前額度 − R ＋ 2」，讓剩餘約 2 分鐘。
3. 觀察：電視右上角出現倒數 → 最後 1 分鐘轉紅 → 「即將關機」→ 電視關閉。
4. 把額度調回正常值，並用遙控器或 HA 把電視開起來。
5. 測家長模式：打開後電視右上角倒數消失、`tv_counting` 變 `off`。

## 更新與移除

- 更新：重新放入新版 `tv_time_guard.yaml`，重新載入自動化即可。
- 移除：刪除 `/config/packages/tv_time_guard.yaml` 並重啟；電視上 `adb uninstall io.github.ilshang2.tvcountdown`。
