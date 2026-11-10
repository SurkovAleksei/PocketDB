import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_anytable.db"
        db.get_db_path = lambda: self.test_db_path
        db.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    # Тест 1: Создание таблицы и проверка её наличия в реестре
    def test_create_table(self):
        columns = [{"name": "Игрок", "type": "Текст"}, {"name": "Очки", "type": "Число"}]
        db.create_table("Баскетбол", columns)
        
        tables = db.get_tables()
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["display_name"], "Баскетбол")
        self.assertTrue(tables[0]["name"].startswith("basketbol"))

    # Тест 2: Добавление записей и их чтение
    def test_add_and_get_rows(self):
        columns = [{"name": "Игрок", "type": "Текст"}, {"name": "Очки", "type": "Число"}]
        db.create_table("Матч", columns)
        table_name = db.get_tables()[0]["name"]

        db.add_row(table_name, {"Игрок": "Лео", "Очки": 30})
        db.add_row(table_name, {"Игрок": "Курри", "Очки": 20})

        rows = db.get_rows(table_name)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Игрок"], "Лео")

    # Тест 3: Фильтрация записей по числу (>) и по тексту (LIKE)
    def test_filter_rows(self):
        columns = [{"name": "Игрок", "type": "Текст"}, {"name": "Очки", "type": "Число"}]
        db.create_table("Матч", columns)
        table_name = db.get_tables()[0]["name"]

        db.add_row(table_name, {"Игрок": "Лео", "Очки": 30})
        db.add_row(table_name, {"Игрок": "Курри", "Очки": 20})

        res_num = db.get_rows(table_name, filters=[("Очки", ">", 25)])
        self.assertEqual(len(res_num), 1)
        self.assertEqual(res_num[0]["Игрок"], "Лео")

        res_text = db.get_rows(table_name, filters=[("Игрок", "LIKE", "Кур")])
        self.assertEqual(len(res_text), 1)
        self.assertEqual(res_text[0]["Игрок"], "Курри")

    # Тест 4: Обновление данных в существующей записи
    def test_update_row(self):
        columns = [{"name": "Игрок", "type": "Текст"}, {"name": "Очки", "type": "Число"}]
        db.create_table("Матч", columns)
        table_name = db.get_tables()[0]["name"]

        db.add_row(table_name, {"Игрок": "Лео", "Очки": 30})
        row_id = db.get_rows(table_name)[0]["id"]

        db.update_row(table_name, row_id, {"Очки": 35})
        updated_row = db.get_rows(table_name)[0]
        self.assertEqual(updated_row["Очки"], 35)

    # Тест 5: Удаление отдельной записи и всей таблицы целиком
    def test_delete_row_and_table(self):
        columns = [{"name": "Игрок", "type": "Текст"}]
        db.create_table("Тест", columns)
        table_name = db.get_tables()[0]["name"]

        db.add_row(table_name, {"Игрок": "Лео"})
        row_id = db.get_rows(table_name)[0]["id"]

        db.delete_row(table_name, row_id)
        self.assertEqual(len(db.get_rows(table_name)), 0)

        db.delete_table(table_name)
        self.assertEqual(len(db.get_tables()), 0)

    # Тест 6: Форматирование вывода чисел (удаление лишнего .0)
    def test_format_value(self):
        self.assertEqual(db.format_value(1.0), "1")
        self.assertEqual(db.format_value(1.5), "1.5")
        self.assertEqual(db.format_value("Текст"), "Текст")
        self.assertEqual(db.format_value(None), "")

    # Тест 7: Резервное копирование базы данных
    def test_backup_db(self):
        import tempfile
        import os
        import shutil
        
        test_dir = tempfile.mkdtemp()
        
        original_expanduser = os.path.expanduser
        os.path.expanduser = lambda x: test_dir
        
        try:
            columns = [{"name": "Игрок", "type": "Текст"}]
            db.create_table("Тест бэкапа", columns)
            
            backup_path = db.backup_db()
            
            self.assertTrue(os.path.exists(backup_path))
            self.assertTrue(backup_path.endswith(".db"))
            self.assertGreater(os.path.getsize(backup_path), 0)
            
        finally:
            os.path.expanduser = original_expanduser
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()