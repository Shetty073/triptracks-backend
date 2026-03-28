// Web implementation of browser Notification API using dart:js_interop
// This file is only compiled on web targets.
import 'dart:js_interop';

@JS('Notification.requestPermission')
external JSPromise _requestPermission();

@JS('eval')
external void _eval(String code);

class WebNotificationApi {
  static void requestPermission() {
    try {
      _requestPermission();
    } catch (_) {}
  }

  static void show({required String title, required String body}) {
    // Escape quotes to avoid injection
    final safeTitle = title.replaceAll('"', '\\"');
    final safeBody = body.replaceAll('"', '\\"');
    try {
      _eval('''
        (function() {
          if (typeof Notification !== "undefined" && Notification.permission === "granted") {
            new Notification("$safeTitle", { body: "$safeBody", icon: "/icons/Icon-192.png" });
          }
        })();
      ''');
    } catch (_) {}
  }
}
