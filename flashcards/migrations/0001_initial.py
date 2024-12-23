# Generated by Django 5.0.9 on 2024-11-08 22:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Comment",
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
                ("comment", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="Flashcard",
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
                ("question", models.CharField(max_length=100)),
                ("answer", models.CharField(max_length=100)),
                (
                    "difficulty",
                    models.CharField(
                        blank=True,
                        choices=[("E", "Easy"), ("M", "Medium"), ("H", "Hard")],
                        default=None,
                        max_length=1,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="User",
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
                ("username", models.CharField(max_length=100)),
                ("admin", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="FlashcardSet",
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
                ("name", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                (
                    "cards",
                    models.ManyToManyField(
                        related_name="sets", to="flashcards.flashcard"
                    ),
                ),
                (
                    "comments",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="flashcards.comment",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="comment",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="flashcards.user"
            ),
        ),
        migrations.CreateModel(
            name="Collection",
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
                    "comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="flashcards.comment",
                    ),
                ),
                (
                    "set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="flashcards.flashcardset",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="flashcards.user",
                    ),
                ),
            ],
        ),
    ]
