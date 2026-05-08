from django.urls import path
from . import views

<<<<<<< HEAD
urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('result/<int:exam_id>/', views.exam_result, name='exam_result'),
=======
app_name = "exam"

urlpatterns = [

    # =========================
    # 🔐 AUTH
    # =========================
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # =========================
    # 📚 EXAM SELECTION
    # =========================
    path('select-exam/', views.select_exam_view, name='select_exam'),

    # =========================
    # 🧠 EXAM (IMPORTANT FIX)
    # =========================
    path('exam/<int:exam_id>/', views.exam_view, name='exam'),

    # =========================
    # 📊 SUBMISSION & RESULT
    # =========================
    path('submit/', views.submit_view, name='submit'),
    path('report/<int:result_id>/', views.report_card_view, name='report_card'),
    path('analysis/<int:result_id>/', views.analysis_view, name='analysis'),

    # =========================
    # 🚨 ERROR
    # =========================
    path('error/', views.error_view, name='error'),
>>>>>>> ce273ed71ba1f53413829f679ae12dd266591d37
]