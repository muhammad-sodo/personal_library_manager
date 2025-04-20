import streamlit as st
import json
import os
from collections import defaultdict

st.markdown("""
<style>
/* Main styling */
.stApp {
    background-color: #eaecc5;
    color: #333;
}

/* Header styling */
h1 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

h2, h3, h4 {
    color: #2c3e50;
}

/* Book card styling */
.book-card {
    background-color: white;
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.book-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.book-card h4 {
    color: #3498db;
    margin-top: 0;
}

/* Button styling */
.stButton>button {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    background-color: #2980b9;
    transform: translateY(-1px);
}

/* Form styling */
.stTextInput>div>div>input, 
.stNumberInput>div>div>input {
    border-radius: 8px;
    border: 1px solid #ddd;
}

/* Radio button styling */
.stRadio>div {
    flex-direction: row;
    gap: 1rem;
}

.stRadio>div>label {
    margin-bottom: 0;
}

/* Metric cards */
.stMetric {
    background-color: white;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Footer styling */
.footer {
    text-align: center;
    color: black
    font-size: 0.9rem;
    margin-top: 2rem;
}

/* Success/error messages */
.stAlert {
    border-radius: 8px;
}

/* Sidebar styling */
.css-1vq4p4l {
    padding: 1rem;
    background-color: #ecf0f1;
    border-radius: 0 10px 10px 0;
}

/* Responsive design */
@media (max-width: 768px) {
    .book-card {
        padding: 1rem;
    }
    
    .stRadio>div {
        flex-direction: column;
        gap: 0.5rem;
    }
}
</style>
        """, unsafe_allow_html=True)

# Library data structure
if 'library' not in st.session_state:
    st.session_state.library = []

# File name for saving/loading data
DATA_FILE = "library.json"

def add_book():
    """Add a new book to the library"""
    with st.form("add_book_form"):
        st.subheader("Add a New Book")
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", key="title").strip()
            author = st.text_input("Author", key="author").strip()
        with col2:
            year = st.number_input("Publication Year", min_value=0, max_value=2023, step=1, key="year")
            genre = st.text_input("Genre", key="genre").strip()
        
        read_status = st.radio("Have you read this book?", ("Yes", "No"), key="read_status")
        
        submitted = st.form_submit_button("Add Book")
        if submitted:
            if not title or not author:
                st.error("Please fill in all required fields")
                return
            
            book = {
                'title': title,
                'author': author,
                'year': year,
                'genre': genre,
                'read': read_status == "Yes"
            }
            
            st.session_state.library.append(book)
            save_library()
            st.success(f"Book '{title}' added successfully!")
            st.balloons()

def remove_book():
    """Remove a book from the library"""
    st.subheader("Remove a Book")
    
    if not st.session_state.library:
        st.warning("Your library is empty!")
        return
    
    search_term = st.text_input("Enter the title of the book to remove:", key="remove_search").strip()
    
    if search_term:
        found_books = [book for book in st.session_state.library 
                      if search_term.lower() in book['title'].lower()]
        
        if not found_books:
            st.error(f"No book with title '{search_term}' found in your library.")
            return
        
        if len(found_books) > 1:
            st.write(f"Multiple books found with '{search_term}':")
            for i, book in enumerate(found_books, 1):
                status = "✔ Read" if book['read'] else "❌ Unread"
                st.write(f"{i}. {book['title']} by {book['author']} ({book['year']}) - {book['genre']} - {status}")
            
            choice = st.number_input("Enter the number of the book to remove:", 
                                   min_value=1, max_value=len(found_books), step=1)
            
            if st.button("Remove Selected Book"):
                book_to_remove = found_books[choice-1]
                st.session_state.library.remove(book_to_remove)
                save_library()
                st.success(f"Book '{book_to_remove['title']}' removed successfully!")
        else:
            if st.button(f"Remove '{found_books[0]['title']}'"):
                st.session_state.library.remove(found_books[0])
                save_library()
                st.success(f"Book '{found_books[0]['title']}' removed successfully!")

def search_books():
    """Search for books by title or author"""
    st.subheader("Search for a Book")
    
    if not st.session_state.library:
        st.warning("Your library is empty!")
        return
    
    search_type = st.radio("Search by:", ["Title", "Author"], key="search_type")
    search_term = st.text_input(f"Enter {search_type.lower()} to search:", key="search_term").strip().lower()
    
    if search_term:
        if search_type == "Title":
            results = [book for book in st.session_state.library 
                      if search_term in book['title'].lower()]
        else:
            results = [book for book in st.session_state.library 
                      if search_term in book['author'].lower()]
        
        if not results:
            st.error("No matching books found.")
        else:
            st.success(f"Found {len(results)} matching book(s):")
            for i, book in enumerate(results, 1):
                status = "✔ Read" if book['read'] else "❌ Unread"
                st.markdown(f"""
                <div class="book-card">
                    <h4>{book['title']}</h4>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['year']} | <strong>Genre:</strong> {book['genre']}</p>
                    <p><strong>Status:</strong> {status}</p>
                </div>
                """, unsafe_allow_html=True)

def display_all_books():
    """Display all books in the library"""
    st.subheader("Your Library")
    
    if not st.session_state.library:
        st.warning("Your library is empty!")
        return
    
    st.write(f"Total books: {len(st.session_state.library)}")
    
    for i, book in enumerate(st.session_state.library, 1):
        status = "✔ Read" if book['read'] else "❌ Unread"
        st.markdown(f"""
        <div class="book-card">
            <h4>{i}. {book['title']}</h4>
            <p><strong>Author:</strong> {book['author']}</p>
            <p><strong>Year:</strong> {book['year']} | <strong>Genre:</strong> {book['genre']}</p>
            <p><strong>Status:</strong> {status}</p>
        </div>
        """, unsafe_allow_html=True)

def display_statistics():
    """Display library statistics"""
    st.subheader("Library Statistics")
    
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Books", total_books)
    with col2:
        if total_books > 0:
            percentage_read = (read_books / total_books) * 100
            st.metric("Percentage Read", f"{percentage_read:.1f}%")
        else:
            st.metric("Percentage Read", "0%")
    
    if total_books > 0:
        st.subheader("Books by Genre")
        genres = defaultdict(int)
        for book in st.session_state.library:
            genres[book['genre']] += 1
        
        for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
            st.write(f"📚 **{genre}**: {count} book{'s' if count != 1 else ''}")

def save_library():
    """Save the library data to a file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(st.session_state.library, f)
    except Exception as e:
        st.error(f"Error saving library: {e}")

def load_library():
    """Load the library data from a file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                st.session_state.library = json.load(f)
        except Exception as e:
            st.error(f"Error loading library: {e}")
            st.session_state.library = []

def main():
    """Main program function"""
    st.title("📚 Personal Library Manager")
    st.markdown("Manage your book collection with ease!")
    
    # Load library data
    load_library()
    
    # Sidebar navigation
    menu_options = {
        "Add Book": add_book,
        "Remove Book": remove_book,
        "Search Books": search_books,
        "View All Books": display_all_books,
        "Library Statistics": display_statistics
    }
    
    selected = st.sidebar.radio("Menu", list(menu_options.keys()))
    
    # Display selected page
    menu_options[selected]()
    
    # Footer
    st.markdown("---")
    st.markdown("<div class='footer'>Made by ❤️ Muhammad Adam Sodo</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()