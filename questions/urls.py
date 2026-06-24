from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuestionListView.as_view(), name='question_list'),
    path('<slug:slug>/', views.QuestionDetailView.as_view(), name='question_detail'),
]
