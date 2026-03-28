class VehicleFuelCost {
  final String vehicleId;
  final String vehicleName;
  final int passengers;
  final double totalFuelCost;
  final double fuelCostPerPerson;

  VehicleFuelCost({
    required this.vehicleId,
    required this.vehicleName,
    required this.passengers,
    required this.totalFuelCost,
    required this.fuelCostPerPerson,
  });

  factory VehicleFuelCost.fromJson(Map<String, dynamic> json) {
    return VehicleFuelCost(
      vehicleId: json['vehicle_id'] ?? '',
      vehicleName: json['vehicle_name'] ?? 'Vehicle',
      passengers: json['passengers'] ?? 1,
      totalFuelCost: (json['total_fuel_cost'] ?? 0.0).toDouble(),
      fuelCostPerPerson: (json['fuel_cost_per_person'] ?? 0.0).toDouble(),
    );
  }
}

class EstimatedCosts {
  final List<VehicleFuelCost> vehicleFuelCosts;
  final double totalFuelCost;
  final double totalStayCost;
  final double stayCostPerPerson;
  final double totalFoodCost;
  final double foodCostPerPerson;

  EstimatedCosts({
    required this.vehicleFuelCosts,
    required this.totalFuelCost,
    required this.totalStayCost,
    required this.stayCostPerPerson,
    required this.totalFoodCost,
    required this.foodCostPerPerson,
  });

  factory EstimatedCosts.fromJson(Map<String, dynamic> json) {
    return EstimatedCosts(
      vehicleFuelCosts: (json['vehicle_fuel_costs'] as List?)
              ?.map((e) => VehicleFuelCost.fromJson(e))
              .toList() ??
          [],
      totalFuelCost: (json['total_fuel_cost'] ?? 0.0).toDouble(),
      totalStayCost: (json['total_stay_cost'] ?? 0.0).toDouble(),
      stayCostPerPerson: (json['stay_cost_per_person'] ?? 0.0).toDouble(),
      totalFoodCost: (json['total_food_cost'] ?? 0.0).toDouble(),
      foodCostPerPerson: (json['food_cost_per_person'] ?? 0.0).toDouble(),
    );
  }
}

class TripParticipant {
  final String userId;
  final bool isDriver;
  final String role;

  TripParticipant({
    required this.userId,
    required this.isDriver,
    required this.role,
  });

  factory TripParticipant.fromJson(Map<String, dynamic> json) {
    return TripParticipant(
      userId: json['user_id'] ?? '',
      isDriver: json['is_driver'] ?? false,
      role: json['role'] ?? 'passenger',
    );
  }
}

class Expense {
  final String id;
  final String description;
  final double amount;
  final String paidBy;
  final Map<String, double> splits;
  final DateTime date;

  Expense({
    required this.id,
    required this.description,
    required this.amount,
    required this.paidBy,
    required this.splits,
    required this.date,
  });

  factory Expense.fromJson(Map<String, dynamic> json) {
    final splitsMap = json['splits'] as Map<String, dynamic>? ?? {};
    final mappedSplits = splitsMap.map((key, value) => MapEntry(key, (value as num).toDouble()));

    return Expense(
      id: json['id'] ?? '',
      description: json['description'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      paidBy: json['paid_by'] ?? '',
      splits: mappedSplits,
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
    );
  }
}

class TripComment {
  final String id;
  final String userId;
  final String username;
  final String text;
  final DateTime timestamp;

  TripComment({
    required this.id,
    required this.userId,
    required this.username,
    required this.text,
    required this.timestamp,
  });

  factory TripComment.fromJson(Map<String, dynamic> json) {
    return TripComment(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      username: json['username'] ?? '',
      text: json['text'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}

class Trip {
  final String id;
  final String organizerId;
  final String title;
  final String status;
  final double totalDistanceKm;
  final int totalEstimatedTimeMins;
  final Map<String, dynamic> source;
  final Map<String, dynamic> destination;
  final List<TripParticipant> participants;
  final List<Expense> expenses;
  final List<TripComment> comments;
  final List<String> photos;
  final EstimatedCosts? estimatedCosts;
  final DateTime createdAt;

  Trip({
    required this.id,
    required this.organizerId,
    required this.title,
    required this.status,
    required this.totalDistanceKm,
    required this.totalEstimatedTimeMins,
    required this.source,
    required this.destination,
    required this.participants,
    required this.expenses,
    required this.comments,
    required this.photos,
    this.estimatedCosts,
    required this.createdAt,
  });

  factory Trip.fromJson(Map<String, dynamic> json) {
    return Trip(
      id: json['id'] ?? '',
      organizerId: json['organizer_id'] ?? '',
      title: json['title'] ?? 'Untitled Trip',
      status: json['status'] ?? 'planned',
      totalDistanceKm: (json['total_distance_km'] ?? 0.0).toDouble(),
      totalEstimatedTimeMins: json['total_estimated_time_mins'] ?? 0,
      source: json['source'] ?? {},
      destination: json['destination'] ?? {},
      participants:
          (json['participants'] as List?)
              ?.map((e) => TripParticipant.fromJson(e))
              .toList() ??
          [],
      expenses:
          (json['expenses'] as List?)
              ?.map((e) => Expense.fromJson(e))
              .toList() ??
          [],
      comments:
          (json['comments'] as List?)
              ?.map((e) => TripComment.fromJson(e))
              .toList() ??
          [],
      photos: (json['photos'] as List?)?.map((e) => e.toString()).toList() ?? [],
      estimatedCosts: json['estimated_costs'] != null
          ? EstimatedCosts.fromJson(json['estimated_costs'])
          : null,
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}
