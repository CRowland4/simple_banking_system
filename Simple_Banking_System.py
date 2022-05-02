import random
import sqlite3


def main_loop():
    """The primary loop of the program."""
    main_selection = main_menu()
    if main_selection == '1':
        create_account()
        return main_loop()
    elif main_selection == '2':
        return login_loop()
    else:
        return exit_menu()


def create_card_table():
    """Creates the table 'card' in the database if it doesn't already exist."""
    global connection
    global cursor

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS card (
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0);'''
    )

    connection.commit()


def main_menu():
    """Presents the user with the main menu, and returns the selection."""
    print("1. Create an account\n2. Log into account\n0. Exit")
    return input()


def create_account():
    """Initializes, creates, and stores a card account."""
    card = CreditCard()
    card.create_card()


def log_in():
    """Gets and validates card number and pin from customer."""
    number = input("\nEnter your card number:\n")
    pin = input("Enter your PIN:\n")
    cursor.execute('SELECT number FROM card')
    stored_numbers = cursor.fetchall()

    if number in [stored_numbers[i][0] for i in range(len(stored_numbers))]:
        cursor.execute(f'SELECT pin FROM card WHERE (number = {number})')
        matched_pin = cursor.fetchone()[0]
    else:
        print('\nWrong card number or PIN!\n')
        return False, main_loop()

    if pin == matched_pin:
        print('\nYou have successfully logged in!\n')
        return True, number
    else:
        print('\nWrong card number or PIN!\n')
        return False, main_loop()


def exit_menu():
    """Exits the program."""
    print("\nBye!")
    return


def login_menu():
    """Prints the login menu and returns user input."""
    print("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")
    return input()


def login_loop():
    """Presents the login menu and directs the user to a screen based on their selection."""
    login = log_in()

    if login[0]:
        number = login[1]
    else:
        return login[1]

    while True:
        login_input = login_menu()
        if login_input == '1':
            print(f'\nBalance: {get_balance(number)}\n')
            continue
        elif login_input == '2':
            deposit_income(number)
            continue
        elif login_input == '3':
            print(transfer(number))
            continue
        elif login_input == '4':
            print(close_account(number))
            return main_loop()
        elif login_input == '5':
            return log_out()
        else:
            return exit_menu()


def close_account(number):
    """Deletes the passed number's account from the database."""
    cursor.execute(f'DELETE FROM card WHERE number = {number}')
    connection.commit()
    return '\nThe account has been closed!\n'


def transfer(number):
    """Transfers a given amount of many from the passed account to a given account."""
    number_from = number
    number_to = input("""\nTransfer
    Enter card number:\n""")
    if number_to == number_from:
        return "You can't transfer money to the same account!"
    elif not luhn_check(number_to):
        return 'Probably you made a mistake in the card number. Please try again!'
    elif not check_for_card(number_to):
        return 'Such a card does not exist.'
    else:
        pass

    amount = int(input("Enter how much money you want to transfer:\n"))
    if amount > get_balance(number_from):
        return 'Not enough money!'
    else:
        balance_to = get_balance(number_to)
        balance_from = get_balance(number_from)
        cursor.execute(f'UPDATE card SET balance = ({amount} + {balance_to}) WHERE number = {number_to};')
        cursor.execute(f'UPDATE card SET balance = ({balance_from} - {amount}) WHERE number = {number_from};')
        connection.commit()
        return 'Success!'


def check_for_card(number):
    cursor.execute('SELECT number FROM card')
    numbers = [item[0] for item in cursor.fetchall()]
    if number in numbers:
        return True
    else:
        return False


def deposit_income(number):
    """Adds an amount of income to the account associated with the passed card number."""
    income = int(input("\nEnter income:\n"))
    cursor.execute(f'SELECT balance FROM card WHERE number = {number}')
    balance = cursor.fetchone()[0]
    cursor.execute(f'UPDATE card SET balance = ({income} + {balance}) WHERE number = {number};')
    connection.commit()
    print('Income was added!\n')


def get_balance(number):
    """Returns the balance of the account associated with the passed number."""
    cursor.execute(f'SELECT balance FROM card WHERE (number = {number})')
    return cursor.fetchone()[0]


def log_out():
    """Returns the user to the main menu from the login menu."""
    print("\nYou have successfully logged out!\n")
    return main_loop()


def luhn_check(number):
    last_digit = number[-1]
    int_list = list(map(int, number[:-1]))

    for i in range(len(int_list)):
        if i % 2 == 0:
            int_list[i] *= 2
        else:
            continue

    for j in range(len(int_list)):
        if int_list[j] > 9:
            int_list[j] -= 9
        else:
            continue

    if (sum(int_list) + int(last_digit)) % 10 == 0:
        return True
    else:
        return False


class CreditCard:
    """A class for credit card objects."""

    def __init__(self):
        """Initializes a credit card."""
        self.card_number = None
        self.pin = None
        self.balance = 0

    def create_card(self):
        """Creates a full credit card and stores the number and pin."""
        self._create_card_number()
        self._create_card_pin()
        self._store_card()

        print("\nYour card has been created\nYour card number:")
        print(self.card_number)
        print(f'Your card PIN:\n{self.pin}\n')

    def _create_card_number(self):
        """Generates a credit card number for the passed card."""
        flag = False
        while not flag:
            iin = '400000'
            account_id = ''
            checksum = '7'

            for _ in range(9):
                account_id += random.choice([str(i) for i in range(10)])

            self.card_number = iin + account_id + checksum

            flag = self._luhn_check()

    def _create_card_pin(self):
        """Generates a credit card pin for the passed card."""
        pin = ''

        for _ in range(4):
            pin += random.choice([str(i) for i in range(10)])

        self.pin = pin

    def _store_card(self):
        """Stores the card number, pin, and balance of the passed card."""
        cursor.execute('SELECT id FROM card')
        ids = cursor.fetchall()
        if len(ids) == 0:
            id_num = 0
        else:
            id_num = len(ids) - 1

        cursor.execute(f'''INSERT INTO card (id, number, pin)
                            VALUES ({id_num}, {self.card_number}, {self.pin});''')

        connection.commit()

    def _luhn_check(self):
        """Runs the luhn algorithm check on a passed card object's number."""
        last_digit = self.card_number[-1]
        int_list = list(map(int, self.card_number[:-1]))

        for i in range(len(int_list)):
            if i % 2 == 0:
                int_list[i] *= 2
            else:
                continue

        for j in range(len(int_list)):
            if int_list[j] > 9:
                int_list[j] -= 9
            else:
                continue

        if (sum(int_list) + int(last_digit)) % 10 == 0:
            return True
        else:
            return False


connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()

create_card_table()
main_loop()
