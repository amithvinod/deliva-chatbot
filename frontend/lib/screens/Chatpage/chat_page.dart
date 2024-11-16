import 'dart:ffi';

import 'package:deliva/const.dart';
import 'package:deliva/screens/Chatpage/chat_page_appbar.dart';
import 'package:flutter/material.dart';
import 'package:dash_chat_2/dash_chat_2.dart';
import 'package:chat_gpt_sdk/chat_gpt_sdk.dart';
import 'package:flutter_gemini/flutter_gemini.dart';
import 'package:google_generative_ai/google_generative_ai.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  Gemini gemini = Gemini.instance;
  ChatUser user = ChatUser(id: '1', firstName: "Amith", lastName: "Vinod");
  ChatUser geminiuser = ChatUser(id: '2', firstName: "Demo", lastName: "bot");

  List<ChatMessage> messages = [];
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(title: "Chat"),
      body: Container(
        color: primaryColor,
        child:
            DashChat(currentUser: user, onSend: _sendMsg, messages: messages),
      ),
    );
  }

  void _sendMsg(ChatMessage m) {
    setState(() {
      messages = [m, ...messages];
    });
    try {
      String quest = m.text;
      gemini.streamGenerateContent(quest).listen((event) {
        ChatMessage? lastmsg = messages.firstOrNull;
        if (lastmsg != null && lastmsg.user == geminiuser) {
          lastmsg = messages.removeAt(0);
          String response =
              event.content?.parts?.fold("", (prev, curr) => "$prev ${curr.text}") ??
                  "";
          lastmsg.text += response;
          setState(() {
            messages = [lastmsg!, ...messages];
          });
        } else {
          String response =
              event.content?.parts?.fold("", (prev, curr) => "$prev ${curr.text}") ??
                  "";
          ChatMessage msg = ChatMessage(
              user: geminiuser, createdAt: DateTime.now(), text: response);
          setState(() {
            messages = [msg, ...messages];
          });
        }
      });
    } catch (e) {
      print(e);
    }
  }
}
