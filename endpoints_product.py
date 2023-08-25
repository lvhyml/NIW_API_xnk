import os
import datetime
from fastapi import APIRouter
from fastapi import UploadFile, File, Form
from connect_db import get_db_connection
from models import SearchHscodeRequest, ProfileCompanyRequest, \
    SaveProductRequest, SearchFieldRequest, SearchFilterRequest, SearchTransactionRequest, \
    ProductUserLike, UpdateProductAddRequest
from config import product_keys, company_importer_keys, company_exporter_keys, transaction_count_user_keys
from fastapi import FastAPI, HTTPException, Depends
from endpoints_login import get_current_username

product_router = APIRouter()


# endpoints to get all product
@product_router.get("/api/get_all_product")
def get_products(page: int = 1, limit: int = 20, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        if page < 1:
            # pass
            raise HTTPException(status_code=400, detail="Invalid page value. Page must be greater than or equal to 1.")
        if limit < 1:
            # pass
            raise HTTPException(status_code=400,
                                detail="Invalid limit value. Limit must be greater than or equal to 1.")

        # Calculate the offset based on the page and limit
        offset = (page - 1) * limit

        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Retrieve the rows using a SQL query with paging and offset
            # query = f"SELECT * FROM products ORDER BY id OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            query = "SELECT * FROM products ORDER BY id OFFSET %s ROWS FETCH NEXT %s ROWS ONLY"
            cursor.execute(query, (offset, limit))
            # cursor.execute(query)
            rows = cursor.fetchall()
            # Convert the rows into a list of dictionaries
            rows_list = []
            for row in rows:
                row_dict = dict(zip(product_keys, row))
                rows_list.append(row_dict)
            # Return the rows as JSON
            query_total = "SELECT COUNT(*) FROM products"
            cursor.execute(query_total)
            total = cursor.fetchall()[0][0]
            return {
                "data": rows_list,
                "total": total,
                "page": page,
                "limit": limit
            }

        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


# API endpoint to search HS code
@product_router.post('/api/search_hscode')
def search_hs_code(request: SearchHscodeRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        hs_code = request.hs_code
        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # cursor.execute("SELECT * FROM products WHERE hscode = ?", hs_code)
            query = "SELECT * FROM products WHERE hscode = %s"
            cursor.execute(query, (hs_code,))
            query_result = cursor.fetchall()

            # Convert the rows into a list of dictionaries
            product_list = []
            for product in query_result:
                product_dict = dict(zip(product_keys, product))
                product_list.append(product_dict)

            # Return the rows as JSON
            return product_list
        except Exception as e:
            return {"code": "406", 'message': 'Error while getting product information.'}
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


# API endpoint to search dimension
# @product_router.post('/api/search_dimension')
# def search_dimension(request: SearchDimensionRequest):
#     productname = request.productname.replace(" ", " %") + "%"
#
#     # Create a database connection
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     try:
#         # Extract the values from the request
#         width = float(request.width) if request.width else None
#         length = float(request.length) if request.length else None
#
#         # Build the SQL query dynamically based on the provided values
#         query = "SELECT * FROM products WHERE productname LIKE ?"
#         params = [productname]
#
#         if width is not None:
#             query += " AND width > ? AND width < ?"
#             params.extend([width - boundary, width + boundary])
#
#         if length is not None:
#             query += " AND length > ? AND length < ?"
#             params.extend([length - boundary, length + boundary])
#
#         # Execute the SQL query
#         cursor.execute(query, params)
#         query_result = cursor.fetchall()
#
#         # Convert the rows into a list of dictionaries
#         product_list = []
#         for product in query_result:
#             product_dict = dict(zip(product_keys, product))
#             product_list.append(product_dict)
#
#         # Return the rows as JSON
#         return product_list
#     except Exception as e:
#         return {"code": "406", 'message': 'Error while getting product information.'}
#     finally:
#         # Close the cursor and database connection
#         cursor.close()
#         conn.close()


def Convert(string):
    li = list(string.split(","))
    return li


@product_router.post('/api/profile_contacts')
def profile_contacts(request: ProfileCompanyRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        conn = get_db_connection()
        cursor = conn.cursor()
        if request.type == "importer":
            tax_code = request.tax_code
            tax_code_list = Convert(tax_code)
            # Create a database connection
            try:
                company_list = []
                for code in tax_code_list:
                    # cursor.execute("SELECT TOP(1) * FROM importer_contact WHERE ma_so_thue = ?", code.strip())
                    query = "SELECT TOP(1) * FROM data_company WHERE ma_so_thue = %s"
                    cursor.execute(query, (code.strip(),))
                    query_result = cursor.fetchall()
                    # Convert the rows into a list of dictionaries
                    for contact in query_result:
                        product_dict = dict(zip(company_importer_keys, contact))
                        company_list.append(product_dict)
                # Return the rows as JSON
                return company_list
            except Exception as e:
                return {"code": "406", 'message': 'Error while getting product information.'}
            finally:
                # Close the cursor and database connection
                cursor.close()
                conn.close()
        elif request.type == "exporter":
            try:
                company_list = []
                offset = (request.page - 1) * request.limit
                query = "SELECT don_vi_doi_tac FROM products WHERE id = %s"
                cursor.execute(query, (request.id,))
                query_result = cursor.fetchone()[0]
                query_result = query_result.split(',')
                for item in query_result[offset:request.limit]:
                    query = "SELECT * FROM data_company WHERE ten_DN = %s"
                    cursor.execute(query, (item.strip(),))
                    query_result = cursor.fetchall()
                    # Convert the rows into a list of dictionaries
                    if len(query_result) > 0:
                        for contact in query_result:
                            product_dict = dict(zip(company_importer_keys, contact))
                            company_list.append(product_dict)
                    else:
                        q = "SELECT TOP(1) Don_vi_Doi_Tac, Duong_Xa, Quan_Huyen, TInh_Thanh_pho, Nuoc_NK FROM importer_transaction WHERE  Don_vi_Doi_Tac Like %s"
                        text = item + '%'
                        cursor.execute(q, (text.strip(),))
                        result = cursor.fetchall()[0]
                        result = list(result)
                        a = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
                        a[1] = result[0]
                        if result[1] is None:
                            result[1] = ""
                        if result[2] is None:
                            result[2] = ""
                        if result[3] is None:
                            result[3] = ""
                        if result[4] is None:
                            result[4] = ""
                        a[4] = result[1] + ', ' + result[2] + ', ' + result[3] + ', ' + result[4]
                        product_dict = dict(zip(company_exporter_keys, tuple(a)))
                        company_list.append(product_dict)
                return company_list
            except Exception as e:
                return {"code": "406", 'message': 'Error while getting product information.'}
            finally:
                cursor.close()
                conn.close()
            pass


@product_router.post('/api/transaction_info')
def transaction_info(request: SearchHscodeRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        hs_code = request.hs_code
        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # cursor.execute("SELECT * FROM products WHERE hscode = ?", hs_code)
            query = "SELECT * FROM products WHERE hscode = %s"
            cursor.execute(query, (hs_code,))
            query_result = cursor.fetchall()

            # Convert the rows into a list of dictionaries
            product_list = []
            for product in query_result:
                product_dict = dict(zip(product_keys, product))
                product_list.append(product_dict)

            # Return the rows as JSON
            return product_list
        except Exception as e:
            return {"code": "406", 'message': 'Error while getting product information.'}
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


@product_router.post('/api/search_field')
def search_field(request: SearchFieldRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        fields = request.interested_field.split(',')
        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            product_list = []
            for field in fields:
                query = "SELECT * FROM products WHERE name LIKE %s"
                name = '%' + field.replace(" ", "%") + '%'
                cursor.execute(query, (name.strip(),))
                query_result = cursor.fetchall()
                for product in query_result:
                    product_dict = dict(zip(product_keys, product))
                    product_list.append(product_dict)
            return product_list
        except Exception as e:
            return {"code": "406", 'message': 'Error while getting product information.'}
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


@product_router.post('/api/search_filter')
def search_filter(request: SearchFilterRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            is_check_len_status = 0
            is_check_len_interested_field = 0
            product_list = []
            if request.country is not None and request.country != "":
                a = ""
                for i in request.country.split(','):
                    if i != "":
                        a += '%[' + i + ']%'
                country = a
            else:
                country = None

            if request.status is not None and request.status != "":
                b = ""
                if len(request.status.split(',')) > 2:
                    for i in request.status.split(','):
                        if i != "":
                            b += '%[' + i + ']%'
                    status = b
                else:
                    is_check_len_status = 1
                    status = request.status.replace(",", "")
            else:
                status = None

            if request.interested_field is not None and request.interested_field != "":
                c = ""
                if len(request.interested_field.split(',')) > 2:
                    for i in request.interested_field.split(','):
                        if i != "":
                            c += '%[' + i + ']%'
                    interested_field = c
                else:
                    is_check_len_interested_field = 1
                    interested_field = request.interested_field.replace(",", "")
            else:
                interested_field = None

            query_result = ""

            if interested_field is not None and status is not None and country is not None:
                query = "SELECT * FROM products WHERE name LIKE %s AND country LIKE %s AND status LIKE %s"
                if is_check_len_status == 1:
                    query = "SELECT * FROM products WHERE name LIKE %s AND country LIKE %s AND status = %s"
                if is_check_len_interested_field == 1:
                    query = "SELECT * FROM products WHERE name = %s AND country LIKE %s AND status LIKE %s"
                if is_check_len_interested_field == 1 and is_check_len_status == 1:
                    query = "SELECT * FROM products WHERE name = %s AND country LIKE %s AND status = %s"
                cursor.execute(query, (interested_field.strip(), country, status))
                query_result = cursor.fetchall()

            elif interested_field is not None and status is not None:
                query = "SELECT * FROM products WHERE interested_field LIKE %s AND status LIKE %s"
                if is_check_len_status == 1:
                    query = "SELECT * FROM products WHERE interested_field LIKE %s AND status = %s"
                if is_check_len_interested_field == 1:
                    query = "SELECT * FROM products WHERE name = %s AND status LIKE %s"
                if is_check_len_interested_field == 1 and is_check_len_status == 1:
                    query = "SELECT * FROM products WHERE name = %s AND status = %s"
                cursor.execute(query, (interested_field.strip(), status))
                query_result = cursor.fetchall()

            elif interested_field is not None and country is not None:
                query = "SELECT * FROM products WHERE name LIKE %s AND country LIKE %s"
                if is_check_len_interested_field == 1:
                    query = "SELECT * FROM products WHERE name = %s AND country LIKE %s"
                cursor.execute(query, (interested_field.strip(), country))
                query_result = cursor.fetchall()

            elif status is not None and country is not None:
                query = "SELECT * FROM products WHERE country LIKE %s AND status like %s"
                if is_check_len_status == 1:
                    query = "SELECT * FROM products WHERE country LIKE %s AND status = %s"
                cursor.execute(query, (country, status))
                query_result = cursor.fetchall()

            elif status is not None:
                query = "SELECT * FROM products WHERE status like %s"
                if is_check_len_status == 1:
                    query = "SELECT * FROM products WHERE status = %s"
                cursor.execute(query, (status,))
                query_result = cursor.fetchall()


            elif country is not None:
                query = "SELECT * FROM products WHERE country LIKE %s"
                cursor.execute(query, (country,))
                query_result = cursor.fetchall()

            elif interested_field is not None:
                query = "SELECT * FROM products WHERE name LIKE %s"
                if is_check_len_interested_field == 1:
                    query = "SELECT * FROM products WHERE name = %s"
                cursor.execute(query, (interested_field.strip(),))
                query_result = cursor.fetchall()

            elif interested_field is None and status is None and country is None:
                query = "SELECT * FROM products"
                cursor.execute(query)
                query_result = cursor.fetchall()

            for product in query_result:
                product_dict = dict(zip(product_keys, product))
                product_list.append(product_dict)
            return product_list
        except Exception as e:
            return product_list
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


@product_router.post('/api/exporter_transaction_info')
def transaction_info(request: SearchTransactionRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        don_vi_doi_tac = request.don_vi_doi_tac
        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # cursor.execute("SELECT * FROM products WHERE hscode = ?", hs_code)
            query = "SELECT COUNT(*) FROM importer_transaction WHERE Don_vi_Doi_Tac = %s"
            cursor.execute(query, (don_vi_doi_tac,))
            query_result = cursor.fetchall()
            # Convert the rows into a list of dictionaries
            #   SELECT MAX(Ngay_DK) AS Ngay_DK FROM [dbo].[importer_transaction] where Don_vi_Doi_Tac='ALWAYS RICH INDUSTRIAL LTD.'
            q = "SELECT MAX(Ngay_DK) AS Ngay_DK FROM importer_transaction where Don_vi_Doi_Tac = %s"
            cursor.execute(q, (don_vi_doi_tac,))
            q_result = cursor.fetchall()
            result = query_result[0] + q_result[0]
            product_dict = dict(zip(transaction_count_user_keys, result))

            # Return the rows as JSON
            return product_dict
        except Exception as e:
            return {"code": "406", 'message': 'Error while getting product information.'}
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


@product_router.post('/api/importer_transaction_info')
def transaction_info(request: SearchTransactionRequest, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        don_vi_doi_tac = request.don_vi_doi_tac
        # Create a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # cursor.execute("SELECT * FROM products WHERE hscode = ?", hs_code)
            query = "SELECT COUNT(*) FROM importer_transaction WHERE Ten_DN = %s"
            cursor.execute(query, (don_vi_doi_tac,))
            query_result = cursor.fetchall()
            # Convert the rows into a list of dictionaries
            #   SELECT MAX(Ngay_DK) AS Ngay_DK FROM [dbo].[importer_transaction] where Don_vi_Doi_Tac='ALWAYS RICH INDUSTRIAL LTD.'
            q = "SELECT MAX(Ngay_DK) AS Ngay_DK FROM importer_transaction where Ten_DN = %s"
            cursor.execute(q, (don_vi_doi_tac,))
            q_result = cursor.fetchall()
            result = query_result[0] + q_result[0]
            product_dict = dict(zip(transaction_count_user_keys, result))

            # Return the rows as JSON
            return product_dict
        except Exception as e:
            return {"code": "406", 'message': 'Error while getting product information.'}
        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


# ===================================================================================================================
from typing import Optional
import datetime


@product_router.post('/api/add_product')
def add_product(hscode: Optional[str] = Form(None),
                name: Optional[str] = Form(None),
                tax_code: Optional[str] = Form(None),
                country: Optional[str] = Form(None),
                length: Optional[str] = Form(None),
                width: Optional[str] = Form(None),
                height: Optional[str] = Form(None),
                status: Optional[str] = Form(None),
                khoi_luong: Optional[str] = Form(None),
                gia_tri: Optional[str] = Form(None),
                ngay_dk: Optional[str] = Form(None),
                don_vi_doi_tac: Optional[str] = Form(None),
                gia_sp: Optional[str] = Form(None),
                images: list[UploadFile] = File(None),
                technical_standards: Optional[str] = Form(None),
                tags: Optional[str] = Form(None),
                description: Optional[str] = Form(None),
                material: Optional[str] = Form(None),
                profile_id: Optional[str] = Form(None),
                price: Optional[str] = Form(None),
                size: Optional[str] = Form(None),
                username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            image_list_url = []
            for image in images:
                image_data = image.file.read()
                image_filename = os.path.join("product_images", f"{name}_{image.filename}")
                with open(image_filename, "wb") as f:
                    f.write(image_data)
                image_list_url.append('http://45.118.146.36:7002/images' + image_filename.replace("product_images", ""))
            query = "INSERT INTO products (hscode, name, tax_code, country, length, width, height, status, khoi_luong, gia_tri, ngay_dk, don_vi_doi_tac, gia_sp, technical_standards, tags, description, material, profile_id, price, size, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (
                hscode, name, tax_code, country, length, width, height, status, khoi_luong, gia_tri, ngay_dk,
                don_vi_doi_tac, gia_sp, technical_standards, tags, description, material, profile_id, price, size,
                ', '.join(image_list_url)))
            conn.commit()

            return {"code": "200", 'message': 'Add product successfully'}

        except Exception as e:
            return {"code": "406", 'message': 'Error while getting product information.'}
        finally:
            cursor.close()
            conn.close()


IMAGE_FOLDER = "product_images"


@product_router.get("/get_image_product/")
async def get_image(product_id: str, profile_id: str, username: str = Depends(get_current_username)):
    if username is not None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT * FROM product_image WHERE profile_id = %s and product_id =%s"
            cursor.execute(query, (profile_id, product_id))
            images = []
            try:
                for row in cursor.fetchall():
                    image_id, product_id, file_name, profile_id = row
                    images.append('http://45.118.146.36:7002/images' + file_name.replace("product_images", ""))
                return images

            except Exception as e:
                return {"error": str(e)}
        finally:
            cursor.close()


from fastapi.responses import FileResponse
from pathlib import Path


@product_router.get("/images/{image_name}")
def get_image(image_name: str):
    image_path = Path(IMAGE_FOLDER) / image_name
    return FileResponse(image_path)


@product_router.post("/api/get_all_product_add")
def get_products_add(profile_id: ProductUserLike, username: str = Depends(get_current_username)):
    # Validate the input values
    if username is not None:
        if profile_id.page < 1:
            raise HTTPException(status_code=400, detail="Invalid page value. Page must be greater than or equal to 1.")
        if profile_id.limit < 1:
            raise HTTPException(status_code=400,
                                detail="Invalid limit value. Limit must be greater than or equal to 1.")

        offset = (profile_id.page - 1) * profile_id.limit

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM products WHERE profile_id = %s ORDER BY id OFFSET %s ROWS FETCH NEXT %s ROWS ONLY"
            cursor.execute(query, (profile_id.profile_id, offset, profile_id.limit))
            rows = cursor.fetchall()
            rows_list = []
            for row in rows:
                row_dict = dict(zip(product_keys, row))
                rows_list.append(row_dict)
            query_total = "SELECT COUNT(*) FROM products WHERE profile_id = %s"
            cursor.execute(query_total, (profile_id.profile_id,))
            total = cursor.fetchall()[0][0]
            return {
                "data": rows_list,
                "total": total,
                "page": profile_id.page,
                "limit": profile_id.limit
            }

        finally:
            # Close the cursor and database connection
            cursor.close()
            conn.close()


@product_router.post('/api/delete_products_add')
def delete_products_add(request: SaveProductRequest, username: str = Depends(get_current_username)):
    if username is not None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # cursor.execute("DELETE FROM user_save_product WHERE profile_id = ?", request.profile_id)
            query = "DELETE FROM products WHERE id = %s and profile_id = %s"
            cursor.execute(query, (request.product_id, request.profile_id))
            conn.commit()
            # file_path = os.path.join(IMAGE_FOLDER, file_name)
            # os.remove(file_path)
            # query = "DELETE FROM product_image WHERE product_id = %s and profile_id = %s"
            # cursor.execute(query, (request.product_id, request.profile_id))
            # conn.commit()
            return {"code": "200", 'message': 'Delete product successful.'}

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail="Error checking email is existed")


@product_router.post('/api/edit_products_add')
def edit_products_add(request: UpdateProductAddRequest, username: str = Depends(get_current_username)):
    if username is not None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # cursor.execute("DELETE FROM user_save_product WHERE profile_id = ?", request.profile_id)
            # UPDATE products SET password = %s WHERE email = %s
            query = "UPDATE products SET name = %s, price = %s, hscode = %d WHERE id = %s and profile_id = %s"
            cursor.execute(query, (request.name, request.price, request.hscode, request.product_id, request.profile_id))
            conn.commit()
            return {"code": "200", 'message': 'Update product successful.'}

        except Exception as e:
            # pass
            raise HTTPException(status_code=500, detail="Error checking email is existed")


@product_router.post('/api/update_add_product')
def update_add_product(profile_id: str = Form(),
                       product_id: int = Form(),
                       hscode: Optional[str] = Form(None),
                       name: Optional[str] = Form(None),
                       status: Optional[str] = Form(None),
                       image_url: Optional[str] = Form(None),
                       images: list[UploadFile] = File(None),
                       technical_standards: Optional[str] = Form(None),
                       tags: Optional[str] = Form(None),
                       description: Optional[str] = Form(None),
                       material: Optional[str] = Form(None),
                       price: Optional[str] = Form(None),
                       size: Optional[str] = Form(None),
                       username: str = Depends(get_current_username)):
    if username is not None:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            current_time = datetime.datetime.now()
            image_list_url = []
            print("=====1111111====", image_url)
            if image_url is not None:
                for i in image_url.split(','):
                    image_list_url.append(i)
            for image in images:
                image_data = image.file.read()
                image_filename = os.path.join("product_images", f"{name}_{image.filename}_{current_time}")
                with open(image_filename, "wb") as f:
                    f.write(image_data)
                image_list_url.append('http://45.118.146.36:7002/images' + image_filename.replace("product_images", ""))
            query = "UPDATE products SET hscode = %s, name = %s, status = %s, technical_standards = %s, tags = %s, description = %s, material = %s, price = %s, size = %s, image_url = %s WHERE profile_id = %s and id = %s"
            print("=========", image_list_url)
            cursor.execute(query, (hscode, name, status, technical_standards, tags, description, material, price, size,
                                   ', '.join(image_list_url), profile_id, product_id))
            conn.commit()
            print("=========", ', '.join(image_list_url))


            return {"code": "200", 'message': 'Add product successfully'}

        except Exception as e:
            return {"code": "406", 'message': 'Error while getting product information.'}
        finally:
            cursor.close()
            conn.close()
