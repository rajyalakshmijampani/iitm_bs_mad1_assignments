from flask import Flask
from flask import render_template
from flask import request
import csv
import sys
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
app = Flask(__name__)

def remove(string):
    return string.replace(" ", "")
def isValid(students_data, id, i):
    for row in students_data:
        if row[i] == id:
            return True
    return False


@app.route("/", methods=["GET","POST"])
def application():
    csv_file = "data.csv"
    file = open(csv_file, mode = 'r')
    data  = csv.reader(file)
    data = list(data)
    for i in data:
        i[0] = remove(i[0])
        i[1] = remove(i[1])
        i[2] = remove(i[2])
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        value = request.form.get("id_value")
        id = request.form.get("ID")
        if id == "student_id":
            valid = isValid(data,value,0)
            if valid == True:
                students_data = []
                result = 0
                for i in data:
                    if i[0]==value:
                        students_data.append(i)
                        try:
                            result = result + int(i[2])
                        except:
                            pass
                
                return render_template("student.html", student_id_data = value, students_data = students_data, total_marks_data = result)
            else:
                return render_template("error.html")
        elif id == "course_id":
            valid = isValid(data,value,1)
            if valid == True:
                highest = 0
                count = 0
                total_marks = 0
                scores = []
                for i in data:
                    if i[1]==value:
                        try:
                            marks = int(i[2])
                            scores.append(marks)
                            total_marks = total_marks + marks
                            count = count + 1
                            if marks > highest:
                                highest = marks
                        except:
                            pass
                
                plt.hist(scores)
                plt.xlabel("Marks")
                plt.ylabel("Frequency")
                plt.savefig('static/imagename.png')
                plt.clf()
                return render_template("course.html",average_marks = total_marks/count, highest_marks = highest, image = 'static/imagename.png')
            else:
                return render_template("error.html")
        else:
            return render_template("error.html")
    else:
        return render_template("error.html")


if __name__== "__main__":
    app.run()