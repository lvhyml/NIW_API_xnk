from fastapi import APIRouter

from models import UserInfoRequest, UpdateAvatarRequest, SearchProfileIdRequest, SaveProductRequest, ProductUserLike, \
    CountSearchUserRequest
from connect_db import get_db_connection
from config import profile_id_search_keys, product_like_keys, product_keys, count_search_user_keys
from fastapi import FastAPI, HTTPException, Depends

from endpoints_login import get_current_username

user_router = APIRouter()


# API endpoint to edit user information
@user_router.put('/api/edit_user_info')
def edit_user_info(request: UserInfoRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        email = request.email
        address = request.address
        phone_number = request.phone_number
        nationality = request.nationality
        sex = request.sex
        tax_number = request.tax_number

        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email exists in the database
            # cursor.execute("SELECT * FROM accounts WHERE email = ?", email)
            query = "SELECT * FROM accounts WHERE email = %s"
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            if row is None:
                pass
                # raise HTTPException(status_code=404, detail='User not found')

            # Determine the appropriate column to update based on tax number or sex presence
            if tax_number:
                # If tax number is provided, set sex to NULL
                # cursor.execute(
                #     "UPDATE accounts SET address = ?, phone = ?, country = ?, sex = NULL, tax = ? WHERE email = ?",
                #     address, phone_number, nationality, tax_number, email)

                query = "UPDATE accounts SET address = %s, phone = %s, country = %s, sex = NULL, tax = %s WHERE email = %s"
                cursor.execute(query, (address, phone_number, nationality, tax_number, email))
            else:
                # If sex is provided, set tax number to NULL
                # cursor.execute(
                #     "UPDATE accounts SET address = ?, phone = ?, country = ?, sex = ?, tax = NULL WHERE email = ?",
                #     address, phone_number, nationality, sex, email)
                query = "UPDATE accounts SET address = %s, phone = %s, country = %s, sex = %s, tax = NULL WHERE email = %s"
                cursor.execute(query, (address, phone_number, nationality, sex, email))
            conn.commit()

            return {"code": "200", 'message': 'User information updated successfully'}
        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail='An error occurred') from e
        finally:
            cursor.close()
            conn.close()


# API endpoint to edit user avatar
@user_router.put('/api/update_avatar')
def update_avatar(request: UpdateAvatarRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        email = request.email
        image_url = request.image_url

        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email exists in the database
            # cursor.execute("SELECT * FROM accounts WHERE email = ?", email)
            query = "SELECT * FROM accounts WHERE email = %s"
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            if row is None:
                # pass
                raise HTTPException(status_code=404, detail='User not found')

            # cursor.execute("UPDATE accounts SET image = ? WHERE email = ?", image_url, email)
            query = "UPDATE accounts SET image = %s WHERE email = %s"
            cursor.execute(query, (image_url, email))
            conn.commit()

            return {'message': 'Avatar updated successfully'}
        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail='An error occurred') from e
        finally:
            cursor.close()
            conn.close()


@user_router.post('/api/delete_user')
def delete_user(request: SearchProfileIdRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "DELETE FROM accounts WHERE profile_id = %s"
            cursor.execute(query, (request.profile_id,))
            conn.commit()

            return {'code': 200, 'message': 'Avatar delete successfully'}
        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail='An error occurred') from e
        finally:
            cursor.close()
            conn.close()


# API endpoint to search user by profile id
@user_router.post('/api/search_profile_id')
def search_profile_id(request: SearchProfileIdRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        profile_id = request.profile_id

        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        columns = ", ".join(profile_id_search_keys)

        try:
            # query = f"SELECT {columns} FROM accounts WHERE profile_id = '{profile_id}'"
            query = "SELECT %s FROM accounts WHERE profile_id = %s"
            cursor.execute(query, (columns, profile_id))
            # cursor.execute(query)
            query_result = cursor.fetchone()

            # Convert the rows into a list of dictionaries
            user_dict = dict(zip(profile_id_search_keys, query_result))

            # Return the rows as JSON
            return user_dict
        except Exception as e:
            return {"code": "402", 'message': 'Error while getting user information.'}
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


@user_router.post('/api/user_save_product')
def user_save_product(request: SaveProductRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Insert user into the database
            conn = get_db_connection()
            cursor = conn.cursor()
            # cursor.execute(
            #     "INSERT INTO user_save_product (profile_id, product_id) "
            #     "VALUES (?, ?)",
            #     request.profile_id, request.product_id)
            query = "INSERT INTO user_save_product (profile_id, product_id) VALUES (%s, %s)"
            cursor.execute(query, (request.profile_id, request.product_id))
            conn.commit()

            return {"code": "200", 'message': 'Save successful.'}

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail="Error checking email is existed")


@user_router.post('/api/user_unsave_product')
def user_save_product(request: SaveProductRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # cursor.execute("DELETE FROM user_save_product WHERE profile_id = ?", request.profile_id)
            query = "DELETE FROM user_save_product WHERE product_id = %s"
            cursor.execute(query, (request.product_id,))
            conn.commit()
            return {"code": "200", 'message': 'UnSave successful.'}

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail="Error checking email is existed")


@user_router.post('/api/get_all_product_user_like')
def user_product_like(profile_id: ProductUserLike, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        try:
            if profile_id.page < 1:
                # pass
                raise HTTPException(status_code=400,
                                    detail="Invalid page value. Page must be greater than or equal to 1.")
            if profile_id.limit < 1:
                # pass
                raise HTTPException(status_code=400,
                                    detail="Invalid limit value. Limit must be greater than or equal to 1.")
            offset = (profile_id.page - 1) * profile_id.limit

            conn = get_db_connection()
            cursor = conn.cursor()
            # cursor.execute("SELECT * FROM user_save_product WHERE profile_id = ?", profile_id)
            query = "SELECT * FROM user_save_product WHERE profile_id = %s ORDER BY id OFFSET %s ROWS FETCH NEXT %s ROWS ONLY"
            cursor.execute(query, (profile_id.profile_id, offset, profile_id.limit))
            rows = cursor.fetchall()
            rows_list = []
            for row in rows:
                row_dict = dict(zip(product_like_keys, row))
                query_product = "SELECT * FROM products WHERE id = %s"
                cursor.execute(query_product, (row_dict['product_id'],))
                product = cursor.fetchone()
                product_dict = dict(zip(product_keys, product))
                rows_list.append(product_dict)

            query_total = "SELECT COUNT(*) FROM user_save_product WHERE profile_id = %s"
            cursor.execute(query_total, (profile_id.profile_id,))
            total = cursor.fetchall()[0][0]
            return {
                "data": rows_list,
                "total": total,
                "page": profile_id.page,
                "limit": profile_id.limit
            }

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail="Error checking email is existed")


@user_router.post('/api/count_search_user')
def count_search_user(request: CountSearchUserRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # UPDATE accounts SET image = %s WHERE email = %s
            query = "UPDATE accounts SET count_search = %s WHERE profile_id = %s"
            cursor.execute(query, (request.count_search, request.profile_id))
            conn.commit()

            return {'code': 200, 'message': 'Update count search successfully'}
        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail='An error occurred') from e
        finally:
            cursor.close()
            conn.close()


@user_router.post('/api/get_count_search_user')
def count_search_user(request: CountSearchUserRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # SELECT * FROM accounts WHERE email=%s AND password=%s
            query = "SELECT profile_id, count_search FROM accounts WHERE profile_id = %s"
            cursor.execute(query, (request.profile_id,))
            rows = cursor.fetchall()
            rows_list = []
            for row in rows:
                row_dict = dict(zip(count_search_user_keys, row))
                rows_list.append(row_dict)
            return rows_list

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail='An error occurred') from e
        finally:
            cursor.close()
            conn.close()

