from elasticsearch_dsl import Document, Text, Keyword, Date, Integer, Nested, InnerDoc
from elasticsearch_dsl.connections import connections
from .models import Article, Book, Dissertation

connections.create_connection(hosts=["http://127.0.0.1:9200"], timeout=30)


class CategoryDoc(InnerDoc):
    id = Integer()
    name = Text()
    parent = Integer()  


# ======================= СТАТЬИ =======================
class ArticleDoc(Document):
    title = Text(analyzer="standard")
    content = Text(analyzer="standard")
    author = Text()
    author_workplace = Text()
    source_name = Text()
    source_url = Keyword()
    newspaper_or_journal = Text()
    type = Keyword()  
    image = Keyword()  

    language = Keyword()
    publication_date = Date()
    rating = Integer()
    views = Integer()

    categories = Nested(CategoryDoc)

    class Index:
        name = "articles"


class Django:
    model = Article

    def prepare_image(self, obj):
        return obj.image.url if obj.image and obj.image.name else None

    def prepare_categories(self, obj):
        return [
            {"id": cat.id, "name": cat.name, "parent": cat.parent_id}
            for cat in obj.categories.all()
        ]


# ======================= КНИГИ =======================
class BookDoc(Document):
    title = Text(analyzer="standard")
    content = Text(analyzer="standard")
    author = Text()
    epub_file = Keyword()
    cover_image = Keyword()

    language = Keyword()
    rating = Integer()
    views = Integer()

    categories = Nested(CategoryDoc)

    class Index:
        name = "books"

    class Django:
        model = Book

        def prepare_epub_file(self, obj):
            return obj.epub_file.url if obj.epub_file and obj.epub_file.name else None

        def prepare_cover_image(self, obj):
            return (
                obj.cover_image.url
                if obj.cover_image and obj.cover_image.name
                else None
            )

        def prepare_categories(self, obj):
            return [
                {"id": cat.id, "name": cat.name, "parent": cat.parent_id}
                for cat in obj.categories.all()
            ]


# ======================= ДИССЕРТАЦИИ =======================
class DissertationDoc(Document):
    title = Text(analyzer="standard")
    content = Text(analyzer="standard")
    author = Text()
    author_workplace = Text()

    language = Keyword()
    publication_date = Date()
    rating = Integer()
    views = Integer()

    categories = Nested(CategoryDoc)

    class Index:
        name = "dissertations"

    class Django:
        model = Dissertation

        def prepare_categories(self, obj):
            return [
                {"id": cat.id, "name": cat.name, "parent": cat.parent_id}
                for cat in obj.categories.all()
            ]
