# Generated by Django 5.0.9 on 2024-11-19 12:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flashcards", "0010_remove_flashcardset_cards_flashcard_flashcardset"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="collection",
            name="set",
        ),
        migrations.AddField(
            model_name="collection",
            name="flashcardset",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collection",
                to="flashcards.flashcardset",
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collection",
                to="flashcards.user",
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="comment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collection",
                to="flashcards.comment",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="flashcardset",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="flashcards.flashcardset",
            ),
        ),
        migrations.AlterField(
            model_name="flashcard",
            name="flashcardset",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flashcard",
                to="flashcards.flashcardset",
            ),
        ),
        migrations.AlterField(
            model_name="flashcardset",
            name="author",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flashcard_set",
                to="flashcards.user",
            ),
        ),
    ]
