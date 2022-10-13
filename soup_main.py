import datetime
import os
import sqlite3
from sqlite3 import Error

import pandas as pd
import requests
from bs4 import BeautifulSoup


eksi_url = "https://eksisozluk.com"

baslik = input("EkşiParser: Hangi başlığı aramak istiyorsunuz?\n")

columns = [
    "id",
    'baslik',
    'Icerik',
    'Yazar',
    'Tarih',
    'Konu',
    'Entry ID',
    'Entry URL'
]
rows = [columns]

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}


base_url = eksi_url+"/basliklar/ara?SearchForm.Keywords=" + baslik + "&SearchForm.Author=&SearchForm.When.From=&SearchForm.When.To=&SearchForm.NiceOnly=false&SearchForm.SortOrder=Date"
r1 = requests.get(base_url, headers=headers)

soup1 = BeautifulSoup(r1.content, "html.parser")
entry_titles = soup1.find_all("ul", {"class": "topic-list"})

for title in entry_titles:

    urls = title.find_all("a")

    for url in urls:

        f_url = url.attrs["href"]
        current_url = eksi_url + str(f_url)
        print(current_url)

        r2 = requests.get(str(eksi_url + f_url), headers=headers)
        soup2 = BeautifulSoup(r2.content, "html.parser")

        topic_title = soup2.find("h1", {"id": "title"}).text.strip()


        try:
            page_count = int(soup2.find("div", {"class": "pager"}).attrs["data-pagecount"])
        except:
            page_count = 1

        print(page_count)

        # Check every page
        for j in range(1, page_count + 1):

            print("All Pages: " + str(page_count) + " Current Page: " + str(j))

            r3 = requests.get(current_url + "?p=" + str(j), headers=headers)

            s3 = BeautifulSoup(r3.content, "html.parser")
            entry_divs = s3.find_all("div", {"class": "content"})

            # Check every entrys
            for entry in entry_divs:

                footer = entry.findNext("footer")

                data_id = str(entry.findParent("li").attrs["data-id"])
                entry_id = "#" + data_id
                entry_url = "https://eksisozluk.com/entry/" + data_id

                author = footer.find_all("a")[0].text
                date = footer.find_all("a")[1].text

                # DATA AREA -->
                rows.append((

                    baslik,
                    entry.text,
                    author,
                    date,
                    topic_title,
                    entry_id,
                    entry_url
                ))
                # <-- DATA AREA

df = pd.DataFrame(rows)
now_time = datetime.datetime.now()


# Write to xlsx file
# writer_b = pd.ExcelWriter('Rapor-' + str(baslik) + '-' + str(now_time.date()) + '.xlsx', engine='xlsxwriter')
# df.to_excel(writer_b,
#             sheet_name=str(now_time.date()),
#             index=False)
#
# # Save to file
# writer_b.save()

# INSERT DATA IN DATABASE
# Create a connection object

# db area -->
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        if os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
        else:
            print("Database file not found!")
            # create_database(db_file)
            conn = sqlite3.connect(db_file)

    except Error as e:
        print(e)

    return conn


try:
    conn = sqlite3.connect('eksi_databasee.db')
    print("Database connection is successful!")

    c = conn.cursor()

    # verileri tabloya ekle

    c.execute(
        "CREATE TABLE IF NOT EXISTS eksi_table (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, icerik TEXT, yazar TEXT, tarih TEXT, konu TEXT, entry_id TEXT, entry_url TEXT)")
    print("Table created successfully!")
    conn.commit()


    # verileri tabloya ekle
    for i in range(1, len(rows)):
        c.execute("INSERT INTO " + "eksi_table" + " VALUES (null,?,?,?,?,?,?,?)", rows[i])

        print((baslik).replace(" ", "_") + " tablosuna veri eklendi.")
        conn.commit()
        print(rows[i], "eklendi.")

    conn.close()

except sqlite3.Error as error:
    print("Failed to insert data into sqlite table", error)

finally:
    if (conn):
        conn.close()
        print("The SQLite connection is closed")

# <-- db area

# Close the connection
conn.close()