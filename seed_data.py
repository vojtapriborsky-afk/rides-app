import sqlite3
from passlib.context import CryptContext

DB = "/data/database.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect(DB)
c = conn.cursor()

users = [
    ("Jan Novak", "driver", "novak", pwd_context.hash("123")),
    ("Petr Dvorak", "driver", "dvorak", pwd_context.hash("123")),
    ("Karel Svoboda", "driver", "svoboda", pwd_context.hash("123")),
    ("Dispecer1", "dispecer", "disp1", pwd_context.hash("123")),
    ("Dispecer2", "dispecer", "disp2", pwd_context.hash("123")),
]
c.executemany("INSERT OR IGNORE INTO users (name, role, login, password) VALUES (?, ?, ?, ?)", users)

cars = [
    ("Škoda Octavia",),
    ("Ford Transit",),
    ("Mercedes Sprinter",)
]
c.executemany("INSERT OR IGNORE INTO cars (name) VALUES (?)", cars)

rides = [
    ("2026-01-20", "08:00", 1, 1, "Praha", "Brno", "navrženo"),
    ("2026-01-20", "09:30", 2, 2, "Ostrava", "Olomouc", "navrženo"),
    ("2026-01-20", "11:00", 3, 3, "Plzeň", "Praha", "navrženo"),
]
c.executemany("INSERT OR IGNORE INTO rides (date, time, car_id, driver_id, start, end, status) VALUES (?, ?, ?, ?, ?, ?, ?)", rides)

ride_changes = [
    (1, "Posun jízdy z 08:00 na 08:30", 4, "čeká na potvrzení"),
    (2, "Změna auta Ford Transit → Mercedes Sprinter", 5, "čeká na potvrzení")
]
c.executemany("INSERT OR IGNORE INTO ride_changes (ride_id, description, changed_by, new_status) VALUES (?, ?, ?, ?)", ride_changes)

conn.commit()
conn.close()
print("Vzorová data vložena!")
