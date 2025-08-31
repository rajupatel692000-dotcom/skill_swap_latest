from django.shortcuts import render, get_object_or_404
from .models import SkillsCategory, Skills, UserSkills
from apps.accounts.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from apps.accounts.views import login_required_custom

def CourseView(request):
    categories = SkillsCategory.objects.all()
    
    # Get all skills that have been added by users
    skills_qs = Skills.objects.select_related("category").filter(user_skills__isnull=False).distinct()

    # Search filter
    search_query = request.GET.get("q")
    if search_query:
        skills_qs = skills_qs.filter(name__icontains=search_query)

    # Category filter
    category_ids = request.GET.getlist("categories[]")  # expects categories[]=1&categories[]=2
    if category_ids and "all" not in category_ids:
        skills_qs = skills_qs.filter(category_id__in=category_ids)

    #Level Filter
    level_filters = request.GET.getlist("levels[]") #expects for levels[]
    if level_filters and "all" not in level_filters:
        skills_qs = skills_qs.filter(level__in=level_filters)

    # Exclude skills added by the current user if logged in
    if 'user_id' in request.session:
        user_id = request.session.get('user_id')
        skills_qs = skills_qs.exclude(user_skills__user_id=user_id)

    paginator = Paginator(skills_qs, 6)
    page_number = request.GET.get("page")
    skills = paginator.get_page(page_number)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("category_skills/courses_grid.html", {"skills": skills})
        return JsonResponse({"html": html})

    return render(
        request,
        "category_skills/courses.html",
        {"categories": categories, "skills": skills , "level_choices" : Skills.LEVEL_CHOICES},
    )

def CourseDetailView(request, skill_id):
    skill = get_object_or_404(Skills, id=skill_id)
    # Get the user who added this skill
    user_skill = UserSkills.objects.filter(skill=skill).first()
    return render(request, "category_skills/course-details.html", {
        "skill": skill,
        "user_skill": user_skill
    })

def InstructorView(request):
    # Get all users who have added skills
    users_with_skills = User.objects.filter(user_skills__isnull=False).distinct().prefetch_related('user_skills__skill__category')
    
    # Group skills by user
    instructors_data = []
    for user in users_with_skills:
        user_skills = user.user_skills.all()
        skills_list = [us.skill for us in user_skills]
        instructors_data.append({
            'user': user,
            'skills': skills_list,
            'skills_count': len(skills_list)
        })
    
    return render(request, "category_skills/instructors.html", {
        "instructors_data": instructors_data
    })

@login_required_custom
def add_skill_to_profile(request, skill_id):
    """Add a skill to user's profile"""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user = get_object_or_404(User, id=user_id)
        skill = get_object_or_404(Skills, id=skill_id)
        user_skill, created = UserSkills.objects.get_or_create(
            user=user,
            skill=skill
        )
        if created:
            return JsonResponse({'success': True, 'message': f'Skill "{skill.name}" added to your profile!'})
        else:
            return JsonResponse({'success': False, 'message': 'Skill already in your profile!'})
    return JsonResponse({'success': False, 'message': 'Invalid request method!'})

@login_required_custom
def remove_skill_from_profile(request, skill_id):
    """Remove a skill from user's profile"""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user = get_object_or_404(User, id=user_id)
        skill = get_object_or_404(Skills, id=skill_id)
        try:
            user_skill = UserSkills.objects.get(user=user, skill=skill)
            user_skill.delete()
            return JsonResponse({'success': True, 'message': f'Skill "{skill.name}" removed from your profile!'})
        except UserSkills.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Skill not found in your profile!'})
    return JsonResponse({'success': False, 'message': 'Invalid request method!'})
