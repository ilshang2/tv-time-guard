package io.github.ilshang2.tvcountdown;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.SystemClock;
import android.provider.Settings;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.TextView;

/**
 * 在電視畫面右上角疊一個倒數計時。由 HA 透過 ADB 控制：
 *   am start-foreground-service -n io.github.ilshang2.tvcountdown/.OverlayService -a SHOW --ei seconds 300
 *   am start-foreground-service -n io.github.ilshang2.tvcountdown/.OverlayService -a HIDE
 * 可選 --es label "文字"（預設「剩餘」）。
 */
public class OverlayService extends Service {
    private static final String CHANNEL = "countdown";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private WindowManager wm;
    private TextView view;
    private long endAt;
    private String label = "剩餘";

    private final Runnable tick = new Runnable() {
        @Override public void run() {
            long left = (endAt - SystemClock.elapsedRealtime() + 999) / 1000;
            if (left <= 0) {
                setText("時間到", true);
                handler.postDelayed(OverlayService.this::hide, 15000);
                return;
            }
            setText(String.format("%s %d:%02d", label, left / 60, left % 60), left <= 60);
            handler.postDelayed(this, 1000);
        }
    };

    @Override public void onCreate() {
        super.onCreate();
        wm = (WindowManager) getSystemService(WINDOW_SERVICE);
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CHANNEL, "倒數計時", NotificationManager.IMPORTANCE_MIN));
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        Notification n = new Notification.Builder(this, CHANNEL)
                .setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle("倒數計時").build();
        startForeground(1, n, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        String action = intent == null ? "HIDE" : String.valueOf(intent.getAction());
        if ("SHOW".equals(action) && Settings.canDrawOverlays(this)) {
            int sec = intent.getIntExtra("seconds", 0);
            String l = intent.getStringExtra("label");
            label = l == null ? "剩餘" : l;
            endAt = SystemClock.elapsedRealtime() + sec * 1000L;
            show();
            handler.removeCallbacks(tick);
            handler.post(tick);
        } else {
            hide();
        }
        return START_NOT_STICKY;
    }

    private void show() {
        if (view != null) return;
        view = new TextView(this);
        view.setTextSize(30);
        view.setTextColor(Color.WHITE);
        view.setPadding(36, 18, 36, 18);
        WindowManager.LayoutParams p = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT, WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                        | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT);
        p.gravity = Gravity.TOP | Gravity.END;
        p.x = 60; p.y = 40;
        wm.addView(view, p);
    }

    private void setText(String s, boolean urgent) {
        if (view == null) return;
        view.setText(s);
        GradientDrawable bg = new GradientDrawable();
        bg.setCornerRadius(24);
        bg.setColor(urgent ? Color.argb(220, 200, 30, 30) : Color.argb(190, 0, 0, 0));
        view.setBackground(bg);
    }

    private void hide() {
        handler.removeCallbacksAndMessages(null);
        if (view != null) { try { wm.removeView(view); } catch (Exception ignored) {} view = null; }
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    @Override public void onDestroy() { hide(); super.onDestroy(); }
    @Override public IBinder onBind(Intent i) { return null; }
}
