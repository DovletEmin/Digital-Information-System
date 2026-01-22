from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0010_alter_article_categories_alter_book_categories_and_more"),
    ]

    operations = [
        # Article indexes
        migrations.AddIndex(
            model_name="article",
            index=models.Index(fields=["views"], name="article_views_idx"),
        ),
        migrations.AddIndex(
            model_name="article",
            index=models.Index(fields=["language"], name="article_language_idx"),
        ),
        migrations.AddIndex(
            model_name="article",
            index=models.Index(fields=["publication_date"], name="article_pubdate_idx"),
        ),
        # Book indexes
        migrations.AddIndex(
            model_name="book",
            index=models.Index(fields=["views"], name="book_views_idx"),
        ),
        migrations.AddIndex(
            model_name="book",
            index=models.Index(fields=["language"], name="book_language_idx"),
        ),
        # Dissertation indexes
        migrations.AddIndex(
            model_name="dissertation",
            index=models.Index(fields=["views"], name="dissertation_views_idx"),
        ),
        migrations.AddIndex(
            model_name="dissertation",
            index=models.Index(fields=["language"], name="dissertation_language_idx"),
        ),
        migrations.AddIndex(
            model_name="dissertation",
            index=models.Index(
                fields=["publication_date"], name="dissertation_pubdate_idx"
            ),
        ),
    ]
