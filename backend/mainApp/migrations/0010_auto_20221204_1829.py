# Generated by Django 3.2.8 on 2022-12-04 17:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainApp', '0009_auto_20221204_1741'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PropositionCommentApproval',
            new_name='CityProjectCommentReview',
        ),
        migrations.RenameModel(
            old_name='CityProjectCommentApproval',
            new_name='PropositionCommentReview',
        ),
        migrations.AlterField(
            model_name='cityprojectcommentreview',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.cityprojectcomment'),
        ),
        migrations.AlterField(
            model_name='propositioncommentreview',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.propositioncomment'),
        ),
        migrations.CreateModel(
            name='PropositionReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('proposition_validated', models.BooleanField()),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('proposition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.proposition')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
