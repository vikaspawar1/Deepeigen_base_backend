from django.shortcuts import render
from .models import Team
# Create your views here.

def team(request):
    academic_advisory_board = Team.objects.order_by('id').filter(category='academic_advisory_board')
    core_team = Team.objects.order_by('id').filter(category='core_team')
    core_team_and_TA = Team.objects.order_by('id').filter(category='core_team_and_TA')
    data = {
        'academic_advisory_board': academic_advisory_board,
        'core_team': core_team,
        'core_team_and_TA': core_team_and_TA,
        'title': 'Team | Deep Eigen',
        'description': "Deep eigen Team consists of Academic Advisory Board Members and Core Team Members.",
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    print("team_:", data)
    return render(request, 'teams/team.html', data)