# Generated by Django 3.2.8 on 2022-10-06 20:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CityProjectComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('validated', models.BooleanField()),
                ('name_displayed', models.BooleanField()),
                ('comment', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PropositionComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('validated', models.BooleanField()),
                ('name_displayed', models.BooleanField()),
                ('comment', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveConstraint(
            model_name='cityprojectvote',
            name='unique_project_vote_per_session',
        ),
        migrations.RemoveField(
            model_name='cityprojectvote',
            name='session',
        ),
        migrations.RemoveField(
            model_name='proposition',
            name='session',
        ),
        migrations.RemoveField(
            model_name='propositionsignature',
            name='session',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='email',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='registereduser',
            name='last_name',
        ),
        migrations.AddField(
            model_name='cityproject',
            name='views',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cityprojectvote',
            name='visitor',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.DO_NOTHING, to='mainApp.visitor'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proposition',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='proposition',
            name='author',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proposition',
            name='views',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='propositionsignature',
            name='user',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registereduser',
            name='registration_provider',
            field=models.CharField(default=-1, max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registereduser',
            name='user',
            field=models.OneToOneField(default=-1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='registereduser',
            name='birth_year',
            field=models.DecimalField(decimal_places=0, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='registereduser',
            name='city',
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='registereduser',
            name='zip_code',
            field=models.DecimalField(decimal_places=0, max_digits=10, null=True),
        ),
        migrations.AddConstraint(
            model_name='cityprojectvote',
            constraint=models.UniqueConstraint(fields=('project', 'visitor'), name='unique_project_vote_per_visitor'),
        ),
        migrations.AddField(
            model_name='propositioncomment',
            name='proposition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.proposition'),
        ),
        migrations.AddField(
            model_name='propositioncomment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='propositioncomment',
            name='visitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainApp.visitor'),
        ),
        migrations.AddField(
            model_name='cityprojectcomment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.cityproject'),
        ),
        migrations.AddField(
            model_name='cityprojectcomment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cityprojectcomment',
            name='visitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mainApp.visitor'),
        ),
    ]