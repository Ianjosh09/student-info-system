"""Interactive entry point. Run from the project root: python -m src.main."""
from src.models.student import Student
from src.services.student_service import StudentService, StorageError
from src.utils.config import load_config
from src.utils.logger import setup_logger

def read_student(existing=None):
    values = {}
    for field in Student.__dataclass_fields__:
        if existing and field == 'student_id':
            values[field] = existing.student_id
            continue
        current = getattr(existing, field) if existing else None
        hint = f' [{current}]' if existing else ''
        value = input(field.replace('_', ' ').title() + hint + ': ').strip()
        values[field] = current if existing and not value else value
        if field in ('age', 'year_level'):
            try:
                values[field] = int(values[field])
            except (ValueError, TypeError) as error:
                raise ValueError(f'{field} must be a whole number.') from error
    return Student(**values)

def display(students):
    if not students:
        print('No matching student records.')
    for student in students:
        print(f'\nID: {student.student_id} | Name: {student.name}')
        print(f'Age: {student.age} | Course: {student.course} | Year: {student.year_level}')
        print(f'Email: {student.email}')
    print(f'Total: {len(students)}')

def main():
    try:
        config = load_config()
        logger = setup_logger(config['log_file'])
        service = StudentService(config['data_file'], logger)
    except (OSError, ValueError) as error:
        print(f'Startup error: {error}')
        return 1
    logger.info('Application started')
    try:
        while True:
            print('\nSTUDENT INFORMATION SYSTEM\n1 Add student\n2 View students\n3 Update student\n4 Delete student\n5 Search\n6 Export CSV\n7 Restore backup\n0 Exit')
            choice = input('Choose: ').strip()
            try:
                if choice == '1':
                    service.add(read_student())
                    print('Student added.')
                elif choice == '2':
                    display(service.all())
                elif choice == '3':
                    student = service.get(input('Student ID: '))
                    print('Press Enter to keep a value.')
                    service.update(student.student_id, read_student(student))
                    print('Student updated.')
                elif choice == '4':
                    student = service.get(input('Student ID: '))
                    if input(f'Delete {student.name}? Type YES: ') == 'YES':
                        service.delete(student.student_id)
                        print('Student deleted.')
                    else:
                        print('Deletion cancelled.')
                elif choice == '5':
                    display(service.search(input('Search ID, name, course or email: ')))
                elif choice == '6':
                    count = service.export_csv(config['export_file'])
                    print(f'Exported {count} records to {config["export_file"]}')
                elif choice == '7':
                    if input('Replace current records with previous saved version? Type RESTORE: ') == 'RESTORE':
                        service.restore_backup()
                        print('Backup restored.')
                elif choice == '0':
                    return 0
                else:
                    print('Choose a listed menu option.')
            except (ValueError, StorageError, OSError) as error:
                logger.warning('Operation failed: %s', type(error).__name__)
                print(f'Error: {error}')
    except (EOFError, KeyboardInterrupt):
        print('\nGoodbye.')
        return 0
    finally:
        logger.info('Application stopped')

if __name__ == '__main__':
    raise SystemExit(main())
