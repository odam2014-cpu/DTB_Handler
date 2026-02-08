def gate(_mess):
    
    bot= _mess["bot"]
    bot.send_message(   _mess["chat"],
                        "RecoveryChatID",
                        ""
            )
    bot.send_message(   _mess["chat"],
                        "",
                        str(_mess["chat"])
        )