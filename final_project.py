# Michelle Li
# May 16, 2025
# This program uses Tkinter to set up a GUI that allows users to look up titles of books in the Project Gutenberg website.
# Users can enter either a book title in the local database or the url to the html e-book.
# If a url is entered, the database is updated with the book title and the 10 most frequenctly occurring words, along with their frequencies.
# If the data from the url is already present in the database, another entry will not be created for that title
# If a book title is entered, the local database is searched to see if information for that book title is present
# If a book title is entered and the local database does not have that information, a message that indicates so will appear

from urllib.request import urlopen
import re
import sqlite3
from tkinter import *

# This starts the main Tkinter window
window = Tk()
window.title("Book Database")

# This is the label for the Book Title text field
tk_title_label = Label(window, text="Enter book title: ").grid(row=1, column=0, sticky=W)


# This creates the text field to enter the title of the book
title_entry = Entry(window, width=50)
title_entry.grid(row=2, column=0, sticky=W)

'''
This is the button to search for the book title in the database.
If the table does not already exist, a table is created.
The database is searched for the matching title.
The title being searched for is printed to the terminal.
If the entry is already in the database, the entry will be printed to the Tkinter window.
The window will display the book title along with the 10 most frequently occurring words.
If the entry is not found, the Tkinter window will display "Book not found."
For any exceptions, the exception will be displayed in the Tkinter window.
'''
def title_click():
    # delete any output being displayed from previous searches
    output.delete("1.0", END)

    # connect to database
    con = sqlite3.connect('web.db')
    cur = con.cursor()

    # Fetches title from database and print title and words if title is in the database
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Books (
                title TEXT,
                words TEXT
            )
        """)

        cur.execute("SELECT * FROM Books WHERE title=?", (title_entry.get(),))
        print(f"Book title being searched for: {title_entry.get()}")
        tk_output = cur.fetchone()

        if tk_output:
            output.insert(END, tk_output)

        else:
            output.insert(END, "Book was not found.")

    except Exception as e:
        output.insert(END, e)
    else:
        con.close()
    
# This button looks for the book title when clicked. Please refer to the title_click function for details.
Button(window, text="SEARCH TITLE", width=12, command=title_click).grid(row=3, column=0, sticky=W)

# This is the label for the text field for the url of the book
tk_url_label = Label(window, text="Enter url: ").grid(row=1, column=5, sticky=W)

# This is a text field to enter the url of the book
url_entry = Entry(window, width=50)
url_entry.grid(row=2, column=5, sticky=W)

'''
When the button is clicked to search for url, this function gets called.
Any output from previous searches will be deleted so that the output of the current search can be easily seen.
This function uses a try and except block to see if the url is valid.
If the url is not valid, the Tkinter window will display "Not a valid URL".
If the url is valid, it will proceed to find the title of the book and convert it to plain text.
It will also find the 10 most frequently occurring words.
If the title is not already in the database, the title and words will be stored in the database.
This function will output the title of the book and the 10 most frequently occurring words in the Tkinter window.
This function also prints various statements to the terminal, indicating which steps of the function have been completed.
'''
def url_click():
    # Deletes any output being displayed from previous searches
    output.delete("1.0", END)

    try:
        # Gets text from URL and converts it to plain text
        url = url_entry.get()
        response = urlopen(url)
        html = response.read()
        plain_text = html.decode()

        # Get title
        match = re.search(r'Title: (.+)', plain_text)
        title = match.group(1).strip()
    
    except Exception as e:
        output.insert(END, "This is not a Project Gutenberg site.")

    else:
        print(title)

        # Gets most frequently occurring words
        word_lst = re.findall(r'\w+', plain_text)
        word_counts = {}
        for word in word_lst:
            lower_word = word.lower()
            if lower_word in word_counts:
                word_counts[lower_word] += 1
            else:
                word_counts[lower_word] = 1

        print("done with words")
        sorted_words = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)
        sorted_words = sorted_words[:10]

        # Connects to the database
        con = sqlite3.connect('web.db')
        cur = con.cursor()

        # Updates database if title is not already present
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Books (
                title TEXT,
                words TEXT
            )
        """)

        cur.execute("SELECT * FROM Books WHERE title=?", (title,))
        tk_output = cur.fetchone()
        print("book exists")

        if tk_output:
            print("output to display1")
            output.insert(END, tk_output)
        else:
            cur.execute("INSERT OR REPLACE INTO Books VALUES (?, ?)", (title, str(sorted_words)))
            con.commit()
            print("inserted")
            cur.execute("SELECT * FROM Books WHERE title=?", (title,))
            output.insert(END, cur.fetchone())
            print("fetched")
            con.close()

# This is the button to search the url. Please see the url_click function for details.
Button(window, text="SEARCH URL", width=10, command=url_click).grid(row=3, column=5, sticky=W)
        
# This is a text field to display the book title, along with the most frequently occurring words and their frequencies
output = Text(window, width=75, height=6, wrap=WORD)
output.grid(row=6, column=0, columnspan=2, sticky=W)

window.mainloop()