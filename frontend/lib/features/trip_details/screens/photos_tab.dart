import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:triptracks/models/trip.dart';
import 'package:triptracks/core/constants.dart';
import 'package:triptracks/features/trip_details/providers/trip_interactions_provider.dart';
import 'package:triptracks/core/utils/error_handler.dart';
import 'package:image_picker/image_picker.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:intl/intl.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class PhotosTab extends ConsumerStatefulWidget {
  final Trip trip;
  const PhotosTab({super.key, required this.trip});

  @override
  ConsumerState<PhotosTab> createState() => _PhotosTabState();
}

class _PhotosTabState extends ConsumerState<PhotosTab> {
  String? _selectedAlbumId;

  Future<void> _pickAndUploadPhoto(String? albumId) async {
    final picker = ImagePicker();
    try {
      final pickedFile = await picker.pickImage(source: ImageSource.gallery, imageQuality: 70);
      if (pickedFile != null) {
        final bytes = await pickedFile.readAsBytes();
        await ref.read(tripInteractionsProvider).addPhoto(
              widget.trip.id,
              bytes,
              pickedFile.name,
              albumId: albumId,
            );
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Photo uploaded successfully!')));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ErrorHandler.getMessage(e))));
      }
    }
  }

  Future<void> _showCreateAlbumDialog() async {
    final controller = TextEditingController();
    final name = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('New Album'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(labelText: 'Album Name', hintText: 'e.g. Day 1, Sceneries'),
          autofocus: true,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text),
            child: const Text('Create'),
          ),
        ],
      ),
    );

    if (name != null && name.isNotEmpty) {
      try {
        await ref.read(tripInteractionsProvider).createAlbum(widget.trip.id, name);
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ErrorHandler.getMessage(e))));
        }
      }
    }
  }

  Future<void> _downloadFile(String url, String fileName) async {
    const storage = FlutterSecureStorage();
    final token = await storage.read(key: 'access_token');
    
    final String fullUrlWithAuth = url.contains('?') 
        ? '${AppConstants.apiBaseUrl}$url&token=$token' 
        : '${AppConstants.apiBaseUrl}$url?token=$token';

    final Uri uri = Uri.parse(fullUrlWithAuth);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Could not start download')));
      }
    }
  }

  Future<void> _downloadAlbum(String albumId) async {
    const storage = FlutterSecureStorage();
    final token = await storage.read(key: 'access_token');
    
    final url = '${AppConstants.apiBaseUrl}/api/trips/${widget.trip.id}/albums/$albumId/download?token=$token';
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Could not start album download')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool canUpload = widget.trip.status == 'in_progress' || widget.trip.status == 'completed';

    // Group photos by album
    final Map<String, List<TripPhoto>> albumMap = {};
    for (var photo in widget.trip.photos) {
      final aid = photo.albumId;
      if (!albumMap.containsKey(aid)) albumMap[aid] = [];
      albumMap[aid]!.add(photo);
    }

    final List<TripAlbum> allAlbums = [
      TripAlbum(id: 'general', name: 'General', createdBy: '', createdAt: DateTime.now()),
      ...widget.trip.albums,
    ];

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          if (canUpload)
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: _showCreateAlbumDialog,
                      icon: const Icon(Icons.create_new_folder),
                      label: const Text('New Album'),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        value: _selectedAlbumId,
                        decoration: const InputDecoration(
                          hintText: 'Select Album for Upload',
                          contentPadding: EdgeInsets.symmetric(horizontal: 12),
                          border: OutlineInputBorder(),
                        ),
                        items: allAlbums.map((a) {
                          return DropdownMenuItem(value: a.id, child: Text(a.name));
                        }).toList(),
                        onChanged: (val) => setState(() => _selectedAlbumId = val),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ...allAlbums.map((album) {
            final photos = albumMap[album.id] ?? [];
            if (photos.isEmpty && album.id != 'general' && !widget.trip.albums.contains(album)) {
              return const SliverToBoxAdapter(child: SizedBox.shrink());
            }

            return SliverMainAxisGroup(
              slivers: [
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          album.name,
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        if (photos.isNotEmpty)
                          IconButton(
                            icon: const Icon(Icons.download_for_offline),
                            tooltip: 'Download Bundle (ZIP)',
                            onPressed: () => _downloadAlbum(album.id),
                          ),
                      ],
                    ),
                  ),
                ),
                if (photos.isEmpty)
                  const SliverToBoxAdapter(
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16.0),
                      child: Text('No photos in this album'),
                    ),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    sliver: SliverGrid(
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 3,
                        crossAxisSpacing: 8,
                        mainAxisSpacing: 8,
                      ),
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final photo = photos[index];
                          final fullUrl = photo.url.startsWith('http') ? photo.url : '${AppConstants.apiBaseUrl}${photo.url}';

                          return GestureDetector(
                            onTap: () => _showPhotoViewer(fullUrl, photo),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Stack(
                                fit: StackFit.expand,
                                children: [
                                  Image.network(fullUrl, fit: BoxFit.cover),
                                  Positioned(
                                    bottom: 0,
                                    right: 0,
                                    child: Container(
                                      decoration: BoxDecoration(
                                        color: Colors.black45,
                                        borderRadius: const BorderRadius.only(topLeft: Radius.circular(8)),
                                      ),
                                      child: IconButton(
                                        icon: const Icon(Icons.download, color: Colors.white, size: 18),
                                        onPressed: () => _downloadFile(photo.url, 'photo_${photo.id}.jpg'),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                        childCount: photos.length,
                      ),
                    ),
                  ),
              ],
            );
          }).toList(),
          const SliverToBoxAdapter(child: SizedBox(height: 100)),
        ],
      ),
      floatingActionButton: canUpload
          ? FloatingActionButton(
              onPressed: () => _pickAndUploadPhoto(_selectedAlbumId),
              child: const Icon(Icons.add_a_photo),
            )
          : null,
    );
  }

  void _showPhotoViewer(String url, TripPhoto photo) {
    showDialog(
      context: context,
      builder: (context) => Dialog.fullscreen(
        child: Stack(
          children: [
            Center(child: Image.network(url)),
            Positioned(
              top: 16,
              left: 16,
              child: CircleAvatar(
                backgroundColor: Colors.black54,
                child: IconButton(
                  icon: const Icon(Icons.close, color: Colors.white),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
            ),
            Positioned(
              bottom: 32,
              left: 16,
              right: 16,
              child: Container(
                padding: const EdgeInsets.all(12),
                color: Colors.black54,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Uploaded by: ${photo.username}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    Text(DateFormat('MMM dd, yyyy HH:mm').format(photo.uploadedAt), style: const TextStyle(color: Colors.white70, fontSize: 12)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
