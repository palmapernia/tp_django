from django.core.management.base import BaseCommand
from accounts.models import PageView, DailyVisits


class Command(BaseCommand):
    help = 'Limpia todas las visitas de la base de datos para empezar desde cero'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma que quieres eliminar todas las visitas',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'Este comando eliminará TODAS las visitas de la base de datos.\n'
                    'Para confirmar, ejecuta: python manage.py clear_visits --confirm'
                )
            )
            return

        # Contar antes de eliminar
        pageviews_count = PageView.objects.count()
        daily_count = DailyVisits.objects.count()

        # Eliminar todos los registros
        PageView.objects.all().delete()
        DailyVisits.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Eliminados {pageviews_count} registros de PageView\n'
                f'✓ Eliminados {daily_count} registros de DailyVisits\n'
                f'✓ Base de datos de visitas limpia. Los contadores empezarán desde 0.'
            )
        )