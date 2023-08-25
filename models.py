from pydantic import BaseModel


# Define user model for registration
class UserRegistration(BaseModel):
    username: str
    password: str
    phone: str
    email: str
    country: str
    tax: str = None
    user_type: str
    mac_address: str
    interested_field: str = None


# Define user model for login
class UserLogin(BaseModel):
    email: str
    password: str
    mac_address: str = None


# Define request body model
class PasswordChangeRequest(BaseModel):
    email: str
    old_password: str
    new_password: str


class MacAddressChangeRequest(BaseModel):
    email: str
    current_mac_address: str
    new_mac_address: str


# Define request body model
class UserInfoRequest(BaseModel):
    email: str
    address: str
    phone_number: str
    nationality: str
    sex: str = None
    tax_number: str = None


class SearchTransactionRequest(BaseModel):
    don_vi_doi_tac: str


# Define request body model
class UpdateAvatarRequest(BaseModel):
    email: str
    image_url: str


# Define request body model
class ExtractInfoRequest(BaseModel):
    product_description: str


# Define request body model
class SearchHscodeRequest(BaseModel):
    hs_code: str


class SearchFieldRequest(BaseModel):
    interested_field: str


class SearchFilterRequest(BaseModel):
    country: str = None
    interested_field: str = None
    status: str = None


class TransactionInfoRequest(BaseModel):
    hs_code: str
    date: str


# Define request body model
class SearchDimensionRequest(BaseModel):
    productname: str
    length: str = None
    width: str = None


# Define request body model
class SearchProfileIdRequest(BaseModel):
    profile_id: str


class CountSearchUserRequest(BaseModel):
    profile_id: str
    count_search: str


class ActiveUser(BaseModel):
    profile_id: str
    active: str


class LicenseUser(BaseModel):
    profile_id: str
    license_type: str


class Item(BaseModel):
    code: str
    message: str


class ProductHscodeRequest(BaseModel):
    Ma_Hang_KB: str


class ProfileCompanyRequest(BaseModel):
    id: int
    tax_code: str
    type: str
    page: int = 1
    limit: int = 10


class SaveProductRequest(BaseModel):
    profile_id: str
    product_id: str


class ProductLikeRequest(BaseModel):
    id: str


class RoleAdmin(BaseModel):
    owner: str
    page: int = 1
    limit: int = 10


class ProductUserLike(BaseModel):
    profile_id: str
    page: int = 1
    limit: int = 20


class UpdateProductAddRequest(BaseModel):
    name: str
    price: str
    hscode: str
    profile_id: str
    product_id: str
