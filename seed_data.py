import psycopg2
from passlib.context import CryptContext

DB = "postgresql://postgres:Straznice1+++@db.wdpeoiiuxsovtxqhxrld.supabase.co:5432/postgres"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = psycopg2.connect(DB)
c = conn.cursor()

users = [
    ("Jan Novak", "driver", "novak", pwd_context.hash("123")),
    ("Petr Dvorak", "driver", "dvorak", pwd_context.hash("123")),
    ("Karel Svoboda", "driver", "svoboda", pwd_context.hash("123")),
    ("Dispecer1", "dispecer", "disp1", pwd_context.hash("123")),
    ("Dispecer2", "dispecer", "disp2", pwd_context.hash("123")),
]
for u in users:
    c.execute("INSERT INTO users (name, role, login, password) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING", u)

cars = [
    ("Škoda Octavia",),
    ("Ford Transit",),
    ("Mercedes Sprinter",)
]
for car in cars:
    c.execute("INSERT INTO cars (name) VALUES (%s) ON CONFLICT DO NOTHING", car)

rides = [
    ("2026-01-20", "08:00", 1, 1, "Praha", "Brno", "navrženo"),
    ("2026-01-20", "09:30", 2, 2, "Ostrava", "Olomouc", "navrženo"),
    ("2026-01-20", "11:00", 3, 3, "Plzeň", "Praha", "navrženo"),
]
for r in rides:
    c.execute("INSERT INTO rides (date,time,car_id,driver_id,start,end,status) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", r)

ride_changes = [
    (1, "Posun jízdy z 08:00 na 08:30", 4, "čeká na potvrzení"),
    (2, "Změna auta Ford Transit → Mercedes Sprinter", 5, "čeká na potvrzení")
]
for rc in ride_changes:
    c.execute("INSERT INTO ride_changes (ride_id, description, changed_by, new_status) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING", rc)

conn.commit()
conn.close()
print("Vzorová data vložena!")
