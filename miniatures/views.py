from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Miniature

def landing_page(request):
    search_query = request.GET.get('search', '')
    miniatures = Miniature.objects.all()
    
    if search_query:
        miniatures = miniatures.filter(
            name__icontains=search_query
        ) | miniatures.filter(
            article__icontains=search_query
        ) | miniatures.filter(
            visual_characteristics__icontains=search_query
        )
    
    context = {
        'miniatures': miniatures,
        'search_query': search_query,
    }
    return render(request, 'miniatures/landing.html', context)

def miniature_detail(request, slug):
    miniature = get_object_or_404(Miniature, slug=slug)
    
    # Find similar miniatures based on shared characteristics
    similar_miniatures = Miniature.objects.exclude(id=miniature.id).filter(
        category=miniature.category
    ).filter(
        era_livery__icontains=miniature.era_livery
    ).order_by('?')[:4]  # Randomly select up to 4 similar items
    
    # If we don't have enough similar items, add more based on just the category
    if similar_miniatures.count() < 4:
        additional_miniatures = Miniature.objects.exclude(
            id__in=[m.id for m in similar_miniatures] + [miniature.id]
        ).filter(
            category=miniature.category
        ).order_by('?')[:4 - similar_miniatures.count()]
        similar_miniatures = list(similar_miniatures) + list(additional_miniatures)
    
    context = {
        'miniature': miniature,
        'similar_miniatures': similar_miniatures,
    }
    return render(request, 'miniatures/detail.html', context)

def get_theme_for_livery(era_livery):
    """
    Returns theme colors based on the era/livery of the miniature
    """
    era_livery = era_livery.lower()
    
    themes = {
        'merah-hijau': {
            'bg_color': 'bg-green-900',
            'text_color': 'text-red-700',
            'accent_color': 'border-red-800',
            'hover_color': 'hover:bg-green-800'
        },
        'putih-biru': {
            'bg_color': 'bg-blue-100',
            'text_color': 'text-blue-900',
            'accent_color': 'border-blue-500',
            'hover_color': 'hover:bg-blue-200'
        },
        'coklat': {
            'bg_color': 'bg-amber-100',
            'text_color': 'text-amber-900',
            'accent_color': 'border-amber-600',
            'hover_color': 'hover:bg-amber-200'
        }
    }
    
    # Default theme
    default_theme = {
        'bg_color': 'bg-gray-100',
        'text_color': 'text-gray-900',
        'accent_color': 'border-gray-500',
        'hover_color': 'hover:bg-gray-200'
    }
    
    # Find matching theme
    for key, theme in themes.items():
        if key in era_livery:
            return theme
            
    return default_theme
