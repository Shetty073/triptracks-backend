import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/models/trip.dart';
import 'package:frontend/core/constants.dart';
import 'package:frontend/features/trip_details/providers/trip_interactions_provider.dart';
import 'package:frontend/core/utils/error_handler.dart';
import 'package:image_picker/image_picker.dart';

class PhotosTab extends ConsumerWidget {
  final Trip trip;
  const PhotosTab({super.key, required this.trip});

  Future<void> _pickAndUploadPhoto(BuildContext context, WidgetRef ref) async {
    final picker = ImagePicker();
    try {
      final pickedFile = await picker.pickImage(source: ImageSource.gallery, imageQuality: 70);
      if (pickedFile != null) {
        final bytes = await pickedFile.readAsBytes();
        await ref.read(tripInteractionsProvider).addPhoto(trip.id, bytes, pickedFile.name);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Photo uploaded successfully!')));
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ErrorHandler.getMessage(e))));
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bool canUpload = trip.status == 'in_progress' || trip.status == 'completed';

    return Stack(
      children: [
        trip.photos.isEmpty
            ? Center(
                child: canUpload 
                    ? const Text('No photos yet. Start capturing memories!') 
                    : const Text('Photos can only be uploaded for active or completed trips.'))
            : GridView.builder(
                padding: const EdgeInsets.all(16).copyWith(bottom: 80),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 8,
                  mainAxisSpacing: 8,
                ),
                itemCount: trip.photos.length,
                itemBuilder: (context, index) {
                  final url = trip.photos[index];
                  // Provide absolute URL since the image resides statically on the backend
                  final String fullUrl;
                  if (url.startsWith('http')) {
                    fullUrl = url;
                  } else {
                    fullUrl = '${AppConstants.apiBaseUrl}$url';
                  }

                  return ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      fullUrl,
                      fit: BoxFit.cover,
                      // For handling token based access if ever implemented, NetworkImage might need headers.
                      // For now static files are public.
                      errorBuilder: (context, error, stackTrace) =>
                          Container(color: Colors.grey[300], child: const Icon(Icons.broken_image)),
                    ),
                  );
                },
              ),
        if (canUpload)
          Positioned(
            bottom: 16,
            right: 16,
            child: FloatingActionButton(
              heroTag: 'uploadPhotoFAB',
              onPressed: () => _pickAndUploadPhoto(context, ref),
              child: const Icon(Icons.add_a_photo),
            ),
          ),
      ],
    );
  }
}
