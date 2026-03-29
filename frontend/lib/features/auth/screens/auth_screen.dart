import 'package:flutter/material.dart';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:triptracks/core/auth_provider.dart';
import 'package:triptracks/shared/widgets/responsive_center.dart';
import 'package:triptracks/core/utils/error_handler.dart';

/// Signup flows through 3 steps:
///   Step 0 — Enter email & send OTP
///   Step 1 — Enter OTP to verify email
///   Step 2 — Fill full name, username, password, service code & register
enum _SignupStep { enterEmail, verifyOtp, fillDetails }

class AuthScreen extends ConsumerStatefulWidget {
  const AuthScreen({super.key});

  @override
  ConsumerState<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends ConsumerState<AuthScreen>
    with SingleTickerProviderStateMixin {
  bool _isLogin = true;
  _SignupStep _signupStep = _SignupStep.enterEmail;

  // Login controllers
  final _loginIdentifierController = TextEditingController();
  final _loginPasswordController = TextEditingController();

  // Signup controllers
  final _signupEmailController = TextEditingController();
  final _otpController = TextEditingController();
  final _fullNameController = TextEditingController();
  final _signupUsernameController = TextEditingController();
  final _signupPasswordController = TextEditingController();
  final _serviceCodeController = TextEditingController();

  bool _obscurePassword = true;
  bool _isLoading = false;
  String? _errorMessage;

  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  Timer? _usernameDebounce;
  bool _isCheckingUsername = false;
  bool? _isUsernameAvailable;
  String _lastCheckedUsername = '';

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    );
    _fadeController.forward();
    _signupUsernameController.addListener(_onUsernameChanged);
  }

  void _onUsernameChanged() {
    final username = _signupUsernameController.text.trim();
    if (username == _lastCheckedUsername) return;
    
    setState(() => _isUsernameAvailable = null);
    if (username.isEmpty) return;

    if (_usernameDebounce?.isActive ?? false) _usernameDebounce!.cancel();
    _usernameDebounce = Timer(const Duration(milliseconds: 600), () async {
      setState(() => _isCheckingUsername = true);
      try {
        final isAvailable = await ref.read(authStateProvider.notifier).checkUsername(username);
        if (mounted) {
          setState(() {
            _isCheckingUsername = false;
            _isUsernameAvailable = isAvailable;
            _lastCheckedUsername = username;
          });
        }
      } catch (e) {
        if (mounted) {
          setState(() {
            _isCheckingUsername = false;
            _isUsernameAvailable = null;
          });
        }
      }
    });
  }

  @override
  void dispose() {
    _loginIdentifierController.dispose();
    _loginPasswordController.dispose();
    _signupEmailController.dispose();
    _otpController.dispose();
    _fullNameController.dispose();
    _signupUsernameController.removeListener(_onUsernameChanged);
    _usernameDebounce?.cancel();
    _signupUsernameController.dispose();
    _signupPasswordController.dispose();
    _serviceCodeController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  void _switchMode() {
    _fadeController.reset();
    setState(() {
      _isLogin = !_isLogin;
      _signupStep = _SignupStep.enterEmail;
      _errorMessage = null;
    });
    _fadeController.forward();
  }

  void _setError(String? msg) => setState(() => _errorMessage = msg);

  Future<void> _handleLogin() async {
    final id = _loginIdentifierController.text.trim();
    final pw = _loginPasswordController.text;
    if (id.isEmpty || pw.isEmpty) {
      _setError('Please fill in all fields.');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      print('Attempting login');
      await ref.read(authStateProvider.notifier).login(id, pw);
      print('Login success');
    } catch (e) {
      print('Caught exception in _handleLogin: $e');
      final msg = ErrorHandler.getMessage(e);
      print('ErrorHandler returned: $msg');
      if (mounted) _setError(msg);
    } finally {
      print('Running finally block in _handleLogin');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _handleSendOtp() async {
    final email = _signupEmailController.text.trim();
    if (email.isEmpty) {
      _setError('Please enter your email.');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authStateProvider.notifier).sendOtp(email);
      if (!mounted) return;
      _fadeController.reset();
      setState(() {
        _signupStep = _SignupStep.verifyOtp;
      });
      _fadeController.forward();
    } catch (e) {
      if (mounted) _setError(ErrorHandler.getMessage(e));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _handleVerifyOtp() async {
    final email = _signupEmailController.text.trim();
    final otp = _otpController.text.trim();
    if (otp.length != 6) {
      _setError('Please enter the 6-digit OTP.');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authStateProvider.notifier).verifyOtp(email, otp);
      if (!mounted) return;
      _fadeController.reset();
      setState(() {
        _signupStep = _SignupStep.fillDetails;
      });
      _fadeController.forward();
    } catch (e) {
      if (mounted) _setError(ErrorHandler.getMessage(e));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _handleRegister() async {
    final username = _signupUsernameController.text.trim();
    final password = _signupPasswordController.text;
    final serviceCode = _serviceCodeController.text.trim().toUpperCase();

    if (username.isEmpty || password.isEmpty || serviceCode.isEmpty) {
      _setError('Username, password, and service code are required.');
      return;
    }
    if (_isUsernameAvailable == false) {
      _setError('Username is already taken.');
      return;
    }
    if (serviceCode.length != 12) {
      _setError('Service code must be exactly 12 characters.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authStateProvider.notifier).register(
            email: _signupEmailController.text.trim(),
            username: username,
            password: password,
            serviceCode: serviceCode,
            fullName: _fullNameController.text.trim().isNotEmpty
                ? _fullNameController.text.trim()
                : null,
          );
    } catch (e) {
      if (mounted) _setError(ErrorHandler.getMessage(e));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final primary = theme.colorScheme.primary;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              primary.withValues(alpha: 0.08),
              theme.scaffoldBackgroundColor,
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: ResponsiveCenter(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
                child: FadeTransition(
                opacity: _fadeAnimation,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Logo
                    CircleAvatar(
                      radius: 36,
                      backgroundColor: primary.withValues(alpha: 0.15),
                      child: Icon(Icons.map_rounded, size: 40, color: primary),
                    ),
                    const SizedBox(height: 20),
                    Text(
                      _isLogin ? 'Welcome Back!' : _stepTitle(),
                      textAlign: TextAlign.center,
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      _isLogin ? 'Sign in to TripTracks' : _stepSubtitle(),
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(
                          alpha: 0.6,
                        ),
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Form content
                    if (_isLogin)
                      _buildLoginForm(theme)
                    else
                      _buildSignupStep(theme),

                    const SizedBox(height: 24),

                    // Switch login/signup
                    TextButton(
                      onPressed: _isLoading ? null : _switchMode,
                      child: Text(
                        _isLogin
                            ? "Don't have an account? Sign Up"
                            : 'Already have an account? Login',
                        style: TextStyle(color: primary),
                      ),
                    ),
                  ],
                ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  String _stepTitle() {
    return switch (_signupStep) {
      _SignupStep.enterEmail => 'Create Account',
      _SignupStep.verifyOtp => 'Verify Email',
      _SignupStep.fillDetails => 'Your Details',
    };
  }

  String _stepSubtitle() {
    return switch (_signupStep) {
      _SignupStep.enterEmail => "We'll send a verification code to your email",
      _SignupStep.verifyOtp =>
        'Enter the 6-digit code sent to ${_signupEmailController.text}',
      _SignupStep.fillDetails =>
        'Almost there! Fill in the rest of your details.',
    };
  }

  Widget _buildLoginForm(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _loginIdentifierController,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Email or Username',
            prefixIcon: Icon(Icons.person_outline),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _loginPasswordController,
          obscureText: _obscurePassword,
          decoration: InputDecoration(
            labelText: 'Password',
            prefixIcon: const Icon(Icons.lock_outline),
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePassword ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: () =>
                  setState(() => _obscurePassword = !_obscurePassword),
            ),
          ),
        ),
        if (_errorMessage != null) _buildError(),
        const SizedBox(height: 24),
        _isLoading
            ? const Center(child: CircularProgressIndicator())
            : ElevatedButton(
                onPressed: _handleLogin,
                child: const Text('Login'),
              ),
      ],
    );
  }

  Widget _buildSignupStep(ThemeData theme) {
    return switch (_signupStep) {
      _SignupStep.enterEmail => _buildStepEmail(),
      _SignupStep.verifyOtp => _buildStepOtp(),
      _SignupStep.fillDetails => _buildStepDetails(),
    };
  }

  Widget _buildStepEmail() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _signupEmailController,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Email Address',
            prefixIcon: Icon(Icons.email_outlined),
          ),
        ),
        if (_errorMessage != null) _buildError(),
        const SizedBox(height: 24),
        _isLoading
            ? const Center(child: CircularProgressIndicator())
            : ElevatedButton(
                onPressed: _handleSendOtp,
                child: const Text('Send Verification Code'),
              ),
      ],
    );
  }

  Widget _buildStepOtp() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _otpController,
          keyboardType: TextInputType.number,
          maxLength: 6,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 28,
            letterSpacing: 8,
            fontWeight: FontWeight.bold,
          ),
          decoration: const InputDecoration(
            hintText: '• • • • • •',
            counterText: '',
          ),
        ),
        if (_errorMessage != null) _buildError(),
        const SizedBox(height: 24),
        _isLoading
            ? const Center(child: CircularProgressIndicator())
            : ElevatedButton(
                onPressed: _handleVerifyOtp,
                child: const Text('Verify Code'),
              ),
        TextButton(
          onPressed: _isLoading
              ? null
              : () {
                  _fadeController.reset();
                  setState(() {
                    _signupStep = _SignupStep.enterEmail;
                    _errorMessage = null;
                  });
                  _fadeController.forward();
                },
          child: const Text('Back / Resend Code'),
        ),
      ],
    );
  }

  Widget _buildStepDetails() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: _fullNameController,
          decoration: const InputDecoration(
            labelText: 'Full Name (optional)',
            prefixIcon: Icon(Icons.badge_outlined),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _signupUsernameController,
          decoration: InputDecoration(
            labelText: 'Username',
            prefixIcon: const Icon(Icons.alternate_email),
            errorText: _isUsernameAvailable == false ? 'Username is taken' : null,
            suffixIcon: _buildUsernameSuffix(),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _signupPasswordController,
          obscureText: _obscurePassword,
          decoration: InputDecoration(
            labelText: 'Password',
            prefixIcon: const Icon(Icons.lock_outline),
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePassword ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: () =>
                  setState(() => _obscurePassword = !_obscurePassword),
            ),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _serviceCodeController,
          maxLength: 12,
          textCapitalization: TextCapitalization.characters,
          decoration: const InputDecoration(
            labelText: 'Service Code',
            prefixIcon: Icon(Icons.vpn_key_outlined),
            hintText: 'XXXXXXXXXXXX',
            counterText: '',
          ),
        ),
        if (_errorMessage != null) _buildError(),
        const SizedBox(height: 24),
        _isLoading
            ? const Center(child: CircularProgressIndicator())
            : ElevatedButton(
                onPressed: _handleRegister,
                child: const Text('Create Account'),
              ),
      ],
    );
  }

  Widget _buildError() {
    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.red.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
        ),
        child: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 18),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                _errorMessage!,
                style: const TextStyle(color: Colors.red, fontSize: 13),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget? _buildUsernameSuffix() {
    if (_signupUsernameController.text.trim().isEmpty) return null;
    if (_isCheckingUsername) {
      return const Padding(
        padding: EdgeInsets.all(12.0),
        child: SizedBox(
          width: 16, height: 16,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }
    if (_isUsernameAvailable == true) {
      return const Icon(Icons.check_circle, color: Colors.green);
    }
    if (_isUsernameAvailable == false) {
      return const Icon(Icons.cancel, color: Colors.red);
    }
    return null;
  }
}
