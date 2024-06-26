# Generated by Django 3.2 on 2024-04-29 05:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flota', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ambulancia',
            name='frontal',
            field=models.ImageField(blank=True, upload_to='media/'),
        ),
        migrations.AlterField(
            model_name='ambulancia',
            name='lateral',
            field=models.ImageField(blank=True, upload_to='media/'),
        ),
        migrations.AlterField(
            model_name='registros',
            name='firma',
            field=models.ImageField(blank=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='registros',
            name='foto',
            field=models.ImageField(blank=True, upload_to='media'),
        ),
        migrations.CreateModel(
            name='Correctivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hora_registro', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_registro', models.DateField(default=django.utils.timezone.now)),
                ('mantenimiento_sistema', models.TextField()),
                ('clase_sistema', models.TextField()),
                ('detalle_mantenimiento', models.TextField()),
                ('repuesto', models.CharField(max_length=30)),
                ('lugar', models.TextField()),
                ('costo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('kilometraje', models.IntegerField()),
                ('numero_factura', models.IntegerField()),
                ('foto_factura', models.ImageField(blank=True, upload_to='media')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
                ('movil', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='flota.ambulancia')),
            ],
        ),
    ]
