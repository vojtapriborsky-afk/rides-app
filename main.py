from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- ZDE VLOŽ svůj Render PostgreSQL connection string ---
DB = "postgres://rides_db_myu5_user:p4oSOKUftm70mQmNuDruYuIRBUnHMK2i@dpg-d5nck00gjchc7399but0-a:5432/rides_db_myu5"

# --- databáze ---
def get_db():
    conn = psycopg2.connect(DB, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # tabulka uživatelů
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT,
        role TEXT,
        login TEXT UNIQUE,
        password TEXT
    )
    ''')
    # tabulka aut
    c.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id SERIAL PRIMARY KEY,
        name TEXT
    )
    ''')
    # tabulka jízd
    c.execute('''
    CREATE TABLE IF NOT EXISTS rides (
        id SERIAL PRIMARY KEY,
        date TEXT,
        time TEXT,
        car_id INTEGER,
        driver_id INTEGER,
        start TEXT,
        end TEXT,
        status TEXT
    )
    ''')
    # tabulka změn jízd
    c.execute('''
    CREATE TABLE IF NOT EXISTS ride_changes (
        id SERIAL PRIMARY KEY,
        ride_id INTEGER,
        description TEXT,
        changed_by INTEGER,
        new_status TEXT
    )
    ''')
    # tabulka potvrzení
    c.execute('''
    CREATE TABLE IF NOT EXISTS confirmations (
        id SERIAL PRIMARY KEY,
        ride_change_id INTEGER,
        driver_id INTEGER,
        confirmed_at TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# inicializace databáze při startu
init_db()

# --- login ---
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE login=%s", (username,))
    user = c.fetchone()
    conn.close()
    if user and pwd_context.verify(password, user["password"]):
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="user_id", value=str(user["id"]))
        response.set_cookie(key="role", value=user["role"])
        return response
    return RedirectResponse(url="/login", status_code=302)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("user_id")
    response.delete_cookie("role")
    return response

# --- dashboard ---
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    user_id = request.cookies.get("user_id")
    role = request.cookies.get("role")
    if not user_id:
        return RedirectResponse("/login")
    
    conn = get_db()
    c = conn.cursor()
    
    if role == "driver":
        c.execute("""
            SELECT rides.*, cars.name as car_name FROM rides
            LEFT JOIN cars ON rides.car_id=cars.id
            WHERE driver_id=%s
        """, (user_id,))
        rides = c.fetchall()
        pending_changes = []
    else:
        c.execute("""
            SELECT rides.*, cars.name as car_name FROM rides
            LEFT JOIN cars ON rides.car_id=cars.id
        """)
        rides = c.fetchall()
        
        c.execute("""
            SELECT rides.id as ride_id, rides.date, rides.time, rides.driver_id, ride_changes.description
            FROM rides
            JOIN ride_changes ON rides.id = ride_changes.ride_id
            LEFT JOIN confirmations ON ride_changes.id = confirmations.ride_change_id
            WHERE confirmations.id IS NULL
            ORDER BY rides.date, rides.time
        """)
        pending_changes = c.fetchall()
    
    conn.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "rides": rides,
        "role": role,
        "pending_changes": pending_changes
    })

# --- potvrzení řidiče ---
@app.post("/confirm/{ride_id}")
def confirm_ride(ride_id: int, request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login")
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO confirmations (ride_change_id, driver_id, confirmed_at)
        VALUES (%s, %s, NOW())
    """, (ride_id, user_id))
    c.execute("UPDATE rides SET status='potvrzeno' WHERE id=%s", (ride_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=302)
