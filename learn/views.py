from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count
from django.http import JsonResponse
from .models import Language, Topic, SubTopic

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

    # Fetch active subtopic if query param exists
    subtopic_slug = request.GET.get('subtopic')
    active_subtopic = None
    if subtopic_slug and active_topic:
        active_subtopic = active_topic.subtopics.filter(slug=subtopic_slug).first()

    # AJAX Response support for instant topic/subtopic load
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
        if active_subtopic:
            sub_content = active_subtopic.content_code if active_subtopic.content_type == 'code' else active_subtopic.content
            return JsonResponse({
                'title': active_subtopic.title,
                'difficulty': active_topic.get_difficulty_display(),
                'content': sub_content,
                'order': active_subtopic.order,
                'is_subtopic': True
            })

        if not active_topic:
            return JsonResponse({'error': 'No content available'}, status=404)
        
        subtopics_list = []
        if active_topic:
            for sub in active_topic.subtopics.all():
                sub_content = sub.content_code if sub.content_type == 'code' else sub.content
                subtopics_list.append({
                    'title': sub.title,
                    'slug': sub.slug,
                    'content': sub_content,
                })
        
        topic_content = active_topic.content_code if active_topic.content_type == 'code' else active_topic.content
        
        return JsonResponse({
            'title': active_topic.title,
            'difficulty': active_topic.get_difficulty_display(),
            'content': topic_content,
            'order': active_topic.order,
            'subtopics': subtopics_list,
            'is_subtopic': False
        })

    # Standard context context
    context = {
        'language': language,
        'topics': topics,
        'active_topic': active_topic,
        'active_subtopic': active_subtopic,
    }
    return render(request, 'learn/learn_detail.html', context)
