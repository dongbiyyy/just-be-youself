from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------- Auth ----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department: str
    is_active: bool


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    email: EmailStr
    full_name: str = ""
    password: str = Field(min_length=6, max_length=128)
    role: str = "viewer"
    department: str = ""


# ---------------- Company ----------------
class CompanyBase(BaseModel):
    name: str
    credit_code: Optional[str] = None
    short_name: str = ""
    legal_representative: str = ""
    reg_capital: Optional[float] = None
    reg_capital_currency: str = "CNY"
    established_date: Optional[date] = None
    reg_address: str = ""
    business_scope: str = ""
    company_type: str = ""
    status: str = "active"
    parent_company_id: Optional[int] = None
    remark: str = ""


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    name: Optional[str] = None


class CompanyOut(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


# ---------------- Person ----------------
class PersonBase(BaseModel):
    name: str
    nationality: str = "中国"
    phone: str = ""
    email: str = ""
    gender: str = ""
    remark: str = ""


class PersonCreate(PersonBase):
    id_card: str = Field(min_length=6, max_length=32)


class PersonUpdate(PersonBase):
    name: Optional[str] = None
    id_card: Optional[str] = None


class PersonOut(PersonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_card_last4: str
    created_at: datetime
    updated_at: datetime


# ---------------- Position ----------------
class PositionBase(BaseModel):
    person_id: int
    company_id: int
    position_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    document_no: str = ""
    remark: str = ""


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    position_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    document_no: Optional[str] = None
    remark: Optional[str] = None


class PositionOut(PositionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    person_name: Optional[str] = None
    company_name: Optional[str] = None


# ---------------- Shareholding ----------------
class ShareholdingBase(BaseModel):
    company_id: int
    shareholder_type: str  # "person" | "company"
    shareholder_id: int
    ratio: Optional[float] = None
    amount: Optional[float] = None
    currency: str = "CNY"
    contribute_method: str = "货币"
    contribute_date: Optional[date] = None
    remark: str = ""


class ShareholdingCreate(ShareholdingBase):
    pass


class ShareholdingOut(ShareholdingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    shareholder_name: Optional[str] = None
    company_name: Optional[str] = None


# ---------------- Alert ----------------
class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kind: str
    severity: str
    title: str
    detail: str
    related_entity_type: str
    related_entity_id: Optional[int]
    status: str
    created_at: datetime


# ---------------- Search ----------------
class SearchHit(BaseModel):
    type: str  # company / person
    id: int
    name: str
    extra: str = ""
