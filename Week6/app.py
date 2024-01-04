
from flask import Flask, request, redirect
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from validation import NotFoundError, BusineesValidationError, BadRequest
import json
        
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///api_database.sqlite3"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()
db.init_app(app)
api = Api(app)
app.app_context().push()

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True,nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    courses = db.relationship('Course', secondary = 'enrollment')


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)


class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)


output_course_fields = {
    "course_id": fields.Integer,
    "course_name": fields.String,
    "course_code": fields.String,
    "course_description": fields.String
}

course_parser = reqparse.RequestParser()
course_parser.add_argument('course_name')
course_parser.add_argument('course_code')
course_parser.add_argument('course_description')

class CourseAPI(Resource):
    @marshal_with(output_course_fields)
    def get(self, course_id):
        course = db.session.query(Course).filter(Course.course_id == course_id).first()
        if course:
            return course
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(output_course_fields)
    def put(self, course_id):
        course = db.session.query(Course).filter(Course.course_id == course_id).first()
        if course:
            pass
        else:
            raise NotFoundError(status_code=404)

        args = course_parser.parse_args()
        course_name = args.get("course_name", None)
        course_code = args.get("course_code", None)
        course_description = args.get("course_description")
        if course_name is None:
            raise BusineesValidationError(status_code=400, error_code="COURSE001", error_message="Course Name is required")
        
        if course_code is None:
            raise BusineesValidationError(status_code=400, error_code="COURSE002", error_message="Course Code is required")

        course.course_name = course_name
        course.course_code = course_code
        course.course_description = course_description
        db.session.commit()
        return course
    
    def delete(self, course_id):
        course = db.session.query(Course).filter(Course.course_id == course_id).first()
        if course is  None:
            raise NotFoundError(status_code=404)
        else:
            db.session.delete(course)
            db.session.commit()
        return "",200

    @marshal_with(output_course_fields)
    def post(self):
        args = course_parser.parse_args()
        course_name = args.get("course_name", None)
        course_code = args.get("course_code", None)
        course_description = args.get("course_description")

        if course_name is None:
            raise BusineesValidationError(status_code=400, error_code="COURSE001", error_message="Course Name is required")
        
        if course_code is None:
            raise BusineesValidationError(status_code=400, error_code="COURSE002", error_message="Course Code is required")

        course = db.session.query(Course).filter(Course.course_code == course_code).first()

        if course:
            raise BadRequest(status_code=409)

        new_course = Course(course_code = course_code, course_description = course_description, course_name = course_name)
        db.session.add(new_course)
        db.session.commit()
        return new_course,201


output_student_fields = {
    "student_id": fields.Integer,
    "first_name": fields.String,
    "last_name": fields.String,
    "roll_number": fields.String
}

student_parser = reqparse.RequestParser()
student_parser.add_argument('first_name')
student_parser.add_argument('last_name')
student_parser.add_argument('roll_number')

class StudentAPI(Resource):
    @marshal_with(output_student_fields)
    def get(self, student_id):
        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student:
            return student
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(output_student_fields)
    def put(self, student_id):
        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student:
            pass
        else:
            raise NotFoundError(status_code=404)

        args = student_parser.parse_args()
        first_name = args.get("first_name", None)
        roll_number = args.get("roll_number", None)
        last_name = args.get("last_name")
        if  roll_number is None:
            raise BusineesValidationError(status_code=400, error_code="STUDENT001", error_message="Roll Number is required")
        
        if first_name is None:
            raise BusineesValidationError(status_code=400, error_code="STUDENT002", error_message="First Name is required")

        student.last_name = last_name
        student.first_name = first_name
        student.roll_number = roll_number
        db.session.commit()
        return student
    
    def delete(self, student_id):
        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student is None:
            raise NotFoundError(status_code=404)
        else:
            db.session.delete(student)
            db.session.commit()
        return "",200

    @marshal_with(output_student_fields)
    def post(self):
        args = student_parser.parse_args()
        first_name = args.get("first_name", None)
        roll_number = args.get("roll_number", None)
        last_name = args.get("last_name")
        if  roll_number is None:
            raise BusineesValidationError(status_code=400, error_code="STUDENT001", error_message="Roll Number is required")
        
        if first_name is None:
            raise BusineesValidationError(status_code=400, error_code="STUDENT002", error_message="First Name is required")

        student = db.session.query(Student).filter(Student.roll_number == roll_number).first()

        if student:
            raise BadRequest(status_code=409)

        new_student = Student(roll_number = roll_number, first_name = first_name, last_name = last_name)
        db.session.add(new_student)
        db.session.commit()
        return new_student,201

output_enrollment_fields = {
    "enrollment_id": fields.Integer,
    "student_id": fields.Integer,
    "course_id": fields.Integer
}

enrollment_parser = reqparse.RequestParser()
enrollment_parser.add_argument('course_id')

class Student_CourseAPI(Resource):
    @marshal_with(output_enrollment_fields)
    def get(self, student_id):
        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student is None:
            raise BusineesValidationError(status_code=400, error_code="ENROLLMENT002", error_message="Student does not exist")

        enrollments = db.session.query(Enrollment).filter(Enrollment.student_id == student_id).all()
        if enrollments:
            return enrollments
        else:
            raise NotFoundError(status_code=404)

    def delete(self, student_id, course_id):
        course = db.session.query(Course).filter(Course.course_id == course_id).first()
        if course is None:
            raise BusineesValidationError(status_code=400, error_code="ENROLLMENT001", error_message="Course does not exist")
        
        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student is None:
            raise BusineesValidationError(status_code=400, error_code="ENROLLMENT002", error_message="Student does not exist")

        enrollments = db.session.query(Enrollment).filter(Enrollment.student_id == student_id).all()
        if enrollments:
            enrolled = db.session.query(Enrollment).filter((Enrollment.course_id == course_id) & (Enrollment.student_id == student_id)).first()
            db.session.delete(enrolled)
            db.session.commit()
        else:
            raise NotFoundError(status_code=404)
        return "",200

    @marshal_with(output_enrollment_fields)
    def post(self,student_id):
        args = enrollment_parser.parse_args()
        course_id = args.get("course_id")
        course = db.session.query(Course).filter(Course.course_id == course_id).first()
        if course is None:
            raise BusineesValidationError(status_code=400, error_code="ENROLLMENT001", error_message="Course does not exist")

        student = db.session.query(Student).filter(Student.student_id == student_id).first()
        if student is None:
            raise NotFoundError(status_code=404)
        

        new_enrollment = Enrollment(student_id = student_id, course_id = course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        return [new_enrollment],201

api.add_resource(CourseAPI,"/api/course","/api/course/<int:course_id>")
api.add_resource(StudentAPI,"/api/student","/api/student/<int:student_id>")
api.add_resource(Student_CourseAPI,"/api/student/<int:student_id>/course/<int:course_id>","/api/student/<int:student_id>/course")
if __name__== "__main__":
    app.run(debug=True)