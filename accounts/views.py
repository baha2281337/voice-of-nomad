from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .decorators import role_required
from .forms import StudentRegistrationForm
from .models import User
from feedback.models import Feedback


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    form = StudentRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        authenticated_user = authenticate(
            request,
            username=user.get_username(),
            password=form.cleaned_data['password1'],
        )
        if authenticated_user is not None:
            login(request, authenticated_user)
            messages.success(request, 'Аккаунт создан. Вы вошли в систему.')
            return redirect('accounts:profile')

        messages.error(request, 'Аккаунт создан. Теперь войдите, используя свои данные.')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    my_feedback = Feedback.objects.none()
    if request.user.role == User.Role.STUDENT:
        my_feedback = request.user.feedback_items.select_related('category').order_by('-created_at')
    return render(request, 'accounts/profile.html', {'my_feedback': my_feedback})


@role_required(User.Role.MODERATOR, User.Role.ADMINISTRATOR)
def staff_area(request):
    return render(request, 'accounts/staff_area.html')
