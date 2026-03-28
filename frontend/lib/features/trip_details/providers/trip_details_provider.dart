import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/api_client.dart';
import 'package:frontend/models/trip.dart';

final tripDetailsProvider = FutureProvider.family<Trip, String>((
  ref,
  tripId,
) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/api/trips/$tripId');
  return Trip.fromJson(response.data);
});

/// Returns a {userId: displayName} map for all trip participants.
final tripParticipantNamesProvider =
    FutureProvider.family<Map<String, String>, String>((
  ref,
  tripId,
) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/api/trips/$tripId/participants/names');
  return Map<String, String>.from(response.data as Map);
});

class TripStatusNotifier {
  final Ref ref;
  TripStatusNotifier(this.ref);

  Future<void> startTrip(String tripId, {bool force = false}) async {
    final dio = ref.read(dioProvider);
    await dio.patch(
      '/api/trips/$tripId/start',
      queryParameters: {'force': force},
    );
    ref.invalidate(tripDetailsProvider(tripId));
  }

  Future<void> completeTrip(String tripId) async {
    final dio = ref.read(dioProvider);
    await dio.patch('/api/trips/$tripId/complete');
    ref.invalidate(tripDetailsProvider(tripId));
  }
}

final tripActionProvider = Provider((ref) => TripStatusNotifier(ref));

final tripBalancesProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, tripId) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/api/trips/$tripId/balances');
  return response.data as Map<String, dynamic>;
});
