import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:frontend/core/api_client.dart';
import 'package:frontend/features/trip_details/providers/trip_details_provider.dart';

class TripInteractionsNotifier {
  final Ref ref;
  TripInteractionsNotifier(this.ref);

  Future<void> addExpense(
    String tripId,
    String description,
    double amount, {
    Map<String, double>? splits,
  }) async {
    final dio = ref.read(dioProvider);
    final data = <String, dynamic>{
      'description': description,
      'amount': amount,
      'paid_by': '', 
    };
    if (splits != null && splits.isNotEmpty) {
      data['splits'] = splits;
    }

    await dio.post(
      '/api/trips/$tripId/expenses',
      data: data,
    );
    ref.invalidate(tripDetailsProvider(tripId));
  }

  Future<void> addComment(String tripId, String text) async {
    final dio = ref.read(dioProvider);
    await dio.post('/api/trips/$tripId/comments', data: {'text': text});
    ref.invalidate(tripDetailsProvider(tripId));
  }

  Future<void> addPhoto(String tripId, List<int> bytes, String filename) async {
    final dio = ref.read(dioProvider);
    final formData = FormData.fromMap({
      'file': MultipartFile.fromBytes(bytes, filename: filename),
    });
    await dio.post('/api/trips/$tripId/photos', data: formData);
    ref.invalidate(tripDetailsProvider(tripId));
  }
}

final tripInteractionsProvider = Provider(
  (ref) => TripInteractionsNotifier(ref),
);
