from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from home.models import Students
from explearning.models import Total_Scores_Exp_Learning
from .models import ExpLearning
from .serializer import ExpLearningSerializer, UpdateExpLearningSerializer
from django.shortcuts import get_object_or_404

class GetExpLearningAPIView(APIView):
    def get(self, request):
        poster_id = request.query_params.get('poster_id', None)

        if poster_id:
            exp_learnings_objects = ExpLearning.objects.filter(poster_id=poster_id)
            if not exp_learnings_objects.exists():
                return Response({"message": f"No scores found for Poster ID {poster_id}."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # poster_id not provided — return blank result instead of all records
            return Response({"Exp_learning_posters": []}, status=status.HTTP_200_OK)

        serialized_data = ExpLearningSerializer(exp_learnings_objects, many=True).data
        return Response({"Exp_learning_posters": serialized_data}, status=status.HTTP_200_OK)

    
#@authentication_classes([JWTAuthentication])
#@permission_classes([IsAuthenticated])
class UpdateExpLearningAPIView(APIView):
    def post(self, request):
        poster_id = request.data.get('poster_id')
        
        if not poster_id:
            return Response({"error": "poster_ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the existing ExpLearning record
        exp_learning = get_object_or_404(ExpLearning, poster_id=poster_id)
        
        # Use serializer to validate and update the instance
        serializer = UpdateExpLearningSerializer(exp_learning, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # return Response({"message": "ExpLearning updated successfully", "updated_fields": serializer.validated_data},
            #                 status=status.HTTP_200_OK)
            return Response({"message": "Updated", "updated_fields": ExpLearningSerializer(exp_learning).data})

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