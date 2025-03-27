from django.contrib import admin
from django.db.models import Count
from explearning.models import ExpLearning, Total_Scores_Exp_Learning
from threemt.models import ThreeMt, Total_Scores_ThreeMT
from .models import (
    Students, Scores_Round_1, Scores_Round_2,
    Total_Scores_Round_2_Graduate, Total_Scores_Round_2_Undergraduate,
    Total_Scores_Round_1_Graduate, Total_Scores_Round_1_Undergraduate,
)
from signup.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'is_superuser')
    list_display_links = ('email',)
    list_filter = ('email',)
    search_fields = ('email',)
    list_per_page = 25


@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('Name', 'poster_ID', 'judged_count_round_1', 'finalist')
    list_display_links = ('Name', 'poster_ID')
    list_filter = ('Name', 'poster_ID')
    search_fields = ('Name', 'poster_ID')
    list_per_page = 25

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _judged_count_round_1=Count('scores_round_1'),
        )
        return queryset

    def judged_count_round_1(self, obj):
        return obj._judged_count_round_1
    judged_count_round_1.admin_order_field = '_judged_count_round_1'


@admin.register(Scores_Round_1)
class Scores_Round_1Admin(admin.ModelAdmin):
    list_display = ('judge', 'Student', 'research_score',
                    'communication_score', 'presentation_score')
    list_display_links = ('judge', 'Student')
    list_filter = ('judge', 'Student')
    search_fields = ('judge', 'Student')
    list_per_page = 25


@admin.register(Total_Scores_Round_1_Graduate)
class Total_Scores_Round_1_GraduateAdmin(admin.ModelAdmin):
    list_display = ('poster_id', 'Name', 'email', 'total_score', 'judged_count',
                    'avg_research_score', 'avg_communication_score', 'avg_presentation_score')
    list_display_links = ('poster_id', 'Name')
    list_filter = ('poster_id', 'Name')
    search_fields = ('poster_id', 'Name')
    list_per_page = 25


@admin.register(Total_Scores_Round_1_Undergraduate)
class Total_Scores_Round_1_UndergraduateAdmin(admin.ModelAdmin):
    list_display = ('poster_id', 'Name', 'email', 'total_score', 'judged_count',
                    'avg_research_score', 'avg_communication_score', 'avg_presentation_score')
    list_display_links = ('poster_id', 'Name')
    list_filter = ('poster_id', 'Name')
    search_fields = ('poster_id', 'Name')
    list_per_page = 25


@admin.register(ExpLearning)
class ExpLearningAdmin(admin.ModelAdmin):
    list_display = ('judge', 'student', 'reflection_score', 'communication_score', 'presentation_score', 'feedback', 'total_score')
    list_display_links = ('judge', 'student')
    list_filter = ('judge', 'student')
    search_fields = ('judge__email', 'student__Name')
    list_per_page = 25

    def total_score(self, obj):
        return obj.calculate_total_score()
    total_score.admin_order_field = 'total_score'


@admin.register(ThreeMt)
class ThreeMtAdmin(admin.ModelAdmin):
    list_display = ('judge', 'student', 'comprehension_content', 'engagement', 'communication', 'overall_impression', 'feedback', 'total_score')
    list_display_links = ('judge', 'student')
    list_filter = ('judge', 'student')
    search_fields = ('judge__email', 'Student__Name')
    list_per_page = 25

    def total_score(self, obj):
        return obj.calculate_total_score()
    total_score.admin_order_field = 'total_score'
    total_score.short_description = 'Total Score'


# ✅ NEW: Admin for Total_Scores_Exp_Learning
@admin.register(Total_Scores_Exp_Learning)
class Total_Scores_Exp_LearningAdmin(admin.ModelAdmin):
    list_display = ('poster_id', 'Name', 'email', 'total_score', 'judged_count',
                    'avg_reflection_score', 'avg_communication_score', 'avg_presentation_score')
    list_display_links = ('poster_id', 'Name')
    list_filter = ('poster_id', 'Name')
    search_fields = ('poster_id', 'Name')
    list_per_page = 25


# ✅ NEW: Admin for Total_Scores_ThreeMT
@admin.register(Total_Scores_ThreeMT)
class Total_Scores_ThreeMTAdmin(admin.ModelAdmin):
    list_display = ('poster_id', 'Name', 'email', 'total_score', 'judged_count',
                    'avg_comprehension_content', 'avg_engagement', 'avg_communication', 'avg_overall_impression')
    list_display_links = ('poster_id', 'Name')
    list_filter = ('poster_id', 'Name')
    search_fields = ('poster_id', 'Name')
    list_per_page = 25
