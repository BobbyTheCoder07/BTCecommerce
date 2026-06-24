from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count
from django.http import JsonResponse
from .models import Language, Topic

class LearnHomeView(TemplateView):
    template_name = 'learn/learn_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch active languages and annotate with their topic count
        context['languages'] = Language.objects.filter(is_active=True).annotate(
            topic_count=Count('topics')
        )
        return context


def learn_detail_view(request, lang_slug, topic_slug=None):
    language = get_object_or_404(Language, slug=lang_slug, is_active=True)
    topics = language.topics.all()

    # Get active topic (default to first topic in ordered list if none chosen)
    if topic_slug:
        active_topic = get_object_or_404(Topic, language=language, slug=topic_slug)
    else:
        active_topic = topics.first()

    # AJAX Response support for instant topic load
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
        if not active_topic:
            return JsonResponse({'error': 'No content available'}, status=404)
        
        return JsonResponse({
            'title': active_topic.title,
            'difficulty': active_topic.get_difficulty_display(),
            'content': active_topic.content,
            'order': active_topic.order
        })

    # Standard context context
    context = {
        'language': language,
        'topics': topics,
        'active_topic': active_topic,
    }
    return render(request, 'learn/learn_detail.html', context)
