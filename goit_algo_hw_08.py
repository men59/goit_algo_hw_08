from datetime import datetime
from collections import UserDict
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        # Check if number has 10 digits
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Wrong phone format")
        else:
            super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            # trying to turn str to datetime object
            date_object = datetime.strptime(value, '%d.%m.%Y')
            if date_object > datetime.now():
                raise ValueError("Birthday cannot be in the future.")
            super().__init__(date_object)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        
class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        phone_instance = str(Phone(phone))  # Создаём экземпляр Phone
        self.phones.append(phone_instance)
    
    def delete_phone(self, phone):
        self.phones = [p for p in  self.phones if p != phone]

    def edit_phone(self, old_phone, new_phone):
        self.delete_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p == phone:
                return p 
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday) if birthday else None

    def get_birthday(self):
        return str(self.birthday) if self.birthday else "No birthday set"

    def __str__(self):
        return f"{self.name.value:<10} | phone: {'; '.join(p for p in self.phones):<10} | birthday: {self.birthday}"


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self,name):
        if name in self.data:
            del self.data[name]

    def find(self,name):
        return self.data.get(name)
    
    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                # Extract the birthday for the current year
                this_year_birthday = record.birthday.value.replace(year=today.year)
                delta_days = (this_year_birthday - today).days
                # Check if the birthday is within the next 30 days
                if 0 <= delta_days <= 30:
                    upcoming_birthdays.append({
                        'name': record.name.value,
                        'birthday': this_year_birthday.strftime("%Y-%m-%d"),
                        'days_until': delta_days
                    })
        return upcoming_birthdays
        
book = AddressBook()

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Wrong input"
        except KeyError:
            return "No such name found"
        except IndexError:
            return "Index error"

    return inner

# Код бота
@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args
@input_error
def add_contact(args, book):
    name, phone, *birthday = args
    birthday = birthday[0] if birthday else None
    record = Record(name)
    record.add_phone(phone)
    record.add_birthday(birthday)
    book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, book):
    name, phone = args
    if name in book:
        book[name] = phone
        return "Contact updated"
    else:
        return 'Error. This name does not exist. Try adding.'
    
def show_birthday(args, book):
    name, = args
    record = book.find(name)
    if record:
        return f"{name}'s birthday: {record.get_birthday()}"
    else:
        return "Error. This name does not exist. Try adding."

def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return upcoming_birthdays
    else:
        return "No upcoming birthdays"

@input_error
def phone(args, book):
    name, = args
    if name in book:
        return f'Phone number of {name} is {book[name]}'
    else:
        return 'Error. This name does not exist. Try adding.'

def show_all(book):
    for name, record in book.data.items():
        print(name,record)

def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.birthday = Birthday(birthday)
        return f"{name}'s birthday: {record.get_birthday()}"
    else:
        return "Error. This name does not exist. Try adding."
        
        return "Birthday updated"

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main(): 
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":                  #change
            print(change_contact(args, book))
        elif command == "phone":
            print(phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "show_birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "add_birthday":
            print(add_birthday(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()