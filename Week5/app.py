from flask import Flask,request,redirect
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
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
def home():
    students=Student.query.all()
    if students==[]:
        return render_template("no_students.html")
    else:
        return render_template("students_list.html",students=students)

@app.route("/student/create",methods=["GET","POST"])
def input():
    if request.method=="GET":
        return render_template("create_student.html")
    
    elif request.method=="POST":
        roll_number=request.form.get("roll")
        first_name=request.form.get("f_name")
        last_name=request.form.get("l_name")
        selected_course_values=request.form.getlist("courses")

        selected_course_ids=[]
        for c in selected_course_values:
            selected_course_ids.append(c[-1]) #selected_course_values come as [course_3,course_4] etc. So last character has the course_id

        student=Student.query.filter_by(roll_number=roll_number).first()

        if student:
            return render_template("already_exists.html")
        else:
            try:
                new_student=Student(roll_number=roll_number,first_name=first_name,last_name=last_name)
                db.session.add(new_student)
                db.session.flush()
                sid=new_student.student_id

                for cid in selected_course_ids:
                    new_enroll=Enrollments(estudent_id=sid,ecourse_id=cid)
                    db.session.add(new_enroll)
            except:
                db.session.rollback()
                return render_template("error.html")
            else:
                db.session.commit()
                return redirect("/")
            
@app.route("/student/<int:student_id>/update",methods=["GET","POST"])
def update(student_id):
    student=Student.query.filter_by(student_id=student_id).first()

    if request.method=="GET":
        return render_template("update_details.html",student=student)
    elif request.method=="POST":
        first_name=request.form.get("f_name")
        last_name=request.form.get("l_name")
        selected_course_values=request.form.getlist("courses")

        selected_course_ids=[]
        for c in selected_course_values:
            selected_course_ids.append(c[-1]) #selected_course_values come as [course_3,course_4] etc. So last character has the course_id

        try:
            student.first_name=first_name
            student.last_name=last_name
            Enrollments.query.filter_by(estudent_id=student.student_id).delete()
            for cid in selected_course_ids:
                new_enrollment=Enrollments(estudent_id=student_id,ecourse_id=cid)
                db.session.add(new_enrollment)
        except:
            db.session.rollback()
            return render_template("error.html")
        else:
            db.session.commit()
            return redirect("/")

@app.route("/student/<int:student_id>/delete", methods = ["GET"])
def delete(student_id):
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
def get_details(student_id):
    if request.method == "GET":
        student_details = Student.query.filter_by(student_id = student_id).first()
        course_ids=Enrollments.query.with_entities(Enrollments.ecourse_id).filter_by(estudent_id = student_id).all()
        course_ids = [cid for cid, in course_ids] #To flatten the tuples returned by with_entities
        courses=[]
        for cid in course_ids:
            courses.append(Course.query.get(cid))
        return render_template("personal_details.html", student_details = student_details, courses = courses)

if __name__=="__main__":
    app.debug=True
    app.run()