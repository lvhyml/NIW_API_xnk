# Configure SQL Server connection
server = '45.118.144.25'
database = 'dev_XuatNhapKhau'
username = 'xnk'
password = 'XuatNhapKhau@2023'
driver = '{ODBC Driver 18 for SQL Server}'

# openai config
openai_api_key = "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"  ## key tai khoan NIW
chatgpt_prompt = "trích xuất thông tin hàng hóa từ đoạn văn bản"
chatgpt_format = "Tên hàng hóa| Loại hàng| Hãng sản xuất| Chất liệu | Chiều dài | Chiều rộng | Chiều cao | Cân nặng | Tình trạng hàng (mới hay cũ)"

# json_keys
account_keys = ["id", "username", "phone", "email", "country", "password", "profile_id", "image", "address", "sex",
                "tax", "owner", "active", "created_account", "type", "mac_address", "expiration_date", "license",
                "activation_date", "interested_field", "license_type", "count_search"]
transaction_keys = ["Id", "So_TK_VNACCS", "Ma_PLTT_SC", "Ma_LH", "Ma_HQ", "Ten_HQ", "Ngay_DK", "Ma_DN", "Ten_DN",
                    "Don_vi_Doi_Tac", "Duong_Xa", "Quan_Huyen", "Tinh_Thanh_pho", "Quoc_gia", "Nuoc_NK",
                    "Ma_Cang_Dich_CC",
                    "Ten_Cang_Dich_CC", "So_GP_1", "Ghi_Chu", "Ma_Hang_KB", "Ten_Hang", "Ten_San_Pham", "Chat_lieu",
                    "Chieu_dai", "Chieu_rong", "Chieu_cao", "Trang_Thai_San_Pham", "Luong", "Ma_DVT", "Ten_DVT",
                    "Tri_Gia_KB", "DGia_KB", "TS_XNK", "Thue_XNK", "Ma_Don_Vi_Uy_Thac", "Ten_DV_Uy_Thac",
                    "Tri_Gia_TT_S"]
chatgpt_keys = ["productname", "producttype", "brand", "material", "lenght", "width", "height", "weight", "status"]
profile_id_search_keys = ["username", "phone", "email", "country", "profile_id", "image", "address", "sex", "tax",
                          "owner"]
product_keys = ["hscode", "name", "tax_code", "country", "length", "width", "height", "status", "khoi_luong",
                "gia_tri", "ngay_dk", "don_vi_doi_tac", "gia_sp", "technical_standards", "tags", "description",
                "material", "profile_id", "price", "size", "id", "image_url"]

company_importer_keys = ["id", "ten_DN", "ten_quoc_te", "ma_so_thue", "dia_chi", "nguoi_dai_dien", "dien_thoai",
                         "ngay_DK", "nganh_nghe_chinh", "tinh_trang_HD", "sdt_khac", "website", "linkedin"]
company_exporter_keys = ["id", "ten_DN", "ten_quoc_te", "ma_so_thue", "dia_chi", "nguoi_dai_dien", "dien_thoai",
                         "ngay_DK", "nganh_nghe_chinh", "tinh_trang_HD", "sdt_khac", "website", "linkedin"]

product_like_keys = ["id", "profile_id", "product_id"]
count_search_user_keys = ["profile_id", "count_search"]

admin_account_keys = ["id", "username", "email", "profile_id", "tax", "active", "created_account", "type",
                      "mac_address", "expiration_date", "license",
                      "activation_date", "interested_field", "license_type"]
transaction_count_user_keys = ["transaction", "last_trading_date"]

# product dimension search boundary
boundary = 10
