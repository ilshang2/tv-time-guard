#!/usr/bin/env bash
# 把倒數 App 裝到電視、授予「顯示在其他 App 上層」權限，並做 5 秒測試。
# 用法：tools/install-overlay.sh <電視IP> [apk路徑]
# 前置：電視已開啟「開發人員選項 → ADB 偵錯」，電腦有 adb（platform-tools）。
set -euo pipefail
TV="${1:?用法: $0 <電視IP> [apk]}"
APK="${2:-android/app/build/outputs/apk/release/app-release.apk}"
PKG="io.github.ilshang2.tvcountdown"
S="$TV:5555"

adb connect "$S"
adb -s "$S" install -r "$APK"
adb -s "$S" shell appops set "$PKG" SYSTEM_ALERT_WINDOW allow
adb -s "$S" shell appops get "$PKG" SYSTEM_ALERT_WINDOW

echo "測試：電視右上角應該出現 5 秒倒數…"
adb -s "$S" shell am start-foreground-service -n "$PKG/.OverlayService" -a SHOW --ei seconds 5
sleep 8
adb -s "$S" shell am start-foreground-service -n "$PKG/.OverlayService" -a HIDE
echo "完成。沒看到倒數的話，見 docs/TROUBLESHOOTING.md"
