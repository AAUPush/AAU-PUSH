from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.contrib.auth import authenticate, login as auth_login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q
from django.contrib.auth.models import User
import datetime, zipfile, io
from main import models

# Create your views here.

def index(request):
        return HttpResponse("Welcome to Push API")

## Returns Educational Institutions
# www.aaupush.com/json/Educational_Institution
def Educational_Institution(request):

    #JSON output
    #Start json array
    output = "["

    # Loop through every Educational Institution and add them as a json object
    for Institution in models.Educational_Institution.objects.all():
        output += "{"
        output += "\"id\":" + str(Institution.id) + ","
        output += "\"name\":" + "\"" + Institution.name + "\"" + ","
        output += "\"country\":" + "\"" + Institution.country + "\"" + ","
        output += "\"city\":" + "\"" + Institution.city + "\"" + ","
        output += "\"ownership_type\":" + "\"" + Institution.ownership_type + "\"" + ","
        output += "\"institution_type\":" + "\"" + Institution.institution_type + "\""
        output += "},"

    # remove the last list separator comma
    output = output[::-1].replace(",", "", 1)[::-1]

    #end of json array
    output += "]"

    return HttpResponse(output, content_type='application/json')


## Returns Departments
# www.aaupush.com/json/Department?by-educational-institution={{Educational_Institution_ID}}
# GET variable is optionl
def Department(request):

    #Check if the api request is based on a specific Educational Institution
    if request.GET.get('by-educational-institution'):

        #Get all departments in that specific Educational_Institution(THE 'ID' ATTRIBUTE SHOULD BE SENT/USED TO SPECIFY THE INSTANCE)
        Departments = models.Department.objects.filter(university_in__id = int(request.GET.get('by-educational-institution')))

    #Get all departments
    else :
        Departments = models.Department.objects.all()


    #JSON output
    #Start json array
    output = "[";

    # Loop through every Department and add them as a json object
    for Department in Departments:
        output += "{"
        output += "\"id\":" + str(Department.id) + ","
        output += "\"university_in\":" + "\"" + Department.university_in.name + "\"" + ","
        output += "\"name\":" + "\"" + Department.name + "\"" + ","
        output += "\"field\":" + "\"" + Department.field + "\""
        output += "},"

    # remove the last list separator comma
    output = output[::-1].replace(",", "", 1)[::-1]

    #end of json array
    output += "]"

    return HttpResponse(output, content_type='application/json')


## Returns Sections
# www.aaupush.com/json/Section?by-educational-institution={{Educational_Institution_ID}}&by-department={{Department_ID}}
# GET variables are optional
def Section(request):

    #Check if the api request is based on a specific Educational Institution
    if request.GET.get('by-educational-institution'):

        #Get all sections in that specific Educational Institution(THE 'ID' ATTRIBUTE SHOULD BE SENT/USED TO SPECIFY THE INSTANCE)
        Sections = models.Section.objects.filter(department_in__university_in__id = int(request.GET.get('by-educational-institution')))

    #Check if the api request is based on a specific Department
    elif request.GET.get('by-department'):

        #Get all sections in that specific Department(THE 'ID' ATTRIBUTE SHOULD BE SENT/USED TO SPECIFY THE INSTANCE)
        Sections = models.Section.objects.filter(department_in__id = int(request.GET.get('by-department')))

    #Get all sections
    else :
        Sections = models.Section.objects.all()


    #JSON output
    #Start json array
    output = "[";

    # Loop through every Section and add them as a json object
    for Section in Sections:
        output += "{"
        output += "\"id\":" + str(Section.id) + ","
        output += "\"department_in\":" + "\"" + Section.department_in.name + "\"" + ","
        output += "\"year\":" + str(Section.year) + ","
        output += "\"section_id\":" + "\"" + Section.section_id + "\"" + ","
        output += "\"section_takes\":" + "["

        # Loop through every course the section takes and add them as a json object
        for Course in Section.section_takes.all():
            output += "{"
            output += "\"id\":" + str(Course.id) + ","
            output += "\"name\":" + "\"" + Course.name + "\"" + ","
            output += "\"course_code\":" + "\"" + Course.course_code + "\"" + ","
            output += "\"module_code\":" + "\"" + Course.module_code + "\"" + ","
            output += "\"given_by\":" + "\"" + Course.given_by.name + "\""
            output += "},"

        if Section.section_takes.all().count() > 0:
            # remove the last list separator comma
            output = output[::-1].replace(",", "", 1)[::-1]

        #Close section_takes array
        output += "]"

        output += "},"

    # remove the last list separator comma
    output = output[::-1].replace(",", "", 1)[::-1]

    #end of json array
    output += "]"

    return HttpResponse(output, content_type='application/json')



## Returns Courses
# www.aaupush.com/json/Course?by-department={{Department_ID}}&by-student={{}}
# The GET variables must be used with every request
def Course(request):

    #Check if the api request is for courses given by a Department
    if request.GET.get('by-department'):

        #Get all courses given by the Department(THE 'ID' ATTRIBUTE SHOULD BE SENT/USED TO SPECIFY THE INSTANCE)
        Courses = models.Course.objects.filter(given_by__id = int(request.GET.get('by-department')))

    #Check if the api request is for courses taken by a student
    elif request.GET.get('by-student'):

        #Get the student instance of the logged in user/student
        student = models.Student.objects.get(user = request.user)

        #Get the ids of the courses the student takes
        ids = student.class_in.values_list('course', flat=True)

        #Get all courses taken by a the student[THE 'ID' ATTRIBUTE ISN'T NEEDED FOR THIS REQUEST, ASSIGN ANY VALUE YOU WANT TO 'by-student']
        Courses = models.Course.objects.filter(pk__in=set(ids))

    #The request wasn't based on department or student, return nothing
    else:
        Courses = {}

    #JSON output
    #Start json array
    output = "["

    # Loop through every Course and add them as a json object
    for Course in Courses:
        output += "{"
        output += "\"id\":" + str(Course.id) + ","
        output += "\"name\":" + "\"" + Course.name + "\"" + ","
        output += "\"course_code\":" + "\"" + Course.course_code + "\"" + ","
        output += "\"module_code\":" + "\"" + Course.module_code + "\"" + ","
        output += "\"given_by\":" + "\"" + Course.given_by.name + "\""
        output += "},"

    # remove the last list separator comma
    output = output[::-1].replace(",", "", 1)[::-1]

    #end of json array
    output += "]"

    return HttpResponse(output, content_type='application/json')



## Returns Posts with ID greater than the specified Post_ID
# www.aaupush.com/json/Post?by-post={{Post_ID}}
# GET variable is a must
def Post(request):

    Posts = []

    #Get the student instance of the logged in user/student
    student = models.Student.objects.get(user = request.user)

    #Get the classes the student takes part in
    classes_in = student.class_in.all()

    #A query to filter posts
    query = Q()

    if request.GET.get('by-type') == "wall":
        #Loop through the classes the student takes to build a query
        for class_in in classes_in:

            #Add every class the student takes to the query
            query.add( Q( post_to = class_in ), Q.OR )

        if request.GET.get('by-class-post'):
            Posts = models.Post_To_Class.objects.filter( post__id__gt = int(request.GET.get('by-class-post'))).filter(query)

        elif request.GET.get('by-student-post'):
            Posts = models.Post_To_Student.objects.filter( post__id__gt = int(request.GET.get('by-student-post'))).filter(query)

        elif request.GET.get('by-page'):
            posts_to_class = models.Post_To_Class.objects.filter(query)
            posts_to_student = models.Post_To_Student.objects.filter( post_to = student )

            Posts = sorted((list(posts_to_class) + list(posts_to_student)), key=lambda x: x.post.pub_date)

        else :
            posts_to_class = models.Post_To_Class.objects.filter(query)
            posts_to_student = models.Post_To_Student.objects.filter( post_to = student )

            Posts = sorted((list(posts_to_class) + list(posts_to_student)), key=lambda x: x.post.pub_date)

    elif request.GET.get('by-type') == "pushboard":
        #Loop through the sections the student is in to build a query
        for section in classes_in:

            #Add every section the student is in to the query
            query.add( Q( post_to = section.section ), Q.OR )

        if request.GET.get('by-section-post'):
            Posts = models.Post_To_Section.objects.filter( post__id__gt = int(request.GET.get('by-section-post'))).filter(query)

        elif request.GET.get('by-page'):
            Posts = models.Post_To_Section.objects.filter(query)

        else :
            Posts = models.Post_To_Section.objects.filter(query)

    elif request.GET.get('by-type') == "class-post-list":
        if request.GET.get('by-class') and student.class_in.filter(id = int(request.GET.get('by-class'))).exists():
            posts = models.Post_To_Class.objects.filter(post_to = student.class_in.get(id = int(request.GET.get('by-class')))).exclude(post__files = None)

        context = {'posts':posts}
        return render(request, 'main/class-posts-snippet.html', context)

    elif request.GET.get('by-type') == "miscellaneous":
        for section in classes_in:

            #Add every section the student is in to the query
            query.add( Q( post_to = section.section ), Q.OR )

        posts_to_section = models.Post_To_Section.objects.filter(query)
        posts_to_student = models.Post_To_Student.objects.filter( post_to = student )

        posts = sorted((list(posts_to_section) + list(posts_to_student)), key=lambda x: x.post.pub_date)
        context = {'posts':posts}
        return render(request, 'main/class-posts-snippet.html', context)
    #JSON output
    #Start json array
    output = "["

    # Loop through every Post and add them as a json object
    for Post in Posts:
        output += "{"
        output += "\"id\":" + str(Post.post.id) + ","
        output += "\"content\":" + "\"" + Post.post.content + "\"" + ","

        #Start json array for Post files
        output += "\"files\":" + "["

        for File in Post.post.files.all():
            output += "{"
            output += "\"id\":" + str(File.id) + ","
            output += "\"name\":" + "\"" + File.name + "\"" + ","
            output += "\"extension\":" + "\"" + File.extension + "\"" + ","
            output += "\"post_by\":" + "\"" + File.post_by.__str__() + "\""
            output += "},"

        if Post.post.files.all().count() > 0:
            # remove the last list separator comma
            output = output[::-1].replace(",", "", 1)[::-1]

        #Close files array
        output += "],"

        #Start json array for Post images
        output += "\"images\":" + "["

        for Image in Post.post.images.all():
            output += "{"
            output += "\"id\":" + str(Image.id) + ","
            output += "\"post_by\":" + "\"" + Image.post_by.__str__() + "\""
            output += "},"

        if Post.post.images.all().count() > 0:
            # remove the last list separator comma
            output = output[::-1].replace(",", "", 1)[::-1]

        #Close images array
        output += "],"

        output += "\"post_type\":" + str(Post.post.post_type) + ","
        output += "\"post_by\":" + "\"" + Post.post.post_by.__str__() + "\"" + ","
        output += "\"pub_date\":" + str(Post.post.pub_date)
        output += "},"

    # remove the last list separator comma
    output = output[::-1].replace(",", "", 1)[::-1]

    #end of json array
    output += "]"

    return HttpResponse(output, content_type='application/json')



## Returns Reminders with ID greater than the specified Reminder_ID
# www.aaupush.com/json/Reminder?by-reminder={{Reminder_ID}}
# GET variable is a must
def Reminder(request):

    #Get the student instance of the logged in user/student
    student = models.Student.objects.get(user = request.user)

    #Get the classes the student takes part in
    classes_in = models.Student_Takes.objects.filter(student = student)

    #A query to filter posts from Reminder_To_Class
    query = Q()

    #Loop through the classes the student takes to build a query
    for class_in in classes_in:

        #Add every class the student takes to the query
        query.add( Q( reminder_to = class_in.class_in ), Q.OR )

    #Get reminders with ID greater than the specified Reminder_ID
    Reminders = models.Reminder_To_Class.objects.filter(query).filter( id__gt = int(request.GET.get('by-reminder')))


    #JSON output
    #Start json array
    output = "[";

    # Loop through every Course and add them as a json object
    for Reminder in Reminders:
        output += "{"
        output += "\"id\":" + str(Reminder.id) + ","
        output += "\"reminder_for\":" + str(Reminder.reminder_for) + ","
        output += "\"title\":" + "\"" + Reminder.title + "\"" + ","
        output += "\"note\":" + "\"" + Reminder.note + "\"" + ","
        output += "\"due_date\":" + str(Reminder.due_date) + ","
        output += "\"due_time\":" + str(Reminder.due_time) + ","
        output += "\"place\":" + "\"" + Reminder.place + "\""
        output += "},"

    # remove the last list separator comma
    output = output[::-1].replace(",", "", 1)[::-1]

    #end of json array
    output += "]"

    return HttpResponse(output, content_type='application/json')



def Instructor_Teaches(request):

    if not request.user.is_authenticated():
        return HttpResponse("{\"role\":\"null\", \"status\":, \"remark\":\"User not authenticated\"}", content_type='application/json')

    #Check if the api request is based on a specific Educational Institution
    if request.GET.get('by-department'):

        #Get all sections in that specific Educational Institution(THE 'ID' ATTRIBUTE SHOULD BE SENT/USED TO SPECIFY THE INSTANCE)
        classes = models.Instructor_Teaches.objects.filter(section__department_in__id = int(request.GET.get('by-department')))

    #Check if the api request is based on a specific Department
    elif request.GET.get('by-student'):
        if models.Student.objects.filter(user=request.user).exists():
            #Get all sections in that specific Department(THE 'ID' ATTRIBUTE SHOULD BE SENT/USED TO SPECIFY THE INSTANCE)
            classes = models.Student.objects.get(user=request.user).class_in.all()

        else:
            return HttpResponse("{\"role\":\"null\", \"status\":4, \"remark\":\"User type not found\"}", content_type='application/json')
    elif request.GET.get('by-staff'):
        if models.Staff.objects.filter(user=request.user).exists():
            #Get all sections in that specific Department(THE 'ID' ATTRIBUTE SHOULD BE SENT/USED TO SPECIFY THE INSTANCE)
            classes =  models.Instructor_Teaches.objects.filter(instructor__user = request.user)

        else:
            return HttpResponse("{\"role\":\"null\", \"status\":4, \"remark\":\"User type not found\"}", content_type='application/json')

    else :
        Sections = models.Section.objects.all()


    #JSON output
    #Start json array
    output = "[";

    # Loop through every Section and add them as a json object
    for Section in Sections:
        output += "{"
        output += "\"id\":" + str(Section.id) + ","
        output += "\"department_in\":" + "\"" + Section.department_in.name + "\"" + ","
        output += "\"year\":" + str(Section.year) + ","
        output += "\"section_id\":" + "\"" + Section.section_id + "\"" + ","
        output += "\"section_takes\":" + "["

        # Loop through every course the section takes and add them as a json object
        for Course in Section.section_takes.all():
            output += "{"
            output += "\"id\":" + str(Course.id) + ","
            output += "\"name\":" + "\"" + Course.name + "\"" + ","
            output += "\"course_code\":" + "\"" + Course.course_code + "\"" + ","
            output += "\"module_code\":" + "\"" + Course.module_code + "\"" + ","
            output += "\"given_by\":" + "\"" + Course.given_by.name + "\""
            output += "},"

        if Section.section_takes.all().count() > 0:
            # remove the last list separator comma
            output = output[::-1].replace(",", "", 1)[::-1]

        #Close section_takes array
        output += "]"

        output += "},"

    # remove the last list separator comma
    output = output[::-1].replace(",", "", 1)[::-1]

    #end of json array
    output += "]"

    return HttpResponse(output, content_type='application/json')



def login(request):
        user = None
        role = ''
        status = ''
        remark = ''

        def staff():
                nonlocal user
                nonlocal role

                staff = models.Staff.objects.get(email = request.POST.get('email'))
                password = request.POST.get('password')
                user = authenticate(username=staff.user.username, password=password)
                role = 'staff'


        def student():
                nonlocal user
                nonlocal role

                student = models.Student.objects.get(reg_id = request.POST.get('reg_id'))
                password = request.POST.get('password')
                user = authenticate(username=student.user.username, password=password)
                role = 'student'

        def success():
                auth_login(request, user)

                nonlocal status
                nonlocal remark

                status = 1
                remark = 'Authentication success'

        def failure():
                nonlocal status
                nonlocal remark

                status = 0
                remark = 'Authentication failed'

        def notActive():
                nonlocal status
                nonlocal remark

                status = 3
                remark = 'Account not active'


        if (request.POST.get('user-type') == 'staff'):
            staff()

        elif (request.POST.get('user-type') == 'student'):
            student()

        else:
                return HttpResponse("{\"role\":\"null\", \"status\":4, \"remark\":\"User type not found\"}", content_type='application/json')


        if user is not None:
                if user.is_active:
                        success()
                else:
                        notActive()
        else:
                failure()


        #JSON output
        #Start json object
        output = "{\"role\":"
        output += "\"" + role + "\","
        output += "\"status\":"
        output +=  str(status) + ","
        output += "\"remark\":"
        output += "\"" + remark + "\"}"

        return HttpResponse(output, content_type='application/json')



def signup(request):
        status = 0
        remark = ""
        fields = []

        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        phone = request.POST.get('phone-number')
        email = request.POST.get('email')
        department_in = models.Department.objects.get(id = int(request.POST.get('department')))
        year = int(request.POST.get('year'))
        section = models.Section.objects.get(department_in = department_in, year = year, section_id = request.POST.get('section'))
        reg_id = request.POST.get('reg-id')
        password = request.POST.get('password')

        def verify():

            return True

        if verify():
            user = User.objects.create_user(reg_id.replace("/","-"), "", password)
            student = models.Student.objects.create(university_in = department_in.university_in, department_in = department_in, year = year, section = section.section_id, first_name = first_name, last_name = last_name, reg_id = reg_id, phone = phone, email = email, user = user)

            for class_in in models.Instructor_Teaches.objects.filter(section=section):
                student.class_in.add(class_in)

            status = 1
            remark = "Sign up successfull"


        #JSON output
        #Start json object
        output = "{\"status\":"
        output +=  str(status) + ","
        output += "\"remark\":"
        output += "\"" + remark + "\"" + ","
        output += "\"fields\":["

        for field in fields:
            output +=  "\"" + field + "\","

        if len(fields) > 0:
            # remove the last list separator comma
            output = output[::-1].replace(",", "", 1)[::-1]

        output += "]}"

        return HttpResponse(output, content_type='application/json')



def account_update(request):
        status = 0
        remark = ""
        fields = []
        role = ""
        password = request.POST.get('password')

        if not request.user.is_authenticated():
            return HttpResponse("{\"role\":\"null\", \"status\":4, \"remark\":\"User not authenticated\"}", content_type='application/json')




        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        phone = request.POST.get('phone-number')
        email = request.POST.get('email')
        department_in = models.Department.objects.get(id = int(request.POST.get('department')))

        if request.POST.get('user-type') == "staff":
                title = request.POST.get('title')
                role = request.POST.get('role')

                if models.Staff.objects.filter(user=request.user).exists():
                    staff = models.Staff.objects.get(user = request.user)
                else:
                    return HttpResponse("{\"role\":\"staff\", \"status\":2, \"remark\":\"Staff not found\"}", content_type='application/json')


                staff.university_in = department_in.university_in
                staff.department_in = department_in
                staff.title = title
                staff.first_name =  first_name
                staff.last_name = last_name
                staff.phone = phone
                staff.role = role

                staff.email = email
                user = models.User.objects.get(id = request.user.id)
                user.username = email

                staff.save()
                user.save()

                status = 1
                remark = "Update successful"
                role = "staff"

        elif request.POST.get('user-type') == "student":
                year = int(request.POST.get('year'))
                section = request.POST.get('section')
                reg_id = request.POST.get('reg-id')

                if models.Student.objects.filter(user=request.user).exists():
                    student = models.Student.objects.get(user = request.user)
                else:
                    return HttpResponse("{\"role\":\"student\", \"status\":2, \"remark\":\"Student not found\"}", content_type='application/json')


                student.university_in = department_in.university_in
                student.department_in = department_in
                student.year = year
                student.section = section
                student.first_name =  first_name
                student.last_name = last_name
                student.phone = phone
                student.email = email

                student.reg_id = reg_id
                user = models.User.objects.get(id = request.user.id)
                user.username = reg_id.replace("/","-")

                student.save()
                user.save()

                status = 1
                remark = "Update successful"
                role = "student"

        else:
                return HttpResponse("{\"role\":\"null\", \"status\":3, \"remark\":\"User type not found\"}", content_type='application/json')


        #JSON output
        #Start json object
        output = "{\"status\":"
        output +=  str(status) + ","
        output += "\"remark\":"
        output += "\"" + remark + "\"" + ","
        output += "\"fields\":["

        for field in fields:
            output +=  "\"" + field + "\","

        if len(fields) > 0:
            # remove the last list separator comma
            output = output[::-1].replace(",", "", 1)[::-1]

        output += "],"
        output += "\"role\":"
        output += "\"" + role + "\"}"

        return HttpResponse(output, content_type='application/json')



def add_drop(request):
        action = ""
        no_of_courses = 0
        html = ""
        course = ""
        drop_class_id = -1

        if not request.user.is_authenticated():
            return HttpResponse("{\"action\":\"null\", \"status\":3, \"remark\":\"User not authenticated\"}", content_type='application/json')

        if models.Student.objects.filter(user=request.user).exists():
            student = models.Student.objects.get(user=request.user)

        else:
            return HttpResponse("{\"action\":\"null\", \"status\":2, \"remark\":\"Student not found\"}", content_type='application/json')


        if request.POST.get('action_type') == "add":
            action = "add"
            classes_id = request.POST.getlist('class')

            for class_id in classes_id:
                if not student.class_in.filter(id = int(class_id)).exists():
                    class_obj = models.Instructor_Teaches.objects.get(id = int(class_id))
                    student.class_in.add(class_obj)

                    html += "<tr class='row-" + class_id + "'>"
                    html += "<td><button onclick='drop_course(" + str(class_obj.id) + ")'>Drop</button></td>"
                    html += "<td>" + class_obj.course.name  + "</td>"
                    html += "<td>" + class_obj.course.course_code + "</td>"
                    html += "<td>" + class_obj.course.module_code + "</td>"
                    html += "<td>3.00</td>"
                    html += "<td>5.00</td>"
                    html += "<td>Year-" + str(class_obj.section.year) + " Section-" + class_obj.section.section_id + "</td>"
                    html += "<td>" + class_obj.instructor.__str__() + "</td>"
                    html += "</tr>"

                    no_of_courses += 1

        elif request.POST.get('action_type') == "drop":
            action = "drop"
            class_id = request.POST.get('class')

            if student.class_in.filter(id = int(class_id)).exists():
                class_obj = models.Instructor_Teaches.objects.get(id = int(class_id))
                course = class_obj.course.name
                drop_class_id = class_obj.id

                student.class_in.remove(class_obj)
                no_of_courses += 1

        else:
                return HttpResponse("{\"action\":\"null\", \"status\":4, \"remark\":\"User type not found\"}", content_type='application/json')


        if len(request.POST.getlist('class')) > 0:
            status = 1
            remark = "Action successul"

        else:
            status = 0
            remark = "No classes sent"
            action = "null"


        #JSON output
        #Start json object
        output = "{\"status\":"
        output +=  str(status) + ","
        output += "\"remark\":"
        output += "\"" + remark + "\"" + ","

        if action == "add":
            output += "\"count\":"
            output +=  str(no_of_courses) + ","
            output += "\"html\":"
            output += "\"" + html + "\"" + ","

        else:
            output += "\"course\":"
            output +=  "\"" + course + "\"" + ","
            output += "\"class_id\":"
            output +=  str(drop_class_id) + ","
        output += "\"action\":"
        output += "\"" + action + "\"}"

        return HttpResponse(output, content_type='application/json')



def post_action(request):
        if not request.user.is_authenticated():
            return HttpResponse("{\"status\":3, \"remark\":\"User not authenticated\"}", content_type='application/json')

        if models.Staff.objects.filter(user=request.user).exists():
            staff = models.Staff.objects.get(user=request.user)

        else:
            return HttpResponse("{\"status\":2, \"remark\":\"Staff not found\"}", content_type='application/json')


        if request.POST.get('action-type') == "chat":
            if not request.POST.get('post-content') or (request.POST.get('post-content').strip() == ""):
                    return HttpResponse("{\"status\":0, \"remark\":\"Content not found\", \"id\":\"#group-chat-post-content-error\", \"html\":\"<p>Post content is required</p>\"}", content_type='application/json')

            if request.FILES.get('image-1'):
                if request.POST.get('image-1').split('.')[-1].strip().isslower() not in ["jpeg","jpg","gif","png","bmp","svg"]:
                    return HttpResponse("{\"status\":0, \"remark\":\"File name not found\",  \"id\":\"#group-chat-attachment-error\", \"html\":\"<p>Image format not supported</p>\"}", content_type='application/json')


            content = request.POST.get('post-content')
            pub_date = datetime.datetime.now()

            post = models.Post.objects.create(content = content, post_type = 1, post_by = staff, pub_date = pub_date)

            if request.FILES.get('file-1'):
                name = request.FILES.get('file-name-1').name
                file = models.File.objects.create(file = request.FILES.get('file-1'), name = name, extension = name.split('.')[-1], post_by = staff)
                post.files.add(file)

            if request.FILES.get('image-1'):
                file = models.Image.objects.create(file = request.FILES.get('image-1'), post_by = staff)
                post.images.add(file)

            models.Post_To_Chat.objects.create(post_to = staff.department_in, post = post)

            latest = models.Post_To_Chat.objects.latest('post__pub_date')

            def sizeof_fmt(num, suffix='B'):
                for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
                    if abs(num) < 1024.0:
                        return "%3.1f%s%s" % (num, unit, suffix)
                    num /= 1024.0
                return "%.1f%s%s" % (num, 'Yi', suffix)

            html = ""

            if latest.post.pub_date.day != post.pub_date.day or latest.post.pub_date.month != post.pub_date.month or latest.post.pub_date.year != post.pub_date.year:
                html += "<div class='mx-3 mt-3'>"
                html += "<p>" + post.pub_date.strftime("%B") + " " + post.pub_date.day + "</p>"
                html += "</div>"

            html += "<div class='card card-body push-corners mb-3'>"
            html += "<div class='post-header'>"
            html += "<p class='font-weight-bold'>" + post.post_by.__str__() + "</p></div>"
            html += "<div class='post-images'>"
            for image in post.images.all():
                html += "<div class='mb-3'>"
                html += "<img width='100%' src='/media/" + image.image + "\'/>"
                html += "</div>"
            html += "</div>"
            html += "<div class='post-content'>"
            html += "<p>" + post.content + "</p>"
            html += "</div>"

            html += "<div>"
            for file in post.files.all():
                html += '<div class="file">'
                html += '<div>'
                html += '<a class="link font-weight-bold" href="/media/' + file.file + '">' +  file.name + '['+ file.extension.isupper + ']</a>'
                html += '</div>'
                html += '<div>'
                html += '<p class="meta mb-2">File size:  ' + sizeof_fmt(file.file.size)  + '</p>'
                html += '</div>'
                html += '</div>'
            html += '</div>'

            html += "<div>"
            html += "<div>"
            html += "<span class='meta'>" + str(post.delivered()) + " Views | </span>"
            html += "<span class='meta'>" + post.pub_date.strftime("%b") + "." + str(post.pub_date.day) + ", " + str(post.pub_date.year) + "</span>"
            html += "</div>"
            html += "</div>"
            html += "</div>"

            return HttpResponse("{\"status\":1, \"remark\":\"Post Successful\", \"html\":\"" + html + "\"}", content_type='application/json')


        if (request.POST.get('post-content').strip() == ""):
                return HttpResponse("{\"status\":0, \"remark\":\"Content not found\", \"id\":\"#post-content-error\", \"html\":\"<p>Post content is required</p>\"}", content_type='application/json')

        if not request.POST.getlist('section-recipients'):
            if not request.POST.getlist('class-recipients'):
                return HttpResponse("{\"status\":0, \"remark\":\"Recipient not found\", \"id\":\"#post-recipient-error\", \"html\":\"<p>Choose at least one post recipient</p>\"}", content_type='application/json')

        if request.FILES.get('file-1'):
            if request.POST.get('file-name-1').strip() == "":
                return HttpResponse("{\"status\":0, \"remark\":\"File name not found\", \"id\":\"#post-file-1-error\", \"html\":\"<p>File name is required</p>\"}", content_type='application/json')

        if request.FILES.get('file-2'):
            if request.POST.get('file-name-2').strip() == "":
                return HttpResponse("{\"status\":0, \"remark\":\"File name not found\",  \"id\":\"#post-file-2-error\", \"html\":\"<p>File name is required</p>\"}", content_type='application/json')

        if request.FILES.get('file-3'):
            if request.POST.get('file-name-3').strip() == "":
                return HttpResponse("{\"status\":0, \"remark\":\"File name not found\",  \"id\":\"#post-file-3-error\", \"html\":\"<p>File name is required</p>\"}", content_type='application/json')

        if request.FILES.get('image-1'):
            if request.POST.get('image-1').split('.')[-1].strip().isslower() not in ["jpeg","jpg","gif","png","bmp","svg"]:
                return HttpResponse("{\"status\":0, \"remark\":\"File name not found\",  \"id\":\"#post-image-1-error\", \"html\":\"<p>Image format not supported</p>\"}", content_type='application/json')

        if request.FILES.get('image-2'):
                if request.POST.get('image-2').split('.')[-1].strip().isslower() not in ["jpeg","jpg","gif","png","bmp","svg"]:
                    return HttpResponse("{\"status\":0, \"remark\":\"File name not found\",  \"id\":\"#post-image-2-error\", \"html\":\"<p>Image format not supported</p>\"}", content_type='application/json')

        content = request.POST.get('post-content')
        pub_date = datetime.datetime.now()

        post = models.Post.objects.create(content = content, post_type = 1, post_by = staff, pub_date = pub_date)

        if request.FILES.get('file-1'):
                name = request.POST.get('file-name-1')
                file = models.File.objects.create(file = request.FILES.get('file-1'), name = name, extension = name.split('.')[-1], post_by = staff)
                post.files.add(file)

        if request.FILES.get('file-2'):
                name = request.POST.get('file-name-2')
                file = models.File.objects.create(file = request.FILES.get('file-2'), name = name, extension = name.split('.')[-1], post_by = staff)
                post.files.add(file)

        if request.FILES.get('file-3'):
                name = request.POST.get('file-name-3')
                file = models.File.objects.create(file = request.FILES.get('file-3'), name = name, extension = name.split('.')[-1], post_by = staff)
                post.files.add(file)


        if request.FILES.get('image-1'):
            file = models.Image.objects.create(file = request.FILES.get('image-1'), post_by = staff)
            post.images.add(file)

        if request.FILES.get('image-2'):
            file = models.Image.objects.create(file = request.FILES.get('image-2'), post_by = staff)
            post.images.add(file)



        section_recipients = request.POST.getlist('section-recipients')

        for recipient in section_recipients:
            detail = recipient.split('-')

            if detail[0] == 'year':
                for section in models.Section.objects.filter(department_in__id = int(detail[1]), year = int(detail[2])):
                    models.Post_To_Section.objects.create(post_to = section, post = post)

            elif detail[0] == 'section':
                section = models.Section.objects.get(id = int(detail[1]))
                models.Post_To_Section.objects.create(post_to = section, post = post)



        class_recipients = request.POST.getlist('class-recipients')

        for recipient in class_recipients:
            detail = recipient.split('-')

            class_ = models.Instructor_Teaches.objects.get(section__id = int(detail[0]), course__id = int(detail[1]))

            models.Post_To_Class.objects.create(post_to = class_, post = post)



        status = 1
        remark = "Action successul"



        #JSON output
        #Start json object
        output = "{\"status\":"
        output +=  str(status) + ","
        output += "\"remark\":"
        output += "\"" + remark + "\"}"


        return HttpResponse(output, content_type='application/json')


def email_exists(request):
        if request.GET.get('email'):
                email = request.GET.get('email')
        else:
                return HttpResponse("Incorrect API request format. Refer to the docmumentaion.")

        #JSON output
        #Start json array
        output = "{"

        if models.Staff.objects.filter(email=email).exists():
                output += " \"status\":true }"

        elif models.Student.objects.filter(email=email).exists():
                output += " \"status\":true }"

        else:
                output += " \"status\":false }"

        return HttpResponse(output, content_type='application/json')



def phone_exists(request):
        if request.GET.get('phone-number'):
                phone = request.GET.get('phone-number')
        else:
                return HttpResponse("Incorrect API request format. Refer to the docmumentaion.")

        #JSON output
        #Start json array
        output = "{"

        if models.Staff.objects.filter(phone = phone).exists():
                output += " \"status\":true }"

        elif models.Student.objects.filter(phone = phone).exists():
                output += " \"status\":true }"

        else:
                output += " \"status\":false }"

        return HttpResponse(output, content_type='application/json')



def reg_id_exists(request):
        if request.GET.get('reg_id'):
                reg_id = request.GET.get('reg_id')
        else:
                return HttpResponse("Incorrect API request format. Refer to the docmumentaion.")

        #JSON output
        #Start json array
        output = "{"

        if models.Student.objects.filter(reg_id = reg_id).exists():
                output += " \"status\":true}"

        else:
                output += " \"status\":false }"

        return HttpResponse(output, content_type='application/json')



def get_latest_app_version(request):

        #JSON output
        #Start json array
        output = "{"

        output += " \"version_name\": \"1.03\" ,"
        output += " \"version_code\": 9 }"

        return HttpResponse(output, content_type='application/json')


@ensure_csrf_cookie
def get_csrf_token(request):

        if not request.user.is_authenticated():
            return HttpResponse("{\"status\": 0}", content_type='application/json')

        return HttpResponse("{\"status\": 1}", content_type='application/json')
