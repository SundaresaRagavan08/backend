from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_model.authentication import IsAuthenticated
from user_model.models import ClassName, Student, Course, Teacher
from .serializers import *
from user_model.permissions import IsAdmin, IsTeacherOrAdmin, IsStudent


class CreateClassView(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsTeacherOrAdmin]

    def post(self, request):
        serializer = ClassNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Class created successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request):
        if request.role == 'teacher':
            classes = ClassName.objects.filter(courses__teacher=request.user).distinct()
        elif request.role == 'admin':
            classes = ClassName.objects.all()
        serializer = ClassNameSerializer(classes, many=True)
        return Response(serializer.data)
    
    def delete(self, request):
        class_id = request.data.get('class_id')
        try:
            class_instance = ClassName.objects.get(id=class_id)
            class_instance.delete()
            return Response({"message": "Class deleted successfully"}, status=200)
        except ClassName.DoesNotExist:
            return Response({"error": "Class not found"}, status=404)
    
class ClassStudentsView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request, id):
        students = Student.objects.filter(classname__id=id)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        try:
            class_instance = ClassName.objects.get(id=id)
        except ClassName.DoesNotExist:
            return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        data['classname'] = class_instance.id  # assign class to student

        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
            student.delete()
            return Response({"message": "Student removed from class successfully"}, status=200)
        except Student.DoesNotExist:
            return Response({"error": "Student not found in the specified class"}, status=404)
        
class TeacherView(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsAdmin]

    def get(self, request):
        teachers = Teacher.objects.all()
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Teacher created successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        teacher_id = request.data.get('teacher_id')
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher.delete()
            return Response({"message": "Teacher deleted successfully"}, status=200)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher not found"}, status=404)

class CoursesView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request):
        if request.role == 'teacher':
            courses = Course.objects.filter(teacher=request.user)
        elif request.role == 'student':
            student = Student.objects.get(id=request.user.id)
            courses = Course.objects.filter(classname=student.classname)
        else:
            courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Course created successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        course_id = request.data.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
            course.delete()
            return Response({"message": "Course deleted successfully"}, status=200)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)

class SingleCoursesView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request, id):
        data = Course.objects.filter(pk=id)
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)
    
class CourseForClassView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request, class_id):
        classe = ClassName.objects.get(id=class_id)
        courses = Course.objects.filter(classname=classe)
        print(courses)
        return Response(CourseSerializer(courses, many=True).data)