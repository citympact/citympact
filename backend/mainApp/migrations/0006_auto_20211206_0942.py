# Generated by Django 3.2.8 on 2021-12-06 08:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainApp', '0005_registereduser_registration_provider'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='petition',
            name='session',
        ),
        migrations.AddField(
            model_name='petition',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registereduser',
            name='registration_provider',
            field=models.CharField(max_length=254),
        ),
    ]
