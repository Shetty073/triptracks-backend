# Generated by Django 5.0.6 on 2024-09-28 21:52

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vehicle_service', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TripVehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('fuel_cost_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('calculated_fuel_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('final_fuel_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('final_fuel_adjustments', models.CharField(blank=True, max_length=250, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('driver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trips_as_driver', to=settings.AUTH_USER_MODEL)),
                ('passengers', models.ManyToManyField(related_name='trips_as_passenger', to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tripvehicles', to='vehicle_service.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('origin_location', models.CharField(max_length=100)),
                ('origin_lat', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)])),
                ('origin_long', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(-100.0), django.core.validators.MaxValueValidator(100.0)])),
                ('destination_location', models.CharField(max_length=100)),
                ('destination_lat', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)])),
                ('destination_long', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(-100.0), django.core.validators.MaxValueValidator(100.0)])),
                ('distance', models.DecimalField(decimal_places=2, max_digits=7)),
                ('distance_unit', models.CharField(choices=[('km', 'Km'), ('mile', 'Mile')], max_length=12)),
                ('average_distance_per_day', models.DecimalField(decimal_places=2, max_digits=7)),
                ('accomodation_days', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('accomodation_cost_per_day', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('calculated_accomodation_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('final_accomodation_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('final_accomodation_adjustments', models.CharField(blank=True, max_length=250, null=True)),
                ('food_cost_per_day', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('calculated_food_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('final_food_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('final_food_adjustments', models.CharField(blank=True, max_length=250, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organizer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trips_organized', to=settings.AUTH_USER_MODEL)),
                ('travellers', models.ManyToManyField(related_name='trips_participated', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trips_updated', to=settings.AUTH_USER_MODEL)),
                ('vehicles', models.ManyToManyField(related_name='trips', to='trip_service.tripvehicle')),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('cost_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('unit_type', models.CharField(choices=[('item', 'Item'), ('litre', 'L'), ('kg', 'Kg'), ('day', 'Day'), ('night', 'Night')], max_length=12)),
                ('no_of_units', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='foods_created', to=settings.AUTH_USER_MODEL)),
                ('paid_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='foods_paid', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='foods_updated', to=settings.AUTH_USER_MODEL)),
                ('trip', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='foods', to='trip_service.trip')),
            ],
            options={
                'indexes': [models.Index(fields=['trip'], name='trip_servic_trip_id_0b74c9_idx'), models.Index(fields=['paid_by'], name='trip_servic_paid_by_f9353b_idx'), models.Index(fields=['created_by'], name='trip_servic_created_a2e412_idx'), models.Index(fields=['updated_by'], name='trip_servic_updated_72938d_idx'), models.Index(fields=['created_at'], name='trip_servic_created_823e58_idx'), models.Index(fields=['updated_at'], name='trip_servic_updated_9a8698_idx')],
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('cost_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('unit_type', models.CharField(choices=[('item', 'Item'), ('litre', 'L'), ('kg', 'Kg'), ('day', 'Day'), ('night', 'Night')], max_length=12)),
                ('no_of_units', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses_created', to=settings.AUTH_USER_MODEL)),
                ('paid_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses_paid', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses_updated', to=settings.AUTH_USER_MODEL)),
                ('trip', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='trip_service.trip')),
            ],
            options={
                'indexes': [models.Index(fields=['trip'], name='trip_servic_trip_id_8c492c_idx'), models.Index(fields=['paid_by'], name='trip_servic_paid_by_ea4819_idx'), models.Index(fields=['created_by'], name='trip_servic_created_6bad19_idx'), models.Index(fields=['updated_by'], name='trip_servic_updated_fc0a12_idx'), models.Index(fields=['created_at'], name='trip_servic_created_363c72_idx'), models.Index(fields=['updated_at'], name='trip_servic_updated_a7179d_idx')],
            },
        ),
        migrations.CreateModel(
            name='Accommodation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('cost_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('unit_type', models.CharField(choices=[('item', 'Item'), ('litre', 'L'), ('kg', 'Kg'), ('day', 'Day'), ('night', 'Night')], max_length=12)),
                ('no_of_units', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accommodations_created', to=settings.AUTH_USER_MODEL)),
                ('paid_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accommodations_paid', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accommodations_updated', to=settings.AUTH_USER_MODEL)),
                ('trip', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accommodations', to='trip_service.trip')),
            ],
            options={
                'indexes': [models.Index(fields=['trip'], name='trip_servic_trip_id_feb2a4_idx'), models.Index(fields=['paid_by'], name='trip_servic_paid_by_37f7ab_idx'), models.Index(fields=['created_by'], name='trip_servic_created_a37a91_idx'), models.Index(fields=['updated_by'], name='trip_servic_updated_2635c3_idx'), models.Index(fields=['created_at'], name='trip_servic_created_817592_idx'), models.Index(fields=['updated_at'], name='trip_servic_updated_62e29a_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='tripvehicle',
            index=models.Index(fields=['vehicle'], name='trip_servic_vehicle_1d92f8_idx'),
        ),
        migrations.AddIndex(
            model_name='tripvehicle',
            index=models.Index(fields=['driver'], name='trip_servic_driver__58c5cc_idx'),
        ),
        migrations.AddIndex(
            model_name='tripvehicle',
            index=models.Index(fields=['created_at'], name='trip_servic_created_5cfce9_idx'),
        ),
        migrations.AddIndex(
            model_name='tripvehicle',
            index=models.Index(fields=['updated_at'], name='trip_servic_updated_b84afd_idx'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['origin_location'], name='trip_servic_origin__d35fdf_idx'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['destination_location'], name='trip_servic_destina_3eae32_idx'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['organizer'], name='trip_servic_organiz_01b053_idx'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['created_at'], name='trip_servic_created_865f12_idx'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['updated_at'], name='trip_servic_updated_3f8d7c_idx'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['distance'], name='trip_servic_distanc_1b1568_idx'),
        ),
        migrations.AddIndex(
            model_name='trip',
            index=models.Index(fields=['distance_unit'], name='trip_servic_distanc_767ee7_idx'),
        ),
    ]
