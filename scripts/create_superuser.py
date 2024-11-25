from django.contrib.auth import get_user_model

User = get_user_model()

def run():
    username = "admin"
    email = "admin@example.com"
    password = "adminpassword"

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        user.role = "admin"  # role alanını ayarla
        user.save()
        print(f"Superuser '{username}' created successfully with role 'admin'.")
    else:
        print(f"Superuser '{username}' already exists.")
