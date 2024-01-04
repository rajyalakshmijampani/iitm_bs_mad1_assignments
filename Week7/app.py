from flask import Flask,request,redirect
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Student(db.Model):
    __tablename__='student'
    student_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    roll_number=db.Column(db.String,unique=True,nullable=False)
    first_name=db.Column(db.String,nullable=False)
    last_name=db.Column(db.String)
    courses=db.relationship("Course",secondary='enrollments')

class Course(db.Model):
    __tablename__='course'
    course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_code=db.Column(db.String,unique=True,nullable=False)
    course_name=db.Column(db.String,nullable=False)
    course_description=db.Column(db.String)

class Enrollments(db.Model):
    __tablename__='enrollments'
    enrollment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    estudent_id=db.Column(db.Integer,db.ForeignKey("student.student_id"),nullable=False)
    ecourse_id=db.Column(db.Integer,db.ForeignKey("course.course_id"),nullable=False)

@app.route("/",methods=["GET"])
def student_home():
    students=Student.query.all()
    if students==[]:
        return render_template("no_students.html")
    else:
        return render_template("students_list.html",students=students)

@app.route("/student/create",methods=["GET","POST"])
def student_create():
    if request.method=="GET":
        return render_template("create_student.html")
    
    elif request.method=="POST":
        roll_number=request.form.get("roll")
        first_name=request.form.get("f_name")
        last_name=request.form.get("l_name")

        student=Student.query.filter_by(roll_number=roll_number).first()

        if student:
            return render_template("student_exists.html")
        else:
            try:
                new_student=Student(roll_number=roll_number,first_name=first_name,last_name=last_name)
                db.session.add(new_student)
                db.session.flush()
                sid=new_student.student_id
                
            except:
                db.session.rollback()
                return render_template("error.html")
            else:
                db.session.commit()
                return redirect("/")
            
@app.route("/student/<int:student_id>/update",methods=["GET","POST"])
def student_update(student_id):
    student=Student.query.filter_by(student_id=student_id).first()
    courses=Course.query.all()

    if request.method=="GET":
        return render_template("update_student_details.html",student=student,courses=courses)
    elif request.method=="POST":
        first_name=request.form.get("f_name")
        last_name=request.form.get("l_name")
        course_id=request.form.get("course")

        try:
            student.first_name=first_name
            student.last_name=last_name
            new_enrollment=Enrollments(estudent_id=student_id,ecourse_id=course_id)
            db.session.add(new_enrollment)
        except:
            db.session.rollback()
            return render_template("error.html")
        else:
            db.session.commit()
            return redirect("/")

@app.route("/student/<int:student_id>/delete", methods = ["GET"])
def student_delete(student_id):
    if request.method == "GET":
        try:
            Student.query.filter_by(student_id = student_id).delete()
            Enrollments.query.filter_by(estudent_id = student_id).delete()
            
        except:
            db.session.rollback()
            return render_template("error.html")
        else:
            db.session.commit()
            return redirect('/')


@app.route("/student/<int:student_id>", methods = ["GET"])
def get_student_details(student_id):
    if request.method == "GET":
        student_details = Student.query.filter_by(student_id = student_id).first()
        course_ids=Enrollments.query.with_entities(Enrollments.ecourse_id).filter_by(estudent_id = student_id).all()
        course_ids = [cid for cid, in course_ids] #To flatten the tuples returned by with_entities
        courses=[]
        for cid in course_ids:
            courses.append(Course.query.get(cid))
        return render_template("personal_details.html", student_details = student_details, courses = courses)

@app.route("/student/<int:student_id>/withdraw/<int:course_id>",methods=["GET"])
def withdraw(student_id,course_id):
    if request.method=="GET":
        try:
            print('Student id is ',student_id,'course id is',course_id)
            Enrollments.query.filter_by(estudent_id = student_id,ecourse_id=course_id).delete()
        except:
            db.session.rollback()
            return render_template("error.html")
        else:
            db.session.commit()
            return redirect('/')

@app.route("/courses",methods=["GET"])
def course_home():
    if request.method=="GET":
        courses=Course.query.all()
        if courses==[]:
            return render_template("no_courses.html")
        else:
            return render_template("courses_list.html",courses=courses)
        
@app.route("/course/create",methods=["GET","POST"])
def course_create():
    if request.method=="GET":
        return render_template("create_course.html")
    
    elif request.method=="POST":
        course_code=request.form.get("code")
        course_name=request.form.get("c_name")
        course_description=request.form.get("desc")

        course=Course.query.filter_by(course_code=course_code).first()

        if course:
            return render_template("course_exists.html")
        else:
            try:
                new_course=Course(course_code=course_code,course_name=course_name,course_description=course_description)
                db.session.add(new_course)
                db.session.flush()
                cid=new_course.course_id
                
            except:
                db.session.rollback()
                return render_template("error.html")
            else:
                db.session.commit()
                return redirect("/courses")
            
@app.route("/course/<int:course_id>/update",methods=["GET","POST"])
def course_update(course_id):
    course=Course.query.filter_by(course_id=course_id).first()

    if request.method=="GET":
        return render_template("update_course_details.html",course=course)
    elif request.method=="POST":
        course_name=request.form.get("c_name")
        course_description=request.form.get("desc")

        try:
            course.course_name=course_name
            course.course_description=course_description
        except:
            db.session.rollback()
            return render_template("error.html")
        else:
            db.session.commit()
            return redirect("/courses")
        
@app.route("/course/<int:course_id>/delete", methods = ["GET"])
def course_delete(course_id):
    if request.method == "GET":
        try:
            Course.query.filter_by(course_id = course_id).delete()            
        except:
            db.session.rollback()
            return render_template("error.html")
        else:
            db.session.commit()
            return redirect('/')
        
@app.route("/course/<int:course_id>", methods = ["GET"])
def get_course_details(course_id):
    if request.method == "GET":
        course = Course.query.filter_by(course_id = course_id).first()
        student_ids=Enrollments.query.with_entities(Enrollments.estudent_id).filter_by(ecourse_id = course_id).all()
        student_ids = [sid for sid, in student_ids] #To flatten the tuples returned by with_entities
        students=[]
        for sid in student_ids:
            students.append(Student.query.get(sid))
        return render_template("course_details.html", course = course, students = students)


if __name__=="__main__":
    app.debug=True
    app.run()