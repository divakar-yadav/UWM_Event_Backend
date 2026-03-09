from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
#from .permissions import IsSuperUser
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
from home.models import Students
from django.db.models import Avg, Count, F, FloatField, ExpressionWrapper
from rest_framework.permissions import IsAuthenticated
from .permissions import IsDashboardUser
from django.contrib.auth.models import Group
from signup.models import User

CATEGORY_MODEL_MAP = {
    '3mt': ThreeMt,
    'exp': ExpLearning,
    'respost': Scores_Round_1
}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    group_names = list(user.groups.values_list("name", flat=True))
    can_access_dashboard = user.is_superuser or ("DashboardAccess" in group_names)

    return Response({
        "email": getattr(user, "email", ""),
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
        "groups": group_names,
        "can_access_dashboard": can_access_dashboard,
    })


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsDashboardUser])
def sorted_scores_view(request):
    print("USER:", request.user)
    print("IS AUTHENTICATED:", request.user.is_authenticated)
    print("IS SUPERUSER:", request.user.is_superuser)
    #return Response({"status": "ok"})
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
            ExpLearning.objects
            .values("student__Name", "student__poster_ID")
            .annotate(
                avg_reflection=Avg("reflection_score"),
                avg_communication=Avg("communication_score"),
                avg_presentation=Avg("presentation_score"),
                judge_count=Count("judge", distinct=True),
            )
            .annotate(
                avg_score=ExpressionWrapper(
                    F("avg_reflection") + F("avg_communication") + F("avg_presentation"),
                    output_field=FloatField(),
                )
            )
            .order_by("-avg_score")
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
@permission_classes([IsDashboardUser])
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
@permission_classes([IsDashboardUser])
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
@permission_classes([IsDashboardUser])
def student_judge_status(request):
    category = request.GET.get("category")
    required = int(request.GET.get("required", 4))  # dynamic
    rng = CATEGORY_RANGES.get(category)
    if not rng:
        return Response({"error": "Invalid category"}, status=400)

    lo, hi = rng
    students = list(
        Students.objects.filter(poster_ID__gte=lo, poster_ID__lte=hi)
        .values("poster_ID", "Name")
        .order_by("poster_ID")
    )

    # map poster -> distinct judge count
    if category == "respost":
        counts = (Scores_Round_1.objects
                  .filter(Student__poster_ID__gte=lo, Student__poster_ID__lte=hi)
                  .values("Student__poster_ID")
                  .annotate(scored=Count("judge", distinct=True)))
        m = {c["Student__poster_ID"]: c["scored"] for c in counts}
    elif category == "exp":
        counts = (ExpLearning.objects
                  .filter(student__poster_ID__gte=lo, student__poster_ID__lte=hi)
                  .values("student__poster_ID")
                  .annotate(scored=Count("judge", distinct=True)))
        m = {c["student__poster_ID"]: c["scored"] for c in counts}
    else:  # 3mt
        counts = (ThreeMt.objects
                  .filter(student__poster_ID__gte=lo, student__poster_ID__lte=hi)
                  .values("student__poster_ID")
                  .annotate(scored=Count("judge", distinct=True)))
        m = {c["student__poster_ID"]: c["scored"] for c in counts}

    result = []
    for s in students:
        pid = s["poster_ID"]
        result.append({
            "student": s["Name"],
            "poster_id": pid,
            "scored": int(m.get(pid, 0)),
            "total": required,
            "category": category,
        })

    return Response(result)




@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsDashboardUser])
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
            avg_score=Avg('reflection_score') + Avg('communication_score') + Avg('presentation_score'),
            judge_count=Count('judge', distinct=True)
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
@permission_classes([IsDashboardUser])
def category_aggregate_view(request):
    category = request.GET.get("category")

    def format_rows(results):
        out = []
        for r in results:
            advisor = (f'{r.get("adv_first","")} {r.get("adv_last","")}'.strip()) or "Unknown"
            out.append({
                "name": r.get("name") or "Unknown",
                "poster_id": r.get("poster_num"),
                "department": r.get("department") or "Unknown",
                "advisor": advisor,
                "title": r.get("title") or "Unknown",
                "total_score": r.get("total_score"),
                "judges_count": r.get("judges_count"),
            })
        return out

    if category == "3mt":
        results = ThreeMt.objects.values(
            name=F("student__Name"),
            poster_num=F("student__poster_ID"),
            department=F("student__department"),
            title=F("student__poster_title"),
            adv_first=F("student__research_adviser_first_name"),
            adv_last=F("student__research_adviser_last_name"),
        ).annotate(
            total_score=Round(
                (Avg("comprehension_content") + Avg("engagement") + Avg("communication") + Avg("overall_impression")) / 4,
                2
            ),
            judges_count=Count("judge", distinct=True),
        ).order_by("-total_score")

        return Response(format_rows(results))

    elif category == "exp":
        results = ExpLearning.objects.values(
            name=F("student__Name"),
            poster_num=F("student__poster_ID"),
            department=F("student__department"),
            title=F("student__poster_title"),
            adv_first=F("student__research_adviser_first_name"),
            adv_last=F("student__research_adviser_last_name"),
        ).annotate(
            total_score=Round(
                (Avg("reflection_score") + Avg("communication_score") + Avg("presentation_score")) / 3,
                2
            ),
            judges_count=Count("judge", distinct=True),
        ).order_by("-total_score")

        return Response(format_rows(results))

    elif category == "respost":
        results = Scores_Round_1.objects.values(
            name=F("Student__Name"),
            poster_num=F("Student__poster_ID"),
            department=F("Student__department"),
            title=F("Student__poster_title"),
            adv_first=F("Student__research_adviser_first_name"),
            adv_last=F("Student__research_adviser_last_name"),
        ).annotate(
            total_score=Round(
                (Avg("research_score") + Avg("communication_score") + Avg("presentation_score")) / 3,
                2
            ),
            judges_count=Count("judge", distinct=True),
        ).order_by("-total_score")

        return Response(format_rows(results))

    return Response({"error": "Invalid category"}, status=400)

CATEGORY_RANGES = {
    "respost": (101, 299),
    "exp": (301, 399),
    "3mt": (401, 499),
}

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsDashboardUser])
def judge_poster_status(request):
    category = request.GET.get("category")
    rng = CATEGORY_RANGES.get(category)
    if not rng:
        return Response({"error": "Invalid category"}, status=400)

    lo, hi = rng
    total_posters = Students.objects.filter(poster_ID__gte=lo, poster_ID__lte=hi).count()

    result = []
    for judge in User.objects.all():
        if category == "respost":
            ids = (Scores_Round_1.objects
                   .filter(judge=judge, Student__poster_ID__gte=lo, Student__poster_ID__lte=hi)
                   .values_list("Student__poster_ID", flat=True)
                   .distinct())
        elif category == "exp":
            ids = (ExpLearning.objects
                   .filter(judge=judge, student__poster_ID__gte=lo, student__poster_ID__lte=hi)
                   .values_list("student__poster_ID", flat=True)
                   .distinct())
        else:  # 3mt
            ids = (ThreeMt.objects
                   .filter(judge=judge, student__poster_ID__gte=lo, student__poster_ID__lte=hi)
                   .values_list("student__poster_ID", flat=True)
                   .distinct())

        ids_list = list(ids)
        result.append({
            "judge_first_name": judge.first_name,
            "judge_email": judge.email,
            "posters_scored": ids_list,
            "posters_scored_count": len(ids_list),
            "total_posters": total_posters,
        })

    return Response(result)

