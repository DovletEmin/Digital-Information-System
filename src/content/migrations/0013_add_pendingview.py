from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0012_remove_article_article_views_idx_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PendingView",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_type",
                    models.CharField(
                        choices=[
                            ("article", "Article"),
                            ("book", "Book"),
                            ("dissertation", "Dissertation"),
                        ],
                        max_length=20,
                    ),
                ),
                ("content_id", models.PositiveIntegerField()),
                ("count", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("content_type", "content_id")},
            },
        ),
    ]
