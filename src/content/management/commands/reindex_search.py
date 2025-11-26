from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from django.db.models import FileField, ImageField, DateField
from content.models import Article, Book, Dissertation


class Command(BaseCommand):
    help = (
        "Пересоздаёт и заполняет Elasticsearch индексы для статей, книг и диссертаций"
    )

    def handle(self, *args, **options):
        es = Elasticsearch(["http://127.0.0.1:9200"])

        indices = {
            "articles": Article,
            "books": Book,
            "dissertations": Dissertation,
        }

        for index_name, Model in indices.items():
            # Удаляем старый индекс
            if es.indices.exists(index=index_name):
                es.indices.delete(index=index_name)
                self.stdout.write(f"Удалён индекс: {index_name}")

            # Создаём новый индекс с мэппингом
            es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "content": {"type": "text"},
                            "author": {"type": "text"},
                            "author_workplace": {"type": "text"},
                            "source_name": {"type": "text"},
                            "source_url": {"type": "keyword"},
                            "newspaper_or_journal": {"type": "text"},
                            "type": {"type": "keyword"},
                            "image": {"type": "keyword"},
                            "epub_file": {"type": "keyword"},
                            "cover_image": {"type": "keyword"},
                            "language": {"type": "keyword"},
                            "publication_date": {"type": "date"},
                            "rating": {"type": "integer"},
                            "views": {"type": "integer"},
                            "categories": {
                                "type": "nested",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "keyword"},
                                    "parent": {"type": "integer"},
                                },
                            },
                        }
                    }
                },
                ignore=400,
            )
            self.stdout.write(f"Создан индекс: {index_name}")

            count = 0
            for obj in Model.objects.all():
                try:
                    data = {}

                    for field in obj._meta.get_fields():
                        # Пропускаем M2M и обратные связи
                        if field.many_to_many or field.one_to_many:
                            continue

                        field_name = field.name
                        value = getattr(obj, field_name, None)

                        # Файловые поля: НЕ трогаем .url, пока не убедимся, что есть имя
                        if isinstance(field, (FileField, ImageField)):
                            if value and getattr(value, "name", None):
                                data[field_name] = value.url
                            else:
                                data[field_name] = None

                        # Даты: сериализуем в ISO
                        elif isinstance(field, DateField):
                            data[field_name] = (
                                value.isoformat() if value is not None else None
                            )

                        # Остальные поля как есть (FK попадёт как объект; при необходимости поменяй на id)
                        else:
                            data[field_name] = value

                    # M2M категории (явно формируем список словарей)
                    data["categories"] = [
                        {
                            "id": c.id,
                            "name": c.name,
                            "parent": c.parent.id
                            if getattr(c, "parent", None)
                            else None,
                        }
                        for c in obj.categories.all()
                    ]

                    # Индексация в Elasticsearch
                    es.index(index=index_name, id=obj.id, body=data)
                    count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Ошибка при индексации {obj.__class__.__name__} ID={obj.id}: {e}"
                        )
                    )

            es.indices.refresh(index=index_name)
            self.stdout.write(f"  → Проиндексировано {count} {Model.__name__}")

        self.stdout.write(self.style.SUCCESS("ГОТОВО! ВСЕ ИНДЕКСЫ ПРОИНДЕКСИРОВАНЫ!"))
