import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

import '../../services/secure_storage_service.dart';
import '../constants/app_constants.dart';
import '../errors/exceptions.dart';

final dioClientProvider = Provider<Dio>((ref) {
  final storage = ref.watch(secureStorageProvider);

  final dio = Dio(BaseOptions(
    baseUrl: AppConstants.apiBaseUrl,
    connectTimeout: const Duration(milliseconds: AppConstants.connectTimeoutMs),
    receiveTimeout: const Duration(milliseconds: AppConstants.receiveTimeoutMs),
    // Dio Map'ni JSON sifatida serialize qilishi uchun aniq constant:
    contentType: Headers.jsonContentType,
    responseType: ResponseType.json,
  ));

  // JWT auth interceptor — har bir requestga access tokenni qo'shadi
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      final token = await storage.getAccessToken();
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
      handler.next(options);
    },
    onError: (e, handler) {
      if (e.response?.statusCode == 401) {
        // TODO(auth): refresh token flow shu yerda ulanadi (keyingi taskda)
      }
      handler.next(_mapDioError(e));
    },
  ));

  // Faqat debug rejimda log
  assert(() {
    dio.interceptors.add(PrettyDioLogger(
      requestBody: true,
      responseBody: true,
      requestHeader: false,
      compact: true,
    ));
    return true;
  }());

  return dio;
});

DioException _mapDioError(DioException e) {
  String message = e.message ?? 'Tarmoq xatosi';
  if (e.response?.data is Map && (e.response!.data as Map)['detail'] != null) {
    message = (e.response!.data as Map)['detail'].toString();
  }
  final wrapped = ApiException(
    message,
    statusCode: e.response?.statusCode,
    data: e.response?.data,
  );
  return DioException(
    requestOptions: e.requestOptions,
    response: e.response,
    type: e.type,
    error: wrapped,
    message: message,
  );
}
