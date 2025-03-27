# Generated by Django 4.1.7 on 2025-03-14 05:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0004_scores_round_1_feedback'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreeMt',
            fields=[
                ('poster_ID', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('comprehension_content', models.FloatField(blank=True, null=True)),
                ('engagement', models.FloatField(blank=True, null=True)),
                ('communication', models.FloatField(blank=True, null=True)),
                ('overall_impression', models.FloatField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.students')),
                ('judge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
