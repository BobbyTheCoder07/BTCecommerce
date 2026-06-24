from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
import os

from .models import Note

class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 6

    def get_queryset(self):
        queryset = Note.objects.all().order_by('-created_at')
        
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(programming_language=language)
            
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['languages'] = Note.LANGUAGE_CHOICES
        context['difficulties'] = Note.DIFFICULTY_CHOICES
        context['selected_language'] = self.request.GET.get('language', '')
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')
        return context


class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'


@login_required
def download_note_pdf(request, slug):
    note = get_object_or_404(Note, slug=slug)
    if not note.pdf_file:
        messages.error(request, "This note does not have a downloadable PDF available.")
        return redirect('note_detail', slug=slug)
        
    try:
        response = FileResponse(note.pdf_file.open(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{note.slug}.pdf"'
        return response
    except FileNotFoundError:
        raise Http404("PDF file does not exist on the server.")
