import 'package:flutter/material.dart';
import 'package:triptracks/models/trip.dart';
import 'package:intl/intl.dart';

class TripCard extends StatelessWidget {
  final Trip trip;
  final VoidCallback onViewMore;

  const TripCard({super.key, required this.trip, required this.onViewMore});

  String _formatStatus(String status) {
    if (status == 'in_progress' || status == 'active') return 'Active';
    if (status == 'planned') return 'Planned';
    if (status == 'completed') return 'Completed';
    return status.toUpperCase();
  }

  Color _getStatusColor(String status) {
    if (status == 'in_progress' || status == 'active') return Colors.green.shade600;
    if (status == 'planned') return Colors.orange.shade600;
    if (status == 'completed') return Colors.blueGrey.shade600;
    return Colors.grey;
  }

  @override
  Widget build(BuildContext context) {
    final sourceName = trip.source['name'] ?? 'Unknown Source';
    final destName = trip.destination['name'] ?? 'Unknown Destination';
    final formattedDate = DateFormat.yMMMd().format(trip.createdAt);

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Stack(
            children: [
              Container(
                height: 120,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.deepPurple.shade300,
                      Colors.deepPurple.shade700,
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: const Center(
                  child: Icon(
                    Icons.terrain,
                    color: Colors.white,
                    size: 60,
                  ),
                ),
              ),
              Positioned(
                top: 12,
                right: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getStatusColor(trip.status),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: const [
                      BoxShadow(color: Colors.black26, blurRadius: 4, offset: Offset(0, 2))
                    ],
                  ),
                  child: Text(
                    _formatStatus(trip.status),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            ],
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  trip.title,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.location_on, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        '$sourceName → $destName',
                        style: const TextStyle(color: Colors.grey),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '${trip.totalDistanceKm.toStringAsFixed(1)} km',
                      style: const TextStyle(fontWeight: FontWeight.w500),
                    ),
                    Text(
                      formattedDate,
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Align(
                  alignment: Alignment.centerRight,
                  child: OutlinedButton(
                    onPressed: onViewMore,
                    style: OutlinedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      foregroundColor: Colors.deepPurple,
                    ),
                    child: const Text('View More'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
