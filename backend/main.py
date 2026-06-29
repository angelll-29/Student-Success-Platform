from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from database import get_db, engine, Base
from models import (
    User,
    StudentProfile,
    FacultyProfile,
    Company,
    Application,
    Student,
    SemesterResult
)
from schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    StudentProfileCreate,
    StudentProfileResponse,
    StudentProfileUpdate,
    FacultyProfileCreate,
    FacultyProfileResponse,
    CompanyCreate,
    CompanyResponse,
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    MyApplicationResponse
)
from security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    require_role
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Success Platform"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Backend Running"}


@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login", response_model=Token)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/me")
def get_current_user(
    authorization: str = Header(None)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    user_data = verify_token(token)

    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    return user_data


def get_logged_in_user(
    authorization: str,
    db: Session
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    user_data = verify_token(token)

    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    user = (
        db.query(User)
        .filter(User.email == user_data["email"])
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@app.get("/student/me")
def get_student_me(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(
        authorization,
        db
    )

    student = (
        db.query(Student)
        .filter(Student.email == current_user.email)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return student
    

@app.post(
    "/student-profile",
    response_model=StudentProfileResponse
)
def create_student_profile(
    profile: StudentProfileCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    
    current_user = get_logged_in_user(
        authorization,
        db
    )

    existing_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
        )
        
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
            )

    student_profile = StudentProfile(
        user_id=current_user.id,
        roll_no=profile.roll_no,
        department=profile.department,
        semester=profile.semester,
        cgpa=profile.cgpa
    )

    db.add(student_profile)
    db.commit()
    db.refresh(student_profile)

    return student_profile


@app.get(
    "/student-profile/{profile_id}",
    response_model=StudentProfileResponse
)
def get_student_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):

    student_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.id == profile_id)
        .first()
    )

    if not student_profile:
        raise HTTPException(
            status_code=404,
            detail="Student Profile Not Found"
        )

    return student_profile


@app.put(
    "/student-profile/{profile_id}",
    response_model=StudentProfileResponse
)
def update_student_profile(
    profile_id: int,
    profile: StudentProfileUpdate,
    db: Session = Depends(get_db)
):

    student_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.id == profile_id)
        .first()
    )

    if not student_profile:
        raise HTTPException(
            status_code=404,
            detail="Student Profile Not Found"
        )

    student_profile.roll_no = profile.roll_no
    student_profile.department = profile.department
    student_profile.semester = profile.semester
    student_profile.cgpa = profile.cgpa

    db.commit()
    db.refresh(student_profile)

    return student_profile


@app.delete("/student-profile/{profile_id}")
def delete_student_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):

    student_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.id == profile_id)
        .first()
    )

    if not student_profile:
        raise HTTPException(
            status_code=404,
            detail="Student Profile Not Found"
        )

    db.delete(student_profile)

    db.commit()

    return {
        "message": "Student Profile Deleted Successfully"
    }


@app.post(
    "/faculty-profile",
    response_model=FacultyProfileResponse
)
def create_faculty_profile(
    profile: FacultyProfileCreate,
    db: Session = Depends(get_db)
):

    faculty_profile = FacultyProfile(
        user_id=1,
        faculty_id=profile.faculty_id,
        department=profile.department,
        designation=profile.designation
    )

    db.add(faculty_profile)

    db.commit()

    db.refresh(faculty_profile)

    return faculty_profile


@app.get(
    "/faculty-profile/{profile_id}",
    response_model=FacultyProfileResponse
)
def get_faculty_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):

    faculty_profile = (
        db.query(FacultyProfile)
        .filter(FacultyProfile.id == profile_id)
        .first()
    )

    if not faculty_profile:
        raise HTTPException(
            status_code=404,
            detail="Faculty Profile Not Found"
        )

    return faculty_profile


@app.put(
    "/faculty-profile/{profile_id}",
    response_model=FacultyProfileResponse
)
def update_faculty_profile(
    profile_id: int,
    profile: FacultyProfileCreate,
    db: Session = Depends(get_db)
):

    faculty_profile = (
        db.query(FacultyProfile)
        .filter(FacultyProfile.id == profile_id)
        .first()
    )

    if not faculty_profile:
        raise HTTPException(
            status_code=404,
            detail="Faculty Profile Not Found"
        )

    faculty_profile.faculty_id = profile.faculty_id
    faculty_profile.department = profile.department
    faculty_profile.designation = profile.designation

    db.commit()
    db.refresh(faculty_profile)

    return faculty_profile


@app.delete("/faculty-profile/{profile_id}")
def delete_faculty_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):

    faculty_profile = (
        db.query(FacultyProfile)
        .filter(FacultyProfile.id == profile_id)
        .first()
    )

    if not faculty_profile:
        raise HTTPException(
            status_code=404,
            detail="Faculty Profile Not Found"
        )

    db.delete(faculty_profile)

    db.commit()

    return {
        "message": "Faculty Profile Deleted Successfully"
    }


@app.post(
    "/companies",
    response_model=CompanyResponse
)
def create_company(
    company: CompanyCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    token = authorization.replace(
        "Bearer ",
        ""
    )

    print("Authorization Header:", authorization)
    print("Extracted Token:", token)

    user_data = verify_token(token)
    
    print("User Data:", user_data)

    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    require_role(
        user_data,
        ["admin", "placement"]
    )

    new_company = Company(
        company_name=company.company_name,
        job_role=company.job_role,
        package=company.package,
        location=company.location,
        logo=company.logo,
        eligibility_cgpa=company.eligibility_cgpa,
        deadline=company.deadline
    )

    db.add(new_company)

    db.commit()

    db.refresh(new_company)

    return new_company


@app.get(
    "/companies",
    response_model=list[CompanyResponse]
)
def get_companies(
    search: str = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):

    query = db.query(Company)

    if search:
        query = query.filter(
            Company.company_name.ilike(f"%{search}%")
        )

    companies = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return companies


@app.get(
    "/companies/{company_id}",
    response_model=CompanyResponse
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company Not Found"
        )

    return company


@app.put(
    "/companies/{company_id}",
    response_model=CompanyResponse
)
def update_company(
    company_id: int,
    company_data: CompanyCreate,
    db: Session = Depends(get_db)
):

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company Not Found"
        )

    company.company_name = company_data.company_name
    company.job_role = company_data.job_role
    company.package = company_data.package
    company.location = company_data.location
    company.logo = company_data.logo
    company.eligibility_cgpa = company_data.eligibility_cgpa
    company.deadline = company_data.deadline

    db.commit()
    db.refresh(company)

    return company


@app.delete("/companies/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db)
):

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company Not Found"
        )

    db.delete(company)

    db.commit()

    return {
        "message": "Company Deleted Successfully"
    }


@app.post(
    "/apply",
    response_model=ApplicationResponse
)
def apply_for_company(
    application: ApplicationCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    current_user = get_logged_in_user(
        authorization,
        db
    )

    existing_application = (
        db.query(Application)
        .filter(
            Application.student_id == current_user.id,
            Application.company_id == application.company_id
            )
            .first()
    )

    if existing_application:
        raise HTTPException(
            status_code=400,
            detail="You have already applied to this company"
        )

    new_application = Application(
        student_id=current_user.id,
        company_id=application.company_id,
        application_date=application.application_date,
        status="Applied"
    )

    db.add(new_application)

    db.commit()

    db.refresh(new_application)

    return new_application


@app.get(
    "/my-applications",
    response_model=list[MyApplicationResponse]
)
def get_my_applications(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(
        authorization,
        db
    )

    applications = (
        db.query(Application, Company)
        .join(
            Company,
            Application.company_id == Company.id
        )
        .filter(Application.student_id == current_user.id)
        .all()
    )

    result = []

    for application, company in applications:
        result.append({
            "id": application.id,
            "company_id": company.id,
            "company_name": company.company_name,
            "job_role": company.job_role,
            "logo": company.logo,
            "package": company.package,
            "location": company.location,
            "application_date": application.application_date,
            "status": application.status,
        })

    return result


@app.get(
    "/applications/{application_id}",
    response_model=ApplicationResponse
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application Not Found"
        )

    return application


@app.put(
    "/applications/{application_id}",
    response_model=ApplicationResponse
)
def update_application(
    application_id: int,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application Not Found"
        )

    application.status = application_data.status

    db.commit()
    db.refresh(application)

    return application


@app.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application Not Found"
        )

    db.delete(application)

    db.commit()

    return {
        "message": "Application Deleted Successfully"
    }


@app.get("/test-header")
def test_header(
    authorization: str = Header(None)
):
    return {
        "authorization": authorization
    }
