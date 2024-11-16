import 'dart:convert';
import 'package:deliva/const.dart';
import 'package:http/http.dart' as http;

class DialogflowService {
  final String projectId = CLOUD_PROJECT_ID;

  // This method will now take a fresh token as input
  Future<Map<String, dynamic>> detectIntent(
      String userInput, String token) async {
    final url = Uri.parse(
      "https://dialogflow.googleapis.com/v2/projects/$projectId/agent/sessions/1200000:detectIntent",
    );

    final headers = {
      "Authorization": "Bearer $token",
      "Content-Type": "application/json",
    };

    final body = jsonEncode({
      "queryInput": {
        "text": {
          "text": userInput,
          "languageCode": "en",
        }
      }
    });

    final response = await http.post(url, headers: headers, body: body);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      print(data);

      // Initialize responseText and quickReplies
      String responseText = "";
      List<Map<String, dynamic>> quickReplies = [];

      // Process fulfillmentMessages if present
      List<dynamic>? fulfillmentMessages =
          data["queryResult"]["fulfillmentMessages"];
      if (fulfillmentMessages != null && fulfillmentMessages.isNotEmpty) {
        for (var message in fulfillmentMessages) {
          if (message.containsKey("text") && responseText.isEmpty) {
            responseText = message["text"]["text"][0];
          }
          if (message.containsKey("quickReplies")) {
            quickReplies = (message["quickReplies"]["quickReplies"] as List)
                .map((reply) => {
                      "title": reply,
                      "value": reply,
                    })
                .toList();
          }
        }
      } else {
        // Use fulfillmentText as a fallback if no messages in fulfillmentMessages
        responseText = data["queryResult"]["fulfillmentText"] ?? "";
      }
      
      return {
        "responseText": responseText,
        "quickReplies": quickReplies,
      };
    } else {
      throw Exception(
          "Failed to communicate with Dialogflow: ${response.body}");
    }
  }
}
