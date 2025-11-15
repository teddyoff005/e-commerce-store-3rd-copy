import time
import getpass
import os
import random



class Product:
    def __init__(self, id, name, price, stock, restock_timer=30):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.restock_time = None
        self.restock_timer = restock_timer

class User:
    def __init__(self, username, password, order_history=None):
        self.username = username
        self.password = password
        self.order_history = order_history if order_history else []

class Store:
    def __init__(self):
        self.products = [
            Product(1, "Water Bottle", 15.00, 20),
            Product(2, "Healthy Snacks", 5.99, 30),
            Product(3, "Toothbrush Set", 8.50, 15),
            Product(4, "Notebook and Pen", 10.00, 25),
            Product(5, "First Aid Kit", 25.00, 10)
        ]
        self.users = []
        self.current_user = None
        self.cart = {}
        self.last_random_restock = time.time()

    def randomly_deplete_stock(self):
        if time.time() - self.last_random_restock >= 120:
            in_stock_products = [p for p in self.products if p.stock > 0]
            if in_stock_products:
                product_to_deplete = random.choice(in_stock_products)
                product_to_deplete.stock = 0
                product_to_deplete.restock_time = time.time()
                self.last_random_restock = time.time()

    def get_product_by_id(self, pid):
        return next((p for p in self.products if p.id == pid), None)

    def restock_products(self):
        for p in self.products:
            if p.stock == 0 and p.restock_time:
                elapsed = time.time() - p.restock_time
                if elapsed >= p.restock_timer:
                    p.stock = random.randint(5, 20)
                    p.restock_time = None
                    print(f"\nRestocked {p.name}!")
                    time.sleep(1)

    def sign_in(self):
        clear_screen()
        print("--- SIGN IN ---")
        username = input("Username: ")
        password = input("Password: ")

        user = next((u for u in self.users if u.username == username), None)
        if user:
            print(f"Stored password: {user.password}")
            print(f"Entered password: {password}")
            if user.password == password:
                self.current_user = user
                print(f"\nWelcome back, {user.username}!")
            else:
                print("\nInvalid credentials.")
        else:
            print("\nInvalid credentials.")
        time.sleep(1.5)

    def sign_up(self):
        clear_screen()
        print("--- SIGN UP ---")
        username = input("Choose a username: ")
        if any(u.username == username for u in self.users):
            print("\nUsername already exists.")
            time.sleep(1.5)
            return
        
        password = input("Choose a password: ")
        print(f"Password entered: {password}")
        self.users.append(User(username, password))
        print("\nAccount created successfully! Please sign in.")
        time.sleep(1.5)

    def logout(self):
        self.current_user = None
        self.cart = {}
        print("\nLogged out successfully.")
        time.sleep(1)

    def view_products(self):
        while True:
            clear_screen()
            print("--- PRODUCT CATALOG ---")
            print(f"{'ID':<5} {'Name':<25} {'Price':<10} {'Stock'}")
            print("-" * 50)
            for p in self.products:
                if p.stock == 0 and p.restock_time:
                    elapsed = time.time() - p.restock_time
                    remaining = p.restock_timer - elapsed
                    if remaining > 0:
                        stock_display = f"Restocks in {int(remaining)}s"
                    else:
                        stock_display = "Restocking..."
                else:
                    stock_display = p.stock
                print(f"#{p.id:<4} {p.name:<25} ${p.price:<9.2f} {stock_display}")
            print("-" * 50)
            
            print("\n[A] Add to Cart | [B] Back to Menu")
            choice = input("Select option: ").upper()

            if choice == 'A':
                try:
                    pid = int(input("Enter Product ID to add: "))
                    qty = int(input("Enter Quantity: "))
                    self.add_to_cart(pid, qty)
                except ValueError:
                    print("Invalid input. Please enter numbers only.")
                    time.sleep(1)
            elif choice == 'B':
                break

    def add_to_cart(self, product_id, quantity):
        product = self.get_product_by_id(product_id)
        if not product:
            print("\nProduct not found.")
        elif quantity <= 0:
             print("\nPlease enter a valid quantity.")
        elif quantity > product.stock:
            print(f"\nSorry, only {product.stock} left in stock.")
        else:
            current_qty = self.cart.get(product_id, 0)
            if current_qty + quantity > product.stock:
                 print(f"\nYou already have {current_qty} in cart. Cannot add {quantity} more (Stock: {product.stock}).")
            else:
                self.cart[product_id] = current_qty + quantity
                print(f"\nAdded {quantity} x {product.name} to cart.")
        time.sleep(1.5)

    def view_cart(self):
        while True:
            clear_screen()
            print("--- YOUR CART ---")
            if not self.cart:
                print("\nYour cart is empty.")
                print("\n[B] Back")
                input("Press Enter to return...")
                return

            total = 0
            print(f"{'Name':<25} {'Qty':<5} {'Subtotal'}")
            print("-" * 45)
            for pid, qty in self.cart.items():
                product = self.get_product_by_id(pid)
                subtotal = product.price * qty
                total += subtotal
                print(f"{product.name:<25} x{qty:<4} ${subtotal:.2f}")
            print("-" * 45)
            print(f"{'TOTAL:':>31} ${total:.2f}")

            print("\n[C] Checkout | [R] Clear Cart | [B] Back")
            choice = input("Select option: ").upper()

            if choice == 'C':
                self.checkout(total)
                return
            elif choice == 'R':
                self.cart = {}
                print("Cart cleared.")
                time.sleep(1)
                return
            elif choice == 'B':
                return

    def checkout(self, total_amount):
        if not self.current_user:
            print("\nPlease sign in to checkout.")
            time.sleep(1.5)
            return

        print("\n--- CHECKOUT ---")
        confirm = input(f"Confirm purchase of ${total_amount:.2f}? (Y/N): ").upper()
        if confirm == 'Y':
            print("\nProcessing payment...")
            time.sleep(2)
            
            for pid, qty in self.cart.items():
                product = self.get_product_by_id(pid)
                product.stock -= qty
                if product.stock == 0:
                    product.restock_time = time.time()
            
            order_details = {
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total": total_amount,
                "items": self.cart.copy()
            }
            self.current_user.order_history.append(order_details)
            
            self.cart = {}
            print("\nSUCCESS! Thank you for your purchase.")
            input("Press Enter to continue...")
        else:
            print("\nCheckout cancelled.")
            time.sleep(1)

    def view_profile(self):
        clear_screen()
        if not self.current_user:
             print("Not logged in.")
             return
        
        print(f"--- PROFILE: {self.current_user.username} ---")
        print(f"Total Orders: {len(self.current_user.order_history)}")
        print("\nRecent Order History:")
        for i, order in enumerate(reversed(self.current_user.order_history[-5:]), 1):
             print(f"{i}. {order['date']} | Total: ${order['total']:.2f}")
             for pid, qty in order['items'].items():
                 product = self.get_product_by_id(pid)
                 print(f"    - {product.name} (x{qty})")
        
        input("\nPress Enter to return...")

    def run(self):
        while True:
            self.restock_products()
            self.randomly_deplete_stock()
            clear_screen()

            print("--- ALERTS ---")
            restocking_products = [p for p in self.products if p.stock == 0 and p.restock_time]
            if not restocking_products:
                print("No products are currently restocking.")
            else:
                for p in restocking_products:
                    elapsed = time.time() - p.restock_time
                    remaining = p.restock_timer - elapsed
                    if remaining > 0:
                        print(f"{p.name} will be restocked in {int(remaining)}s")
            print("-" * 20)
            
            print("=== PYTHON TERMINAL STORE ===")
            if self.current_user:
                print(f"User: {self.current_user.username}")
                cart_count = sum(self.cart.values())
                print(f"Cart: {cart_count} items")
            else:
                print("Status: Guest")
            
            print("\n--- MAIN MENU ---")
            print("1. Browse Products")
            print("2. View Cart")
            if self.current_user:
                print("3. My Profile & Orders")
                print("4. Logout")
            else:
                print("3. Sign In")
                print("4. Sign Up")
            print("Q. Quit")
            
            choice = input("\nSelect an option: ").upper()

            if choice == '1':
                self.view_products()
            elif choice == '2':
                self.view_cart()
            elif choice == '3':
                if self.current_user: self.view_profile()
                else: self.sign_in()
            elif choice == '4':
                if self.current_user: self.logout() 
                else: self.sign_up()
            elif choice == 'Q':
                print("\nThank you for visiting! Goodbye.")
                break
            else:
                print("\nInvalid choice.")
                time.sleep(0.5)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    os.system('mode con: cols=60 lines=30') 
    store = Store()
    store.run()
