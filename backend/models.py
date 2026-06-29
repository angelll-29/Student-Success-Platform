from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Numeric
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        nullable=False
    )

    roll_no = Column(String(50), nullable=False)
    department = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False)
    cgpa = Column(String(10))
    resume_path = Column(String(255), nullable=True)


class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(Integer, nullable=False)

    faculty_id = Column(String(50), nullable=False)

    department = Column(String(100), nullable=False)

    designation = Column(String(100), nullable=False)


class Company(Base):
    __tablename__ = "companies"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    company_name = Column(String(100), nullable=False)

    job_role = Column(String(100), nullable=False)

    package = Column(String(50), nullable=False)

    location = Column(String(100), nullable=True)
    
    logo = Column(String(255), nullable=True)

    eligibility_cgpa = Column(String(10), nullable=False)

    deadline = Column(String(50), nullable=False)


class Application(Base):
    __tablename__ = "applications"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    student_id = Column(Integer, nullable=False)

    company_id = Column(Integer, nullable=False)

    application_date = Column(String(50), nullable=False)

    status = Column(String(50), default="Applied")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    roll_no = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    course = Column(String(50), nullable=False)
    department = Column(String(50), nullable=False)
    current_year = Column(String(20), nullable=False)
    email = Column(String(100))
    phone = Column(String(15))


class SemesterResult(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    cgpa = Column(Numeric(3, 2), nullable=False)