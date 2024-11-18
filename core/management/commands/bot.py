from django.core.management.base import BaseCommand
from core.bot import start_bot


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **kwargs):
        start_bot()
