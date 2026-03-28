/// Maps an ISO 4217 currency code to its display symbol/prefix.
class CurrencyHelper {
  static const _symbols = <String, String>{
    'INR': '₹',
    'USD': '\$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'AUD': 'A\$',
    'CAD': 'C\$',
    'SGD': 'S\$',
    'AED': 'AED ',
    'CHF': 'CHF ',
  };

  /// Returns the symbol for [code], or the code itself as fallback.
  static String symbol(String? code) =>
      _symbols[code?.toUpperCase()] ?? (code ?? '\$');

  /// Formats [amount] with the currency symbol for [code].
  static String format(double amount, String? code) =>
      '${symbol(code)}${amount.toStringAsFixed(2)}';
}
