import cgi
import json
import zipfile
import tempfile
import uuid
import os
import traceback
from http.cookies import SimpleCookie
from urllib.parse import parse_qs


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
        logged = 1

        # Parse cookies
        cookie = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            cookie.load(environ['HTTP_COOKIE'])

        # Get or create session ID
        if 'session_id' in cookie:
            session_id = cookie['session_id'].value

        # Parse URL parameters { "name": [ val1, val2, ...], ... }
        url_params = parse_qs(environ['QUERY_STRING'])

        # Check request method
        method = environ['REQUEST_METHOD']
        if method == 'GET':
            page = 'welcome.html'
            if logged == 1:
                if 'logout' in url_params:
                    # Delete session from database
                    # Clear the session cookie
                    cookie['session_id'] = ''
                    cookie['session_id']['path'] = '/'
                    cookie['session_id']['httponly'] = True
                    cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
                    headers.append(('Set-Cookie', cookie.output(header='').strip()))
                    # TODO: consider creating a goodbye page
                    page = 'welcome.html'
                else:
                    page = 'index.html'
            else:
                if 'login' in url_params:
                    page = 'login.html'
                else:
                    page = 'welcome.html'
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
                row = None
                # Check login:password
                if row is not None:
                    user_id = row[0]
                    # Create new session
                    session_id = str(uuid.uuid4())
                    cookie['session_id'] = session_id
                    cookie['session_id']['path'] = '/'
                    cookie['session_id']['httponly'] = True
                    # Add session ID to headers
                    headers.append(('Set-Cookie', cookie.output(header='').strip()))
                    return redirect(start_response, headers, 'index.html')
                else:
                    # TODO: redirect to login error page
                    print(f"WRONG LOGIN:PASSWORD {email}:{password}")
                    return redirect(start_response, headers, 'login.html')

            elif logged == 0:
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
                                        result = ""
                                    except Exception as e:
                                        result = {
                                            'filename': file,
                                            'error': f"Error processing file: {str(e)}"
                                        }

                                    results.append(result)

                        # Clean up the temporary directory and files
                        for root, dirs, files in os.walk(temp_dir, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        os.rmdir(temp_dir)

                        # Prepare response
                        headers.append(('Content-Type', 'application/json; charset=utf-8'))
                        start_response('200 OK', headers)

                        return [json.dumps(results).encode('utf-8')]

        # For unhandled requests
        start_response('400 ERROR', headers)
        return [b"Send a file\n"]

    except Exception as e:
        start_response('500 Internal Server Error', headers)

        return [b"Error processing request: ", str(e).encode('utf-8'), traceback.format_exc().encode('utf-8')]
