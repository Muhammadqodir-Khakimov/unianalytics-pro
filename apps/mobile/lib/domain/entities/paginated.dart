class Paginated<T> {
  final List<T> items;
  final int total;
  final int page;
  final int pageSize;
  final int totalPages;

  const Paginated({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.totalPages,
  });

  factory Paginated.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>) parse,
  ) {
    final raw = (json['items'] ?? json['data'] ?? const []) as List;
    return Paginated(
      items: raw
          .whereType<Map<String, dynamic>>()
          .map(parse)
          .toList(growable: false),
      total: (json['total'] as num?)?.toInt() ?? raw.length,
      page: (json['page'] as num?)?.toInt() ?? 1,
      pageSize:
          (json['page_size'] ?? json['pageSize'] ?? raw.length) as int,
      totalPages: (json['total_pages'] ?? json['totalPages'] ?? 1) as int,
    );
  }

  bool get hasMore => page < totalPages;
}
