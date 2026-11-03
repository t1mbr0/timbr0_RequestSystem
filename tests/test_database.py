from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "database"


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript((DB_DIR / "schema.sql").read_text(encoding="utf-8"))
        self.conn.executescript((DB_DIR / "seed.sql").read_text(encoding="utf-8"))

    def tearDown(self):
        self.conn.close()

    def test_required_tables_and_seed_data(self):
        tables = {row[0] for row in self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )}
        self.assertTrue({"Users", "Requests", "Statuses", "Categories", "Comments"}.issubset(tables))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM Requests").fetchone()[0], 5)
        self.assertGreaterEqual(self.conn.execute("SELECT COUNT(*) FROM Categories").fetchone()[0], 4)

    def test_foreign_key_rejects_orphan_request(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Requests(number, title, description, applicant_id, category_id, status_id) "
                "VALUES ('REQ-X', 'Тест', 'Тест', 999, 1, 1)"
            )

    def test_unique_login(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO Users(role_id, full_name, login, password_hash) VALUES (4, 'Дубликат', 'timbr0', 'hash')"
            )

    def test_nonempty_comment(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO Comments(request_id, author_id, body) VALUES (1, 5, '   ')")

    def test_category_with_requests_cannot_be_deleted(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("DELETE FROM Categories WHERE id = 1")

    def test_join_returns_expected_executor(self):
        row = self.conn.execute(
            "SELECT u.full_name FROM Requests r JOIN Users u ON u.id = r.executor_id WHERE r.id = 1"
        ).fetchone()
        self.assertEqual(row[0], "Иван Петров")

    def test_full_query_script(self):
        for statement in (DB_DIR / "queries.sql").read_text(encoding="utf-8").split(";"):
            sql = "\n".join(line for line in statement.splitlines() if not line.strip().startswith("--")).strip()
            if sql:
                self.conn.execute(sql)
        self.assertEqual(self.conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM Requests").fetchone()[0], 5)


if __name__ == "__main__":
    unittest.main()
