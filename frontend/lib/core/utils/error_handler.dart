import 'package:dio/dio.dart';

class ErrorHandler {
  static String getMessage(dynamic e) {
    if (e is DioException) {
      final data = e.response?.data;
      if (data is Map<String, dynamic> && data.containsKey('detail')) {
        return data['detail'].toString();
      }
      
      final statusCode = e.response?.statusCode;
      if (statusCode == 400) {
        return 'Request failed. Please check your details and try again.';
      } else if (statusCode == 401 || statusCode == 403) {
        return 'Not authorized. Please log in again.';
      } else if (statusCode == 404) {
        return 'Resource not found.';
      } else if (statusCode != null && statusCode >= 500) {
        return 'Server error. Please try again later.';
      }
      
      switch (e.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return 'Connection timed out. Please check your internet connection.';
        case DioExceptionType.connectionError:
          return 'No internet connection.';
        default:
          return 'An unexpected network error occurred.';
      }
    }
    
    // Fallback for non-Dio exceptions
    final msg = e.toString();
    return msg.replaceFirst('Exception: ', '');
  }
}
