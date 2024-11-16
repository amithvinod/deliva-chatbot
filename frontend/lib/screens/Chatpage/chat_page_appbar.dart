import 'package:deliva/const.dart';
import 'package:flutter/material.dart';


class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final Color? backgroundColor;

  // Constructor
  const CustomAppBar({
    super.key,
    required this.title,
    this.actions,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title,style:const  TextStyle(color: Colors.white)),
      backgroundColor: backgroundColor ?? primaryColor,  // Use a default color if none is provided
      actions: actions,  // Allow custom actions
    );
  }

  // Override the preferredSize property to specify the size of the AppBar
  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
