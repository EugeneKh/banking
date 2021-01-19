import sqlite3
# TODO: создать пользователя с полями или обьект пользователь
# TODO: получать из запроса к БД значения по именам полей как?
# TODO:  проверять что курсор еще жив  отдельной функцией
# FIXME: Implement this.


class Bank:
    def __init__(self):
        self.cur_user = ()
        self.conn = sqlite3.connect('card.s3db')
        self.cursor = self.conn.cursor()
        self.menu(3)

    def menu(self, code):
        while code:
            disp = ['1. Create an account',
                    '2. Log into account',
                    '0. Exit']
            print(*disp, sep="\n")
            code = int(input())
            if code == 1:
                self.create()
            if code == 2:
                code = self.login()
        self.conn.close()
        print("Bye!")

    def create(self):
        card_num, pin = self.generate()
        sql = f"insert into card (number, pin, balance) values({card_num}, {pin}, {0})"
        self.cursor.execute(sql)
        self.conn.commit()
        print('Your card has been created')
        print(f'Your card number:\n{card_num}')
        print(f'Your card PIN:\n{pin}')

    def generate(self) -> (str, str):
        """

        :return:  Card number + PIN
        """
        from string import digits
        from secrets import choice
        bank_id = '400000'
        customer_id = ''.join(choice(digits) for _ in range(9))
        card_num = self.add_lun(bank_id + customer_id)
        pin = ''.join(choice(digits) for _ in range(4))
        return card_num, pin

    @staticmethod
    def add_lun(card_num: str) -> str:
        """
        Добавляет к строке с номером карты
        контрольную цифру по алгоритму Лу`на

        :param card_num: номер карты
        :return: дополненный номер карты
        """
        lun = 0
        for i, n in enumerate(card_num[::-1]):
            n = int(n)
            if i % 2 == 0:
                n *= 2
                if n > 9:
                    n -= 9
            lun += n
        lun = (lun * 9) % 10
        return card_num + str(lun)

    def login(self):
        user_card = input('Enter your card number:')
        user_pin = input('Enter your PIN:')
        sql = f"select * from card " \
              f"where number = {user_card} and pin = {user_pin}"
        self.cursor.execute(sql)
        self.cur_user = self.cursor.fetchone()
        # print(self.cur_user)

        if self.cur_user:
            print('You have successfully logged in!')
            return self.user_menu(3)
        else:
            print('Wrong card number or PIN!')
            return 3

    def user_menu(self, code):
        while code:
            disp = ['1. Balance',
                    '2. Add income',
                    '3. Do transfer',
                    '4. Close account',
                    '5. Log out',
                    '0. Exit']
            print(*disp, sep="\n")
            code = int(input())
            if code == 1:
                bal = self.balance(self.cur_user[1])
                print('Balance: {0}'.format(bal))
            if code == 2:
                if self.add_income(int(input("Enter income:")), self.cur_user[1]):
                    print('Income was added!')
            if code == 3:
                self.transfer()
            if code == 4:
                if self.close_acc(self.cur_user[1]):
                    print("The account has been closed!")
            if code == 5:
                self.cur_user = ()
                print('You have successfully logged out!')
                return 3
        return 0

    def balance(self, user_card) -> int:
        """

        :rtype: int
        :return:
        """
        sql = f"select balance from card where number = {user_card}"
        self.cursor.execute(sql)
        bal = self.cursor.fetchone()
        bal = int(bal[0])
        return bal

    def add_income(self, add_sum: int, user_card):
        sql = f'update card SET balance={self.balance(user_card) + add_sum} where number = {user_card}'
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def transfer(self):
        """

        :return:
        """
        print("Transfer")
        card_to = input("Enter card number:")
        if not self.luhn_test(card_to):
            print("Probably you made a mistake in the card number. Please try again!")
            return
        if not self.card_inbase(card_to):
            print("Such a card does not exist.")
            return
        trans_sum = int(input("Enter how much money you want to transfer:"))
        if not self.have_money(trans_sum):
            print("Not enough money!")
            return
        self.add_income(-trans_sum, self.cur_user[1])
        self.add_income(trans_sum, card_to)
        return

    @staticmethod
    def luhn_test(code) -> bool:
        lookup = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
        evens = sum(int(i) for i in code[-1::-2])
        odds = sum(lookup[int(i)] for i in code[-2::-2])
        return (evens + odds) % 10 == 0

    def card_inbase(self, card_num):
        sql = f"select * from card " \
              f"where number = {card_num}"
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def have_money(self, req_sum: int) -> bool:
        bal = self.balance(self.cur_user[1])
        return bal >= req_sum

    def close_acc(self, card_num) -> bool:
        sql = f"delete from card where number = {card_num}"
        self.cursor.execute(sql)
        self.conn.commit()
        return True


b = Bank()
