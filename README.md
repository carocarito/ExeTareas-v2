# Tareas Recurrentes v2 (Django)

Versión web local, organizada para editarla en equipo:

- `tasks/models.py`: datos y reglas de recurrencia.
- `tasks/views.py`: comportamiento de cada pantalla.
- `tasks/forms.py`: validación del formulario.
- `templates/tasks/`: las cuatro pantallas.
- `static/tasks/styles.css`: colores, tamaños y distribución del mockup.

## Iniciar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations tasks
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

## PWA y Supabase

La aplicación ya expone `manifest.webmanifest` y `service-worker.js` para instalarla desde Chrome/Android cuando se publique con HTTPS.

Mientras no exista `DATABASE_URL`, Django usa SQLite local. Para conectar Supabase, copia `.env.example`, guarda las variables como secretos del hosting y configura `DATABASE_URL` con el pooler de Supabase. Nunca subas una contraseña o `DATABASE_URL` al repositorio.
