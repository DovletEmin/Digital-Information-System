from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0016_alter_article_language_and_more"),
    ]

    operations = [
        # Ensure Book.views is indexed
        migrations.AlterField(
            model_name="book",
            name="views",
            field=models.IntegerField(default=0, db_index=True),
        ),
        # Ensure Dissertation.views is indexed (no-op if already indexed)
        migrations.AlterField(
            model_name="dissertation",
            name="views",
            field=models.IntegerField(default=0, db_index=True),
        ),
        # Composite index to speed up filters by language + publication_date
        migrations.AddIndex(
            model_name="article",
            index=models.Index(
                fields=["language", "publication_date"], name="article_lang_pubdate_idx"
            ),
        ),
        # Composite index for type + language filters
        migrations.AddIndex(
            model_name="article",
            index=models.Index(
                fields=["type", "language"], name="article_type_lang_idx"
            ),
        ),
        # Book: index language + views to help language-filtered ordering by views
        migrations.AddIndex(
            model_name="book",
            index=models.Index(
                fields=["language", "views"], name="book_lang_views_idx"
            ),
        ),
        # Dissertation: composite index language + publication_date
        migrations.AddIndex(
            model_name="dissertation",
            index=models.Index(
                fields=["language", "publication_date"],
                name="dissertation_lang_pubdate_idx",
            ),
        ),
    ]
