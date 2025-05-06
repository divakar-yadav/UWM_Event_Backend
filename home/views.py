from time import sleep
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Students, Scores_Round_1,\
    Total_Scores_Round_1_Graduate, Total_Scores_Round_1_Undergraduate
from explearning.models import ExpLearning
from explearning.serializer import ExpLearningSerializer
from rest_framework import status
from django.http import HttpResponseRedirect
from django.urls import reverse
from .ScoreSerializer import Scores_Round_Serializer, StudentShowJudgeCountSerializer, StudentCreateSerializer




#---------------------------------------------------------------------------------------------------------------------------------------------------------------------


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication

from home.models import Students, Scores_Round_1
from .ScoreSerializer import Scores_Round_Serializer
from explearning.models import ExpLearning
from explearning.serializer import ExpLearningSerializer
from threemt.models import ThreeMt
from threemt.serializer import ThreeMtSerializer


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class HomeAPIView(APIView):
    def get(self, request):
        scoring_type = request.query_params.get('scoring_type') or request.data.get('scoring_type')

        if not scoring_type:
            return Response({"error": "scoring_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if scoring_type == 'research poster':
            score_round_1 = Scores_Round_1.objects.filter(judge=user.id)
            status_of_round_1_table = score_round_1.exists()
            finalist_poster_id = Students.objects.filter(finalist=True).values_list('poster_ID', flat=True)
            serialized_score_round_1 = Scores_Round_Serializer(score_round_1, many=True)

            return Response({
                "status_of_round_1_table": status_of_round_1_table,
                "finalist_poster_id": finalist_poster_id,
                "score_round_1": serialized_score_round_1.data,
                "Judge": f"{user.first_name} {user.last_name}",
            }, status=status.HTTP_200_OK)

        elif scoring_type == 'explearning':
            exp_learning_scores = ExpLearning.objects.filter(judge=user.id)
            status_of_exp_learning_table = exp_learning_scores.exists()
            finalist_poster_id = Students.objects.filter(finalist=True).values_list('poster_ID', flat=True)
            serialized_exp_learning = ExpLearningSerializer(exp_learning_scores, many=True)

            return Response({
                "status_of_exp_learning_table": status_of_exp_learning_table,
                "finalist_poster_id": finalist_poster_id,
                "exp_learning_scores": serialized_exp_learning.data,
                "Judge": f"{user.first_name} {user.last_name}",
            }, status=status.HTTP_200_OK)

        elif scoring_type == 'threemt':
            threemt_scores = ThreeMt.objects.filter(judge=user.id)
            status_of_threemt_table = threemt_scores.exists()
            finalist_poster_id = Students.objects.filter(finalist=True).values_list('poster_ID', flat=True)
            serialized_threemt = ThreeMtSerializer(threemt_scores, many=True)

            return Response({
                "status_of_threemt_table": status_of_threemt_table,
                "finalist_poster_id": finalist_poster_id,
                "threemt_scores": serialized_threemt.data,
                "Judge": f"{user.first_name} {user.last_name}",
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid scoring_type."}, status=status.HTTP_400_BAD_REQUEST)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
class StudentJudgeCountAPIView(APIView):
    """
    """
    def get(self, request):
        students = Students.objects.all()  # Query all Student instances
        data = StudentShowJudgeCountSerializer(students, many=True).data
        return Response(data, status=status.HTTP_200_OK)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class validate_token(APIView):
    def post(self, request):
        # sleep(10)
        return Response(status=status.HTTP_200_OK)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class populate_round_1_table(APIView):
    def get(self, request):

        # scores for undergraduate students whose poster id is in range 100 to 199
        scores = Scores_Round_1.get_average_scores()

        undergraduate_scores = scores.filter(
            Student__poster_ID__range=(100, 199))

        poster_id = undergraduate_scores.values_list(
            'Student__poster_ID', flat=True)

        # delete the scores of undergraduate students from the total scores table

        Total_Scores_Round_1_Undergraduate.objects.exclude(
            poster_id__in=poster_id).delete()

        for score in undergraduate_scores:
            total_score, created = Total_Scores_Round_1_Undergraduate.objects.get_or_create(
                poster_id=Students.objects.get(poster_ID=score['Student__poster_ID']))
            total_score.Name = score['Student__Name']
            total_score.email = score['Student__email']
            total_score.avg_research_score = score['avg_research_score']
            total_score.avg_communication_score = score['avg_communication_score']
            total_score.avg_presentation_score = score['avg_presentation_score']
            total_score.total_score = score['total_score']
            total_score.judged_count = score['judges_count']
            total_score.save()

        # filter the scores for graduate students
        graduate_scores = scores.filter(Student__poster_ID__range=(200, 299))

        poster_ids = graduate_scores.values_list(
            'Student__poster_ID', flat=True)

        Total_Scores_Round_1_Graduate.objects.exclude(
            poster_id__in=poster_ids).delete()

        for score in graduate_scores:
            total_score, created = Total_Scores_Round_1_Graduate.objects.get_or_create(
                poster_id=Students.objects.get(poster_ID=score['Student__poster_ID']))
            total_score.Name = score['Student__Name']
            total_score.email = score['Student__email']
            total_score.avg_research_score = score['avg_research_score']
            total_score.avg_communication_score = score['avg_communication_score']
            total_score.avg_presentation_score = score['avg_presentation_score']
            total_score.total_score = score['total_score']
            total_score.judged_count = score['judges_count']
            total_score.save()

        return HttpResponseRedirect(reverse('admin:index'))
    
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------from rest_framework import serializers

#@authentication_classes([JWTAuthentication])
#@permission_classes([IsAuthenticated])
class StudentCreateAPIView(APIView):
    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student added successfully."}, status=status.HTTP_201_CREATED)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
