from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from .permissions import IsSuperUser
from threemt.models import ThreeMt
from explearning.models import ExpLearning
from home.models import Scores_Round_1
from rest_framework_simplejwt.authentication import JWTAuthentication
from signup.models import User
from django.db.models import Avg, Count, F
from django.db.models.functions import Round
import io
import xlsxwriter
from django.http import HttpResponse

CATEGORY_MODEL_MAP = {
    '3mt': ThreeMt,
    'exp': ExpLearning,
    'respost': Scores_Round_1
}

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUser])
def sorted_scores_view(request):
    print("USER:", request.user)
    print("IS AUTHENTICATED:", request.user.is_authenticated)
    print("IS SUPERUSER:", request.user.is_superuser)
    return Response({"status": "ok"})
    category = request.GET.get("category")
    model = CATEGORY_MODEL_MAP.get(category)

    if not model:
        return Response({"error": "Invalid category"}, status=400)

    if category == "3mt":
        data = (
            model.objects.values('student__Name', 'student__poster_ID')
            .annotate(
                avg_score=Avg('comprehension_content') + Avg('engagement') + Avg('communication') + Avg('overall_impression'),
                judge_count=Count('judge')
            )
            .order_by('-avg_score')
        )

    elif category == "exp":
        data = (
            model.objects.values('student__Name', 'student__poster_ID')
            .annotate(
                avg_score=Avg('content') + Avg('presentation') + Avg('structure') + Avg('language'),
                judge_count=Count('judge')
            )
            .order_by('-avg_score')
        )

    elif category == "respost":
        data = (
            model.objects.values('Student__Name', 'Student__poster_ID')
            .annotate(
                avg_score=Avg('research_score') + Avg('communication_score') + Avg('presentation_score'),
                judge_count=Count('judge')
            )
            .order_by('-avg_score')
        )
    else:
        return Response({"error": "Unsupported category"}, status=400)

    return Response(list(data))

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUser])
def category_scores_view(request):
    category = request.GET.get("category")
    model = CATEGORY_MODEL_MAP.get(category)

    if not model:
        return Response({"error": "Invalid category"}, status=400)

    if category == "3mt":
        data = model.objects.values(
            name=F('student__Name'),
            poster_id=F('student__poster_ID'),
        ).annotate(
            avg_comprehension=Round(Avg('comprehension_content'), 2),
            avg_engagement=Round(Avg('engagement'), 2),
            avg_communication=Round(Avg('communication'), 2),
            avg_impression=Round(Avg('overall_impression'), 2),
            avg_score=Round(
                Avg('comprehension_content') + Avg('engagement') + Avg('communication') + Avg('overall_impression'), 2
            ),
            judge_count=Count('judge')
        )

    elif category == "exp":
        data = model.objects.values(
            name=F('student__Name'),
            poster_id=F('student__poster_ID'),
        ).annotate(
            avg_content=Round(Avg('content'), 2),
            avg_structure=Round(Avg('structure'), 2),
            avg_language=Round(Avg('language'), 2),
            avg_presentation=Round(Avg('presentation'), 2),
            avg_score=Round(
                Avg('content') + Avg('structure') + Avg('language') + Avg('presentation'), 2
            ),
            judge_count=Count('judge')
        )

    elif category == "respost":
        data = model.objects.values(
            name=F('Student__Name'),
            poster_id=F('Student__poster_ID'),
        ).annotate(
            avg_research=Round(Avg('research_score'), 2),
            avg_communication=Round(Avg('communication_score'), 2),
            avg_presentation=Round(Avg('presentation_score'), 2),
            avg_score=Round(
                Avg('research_score') + Avg('communication_score') + Avg('presentation_score'), 2
            ),
            judge_count=Count('judge')
        )

    else:
        return Response({"error": "Unsupported category"}, status=400)

    return Response(list(data))


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUser])
def judge_progress(request):
    category = request.GET.get("category")
    model = CATEGORY_MODEL_MAP.get(category)

    if not model:
        return Response({"error": "Invalid category"}, status=400)

    if category == "3mt":
        data = model.objects.values(email=F('judge__email')).annotate(
            count=Count('student', distinct=True)
        ).order_by('count')

    elif category == "exp":
        data = model.objects.values(email=F('judge__email')).annotate(
            count=Count('student', distinct=True)
        ).order_by('count')

    elif category == "respost":
        data = model.objects.values(email=F('judge__email')).annotate(
            count=Count('Student', distinct=True)
        ).order_by('count')

    else:
        return Response({"error": "Unsupported category"}, status=400)

    return Response(list(data))


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUser])
def student_judge_status(request):
    category = request.GET.get("category")
    model = CATEGORY_MODEL_MAP.get(category)

    if not model:
        return Response({"error": "Invalid category"}, status=400)

    if category == "3mt":
        data = (
            model.objects.values("student__Name", "student__poster_ID")
            .annotate(
                scored=Count("judge", distinct=True),
            )
        )

    elif category == "exp":
        data = (
            model.objects.values("student__Name", "student__poster_ID")
            .annotate(
                scored=Count("judge", distinct=True),
            )
        )

    elif category == "respost":
        data = (
            model.objects.values("Student__Name", "Student__poster_ID")
            .annotate(
                scored=Count("judge", distinct=True),
            )
        )

    else:
        return Response({"error": "Unsupported category"}, status=400)

    # Add `total` if you have fixed number of judges per student (e.g., 4)
    total_judges = 4
    result = []
    for d in data:
        result.append({
            "student": d.get("student__Name") or d.get("Student__Name"),
            "poster_id": d.get("student__poster_ID") or d.get("Student__poster_ID"),
            "scored": d["scored"],
            "total": total_judges,
            "category": category,
        })

    return Response(result)




@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUser])
def export_excel_view(request):
    category = request.GET.get("category")
    model = CATEGORY_MODEL_MAP.get(category)

    if not model:
        return Response({"error": "Invalid category"}, status=400)

    # Use same logic as `sorted_scores_view`
    if category == "3mt":
        scores = model.objects.values('student__Name', 'student__poster_ID').annotate(
            avg_score=Avg('comprehension_content') + Avg('engagement') + Avg('communication') + Avg('overall_impression'),
            judge_count=Count('judge')
        ).order_by('-avg_score')

    elif category == "exp":
        scores = model.objects.values('student__Name', 'student__poster_ID').annotate(
            avg_score=Avg('content') + Avg('presentation') + Avg('structure') + Avg('language'),
            judge_count=Count('judge')
        ).order_by('-avg_score')

    elif category == "respost":
        scores = model.objects.values('Student__Name', 'Student__poster_ID').annotate(
            avg_score=Avg('research_score') + Avg('communication_score') + Avg('presentation_score'),
            judge_count=Count('judge')
        ).order_by('-avg_score')

    else:
        return Response({"error": "Unsupported category"}, status=400)

    # Generate Excel in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet("Scores")

    # Headers
    headers = ["Name", "Poster ID", "Average Score", "Judges Count"]
    for col, header in enumerate(headers):
        sheet.write(0, col, header)

    # Write rows
    for row, item in enumerate(scores, start=1):
        sheet.write(row, 0, item.get("student__Name") or item.get("Student__Name"))
        sheet.write(row, 1, item.get("student__poster_ID") or item.get("Student__poster_ID"))
        sheet.write(row, 2, float(item["avg_score"]))
        sheet.write(row, 3, item["judge_count"])

    workbook.close()
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={category}_scores.xlsx'
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUser])
def category_aggregate_view(request):
    category = request.GET.get("category")

    if category == "3mt":
        results = ThreeMt.objects.values(
            name=F('student__Name'),
            poster_id=F('student__poster_ID'),
            department=F('student__department'),
            advisor=F('student__advisor'),
            title=F('student__title'),
            category=F('student__category')
        ).annotate(
            avg_comprehension=Round(Avg('comprehension_content'), 2),
            avg_engagement=Round(Avg('engagement'), 2),
            avg_communication=Round(Avg('communication'), 2),
            avg_impression=Round(Avg('overall_impression'), 2),
            total_score=Round(
                (Avg('comprehension_content') + Avg('engagement') + Avg('communication') + Avg('overall_impression')) / 4,
                2
            ),
            judges_count=Count('judge')
        ).order_by('-total_score')

    elif category == "exp":
        results = ExpLearning.objects.values(
            name=F('student__Name'),
            poster_id=F('student__poster_ID'),
            department=F('student__department'),
            advisor=F('student__advisor'),
            title=F('student__title'),
            category=F('student__category')
        ).annotate(
            avg_content=Round(Avg('content'), 2),
            avg_structure=Round(Avg('structure'), 2),
            avg_language=Round(Avg('language'), 2),
            avg_presentation=Round(Avg('presentation'), 2),
            total_score=Round(
                (Avg('content') + Avg('structure') + Avg('language') + Avg('presentation')) / 4,
                2
            ),
            judges_count=Count('judge')
        ).order_by('-total_score')

    elif category == "respost":
        results = Scores_Round_1.objects.values(
            name=F('Student__Name'),
            poster_id=F('Student__poster_ID'),
            department=F('Student__department'),
            advisor=F('Student__advisor'),
            title=F('Student__title'),
            category=F('Student__category')
        ).annotate(
            avg_research=Round(Avg('research_score'), 2),
            avg_communication=Round(Avg('communication_score'), 2),
            avg_presentation=Round(Avg('presentation_score'), 2),
            total_score=Round(
                (Avg('research_score') + Avg('communication_score') + Avg('presentation_score')) / 3,
                2
            ),
            judges_count=Count('judge')
        ).order_by('-total_score')

    else:
        return Response({"error": "Invalid category"}, status=400)

    return Response(list(results))


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUser])
def judge_poster_status(request):
    judges = User.objects.all()

    result = []
    for judge in judges:
        scored_posters = Scores_Round_1.objects.filter(judge=judge).values_list('Student__poster_ID', flat=True)
        result.append({
            "judge_first_name": judge.first_name,
            "judge_email": judge.email,
            "posters_scored": list(scored_posters),
            "total_scored": scored_posters.count(),
        })

    return Response(result)