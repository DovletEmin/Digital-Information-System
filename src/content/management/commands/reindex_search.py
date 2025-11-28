# content/management/commands/reindex_search.py

from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from django.conf import settings
from content.models import Article, Book, Dissertation
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Полная переиндексация всех материалов в Elasticsearch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fast", action="store_true", help="Только создать индексы"
        )

    def handle(self, *args, **options):
        es_url = settings.ELASTICSEARCH_DSL["default"]["hosts"]
        es = Elasticsearch(es_url, timeout=30)

        if not es.ping():
            self.stdout.write(self.style.ERROR("Elasticsearch недоступен!"))
            return

        indices = [
            ("articles", Article),
            ("books", Book),
            ("dissertations", Dissertation),
        ]

        for index_name, Model in indices:
            self.stdout.write(f"\nОбработка: {index_name.upper()}")

            # Удаляем и создаём индекс
            if es.indices.exists(index=index_name):
                es.indices.delete(index=index_name)
                self.stdout.write(self.style.WARNING(f"Удалён индекс: {index_name}"))

            mapping = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "author": {"type": "text"},
                        "author_workplace": {"type": "text"},
                        "source_name": {"type": "text"},
                        "source_url": {"type": "keyword"},
                        "newspaper_or_journal": {"type": "text"},
                        "type": {"type": "keyword"},
                        "language": {"type": "keyword"},
                        "publication_date": {"type": "date"},
                        "average_rating": {"type": "float"},
                        "rating_count": {"type": "integer"},
                        "views": {"type": "integer"},
                        "image": {"type": "keyword"},
                        "epub_file": {"type": "keyword"},
                        "cover_image": {"type": "keyword"},
                        "categories": {
                            "type": "nested",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {
                                    "type": "text",
                                    "fields": {"keyword": {"type": "keyword"}},
                                },
                                "parent": {
                                    "type": "integer",
                                    "null_value": None,
                                },  # ← Поддержка null
                            },
                        },
                    }
                }
            }

            es.indices.create(index=index_name, body=mapping)
            self.stdout.write(self.style.SUCCESS(f"Создан индекс: {index_name}"))

            if options["fast"]:
                continue

            count = 0
            total = Model.objects.count()
            self.stdout.write(f"Индексируем {total} записей...")

            for obj in Model.objects.iterator():
                try:
                    doc = {
                        "title": obj.title,
                        "author": obj.author,
                        "language": obj.language,
                        "average_rating": round(float(obj.average_rating), 2),
                        "rating_count": obj.rating_count,
                        "views": obj.views,
                    }

                    if isinstance(obj, Article):
                        doc.update(
                            {
                                "content": obj.content,
                                "author_workplace": obj.author_workplace or None,
                                "type": obj.type,
                                "publication_date": obj.publication_date.isoformat()
                                if obj.publication_date
                                else None,
                                "source_name": obj.source_name,
                                "source_url": obj.source_url,
                                "newspaper_or_journal": obj.newspaper_or_journal,
                                "image": obj.image.url if obj.image else None,
                            }
                        )

                    if isinstance(obj, Book):
                        doc.update(
                            {
                                "content": obj.content or None,
                                "epub_file": obj.epub_file.url
                                if obj.epub_file
                                else None,
                                "cover_image": obj.cover_image.url
                                if obj.cover_image
                                else None,
                            }
                        )

                    if isinstance(obj, Dissertation):
                        doc.update(
                            {
                                "content": obj.content,
                                "author_workplace": obj.author_workplace or None,
                                "publication_date": obj.publication_date.isoformat()
                                if obj.publication_date
                                else None,
                            }
                        )

                    # ← КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: проверяем, есть ли parent!
                    doc["categories"] = [
                        {
                            "id": cat.id,
                            "name": cat.name,
                            "parent": getattr(cat, "parent_id", None)
                            or None,  # ← БЕЗОПАСНО!
                        }
                        for cat in obj.categories.all()
                    ]

                    es.index(index=index_name, id=obj.id, body=doc)
                    count += 1

                    if count % 50 == 0:
                        self.stdout.write(f"   → {count}/{total}")

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Ошибка при {obj.__class__.__name__} ID={obj.id}: {e}"
                        )
                    )

            es.indices.refresh(index=index_name)
            self.stdout.write(
                self.style.SUCCESS(
                    f"ГОТОВО → {count} {Model.__name__} проиндексировано"
                )
            )

        self.stdout.write(
            self.style.SUCCESS("\nВСЁ ГОТОВО! ЭЛАСТИК ПОЛНОСТЬЮ ОБНОВЛЁН!")
        )
