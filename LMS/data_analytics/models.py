from django.db import models
from user_model.models import Teacher, Student, ClassName, Course

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)
    deadline = models.DateTimeField()
    max_marks = models.PositiveIntegerField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classname = models.ForeignKey(ClassName, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.classname.name}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    is_graded = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"