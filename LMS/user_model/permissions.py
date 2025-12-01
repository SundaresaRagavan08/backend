from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.role == "admin"
    
class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.role == "teacher" or request.role == "admin"
    
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.role == "student"