from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Post, Comment

class PostListView(ListView):
    model = Post
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Post.CATEGORY_CHOICES
        context['selected_category'] = self.request.GET.get('category', '')
        
        # Featured post (most viewed or latest)
        context['featured_post'] = Post.objects.order_by('-views').first()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment post pageviews
        obj.views += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.order_by('-created_at')
        
        # Suggest related posts in the same category
        context['related_posts'] = Post.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        return context


@login_required
def add_comment(request, slug):
    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        if not text:
            messages.error(request, "Comment text cannot be empty.")
            return redirect('blog_detail', slug=slug)
            
        post = get_object_or_404(Post, slug=slug)
        Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )
        messages.success(request, "Your comment has been added successfully!")
    return redirect('blog_detail', slug=slug)
