from django.db import models
from signup.models import User
from home.models import Students
from django.db.models import Avg, F, Sum, Count
from django.db.models.functions import Round


class ThreeMt(models.Model):
    poster_id = models.IntegerField(primary_key=True,unique=True)  # New field as Primary Key
    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    comprehension_content = models.FloatField(null=True, blank=True)
    engagement = models.FloatField(null=True, blank=True)
    communication = models.FloatField(null=True, blank=True)
    overall_impression = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.judge.first_name} {self.judge.last_name} has scored the ({self.student.Name})"

    def calculate_total_score(self):
        return round((self.comprehension_content or 0) + (self.engagement or 0) + (self.communication or 0)+(self.overall_impression or 0), 2)

    def save(self, *args, **kwargs):
        if self.student and not self.poster_id:
            self.poster_id = self.student.poster_ID  # Auto-assign poster ID from the Student model
        super().save(*args, **kwargs)

    @staticmethod
    def get_average_scores():
        scores = ThreeMt.objects.values(
            'student__poster_ID', 'student__Name', 'student__email'
        ).annotate(
            avg_comprehension_content=Round(Avg('comprehension_content'), 2),
            avg_engagement=Round(Avg('engagement'), 2),
            avg_communication=Round(Avg('communication'), 2),
            avg_overall_impression=Round(Avg('overall_impression'), 2),
            total_score=Round(
                Avg('comprehension_content') +
                Avg('engagement') +
                Avg('communication') +
                Avg('overall_impression'), 2
            ),
            judges_count=Count('judge', distinct=True)
        ).order_by('-total_score')

        return scores

    
class Total_Scores_ThreeMT(models.Model):
    poster_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField()
    judged_count = models.IntegerField(default=0)
    avg_comprehension_content = models.FloatField(default=0)
    avg_engagement = models.FloatField(default=0)
    avg_communication = models.FloatField(default=0)
    avg_overall_impression = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.Name} ({self.poster_id})"

    class Meta:
        db_table = 'total_scores_three_mt'
        verbose_name = 'Total Scores Three Minute Thesis'
        verbose_name_plural = 'Total Scores Three Minute Thesis'
