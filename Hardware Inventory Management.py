# Importing all necessary modules
import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# Connecting to Database
connector = sqlite3.connect('Inventory.db')
cursor = connector.cursor()

cursor.execute(
    'CREATE TABLE IF NOT EXISTS Inventory (ITEM_SOLD TEXT, QUANTITY TEXT PRIMARY KEY NOT NULL, ITEM_PRICE TEXT, CATEGORY TEXT, GROSS_SALES TEXT)'
)


# Functions
def calculate_gross_sales(quantity, item_price):
    try:
        return float(quantity) * float(item_price)
    except ValueError:
        return 0.0

def defining():
    Cid = sd.askstring('Enter the item Category', 'What is the category of the item?\t\t\t')

    if not Cid:
        mb.showerror('Category cant be null', 'it must have a value')
    else:
        return Cid


def display_records():
    global connector, cursor
    global tree

    tree.delete(*tree.get_children())

    curr = cursor.execute('SELECT * FROM Inventory')
    data = curr.fetchall()

    for records in data:
        tree.insert('', END, values=(records[0], records[1], records[2], records[3], records[4]))

def clear_fields():
    global item_sold, quantity, item_price, category, gross_sales

    item_sold.set('')
    for i in ['item_price', 'quantity', 'category', 'gross_sales']:
        exec(f"{i}.set('')")
        bk_id_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass


def clear_and_display():
    clear_fields()
    display_records()


def add_record():
    global connector
    global item_sold, quantity, item_price, category, gross_sales

    if category.get() == '':
        category.set(defining())

    surety = mb.askyesno('Are you sure?',
                         'Are you sure this is the data you want to enter?')

    if surety:
        gross_sales.set(calculate_gross_sales(quantity.get(), item_price.get()))
        try:
            cursor.execute(
                'INSERT INTO Inventory (ITEM_SOLD, QUANTITY, ITEM_PRICE, CATEGORY, GROSS_SALES) VALUES (?, ?, ?, ?, ?)',
                (item_sold.get(), quantity.get(), item_price.get(), category.get(), gross_sales.get()))
            connector.commit()

            clear_and_display()

            mb.showinfo('Record added', 'The new record was successfully added to your database')
        except sqlite3.IntegrityError:
            mb.showerror(
                'The item price you are trying to enter is already in the database, please alter that  record or check any discrepancies on your side')


def view_record():
    global item_sold, quantity, item_price, category, gross_sales
    global tree

    if not tree.focus():
        mb.showerror('Select a row!',
                     'To view a record, you must select it in the table. Please do so before continuing.')
        return

    current_item_selected = tree.focus()
    values_in_selected_item = tree.item(current_item_selected)
    selection = values_in_selected_item['values']

    item_sold.set(selection[3]);
    quantity.set(selection[0]);
    item_price.set(selection[1])
    category.set(selection[2])
    try:
        gross_sales.set(selection[4])
    except:
        gross_sales.set('')


def update_record():
    def update():
        global item_sold, quantity, item_price, category, gross_sales
        global connector, tree

        if item_sold.get() == '1':  # Compare with the string '1'
            gross_sales.set(defining())
        else:
            gross_sales.set('N/A')

        cursor.execute(
            'UPDATE Inventory SET ITEM_SOLD=?, QUANTITY=?, ITEM_PRICE=?, CATEGORY=?, GROSS_SALES=? WHERE QUANTITY=?',
            (item_sold.get(), quantity.get(), item_price.get(), category.get(), gross_sales.get(), quantity.get()))

        connector.commit()

        clear_and_display()

        edit.destroy()
        item_price.config(state='normal')
        clear.config(state='normal')


    view_record()

    item_price.config(state='disabled')
    clear.config(state='disabled')

    edit = Button(left_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
    edit.place(x=50, y=375)

def remove_record():
    if not tree.selection():
        mb.showerror('Error!', 'Please select an item from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]

    cursor.execute('DELETE FROM Inventory WHERE item_price=?', (selection[1],))
    connector.commit()

    tree.delete(current_item)

    mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')

    clear_and_display()


def delete_inventory():
    if mb.askyesno('Are you sure?',
                   'Are you sure you want to delete the entire inventory?\n\nThis command cannot be reversed'):
        tree.delete(*tree.get_children())

        cursor.execute('DELETE FROM Inventory')
        connector.commit()
    else:
        return


def change_availability():
    global gross_sales, tree, connector, quantity, item_sold

    if not tree.selection():
        mb.showerror('Error!', 'Please select a record from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    selected_item_sold = values['values'][0]
    selected_quantity = values["values"][1]

    if selected_item_sold == 'Sold':
        surety = mb.askyesno('Is sale confirmed?')
        if surety:
            cursor.execute('UPDATE Inventory SET ITEM_SOLD=?, QUANTITY=?, GROSS_SALES=? WHERE QUANTITY=?',
                           ('Available', quantity.get(), 'N/A', selected_quantity))
            connector.commit()
        else:
            mb.showinfo(
                'The item has been sold')
    else:
        cursor.execute('UPDATE Inventory SET ITEM_SOLD=?, QUANTITY=?, GROSS_SALES=? WHERE QUANTITY=?',
                       ('Available', quantity.get(), 'N/A', selected_quantity))
        connector.commit()

    clear_and_display()


# Variables
lf_bg = 'Green'  # Left Frame Background Color
rtf_bg = 'Green'  # Right Top Frame Background Color
rbf_bg = 'Blue'  # Right Bottom Frame Background Color
btn_hlb_bg = 'Black'  # Background color for Head Labels and Buttons

lbl_font = ('Georgia', 13)  # Font for all labels
entry_font = ('Times New Roman', 12)  # Font for all Entry widgets
btn_font = ('Gill Sans MT', 13)

# Initializing the main GUI window
root = Tk()
root.title('FAIR-DEAL HARDWARE INVENTORY MANAGEMENT SYSTEM')
root.geometry('1010x530')
root.resizable(0, 0)

Label(root, text='INVENTORY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg=btn_hlb_bg, fg='White').pack(
    side=TOP, fill=X)

# StringVars
item_sold = StringVar()
quantity = StringVar()
item_price = StringVar()
category = StringVar()
gross_sales = StringVar()

# Frames
left_frame = Frame(root, bg=lf_bg)
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

RB_frame = Frame(root)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame
Label(left_frame, text='Item sold', bg=lf_bg, font=lbl_font).place(x=98, y=25)
Entry(left_frame, width=25, font=entry_font, text=item_sold).place(x=45, y=55)

Label(left_frame, text='Quantity', bg=lf_bg, font=lbl_font).place(x=110, y=105)
bk_id_entry = Entry(left_frame, width=25, font=entry_font, text=quantity)
bk_id_entry.place(x=45, y=135)

Label(left_frame, text='Item price', bg=lf_bg, font=lbl_font).place(x=90, y=185)
Entry(left_frame, width=25, font=entry_font, text=item_price).place(x=45, y=215)

Label(left_frame, text='Category', bg=lf_bg, font=lbl_font).place(x=75, y=265)
dd = OptionMenu(left_frame, category, *['Carpentry', 'Construction', 'Metalwork', 'Plumbing', 'Electrical supplies', 'House_wares', 'General Hardware'])
dd.configure(font=entry_font, width=12)
dd.place(x=75, y=300)

submit = Button(left_frame, text='Add new record', font=btn_font, bg=btn_hlb_bg, width=20, command=add_record)
submit.place(x=50, y=375)

clear = Button(left_frame, text='Clear fields', font=btn_font, bg=btn_hlb_bg, width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame
Button(RT_frame, text='Delete  record', font=btn_font, bg=btn_hlb_bg, width=17, command=remove_record).place(x=8,
                                                                                                                 y=30)
Button(RT_frame, text='Delete full inventory', font=btn_font, bg=btn_hlb_bg, width=17, command=delete_inventory).place(
    x=178, y=30)
Button(RT_frame, text='Update Sale details', font=btn_font, bg=btn_hlb_bg, width=17,
       command=update_record).place(x=348, y=30)

# Right Bottom Frame
Label(RB_frame, text='HARDWARE INVENTORY', bg=rbf_bg, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=TOP, fill=X)

tree = ttk.Treeview(RB_frame, selectmode=BROWSE, columns=('Quantity', 'Item Price', 'Category', 'Item Sold', 'Gross Sales'))

XScrollbar = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
YScrollbar = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
XScrollbar.pack(side=BOTTOM, fill=X)
YScrollbar.pack(side=RIGHT, fill=Y)

tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

tree.heading('Item Sold', text='Item Sold', anchor=CENTER)
tree.heading('Quantity', text='Quantity', anchor=CENTER)
tree.heading('Item Price', text='Item Price', anchor=CENTER)
tree.heading('Category', text='Category', anchor=CENTER)
tree.heading('Gross Sales', text='Gross Sales', anchor=CENTER)

tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=225, stretch=NO)
tree.column('#2', width=70, stretch=NO)
tree.column('#3', width=150, stretch=NO)
tree.column('#4', width=105, stretch=NO)
tree.column('#5', width=132, stretch=NO)

tree.place(y=30, x=0, relheight=0.9, relwidth=1)

clear_and_display()

# Finalizing the window
root.update()
root.mainloop()
from tkinter import END
