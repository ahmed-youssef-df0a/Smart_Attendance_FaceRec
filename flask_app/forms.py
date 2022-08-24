
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField , SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo 
from flask_app.models import   Admin , Professor , Student 



def get_admin_list():
    admin_list = Admin.query.all()
    admin_list = [admin.name for admin in admin_list]
    return admin_list




def get_professor_list():
    professor_list = Professor.query.all()
    professor_list = [professor.name for professor in professor_list]
    return professor_list

def get_student_list():
    student_list = Student.query.all()
    student_list = [student.name for student in student_list]
    return student_list





class LoginForm(FlaskForm):
    
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField(' Sign In')





class AddAdminUserForm(FlaskForm):
    admin_name = SelectField('choose admin name', choices=get_admin_list(), validators = [DataRequired()])
    username = StringField('User Name', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Add User')




class AddProfessorUserForm(FlaskForm):
    professor_name = SelectField('choose Professor name', choices=get_professor_list(), validators = [DataRequired()])
    username = StringField('User Name', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Add User')



    
class AddProfessorForm(FlaskForm):
    name = StringField('Professor Name', validators=[DataRequired()])
    email_address = StringField('Email Address', validators=[DataRequired() ,Email()])
    submit = SubmitField('Add')




class AddAdminForm(FlaskForm):
    name = StringField('Admin Name', validators=[DataRequired()])
    email_address = StringField('Email Address', validators=[DataRequired() ,Email()])
    submit = SubmitField('Add')


    
class AddStudentForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    name = StringField('Student Name', validators=[DataRequired()])
    email_address = StringField('Email Address', validators=[DataRequired() ,Email()])
    submit = SubmitField('Add')

class AddCourseForm(FlaskForm):
    course_id = StringField('Course ID', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired()])
    course_day =  SelectField('choose Professor name', choices=('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday'), validators = [DataRequired()])
    submit = SubmitField('Add')

class AssignCourseToProfForm(FlaskForm):
    professor_name = SelectField('choose Professor name', choices=get_professor_list(), validators = [DataRequired()])
    submit = SubmitField('Choose')

class AssignCourseToStudentForm(FlaskForm):
    student_name = SelectField('choose Student name', choices=get_student_list(), validators = [DataRequired()])
    submit = SubmitField('Choose')

# class ChooseCourseForm(FlaskForm):
#     course_name = SelectField('choose Course name', choices=get_course_list(), validators = [DataRequired()])
#     submit = SubmitField('Choose')