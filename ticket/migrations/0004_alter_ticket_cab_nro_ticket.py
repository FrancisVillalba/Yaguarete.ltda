# Generated by Django 3.2 on 2023-07-25 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0003_ticket_cab_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket_cab',
            name='nro_ticket',
            field=models.IntegerField(default=0, unique=True),
        ),
    ]
