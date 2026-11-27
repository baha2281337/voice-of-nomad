from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import role_required
from accounts.models import User

from .forms import FeedbackSubmissionForm
from .models import Feedback, StatusHistory, Vote


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


@role_required(User.Role.STUDENT)
@require_http_methods(['GET', 'POST'])
def create_feedback(request):
    form = FeedbackSubmissionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            feedback = form.save(commit=False)
            feedback.created_by = request.user
            feedback.save()
            StatusHistory.objects.create(
                feedback=feedback,
                new_status=feedback.status,
                changed_by=request.user,
            )
        messages.success(request, 'Обращение отправлено администрации.')
        return redirect('home')

    return render(request, 'feedback/create.html', {'form': form})
