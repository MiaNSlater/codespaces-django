# Generated by Django 5.0.9 on 2024-11-26 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flashcards", "0014_alter_flashcard_difficulty_alter_user_password"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(max_length=100),
        ),
    ]