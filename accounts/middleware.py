from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.db.models import F
from .models import PageView, DailyVisits
import datetime


def get_client_ip(request):
    """Obtener la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class PageViewMiddleware(MiddlewareMixin):
    """Middleware para trackear todas las visitas a páginas"""
    
    def process_request(self, request):
        # Obtener información de la request
        url = request.get_full_path()
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ''
        
        # Excluir URLs administrativas y estáticas
        excluded_urls = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/api/',
            '/__debug__/',
        ]
        
        # No trackear si es una URL excluida
        if any(url.startswith(excluded) for excluded in excluded_urls):
            return None
            
        # Crear registro de visita
        try:
            # Actualizar estadísticas diarias
            today = timezone.now().date()
            daily_visits, created = DailyVisits.objects.get_or_create(
                date=today,
                defaults={'total_visits': 0, 'unique_visitors': 0}
            )
            
            # Verificar si es un visitante único ANTES de crear el registro
            is_unique_visitor = not PageView.objects.filter(
                ip_address=ip_address,
                timestamp__date=today
            ).exists()
            
            # Crear el registro de visita
            PageView.objects.create(
                url=url,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                session_key=session_key
            )
            
            # Incrementar contadores
            daily_visits.total_visits = F('total_visits') + 1
            
            if is_unique_visitor:
                daily_visits.unique_visitors = F('unique_visitors') + 1
            
            daily_visits.save()
            
        except Exception as e:
            # No fallar si hay error en el tracking
            pass
            
        return None