class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  const ApiException(this.message, {this.statusCode, this.data});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class UnauthorizedException extends ApiException {
  const UnauthorizedException(super.message, {super.data})
      : super(statusCode: 401);
}

class NetworkException extends ApiException {
  const NetworkException(super.message) : super(statusCode: null);
}

class CacheException implements Exception {
  final String message;
  const CacheException(this.message);
  @override
  String toString() => 'CacheException: $message';
}
