import sys
import csv
from jinja2 import Template
import matplotlib.pyplot as plt

def student_profile(student_data,total):
    template_content="""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8"/>
        <title>Student Data</title>
    </head>
    <body>
        <h1>Student Details</h1>
        <table border="1px solid black">
            <thead>
                <tr>
                    <th>Student ID</th>
                    <th>Course ID</th>
                    <th>Marks</th>
                </tr>
            </thead>
            <tbody>
                {%for entry in student_data%}
                    <tr>
                        <td>{{entry['Student id']}}</td>
                        <td>{{entry['Course id']}}</td>
                        <td>{{entry['Marks']}}</td>
                    </tr>
                {%endfor%}
                <tr>
                    <td colspan=2 align='center'>Total Marks</td>
                    <td>{{total}}</td>
                </tr>
            </tbody>
        </table>
    </body>
</html>
"""
    temp=Template(template_content)
    content=temp.render(student_data=student_data,total=total)

    #save the rendered html document
    output_file=open('output.html','w')
    output_file.write(content)
    output_file.close()

def course_profile(course_data):
    average=sum(course_data)/len(course_data)
    maximum=max(course_data)
    template_content="""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8"/>
        <title>Course Data</title>
    </head>
    <body>
        <h1>Course Details</h1>
        <table border="1px solid black">
            <thead>
                <tr>
                    <th>Average Marks</th>
                    <th>Maximum Marks</th>
                </tr>
            </thead>
            <tbody>
                <tr>

                    <td>{{average}}</td>
                    <td>{{maximum}}</td>
                </tr>
            </tbody>
        </table>
        <img src="{{histogram}}" alt="Histogram of Marks">
    </body>
<html>
"""
    plt.hist(course_data)
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.savefig('histogram.jpg')

    temp=Template(template_content)
    content=temp.render(course_data=course_data,average=average,maximum=maximum,histogram='histogram.jpg')

    #save the rendered html document
    output_file=open('output.html','w')
    output_file.write(content)
    output_file.close()

def error_page():
    template_content="""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8"/>
        <title>Something went wrong</title>
    </head>
    <body>
        <h1>Wrong Inputs</h1>
        Something went wrong
"""
    temp=Template(template_content)
    content=temp.render()

    #save the rendered html document
    output_file=open('output.html','w')
    output_file.write(content)
    output_file.close()
    


#import csv to list of dictionaries
all_data=[]
with open('data.csv') as csv_file:
    data=csv_file.read().split("\n")

text=[data[i].split(", ") for i in range(len(data))]
for i in range(1,len(text)):
    all_data.append({text[0][num]:text[i][num] for num in range(len(text[i]))})

try:
    if sys.argv[1]=='-s':
        sid=sys.argv[2]
        student_data=[]
        total=0
        for i in all_data:
            if i['Student id']==sid:
                student_data.append(i)
                total+=int(i['Marks'])
        if student_data!=[]:
            student_profile(student_data,total)
        else:
            error_page()

    elif sys.argv[1]=='-c':
        cid=sys.argv[2]
        course_data=[]
        for i in all_data:
            if i['Course id']==cid:
                course_data.append(int(i['Marks']))
        if course_data!=[]:
            course_profile(course_data)
        else:
            error_page()

    else:
        error_page()
except:
    error_page()



