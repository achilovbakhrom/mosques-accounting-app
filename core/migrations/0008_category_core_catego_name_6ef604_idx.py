# Generated by Django 5.1.1 on 2024-09-29 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_category_percentage'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['name'], name='core_catego_name_6ef604_idx'),
        ),
    ]