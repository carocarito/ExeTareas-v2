import calendar as month_calendar
from datetime import date, timedelta
from uuid import uuid4
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from .forms import PomodoroForm, TaskForm
from .models import Completion, PomodoroSession, Task

ICONS = {"general":"✓", "idea":"💡", "food":"☕", "work":"▣", "sport":"⚽", "music":"♫"}

def healthz(request):
    return JsonResponse({"status": "ok"})

def manifest(request):
    return JsonResponse({"name": "Tareas Recurrentes", "short_name": "Tareas", "start_url": "/", "display": "standalone", "background_color": "#9e62e6", "theme_color": "#9e62e6", "icons": [{"src": "/pwa/icon-192.svg", "sizes": "192x192", "type": "image/svg+xml", "purpose": "any"}, {"src": "/pwa/icon-512.svg", "sizes": "512x512", "type": "image/svg+xml", "purpose": "any"}]}, content_type="application/manifest+json")

def service_worker(request):
    code = """const CACHE='tareitas-v4'; const ASSETS=['/static/tasks/styles.css','/static/tasks/auth.css','/static/tasks/dashboard.css','/static/tasks/themes.css'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => { if (event.request.method !== 'GET') return; const url=new URL(event.request.url); if (!url.pathname.startsWith('/static/')) return; event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request))); });"""
    return HttpResponse(code, content_type="application/javascript")

def pwa_icon(request, size):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 512 512"><rect width="512" height="512" rx="110" fill="#9e62e6"/><rect x="105" y="115" width="302" height="280" rx="36" fill="#f0e2fa"/><path d="M160 252l54 55 139-132" fill="none" stroke="#9e62e6" stroke-width="37" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
    return HttpResponse(svg, content_type="image/svg+xml")

def selected_day(request):
    return parse_date(request.GET.get("day", "")) or date.today()

def month_grid(day, destination):
    """Datos reutilizables para una cuadrícula mensual cuyos días son enlaces."""
    month_start = day.replace(day=1)
    previous_month = (month_start - timedelta(days=1)).replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    weeks = []
    for week in month_calendar.Calendar(firstweekday=0).monthdatescalendar(day.year, day.month):
        weeks.append([{
            "date": current,
            "current_month": current.month == day.month,
            "selected": current == day,
            "url": f"{destination}?day={current.isoformat()}",
        } for current in week])
    months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    return {"weeks": weeks, "month_title": f"{months[day.month - 1]} {day.year}", "previous_month": previous_month, "next_month": next_month}

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(); login(request, user); return redirect("dashboard")
    return render(request, "tasks/register.html", {"form": form})

def guest_login(request):
    if request.method != "POST": return redirect("login")
    User = get_user_model()
    user = User.objects.create_user(username=f"invitado_{uuid4().hex[:12]}")
    user.set_unusable_password(); user.save(update_fields=["password"])
    login(request, user); request.session["guest_mode"] = True
    return redirect("dashboard")

def logout_view(request):
    """Cierra la sesión y siempre vuelve a la portada, incluso desde un enlace."""
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    day = selected_day(request)
    tasks = [task for task in Task.objects.filter(active=True, owner=request.user) if task.is_due_on(day)]
    completed = set(Completion.objects.filter(day=day).values_list("task_id", flat=True))
    week = [day + timedelta(days=offset) for offset in range(-2, 3)]
    return render(request, "tasks/dashboard.html", {"day": day, "tasks": tasks, "completed": completed, "week": week, "icons": ICONS})

@login_required
def categories(request):
    counts = {value: Task.objects.filter(category=value, active=True, owner=request.user).count() for value, _ in Task.Category.choices}
    return render(request, "tasks/categories.html", {"choices": Task.Category.choices, "counts": counts, "icons": ICONS})

@login_required
def task_create(request, category):
    selected = selected_day(request)
    form = TaskForm(request.POST or None, initial={"category": category, "start_date": selected})
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False); task.owner = request.user; task.save(); return redirect("dashboard")
    calendar_data = month_grid(selected, reverse("task_create", args=[category]))
    return render(request, "tasks/task_form.html", {"form": form, "category": category, "icon": ICONS.get(category, "✓"), "editing": False, "selected_day": selected, **calendar_data})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user); form = TaskForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid(): form.save(); return redirect("dashboard")
    return render(request, "tasks/task_form.html", {"form": form, "category": task.category, "icon": ICONS.get(task.category, "✓"), "editing": True, **month_grid(task.start_date, reverse("task_edit", args=[task.pk]))})

@login_required
def calendar_view(request):
    day = selected_day(request)
    return render(request, "tasks/calendar.html", {"day": day, **month_grid(day, reverse("dashboard"))})

@login_required
def pomodoro(request):
    form = PomodoroForm(request.POST or None)
    form.fields["task"].queryset = Task.objects.filter(owner=request.user, active=True)
    if request.method == "POST" and form.is_valid():
        session = form.save(commit=False); session.owner = request.user
        if not session.title.strip() and not session.task:
            number = PomodoroSession.objects.filter(owner=request.user, created_at__date=date.today()).count() + 1
            session.title = f"Ciclo Pomodoro {number}"
        if not session.title.strip() and session.task: session.title = session.task.title
        session.save(); return render(request, "tasks/pomodoro.html", {"form": form, "session": session})
    return render(request, "tasks/pomodoro.html", {"form": form})

@login_required
def toggle_completion(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user); day = parse_date(request.POST.get("day", "")) or date.today()
    completion, created = Completion.objects.get_or_create(task=task, day=day)
    if not created: completion.delete()
    return redirect(f"{reverse('dashboard')}?day={day.isoformat()}")
