import json
import zipfile
tempfile
import tempfile
import uuid
import os
import traceback
import agent
import psycopg2
import re
from http.cookies import SimpleCookie
from urllib.parse import parse_qs
from werkzeug.wrappers import Request

# user_id for the admin
ADMIN_ID = 1

def is_admin(user_id):
    return user_id == ADMIN_ID

def get_start_page(user_id):
    return 'admin.html' if is_admin(user_id) else 'index.html'

# Connect using DATABASE_URL from Render
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return psycopg2.connect(
            dbname=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
    # fallback to env vars
    return psycopg2.connect(
        dbname=os.environ.get('PGDATABASE','pinky'),
        user=os.environ.get('PGUSER','pinky'),
        password=os.environ.get('PGPASS'),
        host=os.environ.get('PGHOST','localhost'),
        port=os.environ.get('PGPORT','5432')
    )

conn = get_db_connection()

def redirect(start_response, headers, url):
    headers.append(('Content-Type', 'text/html; charset=utf-8'))
    try:
        static_path = os.path.join(os.getcwd(), 'static', url)
        with open(static_path, 'rb') as file:
            content = file.read()
        start_response('200 OK', headers)
        return [content]
    except FileNotFoundError:
        start_response('404 Not Found', headers)
        return [b"File not found"]
    except Exception as e:
        start_response('500 Internal Server Error', headers)
        return [b"Error processing request: ", str(e).encode(), traceback.format_exc().encode()]

def application(environ, start_response):
    headers = [
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ('Pragma', 'no-cache'),
        ('Expires', '0')
    ]
    try:
        user_id = 0
        cookie = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            cookie.load(environ['HTTP_COOKIE'])
            session = cookie.get('session_id')
            if session:
                with conn.cursor() as cur:
                    cur.execute("SELECT user_id FROM session WHERE id = %s", (session.value,))
                    row = cur.fetchone()
                    if row:
                        user_id = row[0]

        request = Request(environ)
        method = request.method

        if method == 'GET':
            params = request.args
            if user_id:
                if 'logout' in params:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM session WHERE id = %s", (session.value,))
                        conn.commit()
                    cookie['session_id'] = ''
                    cookie['session_id']['path'] = '/'
                    cookie['session_id']['httponly'] = True
                    cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
                    headers.append(('Set-Cookie', cookie.output(header='').strip()))
                    return redirect(start_response, headers, 'welcome.html')
                elif 'history' in params:
                    history = int(params.get('history', 0))
                    user_filter = '' if is_admin(user_id) else f"AND user_id = {user_id} "
                    with conn.cursor() as cur:
                        cur.execute(
                            f"SELECT id, user_id, TO_CHAR(time, 'YYYY-MM-DD HH24:MI:SS') AS time, file_name, issues FROM history WHERE id > %s {user_filter}LIMIT 100;",
                            (history,)
                        )
                        result = json.dumps(cur.fetchall())
                    headers.append(('Content-Type', 'application/json; charset=utf-8'))
                    start_response('200 OK', headers)
                    return [result.encode()]
                return redirect(start_response, headers, get_start_page(user_id))
            else:
                page = 'login.html' if 'login' in request.args else 'welcome.html'
                return redirect(start_response, headers, page)

        elif method == 'POST':
            # LOGIN
            form = request.form
            if 'email' in form and 'password' in form:
                email = form.get('email')
                password = form.get('password')
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM \"user\" WHERE login = %s AND password = %s", (email, password))
                    row = cur.fetchone()
                if row:
                    user_id = row[0]
                    session_id = str(uuid.uuid4())
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO session (id, user_id) VALUES (%s, %s)", (session_id, user_id))
                        conn.commit()
                    cookie['session_id'] = session_id
                    cookie['session_id']['path'] = '/'
                    cookie['session_id']['httponly'] = True
                    headers.append(('Set-Cookie', cookie.output(header='').strip()))
                    return redirect(start_response, headers, get_start_page(user_id))
                headers.append(('Location', '/?login=1&error=1'))
                start_response('302 Found', headers)
                return []

            if not user_id:
                return redirect(start_response, headers, 'login.html')

            # FILE UPLOAD
            upload = request.files.get('file')
            if upload and upload.filename.lower().endswith('.zip'):
                filename = os.path.basename(upload.filename)
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, filename)
                upload.save(zip_path)
                results = []
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path != zip_path:
                            try:
                                res = agent.evaluate(file_path)
                            except Exception as e:
                                res = {'filename': file, 'error': str(e)}
                            results.append(res)
                result_json = json.dumps(results)
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO history (user_id, file_name, issues) VALUES (%s, %s, %s)", (user_id, filename, result_json))
                    conn.commit()
                headers.append(('Content-Type', 'application/json; charset=utf-8'))
                start_response('200 OK', headers)
                return [result_json.encode()]

        start_response('400 ERROR', headers)
        return [b"Send a file\n"]

    except Exception as e:
        start_response('500 Internal Server Error', headers)
        return [b"Error processing request: ", str(e).encode(), traceback.format_exc().encode()]
