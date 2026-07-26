import streamlit as st

# =========================================================
# MODULE 2: BOOK INVENTORY MANAGEMENT (Polymorphism)
# =========================================================
class Book:
    def __init__(self, title, author, copies):
        self.title = title
        self.author = author
        self.copies = copies

    def show_details(self):
        raise NotImplementedError("Subclasses must override this method")

class Fiction(Book):
    def show_details(self):
        return f"📖 [Fiction] {self.title} by {self.author} | {self.copies} left"

class Science(Book):
    def show_details(self):
        return f"🔬 [Science] {self.title} by {self.author} | {self.copies} left"

class History(Book):
    def show_details(self):
        return f"📜 [History] {self.title} by {self.author} | {self.copies} left"

# =========================================================
# MODULE 1 & 3: USER, AUTH & TRANSACTION MANAGEMENT
# =========================================================
class User:
    def __init__(self, phone, password):
        self.phone = phone
        self.password = password
        self.borrowed_books = []

    def take_book(self, book):
        if book.copies > 0:
            book.copies -= 1
            self.borrowed_books.append(book.title)
            return True, f"Successfully issued '{book.title}'"
        return False, "No copies available!"

    def return_book(self, book):
        if book.title in self.borrowed_books:
            book.copies += 1
            self.borrowed_books.remove(book.title)
            return True, f"Successfully returned '{book.title}'"
        return False, "You haven't borrowed this book!"

# =========================================================
# MODULE 4: REPORT & SYSTEM ADMINISTRATION
# =========================================================
class LibrarySystem:
    def __init__(self):
        self.users = {"admin": User("admin", "admin123")}
        self.books = [
            Fiction("Harry Potter", "J.K. Rowling", 5),
            Science("Brief History of Time", "Stephen Hawking", 2),
            History("Sapiens", "Yuval Noah Harari", 3),
            Fiction("1984", "George Orwell", 4)
        ]

    def authenticate(self, phone, password):
        if phone in self.users and self.users[phone].password == password:
            return self.users[phone]
        return None

    def register(self, phone, password):
        if phone in self.users: return "User already exists!"
        self.users[phone] = User(phone, password)
        return "Registration successful!"

    def search(self, query):
        q = query.lower()
        return [b for b in self.books if q in b.title.lower() or q in b.author.lower()]

# ---------------------------------------------------------
# STREAMLIT INTERFACE
# ---------------------------------------------------------
st.set_page_config(page_title="Library System", page_icon="📚")

if "lib" not in st.session_state:
    st.session_state.lib = LibrarySystem()
if "user" not in st.session_state:
    st.session_state.user = None

lib = st.session_state.lib

if not st.session_state.user:
    st.title("📚 Smart Library Login")
    mode = st.radio("Choose Mode", ["Login", "Register"])
    u_phone = st.text_input("Phone")
    u_pass = st.text_input("Password", type="password")

    if st.button("Submit"):
        if mode == "Login":
            user_obj = lib.authenticate(u_phone, u_pass)
            if user_obj:
                st.session_state.user = user_obj
                st.rerun()
            else:
                st.error("Invalid Credentials")
        else:
            st.info(lib.register(u_phone, u_pass))
else:
    user = st.session_state.user
    st.sidebar.title(f"👤 {user.phone}")

    if user.phone == "admin":
        choice = st.sidebar.selectbox("Admin Panel", ["System Report", "Inventory Management", "Logout"])
        if choice == "System Report":
            st.header("📊 Module 4: System Administration & Reports")
            col1, col2 = st.columns(2)
            col1.metric("Total Books", sum(b.copies for b in lib.books))
            col2.metric("Active Users", len(lib.users))
        elif choice == "Inventory Management":
            st.header("📦 Module 2: Inventory Management")
            for b in lib.books: st.write(b.show_details())
    else:
        choice = st.sidebar.selectbox("User Menu", ["Browse & Search", "My Transactions", "Logout"])
        if choice == "Browse & Search":
            st.header("🔍 Module 2 & 3: Search & Transactions")
            q = st.text_input("Search for a book...")
            for b in lib.search(q):
                if st.button(f"Borrow {b.title}"):
                    s, m = user.take_book(b)
                    st.info(m)

    if choice == "Logout":
        st.session_state.user = None
        st.rerun()
