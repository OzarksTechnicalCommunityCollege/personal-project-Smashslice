from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models.functions import TruncDate
from django.db.models import Count
from .models import GitHubCommit

class CommitCountChartView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        # Group commits by date and count
        data = (
            GitHubCommit.objects
            .annotate(day=TruncDate('date'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        chart_data = {
            'labels': [entry['day'].isoformat() for entry in data],
            'counts': [entry['count'] for entry in data],
        }
        return Response(chart_data)
