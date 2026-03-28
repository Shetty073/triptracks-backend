/// Stub used on mobile platforms (Android/iOS).
/// On web the real `notification_web.dart` is loaded instead.
class WebNotificationApi {
  static void requestPermission() {}
  static void show({required String title, required String body}) {}
}
