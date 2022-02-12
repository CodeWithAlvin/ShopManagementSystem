import sqlite3
import os
from bill import genrate

class Store:
    def __init__(self):
        pass

    def load_store(self):
        # Getting available stores
        available_stores = [store for store in os.listdir('data') if store.endswith('.db')]
        # map store in dict with numbers
        store_dict = {i+1:store for i, store in enumerate(available_stores)}
        # Asking for Store Number
        print('Available stores:')
        for i, store in store_dict.items():
            print(f'{i} - Open {store}')

        # get store number with handling exception
        while True:
            store_number = input('Enter store number: ')
            if store_number.isdigit():
                if int(store_number) in store_dict.keys():
                    break
                else:
                    print('Wrong store number! Please Specify again!')
            else:
                print("Wrong store number! Please Specify as an Integer.")

        # Loading Store
        self.name = store_dict[int(store_number)]
        self.conn = sqlite3.connect(f'data/{self.name}')
        self.cursor = self.conn.cursor()

    def create_store(self):
        name = input('Enter store name: ')
        print("Do you want to create a new store? (y/n)")
        choice = input()
        if choice.lower() == 'y':
            self.name = name
            self.connection = sqlite3.connect(f"{name}.db")
            self.cursor = self.connection.cursor()
            # Creating table
            # table for adding store items
            self.cursor.execute('CREATE TABLE ITEMS (itemname TEXT, quantity INT, PRIMARY KEY (itemname))')
            # Table for adding BORROWINGS details
            self.cursor.execute('CREATE TABLE BORROWINGS (name TEXT,phone INT, amount INT,desc TEXT, date_time DATETIME DEFAULT NOW())')              
            # table for billing details
            self.cursor.execute('CREATE TABLE SALEDITEM (item TEXT,quantity INT)')
            # table for user sales
            self.cursor.execute('CREATE TABLE COSTUMER (name TEXT,phone INT,amount INT)')
            self.conn.commit()
            print(f'{name} created')
        else:
            print('Canceled Store Creation!')
            
    def update_items(self,sign):
        item = input('Enter item: ')
        while True:
            quantity = input('Enter quantity: ')
            if quantity.isdigit():
                quantity = int(quantity)
                break
            else:
                print('Invalid quantity! Please enter again!')
                
        self.cursor.execute(f"SELECT itemname FROM ITEMS WHERE itemname = '{item}'")
        if self.cursor.fetchone():
            self.cursor.execute(f"UPDATE ITEMS SET quantity = quantity {sign}{quantity} WHERE itemname = '{item}'")
            print(f'{item} quantity updated')
        else:
            print('Item not found!')
        self.conn.commit()

    def remove_item(self):
        item = input('Enter item: ')
        self.cursor.execute(f"SELECT itemname FROM ITEMS WHERE itemname = '{item}'")
        if self.cursor.fetchone():
            print("Are you sure you want to remove {item}? (y/n)")
            choice = input()
            if choice.lower() == 'y':
                self.cursor.execute(f"DELETE FROM ITEMS WHERE itemname = '{item}'")
                print(f'{item} removed from store')
            else:
                print(f'{item} not removed')
        else:
            print('Item not found!')
        self.conn.commit()
        
    # Billing system
    def bill(self):
        name = input('Enter name: ')
        while True:
            phone = input('Enter phone: ')
            if phone.isdigit():
                phone = int(phone)
                break
            else:
                print('Invalid phone! Please enter again!')
        basket = []
        while True:
            item = input('Enter item: ')
            price = input('Enter price: ')
            quantity = input('Enter quantity: ')
            if price.isdigit() and quantity.isdigit():
                price = int(price)
                quantity = int(quantity)
                basket.append((item,price,quantity))
                print("Do you want to add more items? (y/n)")
                choice = input()
                if choice.lower() == 'y':
                    continue
                else:
                    break
            else:
                print('Invalid amount! Please enter details again!')

        print('Create Bill? (y/n)')
        choice = input()
        if choice.lower() == 'y':
            genrate(self.name,name,phone,basket)
            # adding bill details to database
            self.cursor.execute(f"INSERT INTO SALEDITEM (item,quantity) VALUES ('{item}',{quantity})")
            self.cursor.execute(f"INSERT INTO COSTUMER (name,phone,amount) VALUES ('{name}',{phone},{price*quantity})")
            # adjusting store items
            for item,price,quantity_saled in basket:
                self.cursor.execute(f"SELECT quantity FROM ITEMS WHERE itemname = '{item}'")
                quantity = self.cursor.fetchone()[0]
                self.cursor.execute(f"UPDATE ITEMS SET quantity = {quantity - quantity_saled} WHERE itemname = '{item}'")
        else:
            print('Canceled Billing!')

if __name__=='main':
    while True:
        print('1 - Load Previous Store\n2 - Create New Store')
        choice = input('Enter your choice: ')
        if choice == '1':
            Store().load_store()
        elif choice == '2':
            Store().create()
