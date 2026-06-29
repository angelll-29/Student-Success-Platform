from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: str
    role: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StudentProfileBase(BaseModel):
    roll_no: str
    department: str
    semester: int
    cgpa: str


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    resume_path: str | None = None

    class Config:
        from_attributes = True


class StudentProfileUpdate(BaseModel):
    roll_no: str
    department: str
    semester: int
    cgpa: str


class FacultyProfileBase(BaseModel):
    faculty_id: str
    department: str
    designation: str


class FacultyProfileCreate(FacultyProfileBase):
    pass


class FacultyProfileResponse(FacultyProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class CompanyBase(BaseModel):
    company_name: str
    job_role: str
    package: str
    location: str
    logo: str
    eligibility_cgpa: str
    deadline: str


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int

    class Config:
        from_attributes = True


class ApplicationBase(BaseModel):
    company_id: int
    application_date: str


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: int
    student_id: int
    status: str

    class Config:
        from_attributes = True


class ApplicationUpdate(BaseModel):
    status: str


class MyApplicationResponse(BaseModel):
    id: int
    company_id: int
    company_name: str
    job_role: str
    logo: str | None = None
    package: str
    location: str
    application_date: str
    status: str

    class Config:
        from_attributes = True