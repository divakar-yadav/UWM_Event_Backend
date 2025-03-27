from time import sleep
from home.models import Students, Scores_Round_1
from signup.models import User
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from precheckposter.views import check_poster_round_1, check_poster_round_1_edit


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class round1_insert(APIView):
    # this will get the poster id from the json and check if the poster is valid or not
    # if the poster is valid then it will return the poster id and the poster title and student name
    # if the poster is not valid then it will return the error message

    def get(self, request, poster_id):
        # check if the poster is valid or not
        # 1 -> vaild poster id and can be scored
        # 2 -> invalid poster id
        # 3 -> poster already scored by the judge
        # 4 -> poster is not a finalist

        poster_status = check_poster_round_1(poster_id, request.user)

        if poster_status == 1:
            poster = Students.objects.filter(poster_ID=poster_id).first()
            poster_title = poster.poster_title
            student_name = poster.Name
            student_email = poster.email
            student_department = poster.department

            return Response({"poster_id": poster_id, "poster_title": poster_title, "student_name": student_name, "student_email": student_email, "student_department": student_department}, status=status.HTTP_200_OK)
        elif poster_status == 2:
            return Response({"error": "Invalid Poster ID"}, status=status.HTTP_400_BAD_REQUEST)
        elif poster_status == 3:
            return Response({"error": "Poster Already Scored"}, status=status.HTTP_400_BAD_REQUEST)
        elif poster_status == 4:
            return Response({"error": "Poster is not a finalist"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # check if the poster is valid or not and if the poster is valid then save the score in Scores_Round_1
        # we will get the poster id, judge from the current user, researchScore, communicationScore, and presentationScore
        # 1 -> vaild poster id and can be scored
        # 2 -> invalid poster id
        # 3 -> poster already scored by the judge

        poster_id = request.data.get("poster_id")
        poster_status = check_poster_round_1(poster_id, request.user)

        if poster_status == 1:
            poster = Students.objects.filter(poster_ID=poster_id).first()
            """
            all the scores should not ne null or empty
            research_score (0-50)
            communication_score (0-30)
            presentation_score (0-20)
            """
            research_score = request.data.get("research_score")
            communication_score = request.data.get("communication_score")
            presentation_score = request.data.get("presentation_score")
            feedback = request.data.get("feedback")

            if research_score is None or research_score == "" or communication_score is None or \
                    communication_score == "" or presentation_score is None or presentation_score == "":
                return Response({"error": "Please submit your score for each category."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                research_score = float(research_score)
                communication_score = float(communication_score)
                presentation_score = float(presentation_score)
            except:
                return Response({"error": "Please enter a valid score."}, status=status.HTTP_400_BAD_REQUEST)

            if research_score < 0 or research_score > 50 or communication_score < 0 or communication_score > 30 or presentation_score < 0 or presentation_score > 20:
                return Response({"error": "Scores out of range or not numeric."}, status=status.HTTP_400_BAD_REQUEST)

            # save the score in Scores_Round_1
            # get the student object from the poster id
            student = Students.objects.filter(poster_ID=poster_id).first()

            scores_round_1 = Scores_Round_1(
                Student=student,
                judge=request.user,
                research_score=research_score,
                communication_score=communication_score,
                presentation_score=presentation_score,
                feedback=feedback
            )
            scores_round_1.save()

            return Response({"success": "Score submitted successfully."}, status=status.HTTP_200_OK)
        elif poster_status == 2:
            return Response({"error": "Invalid Poster ID"}, status=status.HTTP_400_BAD_REQUEST)
        elif poster_status == 3:
            return Response({"error": "Poster Already Scored"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)



@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class round1_edit(APIView):
    # this will get the poster id from the json and check if the poster is valid or not
    # if the poster is valid then it will return the poster id and the poster title and student name
    # if the poster is not valid then it will return the error message

    def get(self, request, poster_id):
        # check if the poster is valid or not
        # 1 -> valid poster id and can be edited
        # 2 -> invalid poster id
        # 3 -> poster is not scored by the judge
        scoring_type = request.query_params.get('scoring_type')
        scoring_type = "research-poster"
        poster_status = check_poster_round_1_edit(poster_id, request.user,scoring_type)
        print(poster_status,"poster_status")
        if poster_status == 1:
            poster = Students.objects.filter(poster_ID=poster_id).first()
            poster_title = poster.poster_title
            student_name = poster.Name
            student_email = poster.email
            student_department = poster.department
            # get the research score, communication score, and presentation score from Scores_Round_1
            scores_round_1 = Scores_Round_1.objects.filter(
                Student=poster, judge=request.user).first()
            research_score = scores_round_1.research_score
            communication_score = scores_round_1.communication_score
            presentation_score = scores_round_1.presentation_score
            feedback = scores_round_1.feedback

            return Response({"poster_id": poster_id, "poster_title": poster_title, "student_name": student_name, "student_email": student_email, "student_department": student_department, "research_score": research_score, "communication_score": communication_score, "presentation_score": presentation_score, "feedback": feedback}, status=status.HTTP_200_OK)
        elif poster_status == 2:
            return Response({"error": "Invalid Poster ID"}, status=status.HTTP_400_BAD_REQUEST)
        elif poster_status == 3:
            return Response({"error": "Poster is not scored by the judge"}, status=status.HTTP_400_BAD_REQUEST)
        else:

            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # check if the poster is valid or not and if the poster is valid then save the score in Scores_Round_2
        # we will get the poster id, judge from the current user, researchScore, communicationScore, and presentationScore
        # 1 -> valid poster id and can be edited
        # 2 -> invalid poster id
        # 3 -> poster is not scored by the judge

        poster_id = request.data.get("poster_id")
        poster_status = check_poster_round_1_edit(poster_id, request.user,"research-poster")

        if poster_status == 1:
            poster = Students.objects.filter(poster_ID=poster_id).first()
            """
            all the scores should not ne null or empty
            research_score (0-50)
            communication_score (0-30)
            presentation_score (0-20)
            """
            research_score = request.data.get("research_score")
            communication_score = request.data.get("communication_score")
            presentation_score = request.data.get("presentation_score")
            feedback = request.data.get("feedback")

            if research_score is None or research_score == "" or communication_score is None or \
                    communication_score == "" or presentation_score is None or presentation_score == "":
                return Response({"error": "Please submit your score for each category."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                research_score = float(research_score)
                communication_score = float(communication_score)
                presentation_score = float(presentation_score)
            except:
                return Response({"error": "Please enter a valid score."}, status=status.HTTP_400_BAD_REQUEST)

            if research_score < 0 or research_score > 50 or communication_score < 0 or communication_score > 30 or presentation_score < 0 or presentation_score > 20:
                return Response({"error": "Scores out of range or not numeric."}, status=status.HTTP_400_BAD_REQUEST)

            # save the score in Scores_Round_2
            # get the student object from the poster id
            student = Students.objects.filter(poster_ID=poster_id).first()

            scores_round_1 = Scores_Round_1.objects.filter(
                Student=student, judge=request.user).first()

            scores_round_1.research_score = research_score
            scores_round_1.communication_score = communication_score
            scores_round_1.presentation_score = presentation_score
            scores_round_1.feedback = feedback
            scores_round_1.save()

            return Response({"success": "Score submitted successfully."}, status=status.HTTP_200_OK)
        elif poster_status == 2:

            return Response({"error": "Invalid Poster ID"}, status=status.HTTP_400_BAD_REQUEST)
        elif poster_status == 3:

            return Response({"error": "Poster is not scored by the judge"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
