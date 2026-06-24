from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Question

class QuestionListView(ListView):
    model = Question
    template_name = 'questions/question_list.html'
    context_object_name = 'questions'
    paginate_by = 10

    def get_queryset(self):
        queryset = Question.objects.all().order_by('-created_at')
        
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['difficulties'] = Question.DIFFICULTY_CHOICES
        context['categories'] = Question.CATEGORY_CHOICES
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'questions/question_detail.html'
    context_object_name = 'question'
