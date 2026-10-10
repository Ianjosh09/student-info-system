"""CRUD, atomic JSON persistence, search, export and explicit recovery.
Single-process storage: do not run concurrent writers against the same file.
"""
import csv
import json
import logging
import os
import tempfile
from pathlib import Path
from src.models.student import Student

class StorageError(Exception):
    """The stored file cannot be safely read or changed."""

class StudentService:
    def __init__(self, path, logger=None):
        self.path = Path(path)
        self.backup = self.path.with_suffix('.json.bak')
        self.logger = logger or logging.getLogger('sis')

    def _read(self, path):
        try:
            raw = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(raw, list):
                raise ValueError('Expected a JSON list.')
            students = [Student(**row) for row in raw]
            ids = [s.student_id.casefold() for s in students]
            if len(ids) != len(set(ids)):
                raise ValueError('Duplicate stored IDs.')
            return students
        except (OSError, ValueError, TypeError) as error:
            self.logger.error('Unable to load records')
            raise StorageError('Cannot read valid records. Original file was preserved; check it or restore a backup.') from error

    def all(self):
        if not self.path.exists():
            if self.backup.exists():
                raise StorageError('Data file missing; restore the available backup first.')
            return []
        return self._read(self.path)

    @staticmethod
    def _atomic_write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as file:
                temporary = Path(file.name)
                file.write(text)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def _save(self, students):
        try:
            if self.path.exists():
                previous = self._read(self.path)
                self._atomic_write(self.backup, self._json(previous))
            self._atomic_write(self.path, self._json(students))
        except OSError as error:
            self.logger.error('Unable to save records')
            raise StorageError('Save failed. Check folder access and available disk space.') from error

    @staticmethod
    def _json(students):
        return json.dumps([s.to_dict() for s in students], indent=2, ensure_ascii=False) + '\n'

    def add(self, student):
        students = self.all()
        if any(s.student_id.casefold() == student.student_id.casefold() for s in students):
            raise ValueError('That student ID already exists.')
        self._save(students + [student])
        self.logger.info('Student added')

    def get(self, student_id):
        for student in self.all():
            if student.student_id.casefold() == student_id.strip().casefold():
                return student
        raise ValueError('Student ID not found.')

    def update(self, student_id, replacement):
        students = self.all()
        for index, student in enumerate(students):
            if student.student_id.casefold() == student_id.strip().casefold():
                if replacement.student_id != student.student_id:
                    raise ValueError('Student ID cannot be changed.')
                students[index] = replacement
                self._save(students)
                self.logger.info('Student updated')
                return
        raise ValueError('Student ID not found.')

    def delete(self, student_id):
        found = self.get(student_id)
        self._save([s for s in self.all() if s.student_id != found.student_id])
        self.logger.info('Student deleted')

    def search(self, query):
        query = query.strip().casefold()
        return [s for s in self.all() if any(query in value.casefold() for value in
                (s.student_id, s.name, s.course, s.email))]

    def export_csv(self, destination):
        students = self.all()
        destination = Path(destination)
        if destination.resolve() in (self.path.resolve(), self.backup.resolve()):
            raise ValueError('Export must not overwrite the data or backup file.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        def safe(value):
            # Prevent spreadsheet programs from evaluating untrusted text.
            return "'" + value if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')) else value
        with destination.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=list(Student.__dataclass_fields__))
            writer.writeheader()
            for student in students:
                writer.writerow({k: safe(v) for k, v in student.to_dict().items()})
        self.logger.info('CSV exported')
        return len(students)

    def restore_backup(self):
        students = self._read(self.backup)
        try:
            # Keep damaged/current bytes separately before explicit replacement.
            if self.path.exists():
                archive = self.path.with_suffix('.json.before-restore')
                self._atomic_write(archive, self.path.read_text(encoding='utf-8', errors='replace'))
            self._atomic_write(self.path, self._json(students))
        except OSError as error:
            raise StorageError('Restore failed. Check folder access.') from error
        self.logger.warning('Backup restored')
