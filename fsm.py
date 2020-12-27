from transitions.extensions import GraphMachine

from utils import send_text_message


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_champion_data(self, event):
        print("checking whether entering champion_data")
        text = event.message.text
        return text == "1"

    def is_going_to_player_data(self, event):
        print("checking whether entering player_data")
        text = event.message.text
        return text == "2"

    def on_enter_champion_data(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        send_text_message(event.reply_token, "請輸入欲查詢的英雄名稱")

    def on_exit_champion_data(self, event = None):
        print("Leaving state1")

    def on_enter_player_data(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入欲查詢的玩家名稱")

    def on_exit_state2(self, event = None):
        print("Leaving state2")

