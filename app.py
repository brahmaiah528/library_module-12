import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Library Management System",
    page_icon="📚",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>

.main{
    background:#f5f7fb;
}

div[data-testid="stMetric"]{
    background:white;
    padding:18px;
    border-radius:12px;
    box-shadow:0px 2px 10px rgba(0,0,0,0.1);
}

.stButton>button{
    width:100%;
    border-radius:10px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BOOK CLASSES (POLYMORPHISM)
# ---------------------------------------------------------
class Book:

    def __init__(self,title,author,copies):

        self.title=title
        self.author=author
        self.copies=copies

    def show_details(self):
        raise NotImplementedError


class Fiction(Book):

    def show_details(self):
        return f"📖 Fiction | {self.title} | {self.author} | Copies : {self.copies}"


class Science(Book):

    def show_details(self):
        return f"🔬 Science | {self.title} | {self.author} | Copies : {self.copies}"


class History(Book):

    def show_details(self):
        return f"📜 History | {self.title} | {self.author} | Copies : {self.copies}"

# ---------------------------------------------------------
# USER CLASS
# ---------------------------------------------------------
class User:

    def __init__(self,phone,password):

        self.phone=phone
        self.password=password

        self.borrowed_books=[]

    def take_book(self,book):

        if book.copies<=0:
            return False,"Book Not Available"

        book.copies-=1

        borrow_date=datetime.now()

        due_date=borrow_date+timedelta(days=14)

        self.borrowed_books.append({

            "Book":book.title,

            "Borrow Date":borrow_date.strftime("%d-%m-%Y"),

            "Due Date":due_date.strftime("%d-%m-%Y"),

            "Status":"Borrowed"

        })

        return True,"Book Issued Successfully"

    def return_book(self,book):

        for item in self.borrowed_books:

            if item["Book"]==book.title:

                book.copies+=1

                item["Status"]="Returned"

                item["Returned On"]=datetime.now().strftime("%d-%m-%Y")

                return True,"Book Returned Successfully"

        return False,"Book Not Borrowed"

    def active_books(self):

        return [x for x in self.borrowed_books if x["Status"]=="Borrowed"]

    def history(self):

        return self.borrowed_books

    def change_password(self,new_pass):

        self.password=new_pass

# ---------------------------------------------------------
# LIBRARY SYSTEM
# ---------------------------------------------------------
class LibrarySystem:

    def __init__(self):

        self.users={}

        self.users["admin"]=User("admin","admin123")

        self.books=[

            Fiction("Harry Potter","J.K Rowling",5),
            Fiction("1984","George Orwell",3),
            Fiction("The Hobbit","J.R.R Tolkien",4),
            Fiction("Moby Dick","Herman Melville",2),
            Fiction("The Great Gatsby","F Scott Fitzgerald",2),

            Science("Physics Fundamentals","Halliday",3),
            Science("Chemistry Basics","Zumdahl",3),
            Science("Biology 101","Campbell",2),
            Science("Astronomy Today","Chaisson",2),
            Science("Computer Science","Tanenbaum",4),

            History("History of India","Romila Thapar",3),
            History("World War II","Stephen Ambrose",3),
            History("French Revolution","Schama",2),
            History("Cold War","John Lewis Gaddis",2),
            History("Ancient Civilizations","Will Durant",2)

        ]

    # -----------------------------

    def register(self,phone,password):

        if phone in self.users:
            return "User Already Exists"

        self.users[phone]=User(phone,password)

        return "Registration Successful"

    # -----------------------------

    def login(self,phone,password):

        if phone in self.users:

            if self.users[phone].password==password:

                return self.users[phone]

        return None

    # -----------------------------

    def search(self,query):

        query=query.lower()

        result=[]

        for book in self.books:

            if query in book.title.lower() or query in book.author.lower():

                result.append(book)

        return result

    # -----------------------------

    def find_book(self,title):

        for book in self.books:

            if book.title.lower()==title.lower():

                return book

        return None

    # -----------------------------

    def add_book(self,title,author,copies,category):

        if category=="Fiction":
            self.books.append(Fiction(title,author,copies))

        elif category=="Science":
            self.books.append(Science(title,author,copies))

        elif category=="History":
            self.books.append(History(title,author,copies))

        return "Book Added Successfully"

    # -----------------------------

    def delete_book(self,title):

        book=self.find_book(title)

        if book:

            self.books.remove(book)

            return "Book Deleted Successfully"

        return "Book Not Found"

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "library" not in st.session_state:

    st.session_state.library=LibrarySystem()

if "user" not in st.session_state:

    st.session_state.user=None

library=st.session_state.library

# ---------------------------------------------------------
# LOGIN / REGISTER
# ---------------------------------------------------------

if st.session_state.user is None:

    st.title("📚 Smart Library Management System")

    login_tab,register_tab=st.tabs(["Login","Register"])

    with login_tab:

        phone=st.text_input("Phone")

        password=st.text_input("Password",type="password")

        if st.button("Login"):

            obj=library.login(phone,password)

            if obj:

                st.session_state.user=obj

                st.rerun()

            else:

                st.error("Invalid Credentials")

    with register_tab:

        phone=st.text_input("Phone",key="reg")

        password=st.text_input("Password",type="password",key="regpass")

        if st.button("Register"):

            st.success(library.register(phone,password))# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

else:

    user = st.session_state.user

    if user.phone == "admin":

        st.sidebar.title("👨‍💼 Admin Panel")

        menu = st.sidebar.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "📚 Inventory",
                "➕ Add Book",
                "❌ Delete Book",
                "👥 Users",
                "📊 Reports",
                "🔑 Change Password",
                "🚪 Logout"
            ]
        )

        # ---------------- DASHBOARD ----------------

        if menu == "🏠 Dashboard":

            st.title("📊 Library Dashboard")

            total_titles = len(library.books)
            total_copies = sum(book.copies for book in library.books)
            total_users = len(library.users)

            borrowed = 0

            for u in library.users.values():
                borrowed += len(u.active_books())

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("📚 Book Titles", total_titles)
            c2.metric("📦 Available Copies", total_copies)
            c3.metric("👥 Registered Users", total_users)
            c4.metric("📖 Borrowed Books", borrowed)

            st.divider()

            st.subheader("📚 Book Inventory")

            data = []

            for book in library.books:

                data.append({

                    "Title": book.title,
                    "Author": book.author,
                    "Category": book.__class__.__name__,
                    "Copies": book.copies

                })

            st.dataframe(pd.DataFrame(data), use_container_width=True)

        # ---------------- INVENTORY ----------------

        elif menu == "📚 Inventory":

            st.title("📚 Inventory")

            search = st.text_input("Search Book")

            books = library.search(search) if search else library.books

            data = []

            for b in books:

                data.append({

                    "Title": b.title,
                    "Author": b.author,
                    "Category": b.__class__.__name__,
                    "Copies": b.copies

                })

            st.dataframe(pd.DataFrame(data), use_container_width=True)

        # ---------------- ADD BOOK ----------------

        elif menu == "➕ Add Book":

            st.title("➕ Add Book")

            title = st.text_input("Book Title")

            author = st.text_input("Author")

            copies = st.number_input(
                "Copies",
                min_value=1,
                value=1
            )

            category = st.selectbox(

                "Category",

                [

                    "Fiction",
                    "Science",
                    "History"

                ]

            )

            if st.button("Add"):

                st.success(

                    library.add_book(

                        title,

                        author,

                        copies,

                        category

                    )

                )

        # ---------------- DELETE BOOK ----------------

        elif menu == "❌ Delete Book":

            st.title("Delete Book")

            title = st.text_input("Book Name")

            if st.button("Delete"):

                st.warning(

                    library.delete_book(title)

                )

        # ---------------- USERS ----------------

        elif menu == "👥 Users":

            st.title("👥 User Details")

            rows = []

            for phone, u in library.users.items():

                if phone == "admin":
                    continue

                if len(u.borrowed_books) == 0:

                    rows.append({

                        "User": phone,
                        "Book": "-",
                        "Borrow Date": "-",
                        "Due Date": "-",
                        "Status": "No Books"

                    })

                else:

                    for item in u.borrowed_books:

                        rows.append({

                            "User": phone,
                            "Book": item["Book"],
                            "Borrow Date": item["Borrow Date"],
                            "Due Date": item["Due Date"],
                            "Status": item["Status"]

                        })

            st.dataframe(

                pd.DataFrame(rows),

                use_container_width=True

            )

        # ---------------- REPORTS ----------------

        elif menu == "📊 Reports":

            st.title("Reports")

            chart = []

            for b in library.books:

                chart.append({

                    "Category": b.__class__.__name__,
                    "Copies": b.copies

                })

            df = pd.DataFrame(chart)

            col1, col2 = st.columns(2)

            with col1:

                fig = px.pie(

                    df,

                    names="Category",

                    values="Copies",

                    title="Books by Category"

                )

                st.plotly_chart(

                    fig,

                    use_container_width=True

                )

            with col2:

                fig2 = px.bar(

                    df.groupby(

                        "Category",

                        as_index=False

                    ).sum(),

                    x="Category",

                    y="Copies",

                    title="Available Copies"

                )

                st.plotly_chart(

                    fig2,

                    use_container_width=True

                )

        # ---------------- PASSWORD ----------------

        elif menu == "🔑 Change Password":

            st.title("Change Password")

            new_pass = st.text_input(

                "New Password",

                type="password"

            )

            if st.button("Update"):

                user.change_password(new_pass)

                st.success("Password Updated")

        # ---------------- LOGOUT ----------------

        elif menu == "🚪 Logout":

            st.session_state.user = None

            st.rerun()    # ==========================================================
    # USER DASHBOARD
    # ==========================================================

    else:

        st.sidebar.title(f"👤 {user.phone}")

        menu = st.sidebar.radio(
            "User Menu",
            [
                "🏠 Dashboard",
                "🔍 Search Books",
                "📥 Borrow Book",
                "📤 Return Book",
                "📚 My Borrowed Books",
                "🔑 Change Password",
                "🚪 Logout"
            ]
        )

        # ---------------- DASHBOARD ----------------

        if menu == "🏠 Dashboard":

            st.title("📚 User Dashboard")

            total_books = len(library.books)

            available = sum(book.copies for book in library.books)

            borrowed = len(user.active_books())

            history = len(user.borrowed_books)

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("📚 Titles", total_books)
            c2.metric("📦 Available", available)
            c3.metric("📖 Borrowed", borrowed)
            c4.metric("📜 History", history)

            st.divider()

            st.subheader("Recently Borrowed")

            if user.borrowed_books:

                st.dataframe(
                    pd.DataFrame(user.borrowed_books),
                    use_container_width=True
                )

            else:

                st.info("No books borrowed yet.")

        # ---------------- SEARCH ----------------

        elif menu == "🔍 Search Books":

            st.title("🔍 Search Books")

            query = st.text_input("Enter title or author")

            books = library.search(query) if query else library.books

            data = []

            for b in books:

                data.append({

                    "Title": b.title,
                    "Author": b.author,
                    "Category": b.__class__.__name__,
                    "Copies": b.copies

                })

            st.dataframe(pd.DataFrame(data), use_container_width=True)

        # ---------------- BORROW ----------------

        elif menu == "📥 Borrow Book":

            st.title("📥 Borrow Book")

            titles = [b.title for b in library.books]

            selected = st.selectbox(
                "Select Book",
                titles
            )

            if st.button("Borrow"):

                book = library.find_book(selected)

                ok, msg = user.take_book(book)

                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        # ---------------- RETURN ----------------

        elif menu == "📤 Return Book":

            st.title("📤 Return Book")

            active = [b["Book"] for b in user.active_books()]

            if active:

                selected = st.selectbox(
                    "Borrowed Book",
                    active
                )

                if st.button("Return"):

                    book = library.find_book(selected)

                    ok, msg = user.return_book(book)

                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

            else:

                st.info("No borrowed books.")

        # ---------------- HISTORY ----------------

        elif menu == "📚 My Borrowed Books":

            st.title("📚 Borrowing History")

            if user.borrowed_books:

                st.dataframe(

                    pd.DataFrame(user.borrowed_books),

                    use_container_width=True

                )

            else:

                st.info("No records found.")

        # ---------------- PASSWORD ----------------

        elif menu == "🔑 Change Password":

            st.title("Change Password")

            new_pass = st.text_input(
                "New Password",
                type="password"
            )

            if st.button("Update Password"):

                user.change_password(new_pass)

                st.success("Password Updated Successfully")

        # ---------------- LOGOUT ----------------

        elif menu == "🚪 Logout":

            st.session_state.user = None

            st.rerun()
