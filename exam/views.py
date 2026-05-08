<<<<<<< HEAD
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
# Registration view for new students
def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			Student.objects.create(user=user)
			messages.success(request, 'Registration successful. You can now log in.')
			return redirect('login')
	else:
		form = UserCreationForm()
	return render(request, 'exam/register.html', {'form': form})
from django.contrib.auth.decorators import login_required
# Homepage: List all available exams
@login_required
def exam_list(request):
	exams = Exam.objects.all()
	return render(request, 'exam/exam_list.html', {'exams': exams})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Exam, Question, Result, Student
from django.contrib.auth.models import User
from django.utils import timezone

@login_required
def take_exam(request, exam_id):
	exam = get_object_or_404(Exam, id=exam_id)
	questions = exam.questions.all()
	if request.method == 'POST':
		score = 0
		total = questions.count()
		for question in questions:
			selected = request.POST.get(f'question_{question.id}')
			if selected == question.correct_option:
				score += 1
		percent = (score / total) * 100 if total > 0 else 0
		student, _ = Student.objects.get_or_create(user=request.user)
		Result.objects.create(student=student, exam=exam, score=percent)
		return redirect('exam_result', exam_id=exam.id)
	return render(request, 'exam/take_exam.html', {'exam': exam, 'questions': questions})

@login_required
def exam_result(request, exam_id):
	exam = get_object_or_404(Exam, id=exam_id)
	student = get_object_or_404(Student, user=request.user)
	result = Result.objects.filter(student=student, exam=exam).last()
	return render(request, 'exam/exam_result.html', {'exam': exam, 'result': result})
=======
from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import Student, Exam, Question, Result, Answer
import random


# =========================
# 🛡️ SESSION CHECK
# =========================
def is_authenticated(request):
    return request.session.get('is_logged_in') and request.session.get('student_id')


# =========================
# 🔐 LOGIN VIEW
# =========================
def login_view(request):
    if request.method == "POST":
        sid = request.POST.get('sid', '').strip()
        name = request.POST.get('name', '').strip()

        student = Student.objects.filter(student_id=sid, name=name).first()

        if not student:
            return render(request, 'exam/login.html', {
                'error': 'Invalid Student ID or Name'
            })

        request.session.flush()
        request.session['student_id'] = student.id
        request.session['student_name'] = student.name
        request.session['student_sid'] = student.student_id
        request.session['is_logged_in'] = True

        return redirect('exam:select_exam')

    return render(request, 'exam/login.html')


# =========================
# 📚 SELECT EXAM VIEW
# =========================
def select_exam_view(request):
    if not is_authenticated(request):
        return redirect('exam:login')

    student = get_object_or_404(Student, id=request.session['student_id'])

    exams = Exam.objects.filter(is_active=True).order_by('-id')

    results = Result.objects.filter(
        student=student,
        is_submitted=True
    ).select_related('exam')

    result_dict = {r.exam_id: r for r in results}
    attempted_exam_ids = [r.exam_id for r in results]
    upcoming_exams = exams.exclude(id__in=attempted_exam_ids).count()
    achieved_count = len(attempted_exam_ids)

    context = {
        'student': student,
        'exams': exams,
        'result_dict': result_dict,
        'today': timezone.now(),
        'upcoming_exams': upcoming_exams,
        'achieved_count': achieved_count,
    }

    return render(request, 'exam/select_exam.html', context)


# =========================
# 🌐 GET CLIENT IP
# =========================
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# =========================
# 🧠 EXAM VIEW
# =========================
def exam_view(request, exam_id):
    if not is_authenticated(request):
        return redirect('exam:login')

    student = get_object_or_404(Student, id=request.session['student_id'])
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)

    # Prevent re-attempt
    if Result.objects.filter(student=student, exam=exam, is_submitted=True).exists():
        return render(request, 'exam/error.html', {
            'msg': 'You have already completed this exam.'
        })

    result, created = Result.objects.get_or_create(
        student=student,
        exam=exam,
        is_submitted=False,
        defaults={
            'started_at': timezone.now(),
            'ip_address': get_client_ip(request),
            'device_info': request.META.get('HTTP_USER_AGENT', '')
        }
    )

    # Load questions once
    if 'questions' not in request.session:
        qs = list(exam.questions.all())

        if exam.shuffle_questions:
            random.shuffle(qs)

        qs = qs[:exam.total_questions]

        request.session['questions'] = [q.id for q in qs]
        request.session['result_id'] = result.id

    questions = Question.objects.filter(id__in=request.session['questions'])

    return render(request, 'exam/exam.html', {
        'exam': exam,
        'questions': questions,
        'student': student,
        'duration': exam.duration * 60  # seconds for timer
    })


# =========================
# 📊 SUBMIT VIEW
# =========================
@transaction.atomic
def submit_view(request):
    if not is_authenticated(request) or request.method != "POST":
        return redirect('exam:login')

    result_id = request.session.get('result_id')
    q_ids = request.session.get('questions', [])

    if not result_id:
        return redirect('exam:login')

    result = get_object_or_404(Result, id=result_id)

    if result.is_submitted:
        return render(request, 'exam/error.html', {'msg': 'Exam already submitted.'})

    score = 0
    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    total_marks = 0

    for qid in q_ids:
        q = get_object_or_404(Question, id=qid)

        selected = request.POST.get(f"q_{qid}")
        selected = int(selected) if selected else None

        total_marks += q.marks

        is_correct = False
        marks_awarded = 0

        if not selected:
            skipped_count += 1

        elif selected == q.correct_option:
            is_correct = True
            marks_awarded = q.marks
            score += q.marks
            correct_count += 1

        else:
            wrong_count += 1
            neg = result.exam.negative_marking or 0
            score -= neg
            marks_awarded = -neg

        Answer.objects.create(
            result=result,
            question=q,
            selected_option=selected,
            is_correct=is_correct,
            marks_awarded=marks_awarded
        )

    # Time taken
    time_taken = int((timezone.now() - result.started_at).total_seconds())

    result.score = max(score, 0)
    result.total = total_marks
    result.percentage = round((result.score / total_marks) * 100, 2) if total_marks else 0

    result.correct_answers = correct_count
    result.wrong_answers = wrong_count
    result.unanswered = skipped_count

    result.time_taken = time_taken
    result.is_submitted = True
    result.submitted_at = timezone.now()

    result.save()

    # Clear session
    # Only remove exam-related session
    request.session.pop('questions', None)
    request.session.pop('result_id', None)

    return redirect('exam:report_card', result_id=result.id)


# =========================
# 🧾 REPORT CARD VIEW
# =========================
def report_card_view(request, result_id):
    if not is_authenticated(request):
        return redirect('exam:login')

    result = get_object_or_404(
        Result,
        id=result_id,
        student_id=request.session['student_id']
    )

    context = {
        'result': result,
        'correct': result.correct_answers,
        'wrong': result.wrong_answers,
        'skipped': result.unanswered
    }

    return render(request, 'exam/report_card.html', context)


# =========================
# 🔍 ANALYSIS VIEW
# =========================
def analysis_view(request, result_id):
    if not is_authenticated(request):
        return redirect('exam:login')

    result = get_object_or_404(
        Result,
        id=result_id,
        student_id=request.session['student_id']
    )

    answers = Answer.objects.filter(result=result).select_related('question')

    context = {
        'result': result,
        'answers': answers,
        'correct': result.correct_answers,
        'wrong': result.wrong_answers,
        'skipped': result.unanswered
    }

    return render(request, 'exam/analysis.html', context)


# =========================
# 🚪 LOGOUT
# =========================
def logout_view(request):
    request.session.flush()
    return redirect('exam:login')


# =========================
# 🚨 ERROR VIEW
# =========================
def error_view(request):
    msg = request.GET.get('msg', 'Something went wrong.')
    return render(request, 'exam/error.html', {'msg': msg})
>>>>>>> ce273ed71ba1f53413829f679ae12dd266591d37
