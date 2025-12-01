from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_model.authentication import IsAuthenticated
from django.db.models import Avg

from user_model.permissions import IsAdmin, IsTeacherOrAdmin, IsStudent
from user_model.models import Teacher, Student, ClassName, Course, Admin
from django.db import models
from .models import Assignment, Submission, Attendance
from .serializers import AssignmentSerializer, SubmissionSerializer, AttendanceSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Avg, Count, Q


class AssignmentView(APIView):
    authentication_classes = [IsAuthenticated]


    def get(self, request, course_id):
        role = request.role
        user = request.user

        if role == "admin":
            assignments = Assignment.objects.filter(course__id=course_id)
        elif role == "teacher":
            assignments = Assignment.objects.filter(teacher=user, course__id=course_id)
        elif role == "student":
            assignments = Assignment.objects.filter(classname=user.classname, course__id=course_id)
        else:
            return Response({"error": "Invalid role"}, status=403)

        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    def post(self, request, course_id):
        if request.role != "teacher":
            return Response({"error": "Only teachers can create assignments"}, status=403)

        teacher = request.user
        data = request.data.copy()
        data['teacher'] = teacher.id
        data['course'] = course_id
        data['classname'] = Course.objects.get(id=course_id).classname.id 

        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Assignment created successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, course_id):
        if request.role != "teacher":
            return Response({"error": "Only teachers can delete assignments"}, status=403)

        assignment_id = request.data.get("assignment_id")
        try:
            assignment = Assignment.objects.get(id=course_id, teacher=request.user)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found or unauthorized"}, status=404)

        assignment.delete()
        return Response({"message": "Assignment deleted successfully"}, status=200)


class SubmissionView(APIView):
    authentication_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, course_id):
        role = request.role
        user = request.user

        if role == "admin":
            submissions = Submission.objects.filter(assignment__id=course_id)
        elif role == "teacher":
            submissions = Submission.objects.filter(assignment__teacher=user,assignment__course__id=course_id)
        elif role == "student":
            submissions = Submission.objects.filter(student=user,assignment__id=course_id)
        else:
            return Response({"error": "Invalid role"}, status=403)

        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request, course_id):
        try:
            if request.role != "student":
                return Response({"error": "Only students can submit assignments"}, status=403)

            data = request.data.copy()
            print(data)
            data["student"] = request.user.id
            serializer = SubmissionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Submission uploaded successfully"}, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=500)
    
    def delete(self, request, course_id):
        if request.role != "student":
            return Response({"error": "Only students can delete submissions"}, status=403)

        try:
            submission = Submission.objects.get(id=course_id, student=request.user)
        except Submission.DoesNotExist:
            return Response({"error": "Submission not found or unauthorized"}, status=404)

        submission.delete()
        return Response({"message": "Submission deleted successfully"}, status=200)


class GradeSubmissionView(APIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsTeacherOrAdmin]

    def post(self, request, submission_id):
        try:
            submission = Submission.objects.get(pk=submission_id)
        except Submission.DoesNotExist:
            return Response({"error": "Submission not found"}, status=404)

        if request.role == "teacher" and submission.assignment.teacher != request.user:
            return Response({"error": "Unauthorized to grade this submission"}, status=403)

        submission.marks_obtained = request.data.get("marks_obtained")
        submission.feedback = request.data.get("feedback", "")
        submission.is_graded = True
        submission.save()

        return Response({"message": "Submission graded successfully"})


class AttendanceView(APIView):
    authentication_classes = [IsAuthenticated]

    def get(self, request,course_id):
        role = request.role
        user = request.user

        if role == "admin" or role == "teacher":
            attendance = Attendance.objects.filter(course__id=course_id)
        elif role == "student":
            attendance = Attendance.objects.filter(student=user, course__id=course_id)
        else:
            return Response({"error": "Invalid role"}, status=403)

        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def post(self, request, course_id):
        try:
            if request.role != "teacher":
                return Response({"error": "Only teachers can mark attendance"}, status=403)
            data = request.data.copy()
            data['course'] = course_id
            serializer = AttendanceSerializer(data=data)
            print(serializer)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Attendance marked successfully"}, status=201)
            print(serializer.errors)
            return Response(serializer.errors, status=400)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=500)
    
class DashboardDataView(APIView):
    authentication_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        role = request.role

        if not role or not user_id:
            return Response({'error': 'role and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        if role.lower() == 'student':
            try:
                student = Student.objects.get(id=user_id)
            except Student.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

            submissions = Submission.objects.filter(student=student)
            attendance = Attendance.objects.filter(student=student)
            assignments = Assignment.objects.filter(classname=student.classname)

            data = {
                "student_name": student.name,
                "class": student.classname.name,
                "total_courses": Course.objects.filter(classname=student.classname).count(),
                "total_assignments": assignments.count(),
                "assignments_submitted": submissions.count(),
                "submission_completion_rate": (
                    (submissions.count() / assignments.count()) * 100 if assignments.exists() else 0
                ),
                "average_marks": submissions.aggregate(avg_marks=Avg('marks_obtained'))['avg_marks'] or 0,
                "attendance_percentage": (
                    (attendance.filter(status="Present").count() / attendance.count()) * 100
                    if attendance.exists() else 0
                ),
                "recent_feedbacks": list(submissions.exclude(feedback=None)
                                         .values('assignment__title', 'feedback', 'marks_obtained')[:5]),
            }
            return Response(data)

        elif role.lower() == 'teacher':
            try:
                teacher = Teacher.objects.get(id=user_id)
            except Teacher.DoesNotExist:
                return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

            courses = Course.objects.filter(teacher=teacher)
            assignments = Assignment.objects.filter(teacher=teacher)
            submissions = Submission.objects.filter(assignment__in=assignments)
            attendance = Attendance.objects.filter(course__in=courses)

            data = {
                "teacher_name": teacher.name,
                "total_courses": courses.count(),
                "total_students": Student.objects.filter(classname__in=courses.values_list('classname', flat=True)).distinct().count(),
                "total_assignments_given": assignments.count(),
                "total_submissions_received": submissions.count(),
                "avg_marks_across_assignments": submissions.aggregate(avg_marks=Avg('marks_obtained'))['avg_marks'] or 0,
                "attendance_overview": list(attendance.values('course__name')
                                             .annotate(present_count=Count('id', filter=Q(status='Present')),
                                                       absent_count=Count('id', filter=Q(status='Absent')))),
                "recent_assignments": list(assignments.values('title', 'course__name', 'deadline').order_by('-id')[:5]),
            }
            return Response(data)

        elif role.lower() == 'admin':
            try:
                admin = Admin.objects.get(id=user_id)
            except Admin.DoesNotExist:
                return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)

            total_students = Student.objects.count()
            total_teachers = Teacher.objects.count()
            total_courses = Course.objects.count()
            total_assignments = Assignment.objects.count()
            total_submissions = Submission.objects.count()

            avg_attendance = Attendance.objects.aggregate(
                present_ratio=Count('id', filter=Q(status='Present')),
                total=Count('id')
            )
            attendance_percent = (
                (avg_attendance['present_ratio'] / avg_attendance['total']) * 100
                if avg_attendance['total'] else 0
            )

            top_courses = (
                Submission.objects.values('assignment__course__name')
                .annotate(total_submissions=Count('id'))
                .order_by('-total_submissions')[:5]
            )

            data = {
                "admin_name": admin.username,
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_courses": total_courses,
                "total_assignments": total_assignments,
                "total_submissions": total_submissions,
                "average_attendance_percent": round(attendance_percent, 2),
                "top_courses_by_activity": list(top_courses),
                "class_wise_strength": list(ClassName.objects.annotate(
                    student_count=Count('students')).values('name', 'student_count')),
                "recent_assignments": list(Assignment.objects.values(
                    'title', 'teacher__name', 'course__name', 'deadline').order_by('-id')[:5]),
            }
            return Response(data)

        else:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)