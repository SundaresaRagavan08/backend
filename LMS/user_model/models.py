from django.db import models


class ClassName(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100,default="Changeme@123")

    def __str__(self):
        return f"{self.name} ({self.roll_no})"


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100,default="Changeme@123")
    classname = models.ForeignKey(ClassName, on_delete=models.CASCADE, related_name="students")

    def __str__(self):
        return f"{self.name} - {self.classname.name}"


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