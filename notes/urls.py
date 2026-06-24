from django.urls import path
from . import views

urlpatterns = [
    path('', views.NoteListView.as_view(), name='note_list'),
    path('<slug:slug>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('<slug:slug>/download/', views.download_note_pdf, name='note_download_pdf'),
]
