# imports
from re import S
import sqlite3 # for store data in database
import os
from unicodedata import name # for path related operations
from bill import genrate # for bill generation

class Store:
    def __init__(self):
        pass

    def load_store(self):
        """
        checks the available stores and loads the store
        """
        # Getting available stores
        available_stores = [store for store in os.listdir('stores') if store.endswith('.db')]
        
        if available_stores:
            # map store in dict with numbers
            store_dict = {i+1:store for i, store in enumerate(available_stores)}
            # Asking for Store Number
            print('\nAvailable stores:')
            # showing available stores with numbers
            for i, store in store_dict.items():
                print(f'{i} - Open {store.split(".")[0]}')
            
            # get store number with handling exception
            while True:
                store_number = input('Enter store number: ')
                
                if store_number.isdigit():
                    
                    if int(store_number) in store_dict.keys():
                        break
                    
                    else:
                        print('Wrong store number! Please Specify again!\n')
                
                else:
                    print("Wrong store number! Please Specify as an Integer.\n")
        
        else:
            print('No stores found!')
            exit()

        # Loading Store
        self.name = store_dict[int(store_number)].split('.')[0]
        print(f'\n***************************{self.name} On Service***************************\n')
        self.connection = sqlite3.connect(f'stores/{store_dict[int(store_number)]}')
        self.cursor = self.connection.cursor()

    def create_store(self):
        """
        creates a new store
        """
        while True:
            name = input('Enter store name: ')
            
            if os.path.exists(f'stores/{name}.db'):
                print('Store already exists!')
            
            else:
                break
        
        print("Do you want to create a new store? (y/n)")
        choice = input()
        
        if choice.lower() == 'y':
            self.name = name
            self.connection = sqlite3.connect(f"stores/{name}.db")
            self.cursor = self.connection.cursor()
            # Creating table
            # table for adding store items
            self.cursor.execute('CREATE TABLE ITEMS (itemname TEXT, quantity INT, PRIMARY KEY (itemname))')
            # Table for adding BORROWINGS details
            self.cursor.execute('CREATE TABLE BORROWINGS (name TEXT,phone INT, amount INT,desc TEXT, date_time DATETIME DEFAULT CURRENT_TIMESTAMP)')              
            # table for billing details
            self.cursor.execute('CREATE TABLE SALEDITEM (item TEXT,quantity INT)')
            # table for user sales
            self.cursor.execute('CREATE TABLE COSTUMER (name TEXT,phone INT,amount INT)')
            self.connection.commit()
            print(f'{name} created')
        
        else:
            print('Canceled Store Creation!')
            exit()
    
    def update_items(self,sign="+"):
        """
        updates the items in the store
        """
        self.show_items()
        item = input('Enter item: ').lower()
        
        while True:
            # for catching unexpected input
            quantity = input('Enter quantity: ')
            
            try:
                quantity = int(quantity)
                break
            
            except:
                print('Invalid quantity! Please enter again!')
        
        # checking if item exists in the store or not
        self.cursor.execute(f"SELECT itemname FROM ITEMS WHERE itemname = '{item}'")
        # if already exists then update the quantity
        if self.cursor.fetchone():
            self.cursor.execute(f"UPDATE ITEMS SET quantity = quantity + {sign}{quantity} WHERE itemname = '{item}'")
            self.show_items()
            print(f'{item} quantity updated')
        # if not exists then add the item
        else:
            self.cursor.execute(f"INSERT INTO ITEMS (itemname,quantity) VALUES ('{item}',{quantity})")
            self.show_items()
            print(f'{item} added to store')
        
        self.connection.commit()

    def remove_item(self):
        """
        removes the item from the store
        """
        item = input('Enter item: ').lower()
        self.cursor.execute(f"SELECT itemname FROM ITEMS WHERE itemname = '{item}'")
        # if item exists then remove it
        if self.cursor.fetchone():
            print("Are you sure you want to remove {item}? (y/n)")
            choice = input()
            # if yes then remove the item
            if choice.lower() == 'y':
                self.cursor.execute(f"DELETE FROM ITEMS WHERE itemname = '{item}'")
                self.show_items()
                print(f'{item} removed from store')
            # if anything else then left it
            else:
                print(f'{item} not removed')
        # if item doesn't exist then print not found
        else:
            print('Item not found!')
        
        self.connection.commit()
    
    def show_items(self):
        '''
        Shows the items in the store
        '''
        print("\n"+"-"*50)
        
        self.cursor.execute('SELECT * FROM ITEMS')
        items = self.cursor.fetchall()
        
        print("ITEMS               QUANTITY")
        
        for item,quan in items:
            print(f'{item}'+' '*(23-len(item))+f'{quan}')
        
        print("\n"+"-"*50+"\n")

    # Billing system
    def bill(self):
        '''
        gather and organize the bill details into a list
        and pass to the genrate() function from bill.py
        update the database with User sales and Item sales
        '''
        name = input('Enter name: ')
        # catching unexpected input
        while True:
            phone = input('Enter phone: ')
            if phone.isdigit():
                phone = int(phone)
                break
            else:
                print('Invalid phone! Please enter again!')
        # initializing the bill list
        basket = []
        # adding items to the bill list
        while True:
            item = input('Enter item: ')
            price = input('Enter price: ')
            quantity = input('Enter quantity: ')
            # catching unexpected input
            if price.isdigit() and quantity.isdigit():
                price = int(price)
                quantity = int(quantity)
                
                basket.append((item,price,quantity))
                # checking if user wants to add more items
                print("Do you want to add more items? (y/n)")
                choice = input()
                # if yes then continue
                if choice.lower() == 'y':
                    continue
                # if no then break
                else:
                    break
            
            else:
                print('Invalid amount! Please enter details again!')
        
        # confirming the bill
        print('Create Bill? (y/n)')
        choice = input()
        # if yes then generate the bill
        if choice.lower() == 'y':
            genrate(self.name,name,phone,basket)
            
            # adding bill details to database
            for item,price,quantity in basket:
                # if item already exists, update quantity else add new item
                self.cursor.execute(f"SELECT * FROM SALEDITEM WHERE item = '{item.lower()}'")
                if self.cursor.fetchone():
                    self.cursor.execute(f"UPDATE SALEDITEM SET quantity = quantity + {quantity} WHERE item = '{item.lower()}'")
                else:
                    self.cursor.execute(f"INSERT INTO SALEDITEM (item,quantity) VALUES ('{item.lower()}',{quantity})")
                
                # if customer already exists, update amount else add new customer
                self.cursor.execute(f"SELECT * FROM COSTUMER WHERE name = '{name.lower()}'")
                if self.cursor.fetchone():
                    self.cursor.execute(f"UPDATE COSTUMER SET amount = amount + {price*quantity} WHERE name = '{name.lower()}' AND phone = {phone}")
                else:
                    self.cursor.execute(f"INSERT INTO COSTUMER (name,phone,amount) VALUES ('{name.lower()}',{phone},{price*quantity})")
            
                # adjusting store items
                self.cursor.execute(f"SELECT quantity FROM ITEMS WHERE itemname = '{item.lower()}'")
                if self.cursor.fetchone():
                    self.cursor.execute(f"UPDATE ITEMS SET quantity = quantity - {quantity} WHERE itemname = '{item.lower()}'")
                
        
        # if anything else then left it
        else:
            print('Canceled Billing!')

        self.connection.commit()

    # stats system
    def stats(self):
        """
        shows the stats of the store
        Most sold item,
        Most Buying customer,
        """
        print("\n"+"-"*50)
        print(f"\n-----------------------{self.name} STATS-----------------------\n")
        # getting most sold item and showing it
        print(f"\n-----------------------MOST BUYED ITEMS-----------------------\n")
        self.cursor.execute('SELECT item,quantity FROM SALEDITEM ORDER BY quantity DESC')                   
        items = self.cursor.fetchall()
        print("ITEM                    QUANTITY")
        for item,quantity in items:
            print(f'{item}'+' '*(25-len(item))+f'{quantity}')
        print("\n"+"-"*50+"\n")
        # getting most buying customer and showing it
        print(f"\n-----------------------TOP BUYERS-----------------------\n")
        self.cursor.execute('SELECT name,amount,phone FROM COSTUMER ORDER BY amount DESC')
        costumers = self.cursor.fetchall()
        print("NAME                AMOUNT                    PHONE")
        for name,amount,phone in costumers:
            print(f'{name}'+' '*(20-len(name))+f'{amount}'+' '*(25-len(str(amount)))+f'{phone}')
        print("\n"+"-"*50+"\n")
        # getting highest borrower and showing it
        print(f"\n-----------------------TOP BORROWERS-----------------------\n")
        # getting the highest borrower from BORROWINGS table and grouping them by name and phone
        self.cursor.execute('SELECT name,phone,SUM(amount) FROM BORROWINGS GROUP BY name,phone ORDER BY SUM(amount) DESC')
        borrowers = self.cursor.fetchall()
        print("NAME                AMOUNT                    PHONE")
        for name,phone,amount in borrowers:
            print(f'{name}'+' '*(20-len(name))+f'{amount}'+' '*(25-len(str(amount)))+f'{phone}')
        print("\n"+"-"*50+"\n")


    # borrowing system
    def borrowings(self,type="+"):
        '''
        add or remove borrowing
        '''
        name = input('Enter name: ')
        
        # catching unexpected input
        while True:
            phone = input('Enter phone: ')
            amount = input('Enter amount: ')
            
            if phone.isdigit() and amount.isdigit():
                phone = int(phone)
                amount = int(amount)
                break
            else:
                print('Invalid phone! Please enter again!')
        
        desc = input('Enter description: ')

        # adding/removing borrowing to the database
        self.cursor.execute(f"INSERT INTO BORROWINGS (name,phone,amount,desc) VALUES ('{name.lower()}',{phone},{type}{amount},'{desc.lower()}')")

        print(f"{name}'s borrowing has been updated {type}{amount}!")
        self.connection.commit()

    # show all borrowings
    def show_all_borrowings(self):
        """
        shows all borrowings of the customers
        """
        print("\n"+"-"*50+"\n")
        self.cursor.execute('SELECT name,phone,SUM(amount) FROM BORROWINGS GROUP BY name,phone ORDER BY SUM(amount) DESC')
        borrowers = self.cursor.fetchall()
        print("NAME                AMOUNT                    PHONE")
        for name,phone,amount in borrowers:
            print(f'{name}'+' '*(20-len(name))+f'{amount}'+' '*(25-len(str(amount)))+f'{phone}')
        print("\n"+"-"*50+"\n")
    
    # show borrowing of a customer
    def show_person_borrowings(self):
        """
        shows the borrowings of a customer
        """
        name = input('Enter name: ')
        # catching unexpected input
        while True:
            phone = input('Enter phone: ')
            
            if phone.isdigit():
                phone = int(phone)
                break
            else:
                print('Invalid phone no! Please enter again!')

        self.cursor.execute(f"SELECT name,phone,amount,desc FROM BORROWINGS WHERE name = '{name.lower()}' AND phone = {phone}")
        borrowers = self.cursor.fetchall()
        print("\n"+"-"*50+"\n")
        print("NAME                AMOUNT                    PHONE                    DESCRIPTION")
        for name,phone,amount,desc in borrowers:
            print(f'{name}'+' '*(20-len(name))+f'{amount}'+' '*(25-len(str(amount)))+f'{phone}'+' '*(25-len(str(phone)))+f'{desc}')
        print("\n"+"-"*50+"\n")

        if borrowers == []:
            print(f"No borrowings found! with name: {name}")
        else:
            # get the total amount of the customer
            self.cursor.execute(f"SELECT SUM(amount) FROM BORROWINGS WHERE name = '{name.lower()}' AND phone = {phone}")
            total = self.cursor.fetchone()[0]
            print(f"Total amount:               {total}")
        
    # get notifaction of the store
    def get_notifaction(self):
        """
        shows the notifications of the store
        """
        self.cursor.execute('SELECT itemname,quantity FROM ITEMS')
        items = self.cursor.fetchall()
        print("\n"+"-"*50+"\n")
        # get how many items left
        for item,quantity in items:
            if quantity <= 10:
                print(f"\nOnly {quantity} {item} left!\n")
        
        print("\n"+"-"*50+"\n")


    def exit(self):
        # close the database connection and exits
        self.connection.close()
        exit()

if __name__=='__main__':
    print('\n***************************Welcome to the Store Management System***************************\n')
    while True:
        while True:
            store=Store()
            print('1 - Load Previous Store\n2 - Create New Store')
            choice = input('Enter your choice: ')
            if choice == '1':
                store.load_store()
                break
            elif choice == '2':
                store.create_store()
                break
            else:
                print('\n Invalid choice! Please enter again!\n')
        # getting notifaction of the store
        store.get_notifaction()
        option_dict = {1:"Update/Create Items",2:"Remove Item From Store",3:"Show Items",4:"Billing",5:"Add Borrowings",6:"Remove Borrowings",7:"Show All Borrowings",8:"Borrowing history of a person",9:"Stats",10:"Exit"}
        
        while True:
            print("\n")
            for key,value in option_dict.items():
                print(f'{key} - {value}')
            print("\n")
            option = input('Enter your choice: ')
            if option.isdigit():
                if int(option) in option_dict.keys():
                    if option == '1':
                        print('1 - Add\n2 - Subtract\n3 - Create')
                        choice = input('Enter your choice: ')
                        if choice == '1':
                            print("\nHow much item you want to add?\n")
                            store.update_items('+')
                        elif choice == '2':
                            print("\nHow much item you want to subtract?\n")
                            store.update_items('-')
                        elif choice == '3':
                            store.update_items()
                    elif option == '2':
                        store.remove_item()
                    elif option == '3':
                        store.show_items()
                    elif option == '4':
                        store.bill()
                    elif option == '5':
                        store.borrowings("+")
                    elif option == '6':
                        store.borrowings("-")
                    elif option == '7':
                        store.show_all_borrowings()
                    elif option == '8':
                        store.show_person_borrowings()
                    elif option == '9':
                        store.stats()
                    elif option == '10':
                        store.exit()
            else:
                print('Invalid option! Please enter a valid option!')