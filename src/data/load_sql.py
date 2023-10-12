import json
import sqlite3
import os


data_file_path = os.path.abspath('src/data/users.json')

with open(data_file_path , 'r') as json_file:
    data = json.load(json_file)

conn = sqlite3.connect('applications.sqlite')
cursor = conn.cursor()

for item in data:
    cursor.execute(
        'INSERT INTO users (id, email, username, hashed_password, avatar, phone_number, is_active, is_superuser, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (item['id'], item['email'], item['username'], item['hashed_password'], item['avatar'], item['phone_number'], item['is_active'], item['is_superuser'], item['is_verified']))
conn.commit()

conn.close()