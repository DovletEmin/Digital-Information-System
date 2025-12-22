from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from content.models import PendingView, Article, Book, Dissertation
from content.tasks import index_object_task
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Flush PendingView buffer into actual models (increment views) and reindex"

    def handle(self, *args, **options):
        pending = list(PendingView.objects.all())
        if not pending:
            self.stdout.write("No pending views to flush.")
            return

        for pv in pending:
            model = None
            if pv.content_type == "article":
                model = Article
            elif pv.content_type == "book":
                model = Book
            elif pv.content_type == "dissertation":
                model = Dissertation

            if model is None:
                self.stdout.write(f"Unknown content_type: {pv.content_type}")
                continue

            try:
                with transaction.atomic():
                    updated = model.objects.filter(id=pv.content_id).update(
                        views=F("views") + pv.count
                    )
                    if updated:
                        # enqueue indexing as a Celery task so retries are handled by Celery
                        index_object_task.delay(
                            model._meta.app_label, model.__name__, pv.content_id
                        )
                        self.stdout.write(
                            f"Flushed {pv.count} views to {pv.content_type}#{pv.content_id}"
                        )
                    else:
                        self.stdout.write(
                            f"Target not found: {pv.content_type}#{pv.content_id}"
                        )
                    # delete pending row
                    pv.delete()
            except Exception as e:
                logger.exception("Error flushing PendingView %s", pv)
                self.stdout.write(f"Error flushing {pv}: {e}")

        self.stdout.write(self.style.SUCCESS("Flush completed."))
