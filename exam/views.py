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
