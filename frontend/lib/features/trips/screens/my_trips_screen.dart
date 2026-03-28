import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/trips/providers/trips_provider.dart';
import 'package:frontend/shared/widgets/trip_card.dart';
import 'package:frontend/models/trip.dart';
import 'package:frontend/features/trip_details/screens/trip_details_screen.dart';
import 'package:frontend/features/plan_trip/screens/plan_trip_screen.dart';

class MyTripsScreen extends ConsumerStatefulWidget {
  const MyTripsScreen({super.key});

  @override
  ConsumerState<MyTripsScreen> createState() => _MyTripsScreenState();
}

class _MyTripsScreenState extends ConsumerState<MyTripsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _tabController.addListener(_handleTabSelection);
  }

  void _handleTabSelection() {
    // Prevent triggering twice on tap or while swiping
    if (_tabController.indexIsChanging) {
      ref.invalidate(myTripsProvider);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tripsAsync = ref.watch(myTripsProvider);

    return Scaffold(
      appBar: TabBar(
        controller: _tabController,
        isScrollable: true,
        labelColor: Colors.deepPurple,
        unselectedLabelColor: Colors.grey,
        indicatorColor: Colors.deepPurple,
        tabs: const [
          Tab(text: "Planned (Me)"),
          Tab(text: "Completed (Me)"),
          Tab(text: "Active (Participant)"),
          Tab(text: "Completed (Participant)"),
        ],
      ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (c) => const PlanTripScreen()),
            );
          },
          icon: const Icon(Icons.add_road),
          label: const Text('Plan a Trip'),
        ),
        body: tripsAsync.when(
          data: (categories) {
            return TabBarView(
              controller: _tabController,
              children: [
                _TripList(
                  trips: categories.plannedByMe,
                  label: "You haven't planned any trips yet",
                ),
                _TripList(
                  trips: categories.completedByMe,
                  label: "You have no completed trips",
                ),
                _TripList(
                  trips: categories.participantActive,
                  label: "You are not participating in active trips",
                ),
                _TripList(
                  trips: categories.participantCompleted,
                  label: "No completed trips as participant",
                ),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, st) => Center(child: Text("Error loading trips: $err")),
        ),
      );
  }
}

class _TripList extends StatelessWidget {
  final List<Trip> trips;
  final String label;

  const _TripList({required this.trips, required this.label});

  @override
  Widget build(BuildContext context) {
    if (trips.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.mode_of_travel, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              label,
              style: const TextStyle(color: Colors.grey, fontSize: 16),
            ),
          ],
        ),
      );
    }
    return ListView.builder(
      itemCount: trips.length,
      itemBuilder: (context, index) {
        return TripCard(
          trip: trips[index],
          onViewMore: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (c) => TripDetailsScreen(tripId: trips[index].id),
              ),
            );
          },
        );
      },
    );
  }
}
