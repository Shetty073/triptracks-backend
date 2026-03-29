import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:frontend/core/constants.dart';
import 'package:frontend/core/auth_provider.dart';
import 'package:frontend/features/auth/screens/auth_screen.dart';
import 'package:frontend/main.dart';

const _storage = FlutterSecureStorage();

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: AppConstants.apiBaseUrl, // Assuming local FastAPI instance
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (DioException e, handler) async {
        if (e.response?.statusCode == 401) {
          final refreshToken = await _storage.read(key: 'refresh_token');
          if (refreshToken != null) {
            try {
              final refreshDio = Dio(BaseOptions(baseUrl: AppConstants.apiBaseUrl));
              final refreshResponse = await refreshDio.post(
                '/api/auth/refresh',
                data: {'refresh_token': refreshToken},
              );
              
              if (refreshResponse.statusCode == 200) {
                final newAccessToken = refreshResponse.data['access_token'];
                final newRefreshToken = refreshResponse.data['refresh_token'];
                
                await _storage.write(key: 'access_token', value: newAccessToken);
                await _storage.write(key: 'refresh_token', value: newRefreshToken);
                
                final requestOptions = e.requestOptions;
                requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';
                
                final cloneReq = await refreshDio.request(
                  requestOptions.path,
                  options: Options(
                    method: requestOptions.method,
                    headers: requestOptions.headers,
                  ),
                  data: requestOptions.data,
                  queryParameters: requestOptions.queryParameters,
                );
                return handler.resolve(cloneReq);
              }
            } catch (_) {
              // Refresh failed, fall through to logout
            }
          }
          
          ref.read(authStateProvider.notifier).logout();
          final context = navigatorKey.currentContext;
          if (context != null) {
            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(builder: (_) => const AuthScreen()),
              (route) => false,
            );
          }
        }
        return handler.next(e);
      },
    ),
  );

  return dio;
});
