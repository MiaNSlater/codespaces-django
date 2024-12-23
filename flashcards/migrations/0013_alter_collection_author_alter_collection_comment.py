# Generated by Django 5.0.9 on 2024-11-19 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flashcards", "0012_collection_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collection",
            name="author",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collection",
                to="flashcards.user",
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="comment",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collection",
                to="flashcards.comment",
            ),
        ),
    ]
