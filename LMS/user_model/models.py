from django.db import models
from django.contrib.auth.hashers import make_password

class ClassName(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100,default="Changeme@123")

    def save(self, *args, **kwargs):
        # Hash only if not hashed already
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100,default="Changeme@123")
    classname = models.ForeignKey(ClassName, on_delete=models.CASCADE, related_name="students")

    def __str__(self):
        return f"{self.name} - {self.classname.name}"
    
    def save(self, *args, **kwargs):
        # Hash only if not hashed already
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Course(models.Model):
    name = models.CharField(max_length=100)
    classname = models.ForeignKey(ClassName, on_delete=models.CASCADE, related_name="courses")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return f"{self.name} ({self.classname.name})"

class Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100,default="Changeme@123")


    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        # Hash only if not hashed already
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
