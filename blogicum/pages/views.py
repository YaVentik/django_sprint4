from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Представление для страницы 'О проекте'."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Представление для страницы 'Правила'."""

    template_name = 'pages/rules.html'


def csrf_failure(request, reason=""):
    """Кастомная страница для ошибки CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Кастомная страница для ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Кастомная страница для ошибки 500."""
    return render(request, 'pages/500.html', status=500)


def registration(request):
    """Страница регистрации пользователя."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
    else:
        form = UserCreationForm()
    return render(request,
                  'registration/registration_form.html', {'form': form})
