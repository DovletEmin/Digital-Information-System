from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0013_add_pendingview"),
    ]

    operations = [
        migrations.CreateModel(
            name="ViewRecord",
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
                    "session_key",
                    models.CharField(
                        max_length=40, null=True, blank=True, db_index=True
                    ),
                ),
                ("content_type", models.CharField(max_length=20)),
                ("content_id", models.PositiveIntegerField()),
                ("last_seen", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        to="auth.user",
                    ),
                ),
            ],
            options={},
        ),
        migrations.AddIndex(
            model_name="viewrecord",
            index=models.Index(
                fields=["session_key", "content_type", "content_id"],
                name="viewrec_sess_ct_cid_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="viewrecord",
            index=models.Index(
                fields=["user", "content_type", "content_id"],
                name="viewrec_user_ct_cid_idx",
            ),
        ),
    ]
