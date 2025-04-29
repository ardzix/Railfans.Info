from django.contrib import admin
from django.utils.html import format_html
from .models import Miniature, Gallery

class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1
    fields = ('image', 'caption', 'order')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Miniature)
class MiniatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year_of_production', 'era_livery', 'thumbnail_preview', 'qr_code_preview')
    list_filter = ('category', 'year_of_production', 'era_livery')
    search_fields = ('name', 'era_livery', 'visual_characteristics')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('qr_code_preview',)
    inlines = [GalleryInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'year_of_production', 'era_livery')
        }),
        ('Visual Information', {
            'fields': ('thumbnail', 'main_image', 'visual_characteristics')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_preview')
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = 'Thumbnail'

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code.url)
        return "-"
    qr_code_preview.short_description = 'QR Code Preview'
