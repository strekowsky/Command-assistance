from tkinter import *  
from tkinter import ttk 
from tkinter import messagebox  
from tkcalendar import * 
from PIL import ImageTk, Image
import sqlite3
import datetime
from tkinter import filedialog
from tkinter import Scrollbar
from tkinter.font import Font
from tkinter import font
from datetime import date


root = Tk()
root.title("Command assistance")
root.iconbitmap("icon.ico")
root.geometry("1080x500")
author = Label(root, text="Autor: Adam Strękowski (wersja testowa)")
author.pack(side="bottom", anchor="e")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")
# set theme to azure light - must be included in program folder
root.tk.call("source", "azure.tcl")
root.tk.call("set_theme", "light")


# set default avatar as "av.jpg" (included in folder) with 125x160 resolution.
av = ImageTk.PhotoImage(Image.open(
    "av.jpg").resize((125, 160), Image.ANTIALIAS))


def default_avatar():
    av = ImageTk.PhotoImage(Image.open(
        "av.jpg").resize((125, 160), Image.ANTIALIAS))
    label_photo.config(text="", image=av)
    label_photo.image = av
    photoentry.insert(0, "")


# function used in search entry, searching in rank, fname, lname, pesel, place of birth, position, adnotations, subdivisions
search_id_list = []
def search(event):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM persons")
    search_id_list.clear()
    key = entry_search.get().lower()
    results = c.fetchall()
    id = 0
    if key.strip() == "":
        show_info(event)
        list_update(person_listbox)
    else:
        for person in results:
            if key in person[0].lower() or \
                    key in person[1].lower() or \
                    key in person[2].lower() or \
                    key in person[3].lower() or \
                    key in person[4].lower() or \
                    key in person[5].lower() or \
                    key in person[8].lower() or \
                    key in person[10].lower() or \
                    key in person[12].lower():
                search_id_list.append(
                    (person[0], person[1], person[2], person[13]))

        person_listbox.delete(0, END)
        for person in search_id_list:
            fullname = f"{person[0]} {person[1]} {person[2]}, id: {person[3]}"
            person_listbox.insert(END, fullname)

    conn.commit()
    conn.close()

# set label image and entry control from which DB gets person avatar adress
def add_avatar():
    adres = add_frame.filename = filedialog.askopenfilename(
        initialdir="", title="Wybierz zdjęcie", filetypes=(("plik jpg", "*.jpg"), ("wszystkie pliki", "*.*")))
    av = ImageTk.PhotoImage(Image.open(
        adres).resize((125, 160), Image.ANTIALIAS))
    label_photo.config(text="", image=av)
    label_photo.image = av
    photoentry.delete(0, END)
    photoentry.insert(0, adres.strip())


# Create or connect DB
conn = sqlite3.connect('persons_list.db')
c = conn.cursor()

# Delete hashtag from the next three rows to create table person, sudivisions, tasks - only with first run

#c.execute("""CREATE TABLE persons (rank text, first_name text, last_name text, pesel text, date_of_birth text, place_of_birth text, father_name text, date_of_join text, position text, gender text, adnotations text, photo text, subdivision text, id integer)""")
#c.execute("CREATE TABLE subdivisions (subdivision text)")
#c.execute("CREATE TABLE tasks (title text, responsible text, entryDate text, endDate text, taskId integer, describe text, tag text)")
conn.commit()
conn.close()

# Function returns object's age in year/month/day format. Uses "birthday" which is "datetime" type
def age(birthday):
    today = datetime.datetime.now()
    age = today - birthday
    years = age.days // 365
    days = age.days % 365
    months = days // 30
    exdays = days % 30
    return years, exdays, months

# Check DB and update given list
def list_update(name_listbox):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM persons")
    results = c.fetchall()
    name_listbox.delete(0, END)
    for item in results:
        if item[0] == "osoba cywilna":
            name_listbox.insert(END, f"p. {item[1]} {item[2]}")
        else:
            name_listbox.insert(
                END, f"{item[0]} {item[1]} {item[2]}, id: {item[13]}")
    conn.commit()
    conn.close()


# Check DB and update subdivison lists
subdivision_list = []
def subdivisions_update():
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM subdivisions")
    results = c.fetchall()
    subdivision_list.clear()

    listbox_subdivision.delete(0, END)
    for item in results:
        listbox_subdivision.insert(END, item[0])
        subdivision_list.append(item[0])
    conn.commit()
    conn.close()

# Add function. Rank, fname, lname is necessary to add, other entries are optional.
def submit():
    confirm = 1
    ok_no = "ok"  #if 'no', fuction return
    empty_entries = ""
    if combo_rank.get() == "":
        messagebox.showerror("Błąd", "Pole 'stopień' nie może być puste.")
        confirm = 0  
        ok_no = "no"  
    elif entry_firstName.get() == "":
        messagebox.showerror("Błąd", "Pole 'imię' nie może być puste.")
        confirm = 0
        ok_no = "no"  
    elif entry_lastName.get() == "":
        messagebox.showerror("Błąd", "Pole 'nazwisko' nie może być puste.")
        confirm = 0
        ok_no = "no"  
    if entry_pesel.get() == "":
        empty_entries += "-Pesel\n"
    if entry_dateOfBirth.get() == "":
        empty_entries += "-Data urodzenia\n"
    if entry_placeOfBirth.get() == "":
        empty_entries += "-Miejsce urodzenia\n"
    if entry_nameOfFather.get() == "":
        empty_entries += "-Imię ojca\n"
    if entry_dateOfJoin.get() == "":
        empty_entries += "-Data rozpoczęcia służby\n"
    if entry_position.get() == "":
        empty_entries += "-Stanowisko\n"
    if empty_entries != "" and ok_no == "ok":
        confirm = messagebox.askyesno(
            "Błąd", f"Następujące pola nie zostały wypełnione:\n\n {empty_entries}\n Czy chcesz kontynuować?")
    #Submit only if user confirm to add without filled entries, if accept then set confirm to 1
    if confirm == 1:
        conn = sqlite3.connect('persons_list.db')
        c = conn.cursor()
        c.execute("SELECT *, oid FROM persons")
        results = c.fetchall()
        c.execute("INSERT INTO persons VALUES (:rank, :first_name, :last_name, :pesel, :dateofbirth, :placeofbirth, :nameoffather, :dateofjoin, :position, :gender, :adnotations, :photo, :subdivision, :id)",
                  {
                      'rank': combo_rank.get(),
                      'first_name': entry_firstName.get(),
                      'last_name': entry_lastName.get(),
                      'pesel': entry_pesel.get(),
                      'dateofbirth': entry_dateOfBirth.get(),
                      'placeofbirth': entry_placeOfBirth.get(),
                      'nameoffather': entry_nameOfFather.get(),
                      'dateofjoin': entry_dateOfJoin.get(),
                      'position': entry_position.get(),
                      'gender': gender.get(),
                      'adnotations': entry_adnotations.get("1.0", END),
                      'photo': photoentry.get(),
                      'subdivision': set_subdivision.get(),
                      'id': len(results)


                  })

        # Clear entries
        combo_rank.set("")
        entry_firstName.delete(0, END)
        entry_lastName.delete(0, END)
        entry_pesel.delete(0, END)
        entry_dateOfBirth.delete(0, END)
        entry_placeOfBirth.delete(0, END)
        entry_nameOfFather.delete(0, END)
        entry_dateOfJoin.delete(0, END)
        entry_position.delete(0, END)
        entry_adnotations.delete("1.0", END)  #text type
        photoentry.delete(0, END)
        set_subdivision.set("")

        # Update lists and clear avatar entry
        default_avatar()
        conn.commit()
        conn.close()
        list_update(person_listbox)
        list_update(edit_listbox)

# Hide calendar after choice
def hide(event):
    entry_dateOfBirth.delete(0, END)
    entry_dateOfBirth.insert(
        0, cal_dateOfBirth.selection_get().strftime("%d.%m.%Y"))
    cal_dateOfBirth.grab_release()
    cal_dateOfBirth.grid_forget()

# Show calendar after event
def show(event):
    cal_dateOfBirth.lift()
    cal_dateOfBirth.grid(row=5, column=2, rowspan=12, padx=70)
    cal_dateOfBirth.grab_set()


# Show calendar for date of join
def showjoin(event):
    cal_dateOfJoin.lift()
    cal_dateOfJoin.grid(row=5, column=2, rowspan=12, padx=70)
    cal_dateOfJoin.grab_set()

# Hide calendar for date of join
def hidejoin(event):
    entry_dateOfJoin.delete(0, END)
    entry_dateOfJoin.insert(
        0, cal_dateOfJoin.selection_get().strftime("%d.%m.%Y"))
    cal_dateOfJoin.grab_release()
    cal_dateOfJoin.grid_forget()


# Person list frame--------------------------------------------------------------------------------------------
person_frame = Frame(notebook)
person_listbox = Listbox(person_frame, width=30, activestyle="none")
person_listbox.grid(row=0, column=0, rowspan=8, sticky="nsew")
# Labels
label_search = Label(person_frame, text="Szukaj")
label_search.grid(row=8, column=0)
# Entries
entry_search = Entry(person_frame, text="", width=30)
entry_search.grid(row=9, column=0, sticky="w")

# Search function, first bind for key press, second for release. It's necessary for proper functioning. Without release bind
# it's working with one-click delay.
entry_search.bind("<Key>", search)
entry_search.bind("<KeyRelease>", search)
# Scrollbar
person_scroll = ttk.Scrollbar(person_frame, orient="vertical")
person_listbox.config(yscrollcommand=person_scroll.set)
person_scroll.config(command=person_listbox.yview)
person_scroll.grid(row=0, column=0, rowspan=8, sticky="nse")
# List update with first program run
list_update(person_listbox)
# dodanie obiektu/konteneru jako zakladka do obiektu notebook
notebook.add(person_frame, text="Lista osób")

# ADD PERSON FRAME-----------------------------------------------------------------------------------------------------
add_frame = Frame(notebook)  # nowa ramka przynalezna do notebook
notebook.add(add_frame, text="Dodaj osobę")  # dodanie zakładki z tekstem

# Labels
label_rank = Label(add_frame, text="Stopień")
label_firstName = Label(add_frame, text="Imię")
label_lastName = Label(add_frame, text="Nazwisko")
label_pesel = Label(add_frame, text="Pesel")
label_dateOfBirth = Label(add_frame, text="Data urodzenia")
label_placeOfBirth = Label(add_frame, text="Miejsce urodzenia")
label_nameOfFather = Label(add_frame, text="Imię ojca")
label_dateOfJoin = Label(add_frame, text="Data rozpoczęcia służby")
label_position = Label(add_frame, text="Stanowisko")
label_photo = Label(add_frame, text="Avatar", image=av)
label_adnotations = Label(add_frame, text="Pozostałe informacje")
label_set_subdivision = Label(add_frame, text="Pododdział:")
# Gender select with default "male"
label_gender = Label(add_frame, text="Płeć")
gender = StringVar()
gender.set("M")

# subdivision combobox
set_subdivision = ttk.Combobox(
    add_frame, state="readonly", values=subdivision_list)
set_subdivision.grid(row=10, column=1, sticky="w", columnspan=2, pady=5)

# add button
button_submit = ttk.Button(add_frame, text="Dodaj osobę",
                           command=submit, width=40, style='Accent.TButton')
button_submit.grid(row=11, column=0, sticky="w", columnspan=2, pady=5)

# Add photo button
add_photo = ttk.Button(add_frame, text="Dodaj zdjęcie",
                       width=17, command=add_avatar)
add_photo.grid(column=2, row=5)

# Ranks list
ranks = ["osoba cywilna", "szer.", "st. szer.",
         "st. szer. spec.", "kpr.", "st. kpr.", "plut.", "sierż.", "st. sierż.",
         "mł. chor.", "chor.", "st. chor.", "st. chor. sztab.", "ppor.",
         "por.", "kpt.", "mjr", "ppłk", "płk"]

# rank combobox
combo_rank = ttk.Combobox(add_frame, values=ranks, state="readonly", width=19)
combo_rank.grid(row=0, column=1, sticky="w")

# Entry fields
entry_firstName = Entry(add_frame, text="")
entry_lastName = Entry(add_frame, text="")
entry_pesel = Entry(add_frame, text="")
entry_dateOfBirth = Entry(add_frame, text="")
entry_placeOfBirth = Entry(add_frame, text="")
entry_nameOfFather = Entry(add_frame, text="")
entry_dateOfJoin = Entry(add_frame, text="")
entry_position = Entry(add_frame, text="")
entry_adnotations = Text(add_frame, width=40, height=7)
photoentry = Entry(add_frame, text="av.jpg")

# calendar create
cal_dateOfBirth = Calendar(add_frame, selectmode="day",
                           year=2022, month=1, day=1, locale="pl")
cal_dateOfJoin = Calendar(add_frame, selectmode="day",
                          year=2022, month=1, day=1, locale="pl")


# Gender radiobuttons
radio_male = ttk.Radiobutton(add_frame, text="M", variable=gender, value="M")
radio_female = ttk.Radiobutton(add_frame, text="K", variable=gender, value="K")
radio_male.grid(row=9, column=1, sticky="w")
radio_female.grid(row=9, column=1, sticky="e")

# Label fields grid
label_rank.grid(row=0, column=0, sticky="w")
label_firstName.grid(row=1, column=0, sticky="w", pady=10)
label_lastName.grid(row=2, column=0, sticky="w", pady=5)
label_pesel.grid(row=3, column=0, sticky="w", pady=5)
label_dateOfBirth.grid(row=4, column=0, sticky="w", pady=5)
label_placeOfBirth.grid(row=5, column=0, sticky="w", pady=5)
label_nameOfFather.grid(row=6, column=0, sticky="w", pady=5)
label_dateOfJoin.grid(row=7, column=0, sticky="w", pady=5)
label_position.grid(row=8, column=0, sticky="w", pady=5)
label_gender.grid(row=9, column=0, sticky="w", pady=5)
label_photo.grid(row=0, column=2, sticky="w", padx=130, rowspan=5)
label_set_subdivision.grid(row=10, column=0, sticky="w", columnspan=2, pady=5)
label_adnotations.grid(row=6, column=2, sticky="w", padx=30)

# Entry fields grid
entry_firstName.grid(row=1, column=1, sticky="w")
entry_lastName.grid(row=2, column=1, sticky="w")
entry_pesel.grid(row=3, column=1, sticky="w")
entry_dateOfBirth.grid(row=4, column=1, sticky="w")
entry_placeOfBirth.grid(row=5, column=1, sticky="w")
entry_nameOfFather.grid(row=6, column=1, sticky="w")
entry_dateOfJoin.grid(row=7, column=1, sticky="w")
entry_position.grid(row=8, column=1, sticky="w")
entry_adnotations.grid(row=7, column=2, sticky="w", padx=30, rowspan=4)

# Open calendar after click on entry field, hide calendar after date choice
entry_dateOfBirth.bind("<Button-1>", show)
cal_dateOfBirth.bind("<<CalendarSelected>>", hide)

# Open calendar for date of join after click on entry field, hide calendar after date choice
entry_dateOfJoin.bind("<Button-1>", showjoin)
cal_dateOfJoin.bind("<<CalendarSelected>>", hidejoin)


person_frame.columnconfigure(1, weight=1, minsize=200)


label_pesel1 = Label(person_frame, text=f"Pesel: ")
label_dateOfBirth1 = Label(person_frame, text=f"Data urodzenia: ")
label_placeOfBirth1 = Label(person_frame, text=f"Miejsce urodzenia: ")
label_nameOfFather1 = Label(person_frame, text=f"Imię ojca: ")
label_dateofjoin1 = Label(person_frame, text=f"Służba od: ")
label_position1 = Label(person_frame, text=f"Stanowisko: ")
label_gender1 = Label(person_frame, text=f"Płeć: ")
label_adnotations1 = Label(person_frame, text=f"Informacje: ")
label_adnotations2 = Text(person_frame, width=40, height=10)
label_av = Label(person_frame, image=av)
label_rank_fname_lname1 = Label(person_frame, text="b.d.")
label_subdivision_personframe = Label(person_frame, text="sdf")
label_age_serve = Label(person_frame, text="")

label_pesel1.grid(row=1, column=1, sticky="w", padx=15)
label_dateOfBirth1.grid(row=2, column=1, sticky="w", padx=15)
label_placeOfBirth1.grid(row=3, column=1, sticky="w", padx=15)
label_nameOfFather1.grid(row=4, column=1, sticky="w", padx=15)
label_dateofjoin1.grid(row=5, column=1, sticky="w", padx=15)
label_position1.grid(row=6, column=1, sticky="w", padx=15)
label_gender1.grid(row=7, column=1, sticky="w", padx=15)
label_adnotations1.grid(row=8, column=1, sticky="w", padx=15)
label_adnotations2.grid(row=9, column=1, sticky="nsew", padx=15, rowspan=7)
label_av.grid(row=0, column=3, rowspan=7, padx=50, sticky="e")
label_rank_fname_lname1.grid(row=7, column=3, sticky="e", padx=55)
label_subdivision_personframe.grid(row=8, column=3, sticky="e", padx=55)
label_age_serve.grid(row=9, column=3, sticky="e", padx=55)

# Adnotations scrollbar
adnotations_scroll = ttk.Scrollbar(person_frame, orient="vertical")
label_adnotations2.config(yscrollcommand=adnotations_scroll.set)
adnotations_scroll.config(command=label_adnotations2.yview)
adnotations_scroll.grid(row=9, column=1, sticky="nse", padx=15, rowspan=7)

# Function to show info about selected person. Get ID from person list, connect to DB, check their ID in DB (results[final_index][4]),
# if correct then show info


def show_info(event):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM persons")
    results = c.fetchall()
    try:
        index = person_listbox.get(person_listbox.curselection())
        index_split = index.split(":")
        final_index = int(index_split[1].strip())
    except:
        return

    if results[final_index][4] != "":
        wiek = results[final_index][4].split(".")
        one = int(wiek[2])
        two = int(wiek[1])
        three = int(wiek[0])
        birthday = datetime.datetime(one, two, three)
        final_age = age(birthday)
    else:
        final_age = " "

    if results[final_index][7] != "":
        wiek = results[final_index][7].split(".")
        serve_one = int(wiek[2])
        serve_two = int(wiek[1])
        serve_three = int(wiek[0])
        servetime = datetime.datetime(serve_one, serve_two, serve_three)
        final_servetime = age(servetime)
    else:
        final_servetime = " "

    def print_serve_time(final_servetime):
        if final_servetime[0] == 1:
            return "rok"
        elif final_servetime[0] == 2 or final_servetime[0] == 3 or final_servetime[0] == 4:
            return "lata"
        else:
            return "lat"

    if len(results[final_index][11]) > 0:
        location = results[final_index][11]
        try:
            newimage = ImageTk.PhotoImage(Image.open(
                location).resize((125, 160), Image.ANTIALIAS))
        except:
            newimage = ImageTk.PhotoImage(Image.open(
                "av.jpg").resize((125, 160), Image.ANTIALIAS))

        label_av.config(image=newimage)
        label_av.image = newimage
    else:
        newimage = ImageTk.PhotoImage(Image.open(
            "av.jpg").resize((125, 160), Image.ANTIALIAS))
        label_av.config(image=newimage)
        label_av.image = newimage

    if len(results[final_index][0]) > 0:
        if results[final_index][0] == "osoba cywilna":
            label_rank_fname_lname1.config(
                text=f"{results[final_index][1]} {results[final_index][2]}")
        else:
            label_rank_fname_lname1.config(
                text=f"{results[final_index][0]} {results[final_index][1]} {results[final_index][2]}")

    if len(results[final_index][3]) > 0:
        label_pesel1.config(text=f"Pesel: {results[final_index][3]}")

    else:
        label_pesel1.config(text=f"Pesel: b.d.")

    if len(results[final_index][4]) > 0:
        label_dateOfBirth1.config(
            text=f"Data urodzenia: {results[final_index][4]}")
    else:
        label_dateOfBirth1.config(text=f"Data urodzenia: b.d.")

    if len(results[final_index][4]) > 0 and len(results[final_index][7]) > 0:
        label_age_serve.config(
            text=f"{final_age[0]} l. / Służy od {final_servetime[0]} l.\n({final_servetime[0]} l. {final_servetime[2]} m. {final_servetime[1]}d.)")

    if len(results[final_index][4]) > 0 and len(results[final_index][7]) < 1:
        label_age_serve.config(text=f"{final_age[0]} l. / b.d.")
    if len(results[final_index][4]) < 1 and len(results[final_index][7]) > 0:
        label_age_serve.config(
            text=f"b.d. / Służy od {final_servetime[0]} l.\n({final_servetime[0]} l. {final_servetime[2]} m. {final_servetime[1]}d.)")

    if len(results[final_index][5]) > 0:
        label_placeOfBirth1.config(
            text=f"Miejsce urodzenia: {results[final_index][5]}")
    else:
        label_placeOfBirth1.config(text=f"Miejsce urodzenia: b.d.")

    if len(results[final_index][6]) > 0:
        label_nameOfFather1.config(
            text=f"Imię ojca: {results[final_index][6]}")
    else:
        label_nameOfFather1.config(text=f"Imię ojca: b.d.")

    if len(results[final_index][7]) > 0:
        label_dateofjoin1.config(text=f"Służba od: {results[final_index][7]}")
    else:
        label_dateofjoin1.config(text=f"Służba od: b.d.")

    if len(results[final_index][8]) > 0:
        label_position1.config(text=f"Stanowisko:  {results[final_index][8]}")
    else:
        label_position1.config(text=f"Stanowisko:  b.d.")

    if len(results[final_index][9]) > 0:
        label_gender1.config(text=f"Płeć: {results[final_index][9]}")
    else:
        label_gender1.config(text=f"Płeć: b.d.")

    if len(results[final_index][12]) > 0:
        label_subdivision_personframe.config(
            text=f"Pododdział: {results[final_index][12]}")
    else:
        label_subdivision_personframe.config(text=f"Pododdział: b.d.")

    label_adnotations2.config(state=NORMAL)
    label_adnotations2.delete(1.0, END)
    if len(results[final_index][10]) > 0:
        label_adnotations2.insert(1.0, results[final_index][10])
    else:
        label_adnotations1.insert(1.0, "Informacje: b.d.")

    label_adnotations2.config(state=DISABLED)
    conn.commit()
    conn.close()


person_listbox.bind("<<ListboxSelect>>", show_info)


def edit():
    entry_pesel1 = Entry(person_frame, text=f"Pesel: ")
    entry_pesel1.grid(row=1, column=1, sticky="w", padx=15)

    entry_dateOfBirth1 = Entry(person_frame, text=f"Data urodzenia: ")
    entry_dateOfBirth1.grid(row=2, column=1, sticky="w", padx=15)

    entry_placeOfBirth1 = Entry(person_frame, text=f"Miejsce urodzenia: ")
    entry_placeOfBirth1.grid(row=3, column=1, sticky="w", padx=15)

    entry_nameOfFather1 = Entry(person_frame, text=f"Imię ojca: ")
    entry_nameOfFather1.grid(row=4, column=1, sticky="w", padx=15)

    entry_dateofjoin1 = Entry(person_frame, text=f"Służba od: ")
    entry_dateofjoin1.grid(row=5, column=1, sticky="w", padx=15)

    entry_position1 = Entry(person_frame, text=f"Stanowisko: ")
    entry_position1.grid(row=6, column=1, sticky="w", padx=15)

    entry_gender1 = Entry(person_frame, text=f"Płeć: ")
    entry_gender1.grid(row=7, column=1, sticky="w", padx=15)

    entry_adnotations1 = Entry(person_frame, text=f"Informacje: ")
    entry_adnotations1.grid(row=8, column=1, sticky="w", padx=15)

    entry_adnotations2 = Entry(person_frame, text=f"")
    entry_adnotations2.grid(row=9, column=1, sticky="w", padx=15, rowspan=7)

    entry_av = Entry(person_frame, image=av)

    entry_av.grid(row=0, column=3, rowspan=7, padx=50, sticky="e")


# EDIT PERSON FRAME ------------------------------------------------------------------------------------------------------
edit_frame = Frame(notebook)
notebook.add(edit_frame, text="Edytuj osobę")
# Labels
label_rank_edit = Label(edit_frame, text="Stopień")
label_firstName_edit = Label(edit_frame, text="Imię")
label_lastName_edit = Label(edit_frame, text="Nazwisko")
label_pesel_edit = Label(edit_frame, text="Pesel")
label_dateOfBirth_edit = Label(edit_frame, text="Data urodzenia")
label_placeOfBirth_edit = Label(edit_frame, text="Miejsce urodzenia")
label_nameOfFather_edit = Label(edit_frame, text="Imię ojca")
label_dateOfJoin_edit = Label(edit_frame, text="Data rozpoczęcia służby")
label_position_edit = Label(edit_frame, text="Stanowisko")
label_photo_edit = Label(edit_frame, text="Avatar", image=av)
label_adnotations = Label(edit_frame, text="Pozostałe informacje")
label_set_subdivision_edit = Label(edit_frame, text="Pododdział:")

# Gender select
label_gender_edit = Label(edit_frame, text="Płeć")
gender_edit = StringVar()
gender_edit.set("M")

# Rank combobox
combo_rank_edit = ttk.Combobox(
    edit_frame, values=ranks, state="readonly", width=19)  # combobox do wyboru stopnia
combo_rank_edit.grid(row=0, column=1, sticky="w")

# Entry fields
entry_firstName_edit = Entry(edit_frame, text="")
entry_lastName_edit = Entry(edit_frame, text="")
entry_pesel_edit = Entry(edit_frame, text="")
entry_dateOfBirth_edit = Entry(edit_frame, text="")
entry_placeOfBirth_edit = Entry(edit_frame, text="")
entry_nameOfFather_edit = Entry(edit_frame, text="")
entry_dateOfJoin_edit = Entry(edit_frame, text="")
entry_position_edit = Entry(edit_frame, text="")
entry_adnotations_edit = Text(edit_frame, width=40, height=7)
photoentry_edit = Entry(edit_frame, text="av.jpg")

# Create calendar
cal_dateOfBirth_edit = Calendar(
    edit_frame, selectmode="day", year=2022, month=1, day=1, locale="pl")
cal_dateOfJoin_edit = Calendar(
    edit_frame, selectmode="day", year=2022, month=1, day=1, locale="pl")

# Gender radiobuttons
radio_male_edit = ttk.Radiobutton(
    edit_frame, text="M", variable=gender_edit, value="M")
radio_female_edit = ttk.Radiobutton(
    edit_frame, text="K", variable=gender_edit, value="K")
radio_male_edit.grid(row=9, column=1, sticky="w")
radio_female_edit.grid(row=9, column=1, sticky="e")

# Label fields grid
label_rank_edit.grid(row=0, column=0, sticky="w")
label_firstName_edit.grid(row=1, column=0, sticky="w", pady=10)
label_lastName_edit.grid(row=2, column=0, sticky="w", pady=5)
label_pesel_edit.grid(row=3, column=0, sticky="w", pady=5)
label_dateOfBirth_edit.grid(row=4, column=0, sticky="w", pady=5)
label_placeOfBirth_edit.grid(row=5, column=0, sticky="w", pady=5)
label_nameOfFather_edit.grid(row=6, column=0, sticky="w", pady=5)
label_dateOfJoin_edit.grid(row=7, column=0, sticky="w", pady=5)
label_position_edit.grid(row=8, column=0, sticky="w", pady=5)
label_gender_edit.grid(row=9, column=0, sticky="w", pady=5)
label_photo_edit.grid(row=0, column=2, sticky="w", padx=130, rowspan=5)
label_adnotations.grid(row=6, column=2, sticky="w", padx=30)
label_set_subdivision_edit.grid(
    row=10, column=0, sticky="w", columnspan=2, pady=5)

# Entry fields grid
entry_firstName_edit.grid(row=1, column=1, sticky="w")
entry_lastName_edit.grid(row=2, column=1, sticky="w")
entry_pesel_edit.grid(row=3, column=1, sticky="w")
entry_dateOfBirth_edit.grid(row=4, column=1, sticky="w")
entry_placeOfBirth_edit.grid(row=5, column=1, sticky="w")
entry_nameOfFather_edit.grid(row=6, column=1, sticky="w")
entry_dateOfJoin_edit.grid(row=7, column=1, sticky="w")
entry_position_edit.grid(row=8, column=1, sticky="w")
entry_adnotations_edit.grid(row=7, column=2, sticky="w", padx=30, rowspan=4)

entry_oid = Entry(edit_frame, text="")
# Delete button in edit frame
button_delete = ttk.Button(edit_frame, text="Usuń osobę")
button_delete.grid(row=5, column=3, sticky="s", pady=15, rowspan=2)

# Set subdivision in edit frame
set_subdivision_edit = ttk.Combobox(
    edit_frame, state="readonly", values=subdivision_list)
set_subdivision_edit.grid(row=10, column=1, sticky="w", columnspan=2, pady=5)

# Update person info from entry fields in edit frame


def update(rank, first_name, last_name, pesel, date_of_birth, place_of_birth, father_name, date_of_join, position, gender, adnotations, photo, subdivision, oid):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("UPDATE persons SET rank = ?, first_name = ?, last_name = ?, pesel = ?, date_of_birth = ?, place_of_birth = ?, father_name = ?, date_of_join = ?, position = ?, gender = ?, adnotations = ?, photo = ?, subdivision = ? WHERE oid = ?""",
              (rank, first_name, last_name, pesel, date_of_birth, place_of_birth, father_name, date_of_join, position, gender, adnotations, photo, subdivision, oid))
    conn.commit()
    conn.close()
    list_update(edit_listbox)
    list_update(person_listbox)


button_submit_edit = ttk.Button(
    edit_frame, text="Zapisz zmiany", width=40, style='Accent.TButton')
button_submit_edit.config(command=lambda: update(combo_rank_edit.get(), entry_firstName_edit.get(), entry_lastName_edit.get(), entry_pesel_edit.get(), entry_dateOfBirth_edit.get(
), entry_placeOfBirth_edit.get(), entry_nameOfFather_edit.get(), entry_dateOfJoin_edit.get(), entry_position_edit.get(), gender_edit.get(), entry_adnotations_edit.get(1.0, END), photoentry_edit.get(), set_subdivision_edit.get(), entry_oid.get()))
button_submit_edit.grid(row=11, column=0, sticky="w", columnspan=2, pady=5)


def add_avatar_edit():
    adres = add_frame.filename = filedialog.askopenfilename(
        initialdir="", title="Wybierz zdjęcie", filetypes=(("plik jpg", "*.jpg"), ("wszystkie pliki", "*.*")))
    av = ImageTk.PhotoImage(Image.open(
        adres).resize((125, 160), Image.ANTIALIAS))
    label_photo_edit.config(text="", image=av)
    label_photo_edit.image = av
    photoentry_edit.delete(0, END)
    photoentry_edit.insert(0, adres.strip())


add_photo_edit = ttk.Button(
    edit_frame, text="Edytuj zdjęcie", width=17, command=add_avatar_edit)
add_photo_edit.grid(column=2, row=5)

edit_listbox = Listbox(edit_frame, width=25, activestyle="none")
edit_listbox.grid(row=0, column=3, rowspan=14, sticky="n")

# Update edit_listbox with program run
list_update(edit_listbox)

# Show info about current selection in edit person listbox


def show_info_edit(event):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM persons")
    results = c.fetchall()
    index = int(edit_listbox.curselection()[0])
    entry_oid.delete(0, END)
    entry_oid.insert(0, index + 1)

# Check selected person info about rank to show in rank combobox
    rank_id = 0
    id = 0
    for rank in ranks:
        if rank == results[index][0]:
            rank_id = id
        id += 1
    combo_rank_edit.current(rank_id)

    entry_firstName_edit.delete(0, END)
    entry_firstName_edit.insert(0, results[index][1])

    entry_lastName_edit.delete(0, END)
    entry_lastName_edit.insert(0, results[index][2])

    entry_pesel_edit.delete(0, END)
    entry_pesel_edit.insert(0, results[index][3])

    entry_dateOfBirth_edit.delete(0, END)
    entry_dateOfBirth_edit.insert(0, results[index][4])

    entry_placeOfBirth_edit.delete(0, END)
    entry_placeOfBirth_edit.insert(0, results[index][5])

    entry_nameOfFather_edit.delete(0, END)
    entry_nameOfFather_edit.insert(0, results[index][6])

    entry_dateOfJoin_edit.delete(0, END)
    entry_dateOfJoin_edit.insert(0, results[index][7])

    entry_position_edit.delete(0, END)
    entry_position_edit.insert(0, results[index][8])

    gender_edit.set(results[index][9])

    entry_adnotations_edit.delete(1.0, END)
    entry_adnotations_edit.insert(1.0, results[index][10])

# Check selected person info about subdivision to show in subdivision combobox
    stopien_id = 0
    id1 = 0
    for subdivision in subdivision_list:
        if subdivision == results[index][12]:
            stopien_id = id1
        id1 += 1
    set_subdivision_edit.delete(0, END)  # clear
    set_subdivision_edit.current(stopien_id)  # set subdivision

    newimage = ImageTk.PhotoImage(Image.open(
        "av.jpg").resize((125, 160), Image.ANTIALIAS))
    label_photo_edit.config(image=newimage)
    label_photo_edit.image = newimage

    if len(results[index][11]) > 0:
        location = results[index][11]
        newimage = ImageTk.PhotoImage(Image.open(
            location).resize((125, 160), Image.ANTIALIAS))

        label_photo_edit.config(image="")
        label_photo_edit.config(image=newimage)
        label_photo_edit.image = newimage

        photoentry_edit.delete(0, END)
        photoentry_edit.insert(0, location)
    else:
        newimage = ImageTk.PhotoImage(Image.open(
            "av.jpg").resize((125, 160), Image.ANTIALIAS))
        label_photo_edit.config(image=newimage)
        label_photo_edit.image = newimage

        photoentry_edit.delete(0, END)
        photoentry_edit.insert(0, "av.jpg")

    conn.commit()
    conn.close()
    button_delete.config(command=lambda: delete(index+1))


edit_listbox.bind("<<ListboxSelect>>", show_info_edit)


def delete(oid):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("DELETE FROM persons WHERE oid = ?", (oid,))
    conn.commit()
    conn.close()

    # Clear fields after delete
    entry_firstName_edit.delete(0, END)
    entry_lastName_edit.delete(0, END)
    entry_pesel_edit.delete(0, END)
    entry_dateOfBirth_edit.delete(0, END)
    entry_placeOfBirth_edit.delete(0, END)
    entry_nameOfFather_edit.delete(0, END)
    entry_dateOfJoin_edit.delete(0, END)
    entry_position_edit.delete(0, END)
    gender_edit.set("M")
    entry_adnotations_edit.delete(1.0, END)
    combo_rank_edit.set("")
    set_subdivision_edit.set("")

    # Set default avatar
    newimage = ImageTk.PhotoImage(Image.open(
        "av.jpg").resize((125, 160), Image.ANTIALIAS))
    label_photo_edit.config(image=newimage)
    label_photo_edit.image = newimage

    # Clear fields in person frame after delete
    label_rank_fname_lname1.config(text=f"")
    label_age_serve.config(text=f"")
    label_pesel1.config(text=f"Pesel: ")
    label_dateOfBirth1.config(text=f"Data urodzenia: ")
    label_placeOfBirth1.config(text=f"Miejsce urodzenia: ")
    label_nameOfFather1.config(text=f"Imię ojca: ")
    label_dateofjoin1.config(text=f"Służba od: .")
    label_position1.config(text=f"Stanowisko: ")
    label_gender1.config(text=f"Płeć: ")

    label_adnotations2.config(state=NORMAL)
    label_adnotations2.delete(1.0, END)
    label_adnotations2.config(state=DISABLED)

    # Default avatar in person fame after delete
    newimage = ImageTk.PhotoImage(Image.open(
        "av.jpg").resize((125, 160), Image.ANTIALIAS))
    label_av.config(image=newimage)
    label_av.image = newimage

    list_update(edit_listbox)
    list_update(person_listbox)


# SUBDIVISION FRAME  --------------------------------------------------------------------------------------------------------
subdivision_frame = Frame(notebook)
notebook.add(subdivision_frame, text="Stwórz pododdział")


def subdivision_add(name_of_subdivision):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("INSERT INTO subdivisions VALUES(:subdivision)",
              {'subdivision': name_of_subdivision})
    conn.commit()
    conn.close()
    subdivisions_update()
    set_subdivision.config(values=subdivision_list)
    set_subdivision_edit.config(values=subdivision_list)
    entry_subdivision.delete(0, END)


label_subdivision = Label(subdivision_frame, text="Nazwa pododdziału:")
entry_subdivision = Entry(subdivision_frame, text="", width=18)
listbox_subdivision = Listbox(subdivision_frame, activestyle="none")
subdivisions_update()

button_subdivision_add = ttk.Button(
    subdivision_frame, text="Dodaj pododdział", width=15)
button_subdivision_add.config(
    command=lambda: subdivision_add(entry_subdivision.get()))

button_subdivision_delete = ttk.Button(
    subdivision_frame, text="Usun pododdział", width=15)


def delete_subdivision():
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    try:
        index_subdivision = listbox_subdivision.curselection()[0]
        name = listbox_subdivision.get(listbox_subdivision.curselection())
        c.execute("DELETE FROM subdivisions WHERE subdivision = ?", (name,))

    except:
        None
    index1 = index_subdivision + 1
    #c.execute("DELETE FROM subdivisions WHERE subdivision = ?", (name1,))
    conn.commit()
    conn.close()
    subdivisions_combobox_update()
    subdivisions_update()


# delete subdiv button
button_subdivision_delete.config(command=lambda: delete_subdivision())
listbox_subdivision.grid(row=0, column=0, rowspan=6, sticky="w")

# grids
label_subdivision.grid(row=0, column=1, sticky="w", padx=20)
entry_subdivision.grid(row=1, column=1, sticky="w", padx=20)
button_subdivision_add.grid(row=2, column=1, sticky="w", padx=20)
button_subdivision_delete.grid(row=3, column=1, sticky="w", padx=20)


def subdivisions_combobox_update():
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()

    c.execute("SELECT *, oid FROM subdivisions")
    results = c.fetchall()
    subdivision_list.clear()

    for item in results:
        subdivision_list.append(item[0])

    conn.commit()
    conn.close()

    set_subdivision.config(values=subdivision_list)
    set_subdivision_edit.config(values=subdivision_list)


subdivisions_combobox_update()

# TASK FRAME  -----------------------------------------------------------------------


def taskAdd():
    task_window = Toplevel(root)
    task_window.title("Dodaj zadanie")
    task_window.geometry("800x300")

    # Label
    label_empty = Label(task_window, text="").grid(row=2, column=0, sticky="w")
    label_title = Label(task_window, text="Tytuł zadania:").grid(
        row=3, column=0, sticky="w")
    label_responsible = Label(task_window, text="Osoba odpowiedzialna: ").grid(
        row=4, column=0, sticky="w")
    label_deadline = Label(task_window, text="Data końcowa wykonania: ").grid(
        row=5, column=0, sticky="w")
    label_describe = Label(task_window, text="Opis zadania:").grid(
        row=6, column=0, sticky="nw", rowspan=5)

    #Entry
    entry_title = Entry(task_window, text="Tytuł zadania:")
    entry_title.grid(row=3, column=1, sticky="w")
    entry_responsible = Entry(task_window, text="Osoba odpowiedzialna: ")
    entry_responsible.grid(row=4, column=1, sticky="w")
    entry_deadline = Entry(task_window, text="Data końcowa wykonania: ")
    entry_deadline.grid(row=5, column=1, sticky="w")
    entry_describe = Text(task_window, height=10, width=70)
    entry_describe.grid(row=6, column=1, sticky="w")

 
    add_task_window = ttk.Button(task_window, text="Dodaj zadanie")
    add_task_window.grid(row=7, column=1, sticky="w")

   
    def add_and_close():
        addTaskDb(entry_title.get(), entry_responsible.get(), date.today().strftime(
            "%d-%m-%Y"), entry_deadline.get(), entry_describe.get("1.0", END), "")
        entry_title.delete(0, END)
        entry_responsible.delete(0, END)
        entry_deadline.delete(0, END)
        entry_describe.delete(1.0, END)
        task_window.destroy()
    

    add_task_window.config(command=lambda: add_and_close())
    


def clear_all_tree():
    for item in tree_task.get_children():
        tree_task.delete(item)


def taskUpdate():
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM tasks")
    results = c.fetchall()
    clear_all_tree()
    for task in results:
        tree_task.insert("", END, values=(
            task[0], task[1], task[2], task[3], task[4], task[5]), tags=(task[6]))
    conn.commit()
    conn.close()


def addTaskDb(title, responsible, entryDate, endDate, describe, tag):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("SELECT *, oid FROM tasks")
    results = c.fetchall()
    id = 1
    if len(results) > 0:
        id = results[-1][4]+1
    else:
        id = 1
    c.execute("INSERT INTO tasks VALUES (:title, :responsible, :entryDate, :endDate, :taskId, :describe, :tag)",
              {
                  'title': title,
                  'responsible': responsible,
                  'entryDate': entryDate,
                  'endDate': endDate,
                  'taskId': id,
                  'describe': describe,
                  'tag': tag,
              })

    conn.commit()
    conn.close()
    taskUpdate()


def task_delete():

    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    selected = tree_task.selection()
    for item in selected:
        selected1 = tree_task.item(item)

        c.execute("DELETE FROM tasks WHERE oid = ?", (selected1['values'][4],))
    conn.commit()
    conn.close()
    taskUpdate()


def editWindow():

    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()

    c.execute("SELECT *, oid FROM tasks")
    results = c.fetchall()
 
    selected_id = None
    selected = tree_task.selection()
    for item in selected:
        selected1 = tree_task.item(item)
        selected_id = selected1['values'][4]

    for item in results:
        if item[4] == selected_id:
            task_window_edit = Toplevel(root)
            task_window_edit.title("Edytuj zadanie")
            task_window_edit.geometry("800x300")
            task_window_edit.iconbitmap("icon.ico")
       
            label_empty = Label(task_window_edit, text="").grid(
                row=2, column=0, sticky="w")
            label_title = Label(task_window_edit, text="Tytuł zadania:").grid(
                row=3, column=0, sticky="w")
            label_responsible = Label(task_window_edit, text="Osoba odpowiedzialna: ").grid(
                row=4, column=0, sticky="w")
            label_deadline = Label(task_window_edit, text="Data końcowa wykonania: ").grid(
                row=5, column=0, sticky="w")
            label_describe = Label(task_window_edit, text="Opis zadania:").grid(
                row=6, column=0, sticky="nw", rowspan=5)
            #


            entry_title = Entry(task_window_edit, text=f"")
            entry_title.insert(0, item[0])
            entry_title.grid(row=3, column=1, sticky="w")
            entry_responsible = Entry(task_window_edit, text=f"{item[1]}")
            entry_responsible.insert(0, item[1])
            entry_responsible.grid(row=4, column=1, sticky="w")
            entry_deadline = Entry(task_window_edit, text=f"{item[3]}")
            entry_deadline.insert(0, item[2])
            entry_deadline.grid(row=5, column=1, sticky="w")
            entry_describe = Text(task_window_edit, height=10, width=70)
            entry_describe.grid(row=6, column=1, sticky="w")
            entry_describe.insert(1.0, item[5])
            


            add_task_window = ttk.Button(
                task_window_edit, text="Edytuj zadanie")
            add_task_window.grid(row=7, column=1, sticky="w")

            add_task_window.config(command=lambda: update_and_close(
                entry_title, entry_responsible, entry_deadline, entry_describe, selected_id))

        def update_and_close(entry_title, entry_responsible, entry_deadline, entry_describe, selected_id):
            task_update(entry_title.get(), entry_responsible.get(), date.today().strftime(
                "%d-%m-%Y"), entry_deadline.get(), entry_describe.get(1.0, END), selected_id)
            entry_title.delete(0, END)
            entry_responsible.delete(0, END)
            entry_deadline.delete(0, END)
            entry_describe.delete(1.0, END)
            task_window_edit.destroy()


    conn.commit()
    conn.close()


def task_update(title, responsible, entryDate, endDate, describe, taskId):
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET title = ?, responsible = ?, entryDate = ?, endDate = ?, describe = ? WHERE taskId = ?""",
              (title, responsible, entryDate, endDate, describe, taskId))
    conn.commit()
    conn.close()
    taskUpdate()


def clear_selection(event):
  
    region = event.widget.identify("region", event.x, event.y)
    if region == "nothing":  # jeśli zaznaczenie jest puste
        tree_task.selection_remove(tree_task.focus())


def greenDoneTask():
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()
    selected_id = None
    selected = tree_task.selection()
    for item in selected:
        selected1 = tree_task.item(item)
        selected_id = selected1['values'][4]
    c.execute("UPDATE tasks SET tag = 'green_done' WHERE taskId = ?",
              (selected_id,))
    conn.commit()
    conn.close()
    taskUpdate()


def redUndoneTask():
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()

    selected_id = None
    selected = tree_task.selection()
    for item in selected:
        selected1 = tree_task.item(item)
        selected_id = selected1['values'][4]
    c.execute("UPDATE tasks SET tag = 'red_undone' WHERE taskId = ?",
              (selected_id,))
    conn.commit()
    conn.close()
    taskUpdate()


def neutralTask():
    conn = sqlite3.connect('persons_list.db')
    c = conn.cursor()

    selected_id = None
    selected = tree_task.selection()
    for item in selected:
        selected1 = tree_task.item(item)
        selected_id = selected1['values'][4]

    c.execute("UPDATE tasks SET tag = '' WHERE taskId = ?", (selected_id,))

    conn.commit()
    conn.close()
    taskUpdate()


task_frame = Frame(notebook)
notebook.add(task_frame, text="Zadania")

tree_task = ttk.Treeview(task_frame, columns=(
    "c1", "c2", "c3", "c4", "c5"), show="headings", height=15)
tree_task.grid(row=0, column=0, columnspan=100)

taskUpdate()

# Treeview config
tree_task.column("c1", anchor=CENTER)
tree_task.heading("c1", text="Tytuł")

tree_task.column("c2", anchor=CENTER)
tree_task.heading("c2", text="Osoba odpowiedzialna")

tree_task.column("c3", anchor=CENTER)
tree_task.heading("c3", text="Data wpisu")

tree_task.column("c4", anchor=CENTER)
tree_task.heading("c4", text="Data końcowa")

tree_task.column("c5", anchor=CENTER)
tree_task.heading("c5", text="Numer zadania")


add_tree_button = ttk.Button(task_frame, text="Dodaj zadanie")
add_tree_button.config(command=lambda: taskAdd())

delete_tree_button = ttk.Button(task_frame, text="Usuń zadanie")
delete_tree_button.config(command=lambda: task_delete())

edit_tree_button = ttk.Button(task_frame, text="Podgląd / Edytuj")
edit_tree_button.config(command=lambda: editWindow())

done_tree_button = ttk.Button(task_frame, text="Oznacz jako wykonane")
done_tree_button.config(command=lambda: greenDoneTask())

notdone_tree_button = ttk.Button(task_frame, text="Oznacz jako niewykonane")
notdone_tree_button.config(command=lambda: redUndoneTask())

inprogress_tree_button = ttk.Button(
    task_frame, text="Oznacz jako aktualnie wykonywane")
inprogress_tree_button.config(command=lambda: neutralTask())

# Buttons grid
add_tree_button.grid(row=1, column=0, sticky="w")
delete_tree_button.grid(row=1, column=1)
edit_tree_button.grid(row=1, column=2, sticky="w")
done_tree_button.grid(row=1, column=3, sticky="w")
notdone_tree_button.grid(row=1, column=4, sticky="w")
inprogress_tree_button.grid(row=1, column=5, sticky="w")

# Scrollbar task_frame
scrollbar = ttk.Scrollbar(task_frame, orient=VERTICAL, command=tree_task.yview)
tree_task.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=101, sticky='ns')


tree_task.tag_configure("green_done", background="green", foreground="white")
tree_task.tag_configure("red_undone", background="red", foreground="white")

tree_task.bind("<Button-1>", clear_selection)

root.mainloop()
