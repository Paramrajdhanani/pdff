import os
import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from converter.models import Document

class Command(BaseCommand):
    help = "Clean up old documents and files to optimize disk usage."

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=2,
            help='Delete files older than this many hours (default: 2)'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        cutoff = timezone.now() - timedelta(hours=hours)

        # 1. Find and delete old Documents
        old_docs = Document.objects.filter(created_at__lt=cutoff)
        count = old_docs.count()
        
        for doc in old_docs:
            if doc.file and os.path.exists(doc.file.path):
                try:
                    os.remove(doc.file.path)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not delete file {doc.file.path}: {e}"))
            doc.delete()

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} old document records and files."))

        # 2. Cleanup orphan files in media folder that aren't in the database
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            now_ts = time.time()
            cutoff_seconds = hours * 3600
            orphan_count = 0
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Check file age
                        file_age = now_ts - os.path.getmtime(file_path)
                        if file_age > cutoff_seconds:
                            os.remove(file_path)
                            orphan_count += 1
                    except Exception:
                        pass
            if orphan_count > 0:
                self.stdout.write(self.style.SUCCESS(f"Cleaned up {orphan_count} expired orphan files from media storage."))
