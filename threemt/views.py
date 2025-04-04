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
                "status": "Poster ID not provided"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2) Validate that poster_id is an integer
        try:
            poster_id = int(poster_id)
        except ValueError:
            return Response({
                "Exp_learning_posters": [],
                "status": "Invalid Poster ID (not an integer)"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure poster_id is within 401-499
        if poster_id < 401 or poster_id > 499:
            return Response({
                "ThreeMT_posters": [],
                "status": "Poster ID must be between 401 and 499"
            }, status=status.HTTP_400_BAD_REQUEST)
        # Check if poster exists in Students table
        try:
            student = Students.objects.get(poster_ID=poster_id)
        except Students.DoesNotExist:
            return Response({
                "ThreeMT_posters": [],
                "status": "Not a Valid Poster Id"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if an ExpLearning entry exists for that poster
        print(request.user.id, "request.user.id")
        print(poster_id, "poster_id")
        three_mt_entries = ThreeMt.objects.filter(poster_id=poster_id, judge=request.user)
        print(three_mt_entries, "three_mt_entries")
        if three_mt_entries.exists():
            # Case 3: Return existing ExpLearning records
            serialized_data = ThreeMtSerializer(three_mt_entries, many=True).data
            return Response({"ThreeMT_posters": serialized_data}, status=status.HTTP_200_OK)
        else:
            # Case 2: Poster exists but no ExpLearning record yet
            return Response({
                "ThreeMT_posters": [{
                    "poster_id": student.poster_ID,
                    "student_name": student.Name,
                    "student_email": student.email,
                    "student":student.id,
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
    # def post(self, request):
    #         poster_id = request.data.get('poster_id')

    #         if not poster_id:
    #             return Response({"error": "poster_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    #         # Get the ThreeMt instance
    #         three_mt = get_object_or_404(ThreeMt, poster_id=poster_id)

    #         # Validate and update using serializer
    #         serializer = UpdateThreeMtSerializer(three_mt, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({
    #                 "message": "Updated",
    #                 "updated_fields": serializer.data
    #             }, status=status.HTTP_200_OK)

    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        poster_id = request.data.get('poster_id')
        student_id = request.data.get('student')

        if not poster_id or not student_id:
            return Response({"error": "poster_id and student are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_obj = Students.objects.get(poster_ID=poster_id)
        except Students.DoesNotExist:
            return Response({"error": "Poster not found."}, status=status.HTTP_404_NOT_FOUND)

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
