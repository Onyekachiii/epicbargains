# Generated by Django 4.2 on 2025-06-14 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0003_alter_profile_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user_Type',
            field=models.CharField(blank=True, choices=[('vendor', 'vendor'), ('customer', 'customer')], default=None, max_length=255, null=True),
        ),
    ]
