from flask_app import db, bcrypt , login_manager
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin




@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))





class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        username = db.Column(db.String(30), nullable=False, unique=True)
        password_hash = db.Column(db.String(60), nullable=False)
        admin_owner = db.Column(db.Integer, db.ForeignKey('admin.id'))
        professor_owner = db.Column(db.Integer, db.ForeignKey('professor.id'))
            

        @property
        def password(self):
            return self.password


        @password.setter
        def password(self, plain_txt_password):
            self.password_hash = bcrypt.generate_password_hash(plain_txt_password).decode('utf-8')

        def check_password(self, attempted_password):
            return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Admin(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        name = db.Column(db.String(30), nullable=False, unique=True)
        email_address = db.Column(db.String(60), nullable=False, unique=True)
        user_admin = db.relationship('User', backref='admin', lazy=True)



class Professor(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        name = db.Column(db.String(30), nullable=False, unique=True)
        email_address = db.Column(db.String(60), nullable=False, unique=True)
        user_professor = db.relationship('User', backref='professor', lazy=True)
        courses_g = db.relationship('Course', backref='professor', lazy=True)


course_student = db.Table('course_student',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

class Student(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        student_id = db.Column(db.String(15), nullable=False, unique=True)
        name = db.Column(db.String(30), nullable=False, unique=True)
        email_address = db.Column(db.String(60), nullable=False, unique=True)
        face_encode = db.Column(db.String, unique=True)
        takes = db.relationship('Course', secondary=course_student, backref='takers')
        
class Course(db.Model):
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        course_id = db.Column(db.String(15), nullable=False, unique=True)
        course_name = db.Column(db.String(30), nullable=False, unique=True)
        course_day = db.Column(db.String(10))

        prof = db.Column(db.Integer, db.ForeignKey('professor.id'))
        
        







class Attendance_Log(db.Model , SerializerMixin):
        
        serialize_only = ('name', 'date', 'time','course_id','student_id')
        
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        student_id = db.Column(db.String(15), nullable=False)
        name = db.Column(db.String(30), nullable=False)
        course_id = db.Column(db.String(15), nullable=False)

        date = db.Column(db.String(20), nullable=False)
        time = db.Column(db.String(20), nullable=False)

        def __repr__(self):
                return f"{self.name} {self.date} {self.time}"
        
