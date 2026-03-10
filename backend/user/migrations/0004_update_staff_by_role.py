from django.db import migrations


def sync_staff_by_role(apps, schema_editor):
    User = apps.get_model('user', 'User')

    User.objects.filter(role='merchant').update(is_staff=True)
    User.objects.filter(role='admin').update(is_staff=True)
    User.objects.filter(role='normal', is_superuser=False).update(is_staff=False)


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_user_role'),
    ]

    operations = [
        migrations.RunPython(sync_staff_by_role, migrations.RunPython.noop),
    ]
