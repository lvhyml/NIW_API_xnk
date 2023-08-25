import ssl
import pymssql

from config import server, database, username, password, driver, account_keys


# Function to establish the SQL Server connection
def get_db_connection():
    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
    # Set the SSL context in the connection
    # conn = pyodbc.connect(
    #     f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;",
    #     SSLCertFile=None,
    #     SSLCertStoreName=None,
    #     SSLCertHostNameChecking=None,
    #     sslContext=ssl_context
    # )

    conn = pymssql.connect(server=server, database=database, user=username, password=password)
    return conn


def get_account_info(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE email=%s", email)
        acc_info = cursor.fetchone()
        acc_dict = dict(zip(account_keys, acc_info))
        return acc_dict
    except Exception as e:
        return {"code": "402", 'message': 'Error while getting user information.'}
