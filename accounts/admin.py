from django.contrib import admin
from .models import PageView, DailyVisits

# Register your models here.

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['url', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp', 'url']
    search_fields = ['url', 'ip_address', 'user__username']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        # No permitir agregar manualmente
        return False

@admin.register(DailyVisits) 
class DailyVisitsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_visits', 'unique_visitors']
    list_filter = ['date']
    ordering = ['-date']
    
    def has_add_permission(self, request):
        # No permitir agregar manualmente
        return False
