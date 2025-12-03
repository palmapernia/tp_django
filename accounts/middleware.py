from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.db.models import F
from .models import PageView, DailyVisits
import datetime
import uuid


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
            
        # Sistema de tracking mejorado
        try:
            today = timezone.now().date()
            
            # Obtener o crear visitor_id único por navegador
            visitor_id = request.COOKIES.get('visitor_id')
            if not visitor_id:
                visitor_id = str(uuid.uuid4())
            
            # Verificar si ya hay una visita en esta sesión del navegador
            session_visit_key = f'session_visited_{today}'
            has_visited_in_session = request.COOKIES.get(session_visit_key, False)
            
            # Solo contar si es la primera página de esta sesión del navegador
            if not has_visited_in_session:
                
                # Verificar si es visitante único (primera vez que viene con este visitor_id)
                is_unique_visitor = not PageView.objects.filter(
                    visitor_id=visitor_id
                ).exists()
                
                # Crear registro de visita
                PageView.objects.create(
                    url=url,
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_key=session_key,
                    visitor_id=visitor_id
                )
                
                # Actualizar estadísticas diarias
                daily_visits, created = DailyVisits.objects.get_or_create(
                    date=today,
                    defaults={'total_visits': 0, 'unique_visitors': 0}
                )
                
                # Incrementar contadores
                daily_visits.total_visits = F('total_visits') + 1
                if is_unique_visitor:
                    daily_visits.unique_visitors = F('unique_visitors') + 1
                
                daily_visits.save()
                
                # Marcar cookies para usar en process_response
                request._visitor_id = visitor_id  # Cookie persistente (1 año)
                request._session_key = session_visit_key  # Cookie de sesión
                
        except Exception as e:
            # No fallar si hay error en el tracking
            pass
            
        return None
    
    def process_response(self, request, response):
        """Establecer cookies necesarias"""
        if hasattr(request, '_visitor_id'):
            # Cookie persistente para visitante único (1 año)
            response.set_cookie(
                'visitor_id', 
                request._visitor_id,
                max_age=365*24*60*60,  # 1 año
                httponly=True,
                samesite='Lax'
            )
            
            # Cookie de sesión que se elimina al cerrar navegador
            response.set_cookie(
                request._session_key,
                'true',
                httponly=True,
                samesite='Lax'
                # Sin max_age = cookie de sesión (se elimina al cerrar navegador)
            )
        return response