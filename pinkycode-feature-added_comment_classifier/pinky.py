import cgi
import json
import zipfile
import tempfile
import uuid
import os
import traceback
import agent
import psycopg2
import re
from http.cookies import SimpleCookie
from urllib.parse import parse_qs

# user_id for the admin
ADMIN_ID = 1


def is_admin(user_id):
    """Checks if the given user ID corresponds to an admin user.
    Args:
        user_id (int): The ID of the user to check.
    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    return user_id == ADMIN_ID


def get_start_page(user_id):
    """Determines the start page for a user based on their admin status.
    Args:
        user_id (int): The ID of the user.
    Returns:
        str: The name of the start page ('admin.html' for admins, 'index.html' for regular users).
    """
    if is_admin(user_id):
        page = 'admin.html'
    else:
        page = 'index.html'
    return page


conn = psycopg2.connect(
    dbname="pinky",
    user="pinky",
    password=os.environ.get('PGPASS'),
    host="localhost",
    port="5432"
)


def redirect(start_response, headers, url):
    headers.append(('Content-Type', 'text/html; charset=utf-8'))
    try:
        with open(f"/home/pinky/www/static/{url}", 'rb') as file:
            content = file.read()
        start_response('200 OK', headers)
        return [content]

    except FileNotFoundError:
        start_response('404 Not Found', headers)
        return [b"File not found"]

    except Exception as e:
        start_response('500 Internal Server Error', headers)
        return [b"Error processing request: ", str(e).encode('utf-8'), traceback.format_exc().encode('utf-8')]


def application(environ, start_response):
    # Set default headers
    headers = [
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ('Pragma', 'no-cache'),
        ('Expires', '0')
    ]

    try:
        session_id = False
        user_id = 0

        # Parse cookies
        cookie = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            cookie.load(environ['HTTP_COOKIE'])

        # Get or create session ID
        if 'session_id' in cookie:
            session_id = cookie['session_id'].value
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM session WHERE id = %s", (session_id,))
                row = cur.fetchone()
                if row:
                    user_id = row[0]
                    print('USER ALREADY LOGGED IN')

        # Parse URL parameters { "name": [ val1, val2, ...], ... }
        url_params = parse_qs(environ['QUERY_STRING'])

        # Check request method
        method = environ['REQUEST_METHOD']
        if method == 'GET':
            page = 'welcome.html'
            if session_id and user_id:
                # NOTE: HERE GO AUTHORIZED USERS
                if 'logout' in url_params:
                    # Delete session from database, available for all user roles
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM session WHERE id = %s", (session_id,))
                        conn.commit()
                    # Clear the session cookie
                    cookie['session_id'] = ''
                    cookie['session_id']['path'] = '/'
                    cookie['session_id']['httponly'] = True
                    cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
                    headers.append(('Set-Cookie', cookie.output(header='').strip()))
                    # TODO: consider creating a goodbye page
                    page = 'welcome.html'
                elif 'history' in url_params:
                    # Request history, available for a USER role with logged user_id
                    # and for ADMIN (no user filters applied)
                    history = int(url_params['history'][0])
                    user_filter = f"AND user_id = {int(user_id)} " if not is_admin(user_id) else ''
                    with conn.cursor() as cur:
                        cur.execute(
                            f"SELECT id, user_id, TO_CHAR(time, 'YYYY-MM-DD HH24:MI:SS') AS time, file_name, issues FROM history WHERE id > %s {user_filter}LIMIT 100;",
                            (history,))
                        result = json.dumps(cur.fetchall())
                    headers.append(('Content-Type', 'application/json; charset=utf-8'))
                    start_response('200 OK', headers)
                    return [result.encode('utf-8')]
                else:
                    # Select starting page based upon user's role ADMIN/USER
                    page = get_start_page(user_id)
            else:
                # NOTE: HERE GO UN-AUTHORIZED USERS
                # WARNING: NO OTHER PAGES THAN WELCOME AND LOGIN FOR UNAUTHORIZED USERS HERE (UNDER THIS ELSE)!!!
                page = 'login.html' if 'login' in url_params else 'welcome.html'
            return redirect(start_response, headers, page)

        elif method == 'POST':
            # Parse the form data
            form = cgi.FieldStorage(
                fp=environ['wsgi.input'],
                environ=environ,
                keep_blank_values=True
            )

            # Check if login in progress
            if 'email' in form and 'password' in form:
                email = form.getvalue('email')
                password = form.getvalue('password')
                # Check login:password
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM \"user\" WHERE login = %s AND password = %s", (email, password))
                    row = cur.fetchone()
                if row is not None:
                    user_id = row[0]
                    # Create a new session
                    session_id = str(uuid.uuid4())
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO session (id, user_id) VALUES (%s, %s)", (session_id, user_id))
                        conn.commit()
                    cookie['session_id'] = session_id
                    cookie['session_id']['path'] = '/'
                    cookie['session_id']['httponly'] = True
                    # Add session ID to headers
                    headers.append(('Set-Cookie', cookie.output(header='').strip()))
                    # Select start page either for the admin account or for a user account
                    page = get_start_page(user_id)
                    return redirect(start_response, headers, page)
                else:
                    # Redirect to login page with error parameter
                    print(f"WRONG LOGIN:PASSWORD {email}:{password}")
                    headers.append(('Location', '/?login=1&error=1'))
                    start_response('302 Found', headers)
                    return []


            elif user_id == 0:
                return redirect(start_response, headers, 'login.html')

            # Check if a file was uploaded
            if 'file' in form:
                file_item = form['file']

                if file_item.file:
                    filename = os.path.basename(file_item.filename)

                    if filename.lower().endswith('.zip'):
                        temp_dir = tempfile.mkdtemp()
                        zip_path = os.path.join(temp_dir, f"{uuid.uuid4()}.zip")

                        # Save the file to temporary directory
                        with open(zip_path, 'wb') as f:
                            while chunk := file_item.file.read(8192):
                                f.write(chunk)

                        # Unpack the zip file
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)

                        # Accumulate results
                        results = []

                        # Iterate through the unpacked files
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if file_path != zip_path:  # Skip the original zip file

                                    try:
                                        result = agent.evaluate(file_path)
                                    except Exception as e:
                                        result = {
                                            'filename': file,
                                            'error': f"Error processing file: {str(e)}"
                                        }

                                    results.append(result)

                        result_json = json.dumps(results)

                        # Clean up the temporary directory and files
                        for root, dirs, files in os.walk(temp_dir, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(temp_dir)

                        # Insert into history

                        with conn.cursor() as cur:
                            cur.execute("INSERT INTO history (user_id, file_name, issues) VALUES (%s, %s, %s);",
                                (user_id, filename, result_json))
                            conn.commit()

                        # Prepare response
                        headers.append(('Content-Type', 'application/json; charset=utf-8'))
                        start_response('200 OK', headers)

                        return [result_json.encode('utf-8')]

        # For unhandled requests
        start_response('400 ERROR', headers)
        return [b"Send a file\n"]

    except Exception as e:
        start_response('500 Internal Server Error', headers)

        return [b"Error processing request: ", str(e).encode('utf-8'), traceback.format_exc().encode('utf-8')]
