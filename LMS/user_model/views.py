from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Admin, Teacher, Student
from .authentication import generate_token, IsAuthenticated
from django.contrib.auth.hashers import check_password

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('roll_no')
        roll_no = request.data.get('roll_no')
        password = request.data.get('password')

        user, role = None, None

        # ADMIN LOGIN
        admin = Admin.objects.filter(username=username).first()
        if admin and (check_password(password, admin.password) or password==admin.password):
            user, role, name = admin, "admin", admin.username

        # TEACHER LOGIN
        if not user:
            teacher = Teacher.objects.filter(roll_no=roll_no).first()
            if teacher and (check_password(password, teacher.password) or password==teacher.password):
                user, role, name = teacher, "teacher", teacher.name

        # STUDENT LOGIN
        if not user:
            student = Student.objects.filter(roll_no=roll_no).first()
            if student and (check_password(password, student.password) or password==student.password):
                user, role, name = student, "student", student.name

        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token = generate_token(user, role)
        return Response({"token": token, "role": role, "name": name})

class GetProfile(APIView):
    authentication_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        role = request.role
        
        if role == "teacher":
            profile_data = {
                "id": user.id,
                "name": user.name,
                "roll_no": user.roll_no,
            }
        elif role == "admin":
            profile_data = {
                "id": user.id,
                "username": user.username,
            }
        elif role == "student":
            profile_data = {
                "id": user.id,
                "name": user.name,
                "roll_no": user.roll_no,
                "class_enrolled": user.classname.name,
            }
        else:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(profile_data)

