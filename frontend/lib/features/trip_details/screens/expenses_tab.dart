// Code for expenses_tab.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/models/trip.dart';
import 'package:frontend/features/trip_details/providers/trip_interactions_provider.dart';
import 'package:frontend/features/trip_details/providers/trip_details_provider.dart';
import 'package:frontend/shared/widgets/responsive_center.dart';
import 'package:frontend/core/utils/error_handler.dart';
import 'package:frontend/core/utils/currency_helper.dart';
import 'package:frontend/features/profile/providers/profile_provider.dart';
import 'package:intl/intl.dart';

class ExpensesTab extends ConsumerWidget {
  final Trip trip;
  const ExpensesTab({super.key, required this.trip});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          const TabBar(
            labelColor: Colors.deepPurple,
            unselectedLabelColor: Colors.grey,
            tabs: [
              Tab(text: "Transactions"),
              Tab(text: "Balances (Settle)"),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                _TransactionsView(trip: trip),
                _BalancesView(trip: trip),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TransactionsView extends ConsumerStatefulWidget {
  final Trip trip;
  const _TransactionsView({required this.trip});

  @override
  ConsumerState<_TransactionsView> createState() => _TransactionsViewState();
}

class _TransactionsViewState extends ConsumerState<_TransactionsView> {
  void _showAddExpenseDialog(Map<String, dynamic> userNames) {
    showDialog(
      context: context,
      builder: (context) => _AddExpenseDialog(trip: widget.trip, userNames: userNames),
    );
  }

  @override
  Widget build(BuildContext context) {
    final balancesAsync = ref.watch(tripBalancesProvider(widget.trip.id));
    double totalExpenses = widget.trip.expenses.fold(0.0, (sum, item) => sum + item.amount);

    return ResponsiveCenter(
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Total: ${CurrencyHelper.format(totalExpenses, ref.read(profileSettingsProvider).value?.currency)}',
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                ElevatedButton.icon(
                  icon: const Icon(Icons.add),
                  label: const Text('Add Expense'),
                  onPressed: balancesAsync.maybeWhen(
                    data: (data) => () => _showAddExpenseDialog(data['user_names'] ?? {}),
                    orElse: () => null,
                  ),
                ),
              ],
            ),
          ),
          const Divider(),
          Expanded(
            child: widget.trip.expenses.isEmpty
                ? const Center(child: Text('No expenses recorded yet.'))
                : ListView.builder(
                    itemCount: widget.trip.expenses.length,
                    itemBuilder: (context, index) {
                      final expense = widget.trip.expenses[index];
                      // Use the balances data to get the name, fallback to ID.
                      final name = balancesAsync.maybeWhen(
                        data: (d) => (d['user_names'] as Map)[expense.paidBy] ?? expense.paidBy,
                        orElse: () => expense.paidBy,
                      );
                      return ListTile(
                        leading: const CircleAvatar(
                          backgroundColor: Colors.deepPurple,
                          child: Icon(Icons.receipt, color: Colors.white),
                        ),
                        title: Text(expense.description),
                        subtitle: Text(
                          'Paid by $name on ${DateFormat.yMd().format(expense.date)}',
                        ),
                        trailing: Text(
                          '${CurrencyHelper.format(expense.amount, ref.read(profileSettingsProvider).value?.currency)}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}

class _AddExpenseDialog extends ConsumerStatefulWidget {
  final Trip trip;
  final Map<String, dynamic> userNames;
  const _AddExpenseDialog({required this.trip, required this.userNames});

  @override
  ConsumerState<_AddExpenseDialog> createState() => _AddExpenseDialogState();
}

class _AddExpenseDialogState extends ConsumerState<_AddExpenseDialog> {
  final _descController = TextEditingController();
  final _amountController = TextEditingController();
  String _splitType = 'Equal'; // 'Equal', 'Amount', 'Percent'

  // controllers for explicit amounts/percents per user
  final Map<String, TextEditingController> _splitControllers = {};

  // We need the list of users to split among.
  late List<String> _userIds;

  // For Equal split: which members are included
  late Set<String> _selectedUserIds;

  @override
  void initState() {
    super.initState();
    _userIds = widget.trip.participants.map((p) => p.userId).toList();
    if (!_userIds.contains(widget.trip.organizerId)) {
      _userIds.add(widget.trip.organizerId);
    }
    // Default: all members selected for equal split
    _selectedUserIds = Set.from(_userIds);
    for (var uid in _userIds) {
      _splitControllers[uid] = TextEditingController();
    }
  }

  @override
  void dispose() {
    _descController.dispose();
    _amountController.dispose();
    for (var c in _splitControllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _submit() async {
    final desc = _descController.text.trim();
    final amount = double.tryParse(_amountController.text) ?? 0.0;
    
    if (desc.isEmpty || amount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Valid description and amount required.")));
      return;
    }

    Map<String, double> splits = {};
    if (_splitType == 'Equal') {
      // Only split among selected members
      final included = _selectedUserIds.toList();
      if (included.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please select at least one member')));
        return;
      }
      final perPerson = amount / included.length;
      for (var uid in included) {
        splits[uid] = perPerson;
      }
    } else {
      double totalSplit = 0.0;
      for (var uid in _userIds) {
        final val = double.tryParse(_splitControllers[uid]!.text) ?? 0.0;
        if (_splitType == 'Percent') {
          splits[uid] = (amount * val) / 100.0;
          totalSplit += val;
        } else {
          splits[uid] = val;
          totalSplit += val;
        }
      }
      if (_splitType == 'Percent' && (totalSplit < 99.9 || totalSplit > 100.1)) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Percentages must sum to 100")));
        return;
      }
      if (_splitType == 'Amount' && (totalSplit < amount - 0.1 || totalSplit > amount + 0.1)) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Amounts must sum to total expense amount")));
        return;
      }
    }

    try {
      await ref.read(tripInteractionsProvider).addExpense(
        widget.trip.id,
        desc,
        amount,
        splits: splits,
      );
      if (context.mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Expense Added')));
        ref.invalidate(tripBalancesProvider(widget.trip.id));
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ErrorHandler.getMessage(e))));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add Split Expense'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _descController,
              decoration: const InputDecoration(labelText: 'Description (e.g. Gas, Lunch)'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _amountController,
              decoration: const InputDecoration(labelText: 'Total Amount', prefixText: '\$'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 24),
            const Text('Split Strategy:', style: TextStyle(fontWeight: FontWeight.bold)),
            DropdownButton<String>(
              value: _splitType,
              isExpanded: true,
              items: const [
                DropdownMenuItem(value: 'Equal', child: Text('Equally among everyone')),
                DropdownMenuItem(value: 'Amount', child: Text('By Exact Amount')),
                DropdownMenuItem(value: 'Percent', child: Text('By Percentages')),
              ],
              onChanged: (v) {
                if (v != null) setState(() => _splitType = v);
              },
            ),
            if (_splitType == 'Equal') ...[
              const SizedBox(height: 16),
              const Text('Split among:', style: TextStyle(fontWeight: FontWeight.w600)),
              ..._userIds.map((uid) {
                final name = widget.userNames[uid]?.toString() ?? uid.substring(0, 8);
                return CheckboxListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  title: Text(name),
                  value: _selectedUserIds.contains(uid),
                  onChanged: (checked) {
                    setState(() {
                      if (checked == true) {
                        _selectedUserIds.add(uid);
                      } else {
                        _selectedUserIds.remove(uid);
                      }
                    });
                  },
                );
              }),
            ],
            if (_splitType != 'Equal') ...[
              const SizedBox(height: 16),
              ..._userIds.map((uid) {
                final name = widget.userNames[uid]?.toString() ?? uid.substring(0, 8);
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Row(
                    children: [
                      Expanded(child: Text(name)),
                      SizedBox(
                        width: 100,
                        child: TextField(
                          controller: _splitControllers[uid],
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            suffixText: _splitType == 'Percent' ? '%' : null,
                            isDense: true,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              }),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        ElevatedButton(onPressed: _submit, child: const Text('Add')),
      ],
    );
  }
}

class _BalancesView extends ConsumerWidget {
  final Trip trip;
  const _BalancesView({required this.trip});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final balancesAsync = ref.watch(tripBalancesProvider(trip.id));

    return balancesAsync.when(
      data: (data) {
        final List transfers = data['transfers'] ?? [];
        if (transfers.isEmpty) {
          return const Center(child: Text('Everyone is settled up! \u{1F389}', style: TextStyle(fontSize: 18)));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: transfers.length,
          itemBuilder: (context, index) {
            final t = transfers[index];
            final amount = t['amount'];
            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.orangeAccent,
                  child: Icon(Icons.currency_exchange, color: Colors.white),
                ),
                title: Text('${t['from_name']} owes ${t['to_name']}'),
                subtitle: Text(CurrencyHelper.format(amount, ref.read(profileSettingsProvider).value?.currency), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                trailing: ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                  onPressed: () async {
                    try {
                      await ref.read(tripInteractionsProvider).addExpense(
                        trip.id,
                        'Settled up (\u{1F4B8} Payment to ${t['to_name']})',
                        amount.toDouble(),
                        splits: { t['to_user_id']: amount.toDouble() },
                      );
                      ref.invalidate(tripBalancesProvider(trip.id));
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Debt marked as settled!')));
                      }
                    } catch (e) {
                      if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ErrorHandler.getMessage(e))));
                    }
                  },
                  child: const Text('Settle', style: TextStyle(color: Colors.white)),
                ),
              ),
            );
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, st) => Center(child: Text("Error: $err")),
    );
  }
}
