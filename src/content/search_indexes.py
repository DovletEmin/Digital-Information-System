# content/search_indexes.py — ФИНАЛЬНЫЙ, ВЕЧНЫЙ, ЛЕГЕНДАРНЫЙ

from elasticsearch_dsl import (
    Document,
    Text,
    Keyword,
    Date,
    Integer,
    Float,
    Nested,
    InnerDoc,
)
from elasticsearch_dsl.connections import connections
from .models import Article, Book, Dissertation

# Подключение к Elasticsearch
connections.create_connection(hosts=["http://127.0.0.1:9200"], timeout=30)


class CategoryDoc(InnerDoc):
    id = Integer()
    name = Text(fields={"keyword": Keyword()})
    parent = Integer()


# ======================= СТАТЬИ =======================
class ArticleDoc(Document):
    title = Text(analyzer="standard", fields={"keyword": Keyword()})
    content = Text(analyzer="standard")
    author = Text(fields={"keyword": Keyword()})
    author_workplace = Text()

    # Источники
    source_name = Text()
    source_url = Keyword()
    newspaper_or_journal = Text()

    # Метаданные
    type = Keyword()
    language = Keyword()
    publication_date = Date()

    # Статистика
    average_rating = Float()
    rating_count = Integer()
    views = Integer()

    # Изображение
    image = Keyword()

    # Категории
    categories = Nested(CategoryDoc)

    class Index:
        name = "articles"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Article

        def prepare_image(self, obj):
            return obj.image.url if obj.image and hasattr(obj.image, "url") else None

        def prepare_average_rating(self, obj):
            return round(float(obj.average_rating), 2)

        def prepare_categories(self, obj):
            return [
                {"id": cat.id, "name": cat.name, "parent": cat.parent_id}
                for cat in obj.categories.all()
            ]


# ======================= КНИГИ =======================
class BookDoc(Document):
    title = Text(analyzer="standard", fields={"keyword": Keyword()})
    content = Text(analyzer="standard")
    author = Text(fields={"keyword": Keyword()})

    # Файлы
    epub_file = Keyword()
    cover_image = Keyword()

    # Метаданные
    language = Keyword()

    # Статистика
    average_rating = Float()
    rating_count = Integer()
    views = Integer()

    # Категории
    categories = Nested(CategoryDoc)

    class Index:
        name = "books"

    class Django:
        model = Book

        def prepare_epub_file(self, obj):
            return (
                obj.epub_file.url
                if obj.epub_file and hasattr(obj.epub_file, "url")
                else None
            )

        def prepare_cover_image(self, obj):
            return (
                obj.cover_image.url
                if obj.cover_image and hasattr(obj.cover_image, "url")
                else None
            )

        def prepare_average_rating(self, obj):
            return round(float(obj.average_rating), 2)

        def prepare_categories(self, obj):
            return [
                {"id": cat.id, "name": cat.name, "parent": cat.parent_id}
                for cat in obj.categories.all()
            ]


# ======================= ДИССЕРТАЦИИ =======================
class DissertationDoc(Document):
    title = Text(analyzer="standard", fields={"keyword": Keyword()})
    content = Text(analyzer="standard")
    author = Text(fields={"keyword": Keyword()})
    author_workplace = Text()

    # Метаданные
    language = Keyword()
    publication_date = Date()

    # Статистика
    average_rating = Float()
    rating_count = Integer()
    views = Integer()

    # Категории
    categories = Nested(CategoryDoc)

    class Index:
        name = "dissertations"

    class Django:
        model = Dissertation

        def prepare_average_rating(self, obj):
            return round(float(obj.average_rating), 2)

        def prepare_categories(self, obj):
            return [
                {"id": cat.id, "name": cat.name, "parent": cat.parent_id}
                for cat in obj.categories.all()
            ]
