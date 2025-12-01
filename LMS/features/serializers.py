from rest_framework import serializers
from user_model.models import ClassName, Student, Course, Teacher

class ClassNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassName
        fields = ['id', 'name']


class StudentSerializer(serializers.ModelSerializer):
    classname = serializers.PrimaryKeyRelatedField(queryset=ClassName.objects.all())

    class Meta:
        model = Student
        fields = ['id', 'name', 'roll_no', 'classname']
        
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'roll_no']

class CourseSerializer(serializers.ModelSerializer):
    classname_name = serializers.CharField(source='classname.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'classname', 'classname_name', 'teacher', 'teacher_name']