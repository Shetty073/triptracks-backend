import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:frontend/models/trip.dart';

/// Wraps the map inside an ExpansionTile so tiles are only fetched when opened.
class TripMapAccordion extends StatefulWidget {
  final Trip trip;
  const TripMapAccordion({super.key, required this.trip});

  @override
  State<TripMapAccordion> createState() => _TripMapAccordionState();
}

class _TripMapAccordionState extends State<TripMapAccordion> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        InkWell(
          onTap: () => setState(() => _expanded = !_expanded),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Colors.deepPurple.shade50,
              border: Border(
                bottom: BorderSide(color: Colors.deepPurple.shade100),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.map_outlined, color: Colors.deepPurple),
                const SizedBox(width: 10),
                const Text(
                  'View Route Map',
                  style: TextStyle(
                    color: Colors.deepPurple,
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                  ),
                ),
                const Spacer(),
                AnimatedRotation(
                  turns: _expanded ? 0.5 : 0,
                  duration: const Duration(milliseconds: 250),
                  child: const Icon(Icons.expand_more, color: Colors.deepPurple),
                ),
              ],
            ),
          ),
        ),
        AnimatedCrossFade(
          firstChild: const SizedBox.shrink(),
          secondChild: SizedBox(
            height: 300,
            width: double.infinity,
            // Only build the actual map once expanded (lazy load)
            child: _expanded ? TripMapWidget(trip: widget.trip) : const SizedBox.shrink(),
          ),
          crossFadeState: _expanded ? CrossFadeState.showSecond : CrossFadeState.showFirst,
          duration: const Duration(milliseconds: 300),
        ),
      ],
    );
  }
}

class TripMapWidget extends StatelessWidget {
  final Trip trip;
  const TripMapWidget({super.key, required this.trip});

  @override
  Widget build(BuildContext context) {
    if (trip.source['lat'] == null) {
      return Container(
        color: Colors.grey.shade200,
        child: const Center(child: Text('Map Location Unavailable')),
      );
    }

    final srcLat = (trip.source['lat'] as num).toDouble();
    final srcLng = (trip.source['lng'] as num).toDouble();
    final sourceLatLng = LatLng(srcLat, srcLng);

    LatLng? destLatLng;
    if (trip.destination['lat'] != null) {
      destLatLng = LatLng(
        (trip.destination['lat'] as num).toDouble(),
        (trip.destination['lng'] as num).toDouble(),
      );
    }

    final List<Marker> markers = [
      Marker(
        point: sourceLatLng,
        width: 48,
        height: 48,
        alignment: Alignment.topCenter,
        child: const Icon(Icons.location_on, color: Colors.green, size: 40),
      ),
      if (destLatLng != null)
        Marker(
          point: destLatLng,
          width: 48,
          height: 48,
          alignment: Alignment.topCenter,
          child: const Icon(Icons.flag, color: Colors.red, size: 40),
        ),
    ];

    // Compute a camera fit that shows both markers with padding
    final CameraFit cameraFit;
    if (destLatLng != null) {
      final minLat = min(srcLat, destLatLng.latitude);
      final maxLat = max(srcLat, destLatLng.latitude);
      final minLng = min(srcLng, destLatLng.longitude);
      final maxLng = max(srcLng, destLatLng.longitude);
      cameraFit = CameraFit.bounds(
        bounds: LatLngBounds(
          LatLng(minLat, minLng),
          LatLng(maxLat, maxLng),
        ),
        padding: const EdgeInsets.all(48),
        maxZoom: 14,
      );
    } else {
      cameraFit = CameraFit.coordinates(
        coordinates: [sourceLatLng],
        padding: const EdgeInsets.all(48),
        maxZoom: 13,
      );
    }

    return FlutterMap(
      options: MapOptions(
        initialCameraFit: cameraFit,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
        ),
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.triptracks.frontend',
          maxZoom: 19,
        ),
        MarkerLayer(markers: markers),
      ],
    );
  }
}
