# tgbot/config.py

class Database:
    def acc_and_pass(self):
        # Реальная логика получения аккаунта и пароля
        return "UC27pubgUP@hotmail.com", "midaSuc8100"

    def done_acc(self, ids, account_and_password):
        # Реальная логика завершения аккаунта
        pass

    def code_reservation(self):
        # Реальная логика получения кода
        return "MEhFcWZJ2n2cGfkeSb"

def get_db():
    return Database()