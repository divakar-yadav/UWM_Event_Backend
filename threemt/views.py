from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from home.models import Students
from .models import ThreeMt, Total_Scores_ThreeMT
from .serializer import ThreeMtSerializer, UpdateThreeMtSerializer
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from home.models import Students
from .models import ThreeMt
# from .serializers import ThreeMtSerializer  # Make sure this serializer exists



class GetThreeMtAPIView(APIView):
    def get(self, request):
        poster_id = request.query_params.get('poster_id', None)

        if not poster_id:
            return Response({
                "Three_mt_posters": [],
                "status": "Poster ID not provided"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the poster exists in the Students table
        try:
            student = Students.objects.get(poster_ID=poster_id)
        except Students.DoesNotExist:
            return Response({
                "Three_mt_posters": [],
                "status": "Not a Valid Poster Id"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if there are any ThreeMt entries for this poster ID
        three_mt_entries = ThreeMt.objects.filter(poster_id=poster_id)

        if three_mt_entries.exists():
            # Case 3: Poster exists in both Students and ThreeMt → return the scored data
            serialized_data = ThreeMtSerializer(three_mt_entries, many=True).data
            return Response({
                "Three_mt_posters": serialized_data
            }, status=status.HTTP_200_OK)
        else:
            # Case 2: Poster exists but hasn't been scored yet in ThreeMt
            return Response({
                "Three_mt_posters": [{
                    "poster_id": student.poster_ID,
                    "student_name": student.Name,
                    "student_email": student.email,
                    "comprehension_content": None,
                    "engagement": None,
                    "communication": None,
                    "overall_impression": None,
                    "feedback": None
                }],
                "status": "Poster exists but has not been scored yet"
            }, status=status.HTTP_200_OK)

#@authentication_classes([JWTAuthentication])
#@permission_classes([IsAuthenticated])
class UpdateThreeMtAPIView(APIView):
    def post(self, request):
        poster_id = request.data.get('poster_id')
        
        if not poster_id:
            return Response({"error": "poster_ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the existing ThreeMt record
        three_mt = get_object_or_404(ThreeMt, poster_id=poster_id)
        
        # Use serializer to validate and update the instance
        serializer = UpdateThreeMtSerializer(three_mt, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "ThreeMt updated successfully", "updated_fields": serializer.validated_data},
                            status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComputeAndStoreThreeMTAggregatesAPIView(APIView):
    def post(self, request):
        try:
            aggregated_scores = ThreeMt.get_average_scores()

            with transaction.atomic():
                for data in aggregated_scores:
                    poster_id = data['student__poster_ID']
                    student_obj = Students.objects.filter(poster_ID=poster_id).first()
                    if not student_obj:
                        continue

                    Total_Scores_ThreeMT.objects.update_or_create(
                        poster_id=student_obj,
                        defaults={
                            'Name': data['student__Name'],
                            'email': data['student__email'],
                            'judged_count': data['judges_count'],
                            'avg_comprehension_content': data['avg_comprehension_content'],
                            'avg_engagement': data['avg_engagement'],
                            'avg_communication': data['avg_communication'],
                            'avg_overall_impression': data['avg_overall_impression'],
                            'total_score': data['total_score'],
                        }
                    )

            return Response({"message": "ThreeMT aggregated scores stored successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
