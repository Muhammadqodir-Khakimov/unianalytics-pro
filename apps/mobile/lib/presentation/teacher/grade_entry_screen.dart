import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Baho qo'yish ekrani — `/grades` POST endpoint orqali. Tezroq MVP uchun
/// oddiy form: student_id, subject_id, grade_value, assessment_type.
/// Real production tizimda guruh tanlash → talabalar ro'yxati keladigan
/// flow bo'lishi kerak (Bosqich 14 da kengaytiriladi).
class GradeEntryScreen extends ConsumerStatefulWidget {
  const GradeEntryScreen({super.key});

  @override
  ConsumerState<GradeEntryScreen> createState() => _GradeEntryScreenState();
}

class _GradeEntryScreenState extends ConsumerState<GradeEntryScreen> {
  final _formKey = GlobalKey<FormState>();
  final _studentIdCtrl = TextEditingController();
  final _subjectIdCtrl = TextEditingController();
  final _valueCtrl = TextEditingController();
  String _assessmentType = 'JN';

  @override
  void dispose() {
    _studentIdCtrl.dispose();
    _subjectIdCtrl.dispose();
    _valueCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Baho qo‘yish')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _studentIdCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Talaba ID',
                  prefixIcon: Icon(Icons.person_outline),
                ),
                validator: (v) => int.tryParse(v ?? '') == null
                    ? 'Raqam kiriting'
                    : null,
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _subjectIdCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Fan ID',
                  prefixIcon: Icon(Icons.menu_book_outlined),
                ),
                validator: (v) => int.tryParse(v ?? '') == null
                    ? 'Raqam kiriting'
                    : null,
              ),
              const SizedBox(height: 14),
              DropdownButtonFormField<String>(
                initialValue: _assessmentType,
                decoration: const InputDecoration(
                  labelText: 'Baholash turi',
                  prefixIcon: Icon(Icons.school_outlined),
                ),
                items: const [
                  DropdownMenuItem(value: 'JN', child: Text('JN')),
                  DropdownMenuItem(value: 'ON', child: Text('ON')),
                  DropdownMenuItem(value: 'YN', child: Text('YN')),
                  DropdownMenuItem(value: 'FINAL', child: Text('Yakuniy')),
                ],
                onChanged: (v) =>
                    setState(() => _assessmentType = v ?? 'JN'),
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _valueCtrl,
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Ball (0-100)',
                  prefixIcon: Icon(Icons.star_outline),
                ),
                validator: (v) {
                  final n = double.tryParse(v ?? '');
                  if (n == null) return 'Raqam kiriting';
                  if (n < 0 || n > 100) return '0 dan 100 gacha';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _submit,
                icon: const Icon(Icons.save_outlined),
                label: const Text('Saqlash'),
              ),
              const SizedBox(height: 16),
              Text(
                'Eslatma: bu MVP forma. Bosqich 14 da guruh → fan → '
                'talabalar grid bilan to‘ldiriladi.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'Saqlash endpointi keyingi iteratsiyada ulanadi (POST /grades)',
        ),
      ),
    );
  }
}
