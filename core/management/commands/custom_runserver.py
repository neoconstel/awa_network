from django.core.management.commands.runserver import Command as runserver
class Command(runserver):
    def handle(self, *args, **options):
        options['addrport'] = "localhost:8000"  # custom ipaddress/port
        super().handle(*args, **options)
        