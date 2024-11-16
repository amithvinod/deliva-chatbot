import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:googleapis_auth/auth_io.dart';

Future<String> generateAccessToken() async {
  
  final jsonCredentials = await rootBundle.loadString('assets/service_account_jua.json');
  
  final credentials = ServiceAccountCredentials.fromJson(json.decode(jsonCredentials));
  final scopes = ['https://www.googleapis.com/auth/cloud-platform'];

  final client = await clientViaServiceAccount(credentials, scopes);

  return client.credentials.accessToken.data;
}
