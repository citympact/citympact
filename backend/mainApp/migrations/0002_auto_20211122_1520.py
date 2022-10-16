# Generated by Django 3.2.8 on 2021-11-22 14:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='cityprojectvote',
            name='unique_project_vote_per_session',
        ),
        migrations.RemoveField(
            model_name='cityprojectvote',
            name='session',
        ),
        migrations.AddField(
            model_name='cityprojectvote',
            name='visitor',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.DO_NOTHING, to='mainApp.visitor'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='cityprojectvote',
            constraint=models.UniqueConstraint(fields=('project', 'visitor'), name='unique_project_vote_per_visitor'),
        ),
    ]