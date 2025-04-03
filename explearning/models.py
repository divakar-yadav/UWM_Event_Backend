from django.db import models
from signup.models import User
from home.models import Students
from django.db.models import Avg, F, Sum, Count
from django.db.models.functions import Round


class ExpLearning(models.Model):
    poster_id = models.IntegerField(null=True, blank=True)  # New field as Primary Key
    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    reflection_score = models.FloatField(null=True, blank=True)
    communication_score = models.FloatField(null=True, blank=True)
    presentation_score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.judge.first_name} {self.judge.last_name} has scored the ({self.student.Name})"

    def calculate_total_score(self):
        return round((self.reflection_score or 0) + (self.communication_score or 0) + (self.presentation_score or 0), 2)

    def save(self, *args, **kwargs):
        if self.student and not self.poster_id:
            self.poster_id = self.student.poster_ID  # Auto-assign poster ID from the Student model
        super().save(*args, **kwargs)

    @staticmethod
    def get_average_scores():
        scores = ExpLearning.objects.filter(
            student__poster_ID=F('student__poster_ID')
        ).values(
            'student__poster_ID', 'student__Name', 'student__email'
        ).annotate(
            avg_reflection_score=Round(
                Avg('reflection_score', output_field=models.FloatField()), 2),
            avg_communication_score=Round(
                Avg('communication_score', output_field=models.FloatField()), 2),
            avg_presentation_score=Round(
                Avg('presentation_score', output_field=models.FloatField()), 2),
            total_score=Round(
                Round(Avg('reflection_score', output_field=models.FloatField()), 2) +
                Round(Avg('communication_score', output_field=models.FloatField()), 2) +
                Round(Avg('presentation_score', output_field=models.FloatField()), 2), 2
            ),
            judges_count=Count('judge', distinct=True)
        ).order_by('-total_score')

        return scores
class Total_Scores_Exp_Learning(models.Model):
    poster_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField()
    judged_count = models.IntegerField(default=0)
    avg_reflection_score= models.FloatField(default=0)
    avg_communication_score = models.FloatField(default=0)
    avg_presentation_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.Name} ({self.poster_id})"

    class Meta:
        db_table = 'total_scores_exp_learning'
        verbose_name = 'Total Scores Exp Learning'
        verbose_name_plural = 'Total Scores Exp Learning'
