from django.db import models
from signup.models import User
from django.db.models import Avg, F, Sum, Count
from django.db.models.functions import Round
# Create your models here.


class Students(models.Model):
    date = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    academic_status = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phonetic_spelling = models.CharField(max_length=100, null=True, blank=True)
    research_adviser_first_name = models.CharField(
        max_length=100, null=True, blank=True)
    research_adviser_last_name = models.CharField(
        max_length=100, null=True, blank=True)
    research_adviser_email = models.EmailField(null=True, blank=True)
    poster_title = models.CharField(max_length=500, null=True, blank=True)
    jacket_size = models.CharField(max_length=100, null=True, blank=True)
    jacket_gender = models.CharField(max_length=100, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    poster_ID = models.IntegerField(null=True, blank=True)
    Name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    scored_By_Judges = models.IntegerField(null=True, blank=True)
    finalist = models.BooleanField(default=False)

    def judged_count_round_1(self):
        return Scores_Round_1.objects.filter(Student=self).count()

    def judged_count_round_2(self):
        return Scores_Round_2.objects.filter(Student=self).count()

    # this function will return the name of the student
    def __str__(self):
        return f"{self.Name} ({self.poster_ID})"

    # this is the meta class which will set the table name

    class Meta:
        db_table = 'students'
        verbose_name = 'Students'
        verbose_name_plural = 'Students'

# create a model for scores_round_1 table
# which has 5 fields
# Judge_Id (foreign key), poster_Id (Foreign key), research_score, communication_score, presentation_score
# judge_id and poster_id are foreign keys from the Judge and Students table


class Scores_Round_1(models.Model):
    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    Student = models.ForeignKey(Students, on_delete=models.CASCADE)
    research_score = models.FloatField(null=True, blank=True)
    communication_score = models.FloatField(null=True, blank=True)
    presentation_score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    # this function will return the name of the student
    def __str__(self):
        return f"{self.judge.first_name} {self.judge.last_name} has scored the poster ({self.Student.Name})"

    def calculate_total_score(self):
        return round(self.research_score + self.communication_score + self.presentation_score, 2)

    """
    SELECT t.Name, t.email, s.poster_Id, avg(s.Research_score), avg(s.Communication_score), avg(s.Presentation_score) 
    from Scores_Round_1 s inner join Students t where t.poster_ID = s.student.poster_ID group by s.student.poster_ID;
    """

    @staticmethod
    def get_average_scores():

        scores = Scores_Round_1.objects.filter(
            Student__poster_ID=F('Student__poster_ID')
        ).values(
            'Student__poster_ID', 'Student__Name', 'Student__email'
        ).annotate(
            avg_research_score=Round(
                Avg('research_score', output_field=models.FloatField()), 2),
            avg_communication_score=Round(
                Avg('communication_score', output_field=models.FloatField()), 2),
            avg_presentation_score=Round(
                Avg('presentation_score', output_field=models.FloatField()), 2),
            total_score=Round(Round(Avg('research_score', output_field=models.FloatField()), 2)
                              + Round(Avg('communication_score',
                                      output_field=models.FloatField()), 2)
                              + Round(Avg('presentation_score', output_field=models.FloatField()), 2), 2),
            judges_count=Count('judge', distinct=True)
        ).order_by('-total_score')

        return scores

    class Meta:
        db_table = 'scores_round_1'
        verbose_name = 'Scores Round 1'
        verbose_name_plural = 'Scores Round 1'


# create a model for scores_round_2 table

class Scores_Round_2(models.Model):
    judge = models.ForeignKey(User, on_delete=models.CASCADE)
    Student = models.ForeignKey(Students, on_delete=models.CASCADE)
    research_score = models.FloatField(null=True, blank=True)
    communication_score = models.FloatField(null=True, blank=True)
    presentation_score = models.FloatField(null=True, blank=True)

    # this function will return the name of the student
    def __str__(self):
        return f"{self.judge.first_name} {self.judge.last_name} has scored the poster ({self.Student.Name})"

    def calculate_total_score(self):
        return round(self.research_score + self.communication_score + self.presentation_score, 2)

    """
    SELECT t.Name, t.email, s.poster_Id, avg(s.Research_score), avg(s.Communication_score), avg(s.Presentation_score) 
    from Scores_Round_2 s inner join Students t where t.poster_ID = s.student.poster_ID group by s.student.poster_ID;
    """

    @staticmethod
    def get_average_scores():

        scores = Scores_Round_2.objects.filter(
            Student__poster_ID=F('Student__poster_ID')
        ).values(
            'Student__poster_ID', 'Student__Name', 'Student__email'
        ).annotate(
            avg_research_score=Round(
                Avg('research_score', output_field=models.FloatField()), 2),
            avg_communication_score=Round(
                Avg('communication_score', output_field=models.FloatField()), 2),
            avg_presentation_score=Round(
                Avg('presentation_score', output_field=models.FloatField()), 2),
            total_score=Round(Round(Avg('research_score', output_field=models.FloatField()), 2)
                              + Round(Avg('communication_score',
                                      output_field=models.FloatField()), 2)
                              + Round(Avg('presentation_score', output_field=models.FloatField()), 2), 2)
        ).order_by('-total_score')

        return scores

    class Meta:
        db_table = 'scores_round_2'
        verbose_name = 'Scores Round 2'
        verbose_name_plural = 'Scores Round 2'


class Total_Scores_Round_1_Undergraduate(models.Model):
    poster_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField()
    judged_count = models.IntegerField(default=0)
    avg_research_score = models.FloatField(default=0)
    avg_communication_score = models.FloatField(default=0)
    avg_presentation_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.Name} ({self.poster_id})"

    class Meta:
        db_table = 'total_scores_round_1_undergraduate'
        verbose_name = 'Total Scores Round 1 Undergraduate'
        verbose_name_plural = 'Total Scores Round 1 Undergraduate'


class Total_Scores_Round_1_Graduate(models.Model):
    poster_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField()
    judged_count = models.IntegerField(default=0)
    avg_research_score = models.FloatField(default=0)
    avg_communication_score = models.FloatField(default=0)
    avg_presentation_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.Name} ({self.poster_id})"

    class Meta:
        db_table = 'total_scores_round_1_graduate'
        verbose_name = 'Total Scores Round 1 Graduate'
        verbose_name_plural = 'Total Scores Round 1 Graduate'


class Total_Scores_Round_2_Undergraduate(models.Model):
    poster_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField()
    avg_research_score = models.FloatField(default=0)
    avg_communication_score = models.FloatField(default=0)
    avg_presentation_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.Name} ({self.poster_id})"

    class Meta:
        db_table = 'total_scores_round_2_undergraduate'
        verbose_name = 'Total Scores Round 2 Undergraduate'
        verbose_name_plural = 'Total Scores Round 2 Undergraduate'


class Total_Scores_Round_2_Graduate(models.Model):
    poster_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    email = models.EmailField()
    avg_research_score = models.FloatField(default=0)
    avg_communication_score = models.FloatField(default=0)
    avg_presentation_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.Name} ({self.poster_id})"

    class Meta:
        db_table = 'total_scores_round_2_graduate'
        verbose_name = 'Total Scores Round 2 Graduate'
        verbose_name_plural = 'Total Scores Round 2 Graduate'
