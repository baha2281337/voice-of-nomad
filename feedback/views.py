from django.db.models import Count
from django.shortcuts import render

from .models import Feedback, Vote


def home(request):
    feedback_with_votes = Feedback.objects.select_related(
        'category',
        'created_by',
    ).annotate(vote_count=Count('votes'))

    context = {
        'total_count': Feedback.objects.count(),
        'active_count': Feedback.objects.filter(
            status__in=(
                Feedback.Status.UNDER_REVIEW,
                Feedback.Status.ACCEPTED,
                Feedback.Status.IN_PROGRESS,
            ),
        ).count(),
        'resolved_count': Feedback.objects.filter(status=Feedback.Status.RESOLVED).count(),
        'vote_count': Vote.objects.count(),
        'latest_feedback': feedback_with_votes.order_by('-created_at')[:4],
        'popular_proposals': feedback_with_votes.filter(
            kind=Feedback.Kind.PROPOSAL,
        ).order_by('-vote_count', '-created_at')[:3],
        'resolved_feedback': feedback_with_votes.filter(
            status=Feedback.Status.RESOLVED,
        ).order_by('-updated_at')[:3],
    }
    return render(request, 'home.html', context)
