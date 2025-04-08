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
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class GetThreeMtAPIView(APIView):
    def get(self, request):
        poster_id = request.query_params.get('poster_id', None)
        if not poster_id:
            return Response({
                "ThreeMT_posters": [],
                "status": "Thesis ID not provided"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate that poster_id is an integer
        try:
            poster_id = int(poster_id)
        except ValueError:
            return Response({
                "ThreeMT_posters": [],
                "status": "Invalid Thesis ID (not an integer)"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure poster_id is within 401-499
        if poster_id < 401 or poster_id > 499:
            return Response({
                "ThreeMT_posters": [],
                "status": "Thesis ID must be between 401 and 499"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if poster exists in Students table
        try:
            student = Students.objects.get(poster_ID=poster_id)
        except Students.DoesNotExist:
            return Response({
                "ThreeMT_posters": [],
                "status": "Not a Valid Thesis Id"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if a ThreeMt entry exists for that poster & current judge
        three_mt_entries = ThreeMt.objects.filter(
            poster_id=poster_id,
            judge=request.user
        )

        if three_mt_entries.exists():
            # Case: Return existing ThreeMt records, adding extra fields
            output_list = []
            for entry in three_mt_entries:
                # Build a dictionary of existing data plus extra fields
                output_list.append({
                    "poster_id": entry.poster_id,
                    "student_name": entry.student.Name,
                    "student_email": entry.student.email,
                    "poster_title": entry.student.poster_title,  # from Students model
                    "student": entry.student.id,
                    "comprehension_content": entry.comprehension_content,
                    "engagement": entry.engagement,
                    "communication": entry.communication,
                    "overall_impression": entry.overall_impression,
                    "feedback": entry.feedback if entry.feedback else "",
                })
            return Response({"ThreeMT_posters": output_list}, status=status.HTTP_200_OK)
        else:
            # Poster exists but no ThreeMt record yet
            return Response({
                "ThreeMT_posters": [{
                    "poster_id": student.poster_ID,
                    "student_name": student.Name,
                    "student_email": student.email,
                    "poster_title": student.poster_title,  # from Students model
                    "student": student.id,
                    "comprehension_content": None,
                    "engagement": None,
                    "communication": None,
                    "overall_impression": None,
                    "feedback": '',
                }],
                "status": "Poster exists but has not been scored yet"
            }, status=status.HTTP_200_OK)



@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UpdateThreeMtAPIView(APIView):

    def post(self, request):
        poster_id = request.data.get('poster_id')
        student_id = request.data.get('student')

        if not poster_id or not student_id:
            return Response({"error": "poster_id and student are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_obj = Students.objects.get(poster_ID=poster_id)
        except Students.DoesNotExist:
            return Response({"error": "Thesis not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get or create ExpLearning record
        three_mt, created = ThreeMt.objects.get_or_create(
            poster_id=poster_id,
            student=student_obj,
            judge=request.user
        )

        # Validate and update
        serializer = UpdateThreeMtSerializer(three_mt, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            message = "Created" if created else "Updated"
            return Response({
                "message": message,
                "updated_fields": UpdateThreeMtSerializer(three_mt).data
            }, status=status.HTTP_200_OK)

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
