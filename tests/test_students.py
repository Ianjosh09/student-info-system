"""Isolated tests use temporary directories, never the project data."""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.models.student import Student
from src.services.student_service import StudentService, StorageError

class StudentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'students.json'
        self.service = StudentService(self.path)
        self.student = Student('S001', 'Sample Student', 20, 'BSIT', 2, 'sample@example.com')

    def test_crud_and_restart(self):
        self.service.add(self.student)
        self.assertEqual(StudentService(self.path).get('s001'), self.student)
        changed = Student('S001', 'Updated Student', 21, 'BSCS', 3, 'new@example.com')
        self.service.update('S001', changed)
        self.assertEqual(self.service.all(), [changed])
        self.service.delete('s001')
        self.assertEqual(self.service.all(), [])

    def test_duplicate_case_insensitive(self):
        self.service.add(self.student)
        with self.assertRaises(ValueError):
            self.service.add(Student('s001', 'Other', 20, 'BSIT', 2, 'a@example.com'))
        self.assertEqual(len(self.service.all()), 1)

    def test_invalid_fields(self):
        for field, value in [('age', 0), ('age', 121), ('age', True), ('year_level', 7),
                             ('email', 'bad'), ('name', ''), ('student_id', '../id')]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                Student(**(self.student.to_dict() | {field: value}))

    def test_boundary_values(self):
        for age in (1, 120):
            for year in (1, 6):
                Student(**(self.student.to_dict() | {'age': age, 'year_level': year}))

    def test_missing_student(self):
        with self.assertRaises(ValueError):
            self.service.delete('missing')
        with self.assertRaises(ValueError):
            self.service.update('missing', self.student)

    def test_search(self):
        self.service.add(self.student)
        for query in ('s001', 'SAMPLE', 'bsit', '@example'):
            self.assertEqual(self.service.search(query), [self.student])
        self.assertEqual(self.service.search('absent'), [])

    def test_corruption_preserved(self):
        self.path.write_text('{broken')
        with self.assertRaises(StorageError):
            self.service.add(self.student)
        self.assertEqual(self.path.read_text(), '{broken')

    def test_backup_restore(self):
        self.service.add(self.student)
        self.service.delete('S001')
        self.path.write_text('{broken')
        self.service.restore_backup()
        self.assertEqual(self.service.all(), [self.student])
        self.assertEqual(self.path.with_suffix('.json.before-restore').read_text(), '{broken')

    def test_missing_file_with_backup(self):
        self.service.add(self.student)
        self.service.delete('S001')
        self.path.unlink()
        with self.assertRaises(StorageError):
            self.service.all()
        self.service.restore_backup()
        self.assertEqual(self.service.all(), [self.student])

    def test_failed_save_keeps_original(self):
        self.service.add(self.student)
        with patch('src.services.student_service.os.replace', side_effect=OSError('denied')):
            with self.assertRaises(StorageError):
                self.service.delete('S001')
        self.assertEqual(self.service.all(), [self.student])

    def test_csv_formula_protection(self):
        self.service.add(Student('S002', '=1+1', 20, 'BSIT', 1, 'a@example.com'))
        target = self.path.parent / 'export.csv'
        self.assertEqual(self.service.export_csv(target), 1)
        with target.open(newline='') as file:
            self.assertEqual(next(csv.DictReader(file))['name'], "'=1+1")
        with self.assertRaises(ValueError):
            self.service.export_csv(self.path)

    def test_invalid_stored_schema(self):
        for content in ('{}', '[{}]', '[null]'):
            self.path.write_text(content)
            with self.assertRaises(StorageError):
                self.service.all()

if __name__ == '__main__':
    unittest.main()
