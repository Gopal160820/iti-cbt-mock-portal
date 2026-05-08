from django.contrib import admin
from .models import Exam, Question, Student, Result

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
	list_display = ("title", "start_time", "end_time")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ("text", "exam", "correct_option")
	list_filter = ("exam",)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("user",)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
	list_display = ("student", "exam", "score", "taken_at")
