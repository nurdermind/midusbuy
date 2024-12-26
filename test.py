from unittest.mock import Mock, patch

# Создаем моки для функций из модуля tgbot
mock_db = Mock()

# Моки для функций
mock_db.acc_and_pass.return_value = ("UC27pubgUP@hotmail.com", "midaSuc8100")
mock_db.done_acc.return_value = True
mock_db.code_reservation.return_value = "MEhFcWZJ2n2cGfkeSb"

# Моки для get_db
mock_get_db = Mock(return_value=mock_db)


# Пример использования моков
def test_active_code():
    with patch("tgbot.config.get_db", mock_get_db):
        from browser import active_code  # Импортируем функцию, которую хотим протестировать

        # Вызываем функцию с моками
        active_code("51793877877", 60)


# Запуск теста
if __name__ == "__main__":
    test_active_code()
