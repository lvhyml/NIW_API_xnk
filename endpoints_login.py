from fastapi import APIRouter

from models import UserRegistration, UserLogin, PasswordChangeRequest, UserInfoRequest, UpdateAvatarRequest, Item, \
    RoleAdmin, SearchProfileIdRequest, ActiveUser, LicenseUser, MacAddressChangeRequest
from connect_db import get_db_connection, get_account_info
from config import admin_account_keys, product_keys, account_keys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import random
import string
import datetime
import jwt

login_router = APIRouter()

# JWT configuration
JWT_SECRET = 'secret_key'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 24 * 60
pwd_context = CryptContext(schemes=['bcrypt'])


def generate_token(username: str) -> str:
    payload = {
        'sub': username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
    }
    print(username)
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(token)
    return token


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


def get_current_username(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    return verify_token(token.credentials)


# API endpoint for user registration
@login_router.post('/api/register')
def register(user: UserRegistration):
    # Check if user already exists in the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # cursor.execute("SELECT COUNT(*) FROM accounts WHERE email=?", user.email)
        query = "SELECT COUNT(*) FROM accounts WHERE email=%s"
        cursor.execute(query, (user.email,))
        count = cursor.fetchone()[0]
        if count == 1:
            return {"code": "401", 'message': 'This email have been registered before.'}
        else:
            try:
                created_account = datetime.datetime.now()
                query = "INSERT INTO accounts (username, password, phone, email, country, tax, owner, active, created_account, type, mac_address, interested_field, license_type ,count_search) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (
                    user.username, user.password, user.phone, user.email, user.country, user.tax, "0",
                    "0", created_account, user.user_type, user.mac_address, user.interested_field, "0", "0"))

                conn.commit()

                return {"code": "200", 'message': 'Registration successful.'}
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error while trying to register")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking email is existed")


# API endpoint for user login
@login_router.post('/api/login_app')
def login(user: UserLogin):
    try:
        # Check if user exists in the database
        check_log = 0
        conn = get_db_connection()
        cursor = conn.cursor()
        # cursor.execute("SELECT COUNT(*) FROM accounts WHERE email=? AND password=?", user.email, user.password)
        query = "SELECT email, expiration_date, mac_address FROM accounts WHERE email=%s AND password=%s"
        cursor.execute(query, (user.email, user.password))
        row = cursor.fetchone()
        result = row[0]
        date_user = row[1]
        mac_address = row[2]
        if result is not None:
            if user.mac_address == mac_address:
                if date_user is not None:
                    expiration_date = datetime.datetime.strptime(date_user, "%Y-%m-%d %H:%M:%S.%f")
                    date_now = datetime.datetime.strptime(str(datetime.datetime.now()), "%Y-%m-%d %H:%M:%S.%f")

                    if date_now < expiration_date:
                        token = generate_token(user.email)
                        return {'Access_Token': token}
                    else:
                        check_log = 1
                        raise HTTPException(status_code=406, detail='License Expired')
                else:
                    token = generate_token(user.email)
                    return {'Access_Token': token}
            else:
                # token = generate_token(user.email)
                # return {'Access_Token': token}
                check_log = 2
                raise HTTPException(status_code=405, detail='MacAddress not valid')

    except Exception as e:
        if check_log == 1:
            raise HTTPException(status_code=406, detail='License Expired')
        elif check_log == 2:
            raise HTTPException(status_code=405, detail='MacAddress not valid')
        else:
            raise HTTPException(status_code=401, detail='Invalid username or password')
        # else:
        #     raise HTTPException(status_code=500, detail=str(e))


@login_router.get('/api/info_user')
def get_account_info(username: str = Depends(get_current_username)):
    if username is not None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE email=%s", username)
            acc_info = cursor.fetchone()
            acc_dict = dict(zip(account_keys, acc_info))
            return acc_dict
        except Exception as e:
            return {"code": "402", 'message': 'Error while getting user information.'}


# API endpoint to change password
@login_router.post('/api/change_password')
def change_password(request: PasswordChangeRequest, username: str = Depends(get_current_username)):
    if username is not None:
        email = request.email
        old_password = request.old_password
        new_password = request.new_password

        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email and old password are valid
            # cursor.execute("SELECT * FROM accounts WHERE email = ? AND password = ?", email, old_password)
            query = "SELECT * FROM accounts WHERE email=%s AND password=%s"
            cursor.execute(query, (email, old_password))
            row = cursor.fetchone()
            if row is None:
                return {"code": "403", 'message': 'Invalid email or password.'}

            # Update the new password in the database
            # cursor.execute("UPDATE accounts SET password = ? WHERE email = ?", new_password, email)
            query = "UPDATE accounts SET password = %s WHERE email = %s"
            cursor.execute(query, (new_password, email))
            conn.commit()

            return {"code": "200", 'message': 'Password updated successfully'}
        except Exception as e:
            raise HTTPException(status_code=500, detail='An error occurred') from e
        finally:
            cursor.close()
            conn.close()


@login_router.post('/api/list_account')
def user_product_like(owner: RoleAdmin, username: str = Depends(get_current_username)):
    if username is not None:
        try:
            if owner.page < 1:
                raise HTTPException(status_code=400,
                                    detail="Invalid page value. Page must be greater than or equal to 1.")
            if owner.limit < 1:
                raise HTTPException(status_code=400,
                                    detail="Invalid limit value. Limit must be greater than or equal to 1.")

                # Calculate the offset based on the page and limit
            offset = (owner.page - 1) * owner.limit
            if (owner.owner == "1"):
                conn = get_db_connection()
                cursor = conn.cursor()
                query = "SELECT id, username, email, profile_id, tax, active, created_account,type, mac_address, expiration_date, license, activation_date, interested_field, license_type FROM accounts ORDER BY id OFFSET %s ROWS FETCH NEXT %s ROWS ONLY"
                cursor.execute(query, (offset, owner.limit))
                rows = cursor.fetchall()
                rows_list = []
                for row in rows:
                    row_dict = dict(zip(admin_account_keys, row))
                    rows_list.append(row_dict)

                query_total = "SELECT COUNT(*) FROM accounts"
                cursor.execute(query_total)
                total = cursor.fetchall()[0][0]
                return {
                    "data": rows_list,
                    "total": total,
                    "page": owner.page,
                    "limit": owner.limit
                }
            else:
                raise HTTPException(status_code=400, detail="Dermission denied")

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail="Error checking email is existed")


def generate_serial(length):
    serial = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    return serial


@login_router.post('/api/actived_user')
def user_product_like(active: ActiveUser, username: str = Depends(get_current_username)):
    if username is not None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # cursor.execute("SELECT * FROM user_save_product WHERE profile_id = ?", profile_id)
            time_active_license = datetime.datetime.now()
            license_type = 0
            query = "UPDATE accounts SET active = %s, activation_date = %s, license_type = %s WHERE profile_id = %s"
            cursor.execute(query,
                           (active.active, time_active_license, license_type, active.profile_id))
            conn.commit()

            return {"code": "200", 'message': 'Active successfully'}

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail="Error checking email is existed")


def time_license(type: str, profile_id: str):
    day = 0
    if type == "1":
        day = 7
    if type == "2":
        day = 30
    if type == "3":
        day = 90
    if type == "4":
        day = 120
    if type == "5":
        day = 360

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT expiration_date FROM accounts where profile_id = %s"
    cursor.execute(query, (profile_id,))
    rows = cursor.fetchall()[0]
    time_now_active = datetime.datetime.now()
    if rows[0] is not None and rows[0] != "":
        expiration_current = datetime.datetime.strptime(rows[0], "%Y-%m-%d %H:%M:%S.%f")
        if time_now_active > expiration_current:
            time_expiration_license = time_now_active + datetime.timedelta(days=day)
        else:
            time_expiration_license = expiration_current + datetime.timedelta(days=day)
    else:
        time_expiration_license = time_now_active + datetime.timedelta(days=day)

    return time_now_active, time_expiration_license


@login_router.post('/api/license_user')
def user_product_like(license: LicenseUser, username: str = Depends(get_current_username)):
    if username is not None:
        try:
            time_active_license, time_expiration_license = time_license(license.license_type, license.profile_id)
            conn = get_db_connection()
            cursor = conn.cursor()

            query = "UPDATE accounts SET license = %s, license_type = %s, activation_date = %s, expiration_date = %s WHERE profile_id = %s"
            cursor.execute(query,
                           (generate_serial(16), license.license_type, time_active_license, time_expiration_license,
                            license.profile_id))
            conn.commit()

            return {"code": "200", 'message': 'Active successfully'}

        except Exception as e:
            raise HTTPException(status_code=500, detail="Error checking email is existed")


@login_router.post('/api/login')
def login(user: UserLogin):
    try:
        # Check if user exists in the database
        check_log = 0
        conn = get_db_connection()
        cursor = conn.cursor()
        # cursor.execute("SELECT COUNT(*) FROM accounts WHERE email=? AND password=?", user.email, user.password)
        query = "SELECT email FROM accounts WHERE email=%s AND password=%s"
        cursor.execute(query, (user.email, user.password))
        row = cursor.fetchone()
        result = row[0]
        if result is not None:
            token = generate_token(user.email)
            return {'Access_Token': token}
        else:
            check_log = 1
            raise HTTPException(status_code=401, detail='Invalid username or password')

    except Exception as e:
        if check_log == 1:
            raise HTTPException(status_code=401, detail='Invalid username or password')
        else:
            raise HTTPException(status_code=500, detail=str(e))


@login_router.post('/api/update_mac_address')
def update_mac_address(request: MacAddressChangeRequest, username: str = Depends(get_current_username)):
    if username is not None:
        email = request.email
        current_mac_address = request.current_mac_address
        new_mac_address = request.new_mac_address

        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email and old password are valid
            # cursor.execute("SELECT * FROM accounts WHERE email = ? AND password = ?", email, old_password)
            query = "SELECT * FROM accounts WHERE email=%s AND mac_address=%s"
            cursor.execute(query, (email, current_mac_address))
            row = cursor.fetchone()
            if row is None:
                return {"code": "403", 'message': 'Invalid email or mac address.'}

            # Update the new password in the database
            # cursor.execute("UPDATE accounts SET password = ? WHERE email = ?", new_password, email)
            query = "UPDATE accounts SET mac_address = %s WHERE email = %s"
            cursor.execute(query, (new_mac_address, email))
            conn.commit()

            return {"code": "200", 'message': 'Mac Address updated successfully'}
        except Exception as e:
            raise HTTPException(status_code=500, detail='An error occurred') from e
        finally:
            cursor.close()
            conn.close()
