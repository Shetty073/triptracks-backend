import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

// Conditional import: only the web file uses dart:js_interop
import 'notification_stub.dart'
    if (dart.library.js_interop) 'notification_web.dart';

/// Platform-agnostic push notification service.
/// Web  → browser Notification API (no server required)
/// Mobile → flutter_local_notifications (Android + iOS)
class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  final _plugin = FlutterLocalNotificationsPlugin();
  bool _ready = false;

  Future<void> initialize() async {
    if (_ready) return;
    _ready = true;

    if (kIsWeb) {
      // Permission must be requested from a user gesture — see requestWebPermission()
      return;
    }

    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    await _plugin.initialize(
      const InitializationSettings(android: android, iOS: ios),
    );

    // Android 13+ runtime permission
    await _plugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();
  }

  /// Call this from a user-gesture handler (button tap) on Web.
  void requestWebPermission() {
    if (kIsWeb) WebNotificationApi.requestPermission();
  }

  /// Call this when a new chat message arrives from the WebSocket
  /// while the user is NOT viewing that particular chat.
  Future<void> showChatMessage({
    required String tripTitle,
    required String sender,
    required String text,
  }) async {
    if (!_ready) await initialize();

    final title = '$sender · $tripTitle';

    if (kIsWeb) {
      WebNotificationApi.show(title: title, body: text);
      return;
    }

    const androidDetails = AndroidNotificationDetails(
      'triptracks_chat',           // channel id
      'Trip Chat',                  // channel name
      channelDescription: 'New messages from your trip crew',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
      playSound: true,
    );
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentSound: true,
      presentBadge: true,
    );

    await _plugin.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000 & 0x7FFFFFFF,
      title,
      text,
      const NotificationDetails(android: androidDetails, iOS: iosDetails),
    );
  }
}
