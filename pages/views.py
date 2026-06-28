from django.shortcuts import render


def guides_view(request):
    return render(request, "guides/guides.html")


def community_view(request):
    return render(request, "community/community.html")
