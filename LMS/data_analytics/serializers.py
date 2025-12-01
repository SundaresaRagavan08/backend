from rest_framework import serializers
from .models import Assignment, Submission, Attendance

class AssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    class_name = serializers.CharField(source='classname.name', read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['teacher_name', 'course_name', 'class_name']


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    teacher_name = serializers.CharField(source='assignment.teacher.username', read_only=True)
    course_name = serializers.CharField(source='assignment.course.name', read_only=True)

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['student_name', 'assignment_title', 'teacher_name', 'course_name']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['student_name', 'course_name']
