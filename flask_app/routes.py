import datetime
from flask_app import app , db , red
from flask import render_template , redirect , url_for ,flash , request , Response , session
from flask_app.models import Attendance_Log, Course, User, Admin, Professor, Student 
from flask_login import login_user, current_user, logout_user, login_required
from flask_app.forms import  AddCourseForm, AssignCourseToProfForm, AssignCourseToStudentForm, LoginForm , AddAdminUserForm , AddProfessorUserForm , AddProfessorForm , AddAdminForm , AddStudentForm
from flask_app.cam import wcam, face_detect, get_encode
import json
from datetime import date
import calendar
import csv



def set_course(course_id):
    global active_course
    active_course = course_id

def get_course():
    global active_course
    return active_course



def at_log():

    course_id = get_course()
    course = Course.query.filter_by(course_id=course_id).first()
    name = course.course_name
    today = datetime.datetime.now().date()
    logs = Attendance_Log.query.filter_by(course_id=course_id,date=today)
    # check if logs does not have any logs
    if logs.count() == 0:
        return None
    else:
        outfile = open('attandance/'+name+'-'+str(today)+'.csv', 'w')
        outcsv = csv.writer(outfile)
        outcsv.writerow(['StudentId', 'Name', 'CourseId','Date','Time'])
        for log in logs:
            outcsv.writerow([log.student_id, log.name,log.course_id,log.date,log.time])


@app.route("/" , methods=['GET','POST'])
@app.route("/home" , methods=['GET','POST'])
@login_required
def home():
    red.set('action','2')
    my_date = date.today()
    today = calendar.day_name[my_date.weekday()] 
    id = current_user.professor_owner
    courses = Course.query.filter_by(prof=id, course_day=today ).all()
    name = current_user.username
    if request.method == 'POST':
        if request.form['action'] == 'start':
            course_id = request.form['course_id']
            set_course(course_id)
            return redirect(url_for('lecture'))
        
    return render_template('home.html' , name=name, courses=courses)

@app.route("/lecture", methods=['GET', 'POST'])
def lecture():
    course_id = get_course()
    course = Course.query.filter_by(course_id=course_id).first()
    prof_id = current_user.professor_owner
    prof_name = Professor.query.filter_by(id=prof_id).first().name
    course_name = course.course_name
    red.set('action', '1')
    if request.method == 'POST':
        if request.form['action'] == 'stop':
            at_log()
            red.set('action', '2')
            return redirect(url_for('home'))
    return render_template('lecture.html' , prof_name=prof_name , course_name=course_name)

    

# route to return json data with attandance log
@app.route("/log")
def log():
    today = datetime.datetime.now().date()
    # quary database for all attandance log
    log = Attendance_Log.query.filter_by(course_id=get_course(),date=today).all()
    json_string = json.dumps([i.to_dict() for i in log], sort_keys=True)
    # return json data
    return Response(json_string, mimetype='application/json')



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            id = user.admin_owner
            is_admin = Admin.query.filter_by(id=id).first()
            if is_admin:
                login_user(user)
                flash(f'[SUCCESS][LOGIN]Welcome Admin.{user.username}!', category='success')
                return redirect(url_for('admin'))
            else:
                login_user(user)
                
                flash(f'[SUCCESS][LOGIN]Welcome Professor.{user.username}!', category='success')
                return redirect(url_for('home'))   
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash(f'[SUCCESS][LOGOUT]You have been logged out', category='info')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    if current_user.admin_owner:
        return render_template('admin.html')
    else:
        flash(f'[ERROR][LOGIN]You are not an admin', category='danger')
        return redirect(url_for('login'))

@app.route('/addadminuser', methods=['GET', 'POST'])
@login_required
def addadminuser():
        form = AddAdminUserForm()
        #refresh the list of admins
        form.admin_name.choices = [(admin.id, admin.name) for admin in Admin.query.all()]
        if form.validate_on_submit():
            print(form.admin_name.data)
            admin_id = Admin.query.filter_by(id=form.admin_name.data).first().id
            name_in_db = User.query.filter_by(username=form.username.data).first()
            if name_in_db:
                flash(f'[ADMIN][ERROR][SIGNIN]Username {form.username.data} already exist', category='danger')
                return redirect(url_for('addadminuser'))
            else:
                user_to_create = User(username=form.username.data,
                                    password=form.password1.data,
                                    admin_owner=admin_id)
                db.session.add(user_to_create)
                db.session.commit()
                flash(f'[ADMIN][SUCCESS][SIGNIN]Account created for Admin.{form.username.data}!', category='success')
                return redirect(url_for('manageusers'))
        if form.errors != {} : #if there are errors from form validation
            for error_msg in form.errors.values():
                flash(f'[ADMIN][ERROR][SIGNUP]{error_msg}', category='danger')
                
        return render_template('addadminuser.html', form=form)
    

@app.route('/addprofessoruser', methods=['GET', 'POST'])
@login_required
def addprofessoruser():
        form = AddProfessorUserForm()
        #refresh the list of professors
        form.professor_name.choices = [(professor.id, professor.name) for professor in Professor.query.all()]
        if form.validate_on_submit():
            name_in_db = User.query.filter_by(username=form.username.data).first()
            professor_id = Professor.query.filter_by(id=form.professor_name.data).first().id
            if name_in_db:
                flash(f'[PROFESSOR][ERROR][SIGNIN]Username {form.username.data} already exist', category='danger')
                return redirect(url_for('addprofessoruser'))
            else:
                user_to_create = User(username=form.username.data,
                                    password=form.password1.data,
                                    professor_owner=professor_id)
                db.session.add(user_to_create)
                db.session.commit()
                flash(f'[PROFESSOR][SUCCESS][SIGNIN]Account created for Professor.{form.username.data}!', category='success')
                return redirect(url_for('manageusers'))
        if form.errors != {} : #if there are errors from form validation
            for error_msg in form.errors.values():
                flash(f'[ADMIN][ERROR][SIGNUP]{error_msg}', category='danger')
        return render_template('addprofessoruser.html', form=form)


@app.route('/manageusers', methods=['GET', 'POST'])
@login_required
def manageusers():
    #query the database for all users with admin_owner = not null 
    useradmin = db.session.query(User.id, User.username, Admin.name).join(Admin, User.admin_owner == Admin.id).filter(User.admin_owner != None).all()
    userprof = db.session.query(User.id, User.username, Professor.name).join(Professor, User.professor_owner == Professor.id).filter(User.professor_owner != None).all()

    if request.method == 'POST':
        if request.form['action'] == 'deleteadmin':
            user_id = request.form['user_id']
            user_to_delete = User.query.filter_by(id=user_id).first()
            db.session.delete(user_to_delete)
            db.session.commit()
            flash(f'[SUCCESS][DELETE]Admin User.{user_to_delete.username} deleted!', category='success')
            return redirect(url_for('manageusers'))
        if request.form['action'] == 'deleteprof':
            user_id = request.form['user_id']
            user_to_delete = User.query.filter_by(id=user_id).first()
            db.session.delete(user_to_delete)
            db.session.commit()
            flash(f'[SUCCESS][DELETE]Professor User.{user_to_delete.username} deleted!', category='success')
            return redirect(url_for('manageusers'))
    return render_template('manageusers.html', useradmin=useradmin , userprof=userprof)




@app.route('/addprofessor', methods=['GET', 'POST'])
@login_required
def addprofessor():
    if request.method == 'POST':
        form = AddProfessorForm()
        if request.form['action'] == 'delete':
            professor_to_delete = Professor.query.filter_by(id=request.form['id']).first()
            db.session.delete(professor_to_delete)
            db.session.commit()
            flash(f'[PROFESSOR][SUCCESS][DELETE]Professor has been Deleted.{professor_to_delete.name}!', category='success')
        elif request.form['action'] == 'add':
            if form.validate_on_submit():
                # check if the email is already in the database
                name_in_db = Professor.query.filter_by(name=form.name.data).first()
                email_in_db = Professor.query.filter_by(email_address=form.email_address.data).first()
                if email_in_db or name_in_db:
                    flash(f'[ERROR][PROFESSOR][ADD]Email address or Name already exists in the database [ {form.email_address.data} , {form.name.data} ]', category='danger')
                    return redirect(url_for('addprofessor'))
                professor_to_create = Professor(name=form.name.data,
                                        email_address=form.email_address.data,
                                        )
                db.session.add(professor_to_create)
                db.session.commit()
                flash(f'[PROFESSOR][SUCCESS][SIGNUP]Professor has been Added.{form.name.data}!', category='success')
                return redirect(url_for('addprofessor'))
        
            
        if form.errors != {} :
                for error_msg in form.errors.values():
                    flash(f'[PROFESSOR][ERROR][SIGNUP]{error_msg}', category='danger')
                            
        return redirect(url_for('addprofessor'))

    if request.method == 'GET':
        form = AddProfessorForm()
        professors = Professor.query.all()
        
        return render_template('addprofessor.html', form=form , professors=professors)


@app.route('/addadmin', methods=['GET', 'POST'])
@login_required
def addadmin():
    if request.method == 'POST':
        form = AddAdminForm()
        if request.form['action'] == 'delete':
            admin_to_delete = Admin.query.filter_by(id=request.form['id']).first()
            db.session.delete(admin_to_delete)
            db.session.commit()
            flash(f'[ADMIN][SUCCESS][DELETE]Admin has been Deleted.{admin_to_delete.name}!', category='success')
        elif request.form['action'] == 'add':
            if form.validate_on_submit():
                # check if the email is already in the database
                name_in_db = Admin.query.filter_by(name=form.name.data).first()
                email_in_db = Admin.query.filter_by(email_address=form.email_address.data).first()
                if email_in_db or name_in_db:
                    flash(f'[ERROR][ADMIN][ADD]The email address or Name is already in the database [ {form.email_address.data} , {form.name.data} ]', category='danger')
                    return redirect(url_for('addadmin'))
                admin_to_create = Admin(name=form.name.data,
                                        email_address=form.email_address.data,
                                        )
                db.session.add(admin_to_create)
                db.session.commit()
                flash(f'[ADMIN][SUCCESS][SIGNUP]Admin has been Added.{form.name.data}!', category='success')
                return redirect(url_for('addadmin'))
        
            
        if form.errors != {} :
                for error_msg in form.errors.values():
                    flash(f'[ADMIN][ERROR][SIGNUP]{error_msg}', category='danger')
                            
        return redirect(url_for('addadmin'))

    if request.method == 'GET':
        form = AddAdminForm()
        admins = Admin.query.all()
        
        return render_template('addadmin.html', form=form , admins=admins)

    
    


@app.route('/addstudent', methods=['GET', 'POST'])
@login_required
def addstudent():
    red.set('action', '1')
    if request.method == 'POST':
        form = AddStudentForm()
        if request.form['action'] == 'delete':
            student_to_delete = Student.query.filter_by(id=request.form['id']).first()
            db.session.delete(student_to_delete)
            db.session.commit()
            flash(f'[STUDENT][SUCCESS][DELETE]Student has been Deleted.{student_to_delete.name}!', category='success')
        elif request.form['action'] == 'add':
            if form.validate_on_submit():
                email_in_db = Student.query.filter_by(email_address=form.email_address.data).first()
                student_id_in_db = Student.query.filter_by(student_id=form.student_id.data).first()
                
                data = get_encode()
                
                
                if email_in_db  or student_id_in_db:
                    flash(f'[ERROR][Student][ADD]The email address or Student ID is already in the database [ {form.email_address.data} , {form.name.data} ,{form.student_id.data} ]', category='danger')
                    return redirect(url_for('addstudent'))
                if data is None:
                        flash(f'[ERROR][STUDENT][ADD]There is No face', category='danger')
                        return redirect(url_for('addstudent'))
                student_to_create = Student(student_id=form.student_id.data,
                                        name=form.name.data,
                                        email_address=form.email_address.data,
                                        face_encode=data
                                        )
                db.session.add(student_to_create)
                db.session.commit()
                flash(f'[STUDENT][SUCCESS][SIGNUP]Student has been Added.{student_to_create.name}!', category='success')
                return redirect(url_for('addstudent'))
        
            
        if form.errors != {} :
                for error_msg in form.errors.values():
                    flash(f'[STUDENT][ERROR][SIGNUP]{error_msg}', category='danger')
                            
        return redirect(url_for('addstudent'))

    if request.method == 'GET':
        form = AddStudentForm()
        students = Student.query.all()

        return render_template('addstudent.html', form=form , students=students)


@app.route('/course', methods=['GET', 'POST'])
@login_required
def course():
    form = AddCourseForm()
    courses = Course.query.all()
    if request.method == 'GET':
        return render_template('course.html', form=form , courses=courses)
    if request.method == 'POST':
        if request.form['action'] == 'delete':
            course_to_delete = Course.query.filter_by(course_id=request.form['course_id']).first()
            db.session.delete(course_to_delete)
            db.session.commit()
            flash(f'[COURSE][SUCCESS][DELETE]Course has been Deleted.{course_to_delete.course_name}!', category='success')
            return redirect(url_for('course'))
        elif request.form['action'] == 'add':
            if form.validate_on_submit():
                name_in_db = Course.query.filter_by(course_name=form.course_name.data).first()
                course_id_in_db = Course.query.filter_by(course_id=form.course_id.data).first()
                if name_in_db or course_id_in_db:
                    flash(f'[ERROR][COURSE][ADD]The name or the course_id is already in the database [ {form.course_name.data} ][{form.course_id.data}] ', category='danger')
                    return redirect(url_for('course'))

                course_to_create = Course(course_id = form.course_id.data,
                                        course_name=form.course_name.data,
                                        course_day=form.course_day.data,
                                        )
                db.session.add(course_to_create)
                db.session.commit()
                flash(f'[COURSE][SUCCESS][SIGNUP]Course has been Added.{course_to_create.course_name}!', category='success')
                return redirect(url_for('course'))
        elif request.form['action'] == 'delete':
            course_to_delete = Course.query.filter_by(course_id=request.form['course_id']).first()
            db.session.delete(course_to_delete)
            db.session.commit()
            flash(f'[COURSE][SUCCESS][DELETE]Course has been Deleted.{course_to_delete.course_name}!', category='success')
            return redirect(url_for('course'))

        if form.errors != {} :
                for error_msg in form.errors.values():
                    flash(f'[COURSE][ERROR][SIGNUP]{error_msg}', category='danger')

        return redirect(url_for('course'))


@app.route('/assigncoursetoprof', methods=['GET', 'POST'])
@login_required
def assigncoursetoprof():
    def set_prof(name):
        global prof
        prof = name
    def get_prof():
        if 'prof' not in globals():
            return None
        else:
            global prof
            return prof
        

    form = AssignCourseToProfForm()
    form.professor_name.choices = [professor.name for professor in Professor.query.all()]


    courses = Course.query.all()

    if request.method == 'GET':
        return render_template('assigncoursetoprof.html', form=form , courses=courses , assigned_courses = [])
    if request.form['action'] == 'choose':
        prof = form.professor_name.data
        set_prof(prof)
        prof_id = Professor.query.filter_by(name=prof).first().id
        assigned_courses = Course.query.filter_by(prof=prof_id).all()
        return render_template('assigncoursetoprof.html', form=form , courses=courses, assigned_courses=assigned_courses)
    if request.form['action'] == 'assign':
        prof = get_prof()
        if prof is None:
            flash(f'[ERROR][COURSE][ASSIGN]Please choose a professor first', category='danger')
            return redirect(url_for('assigncoursetoprof'))
        prof_id = Professor.query.filter_by(name=prof).first().id
        

        course_id = request.form['course_id']
        course_to_update = Course.query.filter_by(course_id=course_id).first()
        course_to_update.prof = prof_id
        db.session.commit()
        assigned_courses = Course.query.filter_by(prof=prof_id).all()
        flash(f'[COURSE][SUCCESS][ASSIGN]Course has been Assigned.{course_to_update.course_name}!', category='success')
        return render_template('assigncoursetoprof.html', form=form , courses=courses, assigned_courses=assigned_courses)
    if request.form['action'] == 'delete':
        prof = get_prof()
        
        prof_id = Professor.query.filter_by(name=prof).first().id
        
        course_id = request.form['course_id']
        course_to_update = Course.query.filter_by(course_id=course_id).first()
        course_to_update.prof = None
        db.session.commit()
        assigned_courses = Course.query.filter_by(prof=prof_id).all()
        flash(f'[COURSE][SUCCESS][DELETE]Course has been Deleted.{course_to_update.course_name}!', category='success')
        return render_template('assigncoursetoprof.html', form=form , courses=courses, assigned_courses=assigned_courses)
    
    if form.errors != {} :
            for error_msg in form.errors.values():
                flash(f'[COURSE][ERROR][SIGNUP]{error_msg}', category='danger')

    return redirect(url_for('assigncoursetoprof'))


@app.route('/assigncoursetostudent', methods=['GET', 'POST'])
@login_required
def assigncoursetostudent():
    def set_student(name):
        global student
        student = name
    def get_student():
        if 'student' not in globals():
            return None
        else:
            global student
            return student

    form = AssignCourseToStudentForm()
    form.student_name.choices = [student.name for student in Student.query.all()]

    courses = Course.query.all()
    if request.method == 'GET':
        return render_template('assigncoursetostudent.html', form=form , courses=courses , assigned_courses = [])
    if request.form['action'] == 'choose':
        student_name = form.student_name.data
        set_student(student_name)
        student = Student.query.filter_by(name=student_name).first()
        assigned_courses = student.takes
        
        return render_template('assigncoursetostudent.html', form=form , courses=courses, assigned_courses=assigned_courses)
    if request.form['action'] == 'assign':
        student_name = get_student()
        if student_name is None:
            flash(f'[ERROR][COURSE][ASSIGN]Please choose a student first', category='danger')
            return redirect(url_for('assigncoursetostudent'))
        student = Student.query.filter_by(name=student_name).first()

        course_id = request.form['course_id']
        course_to_add = Course.query.filter_by(course_id=course_id).first()
        student.takes.append(course_to_add)
        db.session.commit()
        assigned_courses = student.takes
        flash(f'[COURSE][SUCCESS][ASSIGN]Course has been Assigned.{course_to_add.course_name}!', category='success')
        return render_template('assigncoursetostudent.html', form=form , courses=courses, assigned_courses=assigned_courses)
    if request.form['action'] == 'delete':
        student_name = get_student()
        
        student = Student.query.filter_by(name=student_name).first()
        
        course_id = request.form['course_id']
        course_to_update = Course.query.filter_by(course_id=course_id).first()
        student.takes.remove(course_to_update)
        db.session.commit()
        assigned_courses = student.takes
        flash(f'[COURSE][SUCCESS][DELETE]Course has been Deleted.{course_to_update.course_name}!', category='success')
        return render_template('assigncoursetostudent.html', form=form , courses=courses, assigned_courses=assigned_courses)

    if form.errors != {} :
            for error_msg in form.errors.values():
                flash(f'[COURSE][ERROR][SIGNUP]{error_msg}', category='danger')

    return redirect(url_for('assigncoursetostudent'))



        



@app.route('/video_feed')
def video_feed():
        return Response(wcam(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ai')
def ai():
        course_id = get_course()
        return Response(face_detect(course_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')