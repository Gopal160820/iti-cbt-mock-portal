#http://127.0.0.1:8000//admin/exam/exam/2/bulk-upload/

from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.html import format_html

from .models import Student, Exam, Question, Result, Answer


# =========================
# 👤 STUDENT ADMIN
# =========================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'student_id', 'created_at')
    search_fields = ('name', 'student_id')


# =========================
# 📘 EXAM ADMIN (WITH BULK UPLOAD BUTTON)
# =========================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'duration', 'total_questions', 'is_active', 'upload_link')

    def upload_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Upload Questions</a>',
            f"{obj.id}/bulk-upload/"
        )
    upload_link.short_description = "Bulk Upload"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:exam_id>/bulk-upload/',
                self.admin_site.admin_view(self.bulk_upload),
                name='exam_bulk_upload'
            ),
        ]
        return custom_urls + urls


    # =========================
    # 📥 BULK UPLOAD FUNCTION
    # =========================
    def bulk_upload(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)

        if request.method == "POST":
            text = request.POST.get("bulk_text")

            if not text:
                messages.error(request, "No data provided ❌")
                return redirect(request.path)

            lines = text.strip().split("\n")

            q = None
            options = {}
            correct_ans = None
            count = 0

            for line in lines:
                line = line.strip()

                if line.startswith("Q:"):
                    # save previous question
                    if q and correct_ans:
                        Question.objects.create(
                            exam=exam,
                            text=q,
                            option1=options.get("A", ""),
                            option2=options.get("B", ""),
                            option3=options.get("C", ""),
                            option4=options.get("D", ""),
                            correct_option=self.map_correct(correct_ans),
                            marks=1
                        )
                        count += 1

                    # reset
                    q = line.replace("Q:", "").strip()
                    options = {}
                    correct_ans = None

                elif line.startswith("A)"):
                    options["A"] = line[2:].strip()
                elif line.startswith("B)"):
                    options["B"] = line[2:].strip()
                elif line.startswith("C)"):
                    options["C"] = line[2:].strip()
                elif line.startswith("D)"):
                    options["D"] = line[2:].strip()

                elif line.startswith("ANS:"):
                    correct_ans = line.replace("ANS:", "").strip().upper()

            # save last question
            if q and correct_ans:
                Question.objects.create(
                    exam=exam,
                    text=q,
                    option1=options.get("A", ""),
                    option2=options.get("B", ""),
                    option3=options.get("C", ""),
                    option4=options.get("D", ""),
                    correct_option=self.map_correct(correct_ans),
                    marks=1
                )
                count += 1

            messages.success(request, f"✅ {count} Questions uploaded successfully!")
            return redirect("/admin/exam/exam/")

        return render(request, "admin/upload_questions.html", {"exam": exam})


    # =========================
    # 🔄 MAP ANSWER A/B/C/D → 1/2/3/4
    # =========================
    def map_correct(self, ans):
        return {
            "A": 1,
            "B": 2,
            "C": 3,
            "D": 4
        }.get(ans, 1)


# =========================
# ❓ QUESTION ADMIN
# =========================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'short_text', 'correct_option', 'marks')
    search_fields = ('text',)
    list_filter = ('exam',)

    def short_text(self, obj):
        return obj.text[:50]


# =========================
# 📊 RESULT ADMIN
# =========================
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'exam',
        'score',
        'percentage',
        'is_submitted',
        'started_at',
        'submitted_at',
        'ip_address'
    )

    list_filter = ('exam', 'is_submitted')
    search_fields = ('student__name', 'student__student_id')


# =========================
# 🧠 ANSWER ADMIN
# =========================
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'result',
        'question',
        'selected_option',
        'is_correct',
        'marks_awarded'
    )

    list_filter = ('is_correct',)
    search_fields = ('question__text',)