from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()

	def __str__(self):
		return self.title

class Question(models.Model):
	exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
	text = models.TextField()
	option_a = models.CharField(max_length=200)
	option_b = models.CharField(max_length=200)
	option_c = models.CharField(max_length=200)
	option_d = models.CharField(max_length=200)
	correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])

	def __str__(self):
		return self.text

class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	# Add more student-specific fields if needed

	def __str__(self):
		return self.user.username

class Result(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
	score = models.FloatField()
	taken_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.student} - {self.exam} - {self.score}"
