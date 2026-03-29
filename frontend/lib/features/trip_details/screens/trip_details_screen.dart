import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:triptracks/features/trip_details/providers/trip_details_provider.dart';
import 'package:triptracks/models/trip.dart';
import 'package:triptracks/features/trip_details/screens/map_widget.dart';
import 'package:triptracks/features/trip_details/screens/expenses_tab.dart';
import 'package:triptracks/features/trip_details/screens/chat_tab.dart';
import 'package:triptracks/features/trip_details/screens/comments_tab.dart';
import 'package:triptracks/features/trip_details/screens/photos_tab.dart';
import 'package:triptracks/core/utils/error_handler.dart';
import 'package:triptracks/core/utils/currency_helper.dart';
import 'package:triptracks/features/profile/providers/profile_provider.dart';
import 'package:triptracks/core/auth_provider.dart';

class TripDetailsScreen extends ConsumerWidget {
  final String tripId;

  const TripDetailsScreen({super.key, required this.tripId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tripAsync = ref.watch(tripDetailsProvider(tripId));

    return Scaffold(
      appBar: AppBar(title: const Text('Trip Details')),
      body: tripAsync.when(
        data: (trip) => _TripDetailsView(trip: trip),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, st) => Center(child: Text('Error: $e')),
      ),
    );
  }
}

class _TripDetailsView extends ConsumerWidget {
  final Trip trip;
  const _TripDetailsView({required this.trip});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 5,
      child: Column(
        children: [
          TripMapAccordion(trip: trip),

          const TabBar(
            isScrollable: true,
            labelColor: Colors.deepPurple,
            unselectedLabelColor: Colors.grey,
            tabs: [
              Tab(text: "Info"),
              Tab(text: "Expenses"),
              Tab(text: "Chat"),
              Tab(text: "Comments"),
              Tab(text: "Photos"),
            ],
          ),

          Expanded(
            child: TabBarView(
              children: [
                _InfoTab(trip: trip),
                ExpensesTab(trip: trip),
                ChatTab(tripId: trip.id),
                CommentsTab(trip: trip),
                PhotosTab(trip: trip),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoTab extends ConsumerWidget {
  final Trip trip;
  const _InfoTab({required this.trip});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentUser = ref.watch(authStateProvider).value;
    final isOrganizer = currentUser?.id == trip.organizerId;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          trip.title,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        Text(
          'Status: ${trip.status.toUpperCase()}',
          style: TextStyle(
            color: trip.status == 'active' ? Colors.green : Colors.grey,
          ),
        ),
        const SizedBox(height: 16),
        ListTile(
          title: Text(trip.source['name'] ?? 'Source'),
          subtitle: const Text('Start'),
          leading: const Icon(Icons.location_on, color: Colors.green),
        ),
        ListTile(
          title: Text(trip.destination['name'] ?? 'Destination'),
          subtitle: const Text('End'),
          leading: const Icon(Icons.flag, color: Colors.red),
        ),
        const SizedBox(height: 16),
        Text('Distance: ${trip.totalDistanceKm} km', style: const TextStyle(fontSize: 16)),
        Text(
          'Est. Time: ${(trip.totalEstimatedTimeMins / 60).toStringAsFixed(1)} hours',
          style: const TextStyle(fontSize: 16),
        ),

        if (trip.estimatedCosts != null) ...[
          const SizedBox(height: 16),
          Builder(builder: (context) {
            final currency = ref
                .watch(profileSettingsProvider)
                .value
                ?.currency;
            final costs = trip.estimatedCosts!;
            return Card(
              color: Colors.deepPurple.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('💰 Estimated Projections',
                        style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.deepPurple)),
                    const Divider(),
                    Text('Food (Total): ${CurrencyHelper.format(costs.totalFoodCost, currency)}'),
                    Text(
                      'Food (Per Person): ${CurrencyHelper.format(costs.foodCostPerPerson, currency)}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text('Stay (Total): ${CurrencyHelper.format(costs.totalStayCost, currency)}'),
                    Text(
                      'Stay (Per Person): ${CurrencyHelper.format(costs.stayCostPerPerson, currency)}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    const Text('Fuel by Vehicle:',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    ...costs.vehicleFuelCosts.map((v) => Padding(
                          padding: const EdgeInsets.only(left: 8.0, top: 4.0),
                          child: Text(
                            '🚗 ${v.vehicleName}: ${CurrencyHelper.format(v.totalFuelCost, currency)} '
                            '(👥 ${CurrencyHelper.format(v.fuelCostPerPerson, currency)}/person)',
                            style: TextStyle(color: Colors.grey.shade800),
                          ),
                        )),
                  ],
                ),
              ),
            );
          }),
        ],

        const SizedBox(height: 24),
        if (trip.status == 'planned' && isOrganizer)
          ElevatedButton(
            onPressed: () async {
              try {
                await ref.read(tripActionProvider).startTrip(trip.id);
              } catch (e) {
                final msg = ErrorHandler.getMessage(e);
                if (context.mounted && msg.contains('force=true')) {
                  showDialog(
                    context: context,
                    builder: (c) => AlertDialog(
                      title: const Text('Conflicting Trips'),
                      content: Text(msg.replaceAll('. Use force=true to remove them and start anyway.', '')),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(c),
                          child: const Text('Cancel'),
                        ),
                        TextButton(
                          onPressed: () async {
                            Navigator.pop(c);
                            try {
                              await ref.read(tripActionProvider).startTrip(trip.id, force: true);
                            } catch (e2) {
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text(ErrorHandler.getMessage(e2))),
                                );
                              }
                            }
                          },
                          child: const Text('Kick & Start', style: TextStyle(color: Colors.red)),
                        ),
                      ],
                    ),
                  );
                } else if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
                }
              }
            },
            child: const Text('Start Trip'),
          ),
        if (trip.status == 'active' && isOrganizer)
          ElevatedButton(
            onPressed: () => _showCompleteTripDialog(context, ref),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: const Text('Complete Trip'),
          ),
      ],
    );
  }

  Future<void> _showCompleteTripDialog(BuildContext context, WidgetRef ref) async {
    String roadCondition = 'Average';
    String description = '';
    bool isPublic = false;

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Complete Trip'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: roadCondition,
                  decoration: const InputDecoration(labelText: 'Road Condition'),
                  items: ['Poor', 'Average', 'Good']
                      .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                      .toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => roadCondition = val);
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  decoration: const InputDecoration(labelText: 'Trip Description (Optional)'),
                  maxLines: 3,
                  onChanged: (val) => description = val,
                ),
                const SizedBox(height: 12),
                CheckboxListTile(
                  title: const Text('Publish for public view'),
                  subtitle: const Text('Others can see this in their feed.'),
                  value: isPublic,
                  onChanged: (val) {
                    if (val != null) setState(() => isPublic = val);
                  },
                  contentPadding: EdgeInsets.zero,
                  controlAffinity: ListTileControlAffinity.leading,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                try {
                  await ref.read(tripActionProvider).completeTrip(
                        trip.id,
                        roadCondition: roadCondition.toLowerCase(),
                        description: description.isNotEmpty ? description : null,
                        isPublic: isPublic,
                      );
                  if (context.mounted) {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Trip Completed!')));
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ErrorHandler.getMessage(e))));
                  }
                }
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              child: const Text('Complete'),
            ),
          ],
        ),
      ),
    );
  }
}
