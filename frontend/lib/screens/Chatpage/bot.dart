import 'package:deliva/const.dart';
import 'package:deliva/dialogflow.dart';
import 'package:deliva/generate_access_token.dart';
import 'package:deliva/screens/Chatpage/chat_page_appbar.dart';
import 'package:flutter/material.dart';
import 'package:dash_chat_2/dash_chat_2.dart';
// Import your Dialogflow service

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  ChatUser user = ChatUser(id: '1', firstName: "Amith", lastName: "Vinod");
  ChatUser botUser = ChatUser(id: '2', firstName: "Bot", lastName: "Assistant");

  List<ChatMessage> messages = [];
  final DialogflowService dialogflowService =
      DialogflowService(); // Initialize Dialogflow service

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(title: "Chat"),
      body: Container(
        color: primaryColor,
        child: DashChat(
          currentUser: user,
          onSend: _sendMsg,
          messages: messages,
          inputOptions: const InputOptions(sendOnEnter: true),
          quickReplyOptions: QuickReplyOptions(
            
            onTapQuickReply: (p0) {

            return _onTapQuickReply(p0);
          },
          
          ),
        ),
      ),
    );
  }

  void _sendMsg(ChatMessage message) async {
    setState(() {
      messages = [message, ...messages];
    });

    try {
      String token = await generateAccessToken();
      // Send the user's message to Dialogflow
      Map<String, dynamic> response =
          await dialogflowService.detectIntent(message.text, token);

      // Extract responseText and quickReplies from the response JSON
      String responseText = response["responseText"] ?? "";
      List<QuickReply> _quickReplies = [];
      if (response["quickReplies"] != null) {
        _quickReplies = (response["quickReplies"] as List)
            .map((quickReply) => QuickReply.fromJson(quickReply))
            .toList();
      }

      // Create a response message from the bot
      ChatMessage botMessage = ChatMessage(
          user: botUser,
          createdAt: DateTime.now(),
          isMarkdown: true,
          text: responseText,
          quickReplies: _quickReplies,
          
          );

      setState(() {
        messages = [botMessage, ...messages];
      });
    } catch (e) {
      print("Error sending message to Dialogflow: $e");
    }
  }

  void _onTapQuickReply(QuickReply quickReply) {
    // Extract the title from the quick reply and send it as a message
    String selectedReply = quickReply.title;
    ChatMessage _chatmsg = ChatMessage(user: user, createdAt: DateTime.now(),text: selectedReply);
    // Call the function to send the message
    _sendMsg(_chatmsg);
  }
}
