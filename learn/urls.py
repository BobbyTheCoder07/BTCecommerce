from django.urls import path
from . import views

urlpatterns = [
    path('', views.LearnHomeView.as_view(), name='learn_home'),
    path('<slug:lang_slug>/', views.learn_detail_view, name='learn_detail'),
    path('<slug:lang_slug>/<slug:topic_slug>/', views.learn_detail_view, name='topic_detail'),
]
