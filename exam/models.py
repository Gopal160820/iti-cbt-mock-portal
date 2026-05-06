from django.db import models
from django.utils import timezone


# =========================
# 👤 STUDENT
# =========================
class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  # store hashed password

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


# =========================
# 📘 EXAM
# =========================
class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    duration = models.PositiveIntegerField(help_text="Minutes")
    total_questions = models.PositiveIntegerField()

    is_active = models.BooleanField(default=False)

    negative_marking = models.FloatField(default=0)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    shuffle_questions = models.BooleanField(default=True)  # 🎲 Randomization
    shuffle_options = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.title


# =========================
# ❓ QUESTION
# =========================
class Question(models.Model):

    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'

    LEVEL_CHOICES = [
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    text = models.TextField()

    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)

    correct_option = models.PositiveSmallIntegerField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        default=1
    )
    marks = models.FloatField(default=1)
    difficulty = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=MEDIUM)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.text[:60]


# =========================
# 📊 RESULT / ATTEMPT
# =========================
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    attempt_no = models.PositiveIntegerField(default=1)

    score = models.FloatField(default=0)
    total = models.FloatField(default=0)
    percentage = models.FloatField(default=0)

    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    unanswered = models.IntegerField(default=0)

    is_submitted = models.BooleanField(default=False)

    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)

    time_taken = models.IntegerField(default=0, help_text="Seconds")

    ip_address = models.GenericIPAddressField(null=True, blank=True)  # 🛡️ Anti-cheat
    device_info = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ['student', 'exam', 'attempt_no']
        ordering = ['-score']  # 🏆 Leaderboard ready

    def __str__(self):
        return f"{self.student.name} - {self.exam.title} (Attempt {self.attempt_no})"


# =========================
# 🧠 ANSWER
# =========================
class Answer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_option = models.PositiveSmallIntegerField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        null=True,
        blank=True
    )

    is_correct = models.BooleanField(default=False)
    marks_awarded = models.FloatField(default=0)

    answered_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.result.student.name} - Q{self.question.id}"


# =========================
# 🏆 LEADERBOARD (OPTIONAL CACHE TABLE)
# =========================
class Leaderboard(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    score = models.FloatField()
    percentage = models.FloatField()

    rank = models.PositiveIntegerField()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"{self.rank}. {self.student.name} - {self.score}"