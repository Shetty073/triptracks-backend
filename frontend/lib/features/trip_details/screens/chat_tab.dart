import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/auth_provider.dart';
import 'package:frontend/core/api_client.dart';
import 'package:frontend/core/constants.dart';
import 'package:frontend/core/notification_service.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:intl/intl.dart';

class ChatMessage {
  final String id;
  final String type;
  final String userId;
  final String username;
  final String text;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.type,
    required this.userId,
    required this.username,
    required this.text,
    required this.timestamp,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? '',
      type: json['type'] ?? 'chat',
      userId: json['user_id'] ?? '',
      username: json['username'] ?? '',
      text: json['text'] ?? json['message'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
    );
  }
}

class ChatTab extends ConsumerStatefulWidget {
  final String tripId;
  const ChatTab({super.key, required this.tripId});

  @override
  ConsumerState<ChatTab> createState() => _ChatTabState();
}

class _ChatTabState extends ConsumerState<ChatTab>
    with AutomaticKeepAliveClientMixin {
  final List<ChatMessage> _messages = [];
  final _textController = TextEditingController();
  final _scrollController = ScrollController();
  final _inputFocusNode = FocusNode();   // ← keeps keyboard focus after send
  WebSocketChannel? _channel;
  String? _currentUserId;
  String? _tripTitle;  // for notification title

  bool _isLoadingHistory = false;
  bool _hasMoreHistory = true;
  String? _oldestLoadedId; // cursor for pagination
  bool _notifBannerDismissed = false;

  @override
  bool get wantKeepAlive => true; // Prevents widget destruction on tab switch

  @override
  void initState() {
    super.initState();
    // Defer so the Riverpod auth state is guaranteed to be resolved
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _connectWebSocket();
      _loadHistory();
    });
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _channel?.sink.close();
    _textController.dispose();
    _scrollController.dispose();
    _inputFocusNode.dispose();
    super.dispose();
  }

  // ── History loading ────────────────────────────────────────────────────────

  Future<void> _loadHistory({String? beforeId}) async {
    if (_isLoadingHistory || !_hasMoreHistory) return;
    setState(() => _isLoadingHistory = true);

    try {
      final dio = ref.read(dioProvider);
      final uri = '/ws/trips/${widget.tripId}/history?limit=10'
          '${beforeId != null ? '&before_id=$beforeId' : ''}';
      final resp = await dio.get(uri);
      final List<dynamic> data = resp.data as List<dynamic>;
      final List<ChatMessage> fetched =
          data.map((j) => ChatMessage.fromJson(j)).toList();

      if (fetched.isEmpty) {
        setState(() => _hasMoreHistory = false);
        return;
      }

      setState(() {
        _messages.insertAll(0, fetched); // prepend older messages at top
        _oldestLoadedId = fetched.first.id;
        if (fetched.length < 10) _hasMoreHistory = false;
      });
    } catch (_) {
      // silently fail — live chat still works
    } finally {
      if (mounted) setState(() => _isLoadingHistory = false);
    }
  }

  void _onScroll() {
    // When user scrolls to the very top, fetch older messages
    if (_scrollController.position.pixels <=
            _scrollController.position.minScrollExtent + 40 &&
        !_isLoadingHistory &&
        _hasMoreHistory) {
      _loadHistory(beforeId: _oldestLoadedId);
    }
  }

  // ── WebSocket ──────────────────────────────────────────────────────────────

  void _connectWebSocket() {
    final user = ref.read(authStateProvider).value;
    if (user == null) return;
    _currentUserId = user.id;

    final wsUrl = Uri.parse(
      AppConstants.chatWebSocketUrl(widget.tripId, user.id, user.username),
    );

    _channel = WebSocketChannel.connect(wsUrl);
    _channel!.stream.listen(
      (data) {
        if (!mounted) return;
        try {
          final decodedData = json.decode(data.toString()) as Map<String, dynamic>;
          setState(() {
            if (decodedData['type'] == 'chat' ||
                decodedData['type'] == 'system') {
              _messages.add(ChatMessage.fromJson(decodedData));
            }
          });
          // Notify if message is from someone else
          if (decodedData['type'] == 'chat' &&
              decodedData['user_id'] != _currentUserId) {
            try {
              NotificationService.instance.showChatMessage(
                tripTitle: _tripTitle ?? 'Trip Chat',
                sender: decodedData['username'] ?? 'Someone',
                text: decodedData['text'] ?? '',
              );
            } catch (_) {}
          }
          // Auto-scroll to bottom
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (_scrollController.hasClients) {
              _scrollController.animateTo(
                _scrollController.position.maxScrollExtent,
                duration: const Duration(milliseconds: 200),
                curve: Curves.easeOut,
              );
            }
          });
        } catch (_) {}
      },
      onError: (_) {},
      cancelOnError: false,
    );
  }

  void _sendMessage() {
    if (_textController.text.trim().isEmpty || _channel == null) return;
    _channel!.sink.add(json.encode({'type': 'chat', 'text': _textController.text.trim()}));
    _textController.clear();
    // Keep keyboard open and input focused after sending
    _inputFocusNode.requestFocus();
  }

  // ── UI ─────────────────────────────────────────────────────────────────────

  Widget _buildMessage(ChatMessage msg) {
    if (msg.type == 'system') {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Center(
          child: Text(
            msg.text,
            style: const TextStyle(
              color: Colors.grey,
              fontStyle: FontStyle.italic,
              fontSize: 12,
            ),
          ),
        ),
      );
    }

    final isMe = msg.userId == _currentUserId;
    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isMe ? Colors.deepPurple : Colors.grey.shade300,
          borderRadius: BorderRadius.circular(16).copyWith(
            bottomRight: isMe ? const Radius.circular(0) : const Radius.circular(16),
            bottomLeft: !isMe ? const Radius.circular(0) : const Radius.circular(16),
          ),
        ),
        child: Column(
          crossAxisAlignment:
              isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!isMe)
              Text(
                msg.username,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                  color: Colors.deepPurple.shade900,
                ),
              ),
            Text(
              msg.text,
              style: TextStyle(
                color: isMe ? Colors.white : Colors.black,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              DateFormat.Hm().format(msg.timestamp),
              style: TextStyle(
                color: isMe ? Colors.white70 : Colors.black54,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    super.build(context); // Required for AutomaticKeepAliveClientMixin
    return Column(
      children: [
        // ── Notification permission banner (Web only) ──────────────────────
        if (kIsWeb && !_notifBannerDismissed)
          MaterialBanner(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            content: const Text(
              '🔔 Enable notifications to get alerted about new messages.',
              style: TextStyle(fontSize: 13),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  NotificationService.instance.requestWebPermission();
                  setState(() => _notifBannerDismissed = true);
                },
                child: const Text('Enable'),
              ),
              TextButton(
                onPressed: () => setState(() => _notifBannerDismissed = true),
                child: const Text('Dismiss'),
              ),
            ],
          ),
        // ── "Load more" spinner at the top ──────────────────────────────────
        if (_isLoadingHistory)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 8),
            child: Center(
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
          ),
        if (!_hasMoreHistory && _messages.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Center(
              child: Text(
                '— Beginning of chat —',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
              ),
            ),
          ),

        // ── Message list ────────────────────────────────────────────────────
        Expanded(
          child: _messages.isEmpty && !_isLoadingHistory
              ? const Center(child: Text('No messages yet. Say hi! 👋'))
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length,
                  itemBuilder: (_, i) => _buildMessage(_messages[i]),
                ),
        ),

        // ── Input bar ───────────────────────────────────────────────────────
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          color: Theme.of(context).scaffoldBackgroundColor,
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _textController,
                  focusNode: _inputFocusNode,
                  decoration: InputDecoration(
                    hintText: 'Type a message...',
                    filled: true,
                    fillColor: Colors.grey.shade200,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 8),
              CircleAvatar(
                backgroundColor: Colors.deepPurple,
                child: IconButton(
                  icon: const Icon(Icons.send, color: Colors.white, size: 20),
                  onPressed: _sendMessage,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
