import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:frontend/models/trip.dart';

class TripMapWidget extends StatelessWidget {
  final Trip trip;

  const TripMapWidget({super.key, required this.trip});

  @override
  Widget build(BuildContext context) {
    if (trip.source['lat'] == null) {
      return Container(
        color: Colors.grey.shade200,
        child: const Center(child: Text("Map Location Unavailable")),
      );
    }

    final sourceLatLng = LatLng(
      (trip.source['lat'] as num).toDouble(),
      (trip.source['lng'] as num).toDouble(),
    );

    List<Marker> markers = [
      Marker(
        point: sourceLatLng,
        width: 80,
        height: 80,
        alignment: Alignment.topCenter,
        child: const Icon(Icons.location_on, color: Colors.green, size: 40),
      )
    ];

    if (trip.destination['lat'] != null) {
      final destLatLng = LatLng(
        (trip.destination['lat'] as num).toDouble(),
        (trip.destination['lng'] as num).toDouble(),
      );
      markers.add(
        Marker(
          point: destLatLng,
          width: 80,
          height: 80,
          alignment: Alignment.topCenter,
          child: const Icon(Icons.flag, color: Colors.red, size: 40),
        ),
      );
    }

    return FlutterMap(
      options: MapOptions(
        initialCenter: sourceLatLng,
        initialZoom: 12.0,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
        ),
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.triptracks.frontend',
        ),
        MarkerLayer(markers: markers),
      ],
    );
  }
}
