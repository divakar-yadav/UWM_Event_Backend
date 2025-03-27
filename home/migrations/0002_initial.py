# Generated by Django 4.1.7 on 2024-03-08 23:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='scores_round_2',
            name='judge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='scores_round_1',
            name='Student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.students'),
        ),
        migrations.AddField(
            model_name='scores_round_1',
            name='judge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
