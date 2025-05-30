from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from home.models import Students
from explearning.models import Total_Scores_Exp_Learning
from .models import ExpLearning
from .serializer import ExpLearningSerializer, UpdateExpLearningSerializer
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from home.models import Students
from .models import ExpLearning
# from .serializers import ExpLearningSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated



@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class GetExpLearningAPIView(APIView):
    def get(self, request):
        # 1) Retrieve poster_id
        poster_id_str = request.query_params.get('poster_id', None)
        if not poster_id_str:
            return Response({
                "Exp_learning_posters": [],
                "status": "Poster ID not provided"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2) Validate that poster_id is an integer
        try:
            poster_id = int(poster_id_str)
        except ValueError:
            return Response({
                "Exp_learning_posters": [],
                "status": "Invalid Poster ID (not an integer)"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3) Ensure poster_id is within 301-399 range
        if poster_id < 301 or poster_id > 399:
            return Response({
                "Exp_learning_posters": [],
                "status": "Poster ID must be between 301 and 399"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4) Check if poster exists in Students table
        try:
            student = Students.objects.get(poster_ID=poster_id)
        except Students.DoesNotExist:
            return Response({
                "Exp_learning_posters": [],
                "status": "Not a Valid Poster ID"
            }, status=status.HTTP_404_NOT_FOUND)

        # 5) Check if an ExpLearning entry exists for that poster + this judge
        exp_learning_entries = ExpLearning.objects.filter(
            poster_id=poster_id,
            judge=request.user.id
        )

        if exp_learning_entries.exists():
            # Case: Poster already scored by this judge
            output_list = []
            for entry in exp_learning_entries:
                # Manually merge fields from ExpLearning + Students
                output_list.append({
                    "poster_id": entry.poster_id,
                    "student_name": entry.student.Name,
                    "student_email": entry.student.email,
                    "poster_title": entry.student.poster_title,  # from Students model
                    "student_id": entry.student.id,
                    "reflection_score": entry.reflection_score,
                    "communication_score": entry.communication_score,
                    "presentation_score": entry.presentation_score,
                    "feedback": entry.feedback if entry.feedback else None,
                })
            return Response({"Exp_learning_posters": output_list}, status=status.HTTP_200_OK)
        else:
            # Case: Poster exists but no ExpLearning record yet
            return Response({
                "Exp_learning_posters": [{
                    "poster_id": student.poster_ID,
                    "student_name": student.Name,
                    "student_email": student.email,
                    "poster_title": student.poster_title,  # from Students model
                    "student_id": student.id,
                    "reflection_score": None,
                    "communication_score": None,
                    "presentation_score": None,
                    "feedback": None,
                }],
                "status": "Poster exists but has not been scored yet"
            }, status=status.HTTP_200_OK)




    
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])

class UpdateExpLearningAPIView(APIView):
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def post(self, request):
        poster_id = request.data.get('poster_id')
        student_id = request.data.get('student')

        if not poster_id or not student_id:
            return Response({"error": "poster_id and student are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_obj = Students.objects.get(id=student_id)
        except Students.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get or create ExpLearning record
        exp_learning, created = ExpLearning.objects.get_or_create(
            poster_id=poster_id,
            student=student_obj,
            judge=request.user
        )

        # Validate and update
        serializer = UpdateExpLearningSerializer(exp_learning, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            message = "Created" if created else "Updated"
            return Response({
                "message": message,
                "updated_fields": ExpLearningSerializer(exp_learning).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class ComputeAndStoreExpLearningAggregatesAPIView(APIView):
    def post(self, request):
        try:
            # Optional: Clean previous aggregation if required
            # Total_Scores_Exp_Learning.objects.all().delete()

            # Fetch aggregated scores
            aggregated_scores = ExpLearning.get_average_scores()

            with transaction.atomic():  # Ensure atomic DB transaction
                for data in aggregated_scores:
                    poster_id = data['student__poster_ID']
                    student_obj = Students.objects.filter(poster_ID=poster_id).first()
                    if not student_obj:
                        continue  # Skip if student record not found

                    # Create or update aggregated score entry
                    Total_Scores_Exp_Learning.objects.update_or_create(
                        poster_id=student_obj,
                        defaults={
                            'Name': data['student__Name'],
                            'email': data['student__email'],
                            'judged_count': data['judges_count'],
                            'avg_reflection_score': data['avg_reflection_score'],
                            'avg_communication_score': data['avg_communication_score'],
                            'avg_presentation_score': data['avg_presentation_score'],
                            'total_score': data['total_score'],
                        }
                    )

            return Response({"message": "Aggregated scores stored successfully in Total_Scores_Exp_Learning."},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)