import unittest
import sys
import os

# Добавляем корень проекта в путь, чтобы найти папку widgets
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем реальный валидатор из приложения
from widgets.validators import validate_field

class TestValidation(unittest.TestCase):

    # Тест 1: Строгая проверка чисел (запрет букв и лишних символов)
    def test_number_validation(self):
        self.assertEqual(validate_field("Число", "42"), (True, 42, None))
        self.assertEqual(validate_field("Число", "-10"), (True, -10, None))
        self.assertEqual(validate_field("Число", "3,14"), (True, 3.14, None))
        
        self.assertFalse(validate_field("Число", "abc")[0])
        self.assertFalse(validate_field("Число", "+10")[0])
        self.assertFalse(validate_field("Число", "1e5")[0])
        self.assertFalse(validate_field("Число", "10.5.5")[0])

    # Тест 2: Проверка логического типа "Да/Нет"
    def test_boolean_validation(self):
        for val in ["1", "да", "yes", "true", "+"]:
            self.assertEqual(validate_field("Да/Нет", val), (True, 1, None))
        for val in ["0", "нет", "no", "false", "-"]:
            self.assertEqual(validate_field("Да/Нет", val), (True, 0, None))
        self.assertFalse(validate_field("Да/Нет", "может быть")[0])

    # Тест 3: Проверка дат 
    def test_date_validation(self):
        self.assertEqual(validate_field("Дата", "13.10.2026"), (True, "2026-10-13", None))
        self.assertEqual(validate_field("Дата", "13/10/2026"), (True, "2026-10-13", None))
        self.assertEqual(validate_field("Дата", "2026-10-13"), (True, "2026-10-13", None))
        
        self.assertFalse(validate_field("Дата", "31.02.2026")[0])
        self.assertFalse(validate_field("Дата", "1899-01-01")[0])
        self.assertFalse(validate_field("Дата", "завтра")[0])

    # Тест 4: Проверка времени 
    def test_time_validation(self):
        self.assertEqual(validate_field("Время", "13.30"), (True, "13:30", None))
        self.assertEqual(validate_field("Время", "1330"), (True, "13:30", None))
        self.assertEqual(validate_field("Время", "9.05"), (True, "09:05", None))
        
        self.assertFalse(validate_field("Время", "24:00")[0])
        self.assertFalse(validate_field("Время", "12:60")[0])
        self.assertFalse(validate_field("Время", "утро")[0])

if __name__ == '__main__':
    unittest.main()