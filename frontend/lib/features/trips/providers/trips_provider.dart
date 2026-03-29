import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:triptracks/core/api_client.dart';
import 'package:triptracks/models/trip.dart';

class CategorizedTrips {
  final List<Trip> active;
  final List<Trip> planned;
  final List<Trip> completed;

  CategorizedTrips({
    required this.active,
    required this.planned,
    required this.completed,
  });

  factory CategorizedTrips.fromJson(Map<String, dynamic> json) {
    return CategorizedTrips(
      active: (json['active'] as List)
          .map((t) => Trip.fromJson(t))
          .toList(),
      planned: (json['planned'] as List)
          .map((t) => Trip.fromJson(t))
          .toList(),
      completed: (json['completed'] as List)
          .map((t) => Trip.fromJson(t))
          .toList(),
    );
  }
}

final myTripsProvider = FutureProvider<CategorizedTrips>((ref) async {
  final dio = ref.watch(dioProvider);
  final response = await dio.get('/api/trips/user/categories');
  return CategorizedTrips.fromJson(response.data);
});
