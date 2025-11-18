# Generated migration for dashboards app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_id', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('widget_type', models.CharField(choices=[('statistics', 'Statistics Card'), ('chart', 'Chart/Graph'), ('table', 'Data Table'), ('list', 'List View'), ('calendar', 'Calendar'), ('notifications', 'Notifications'), ('quick_actions', 'Quick Actions'), ('custom', 'Custom Widget')], max_length=20)),
                ('available_for_roles', models.JSONField(default=list, help_text='List of roles that can see this widget')),
                ('default_size', models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium', max_length=20)),
                ('default_position', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Dashboard Widget',
                'verbose_name_plural': 'Dashboard Widgets',
                'ordering': ['default_position'],
            },
        ),
        migrations.CreateModel(
            name='DashboardPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_layout', models.JSONField(default=dict, help_text='Widget positions and sizes')),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light', max_length=20)),
                ('visible_widgets', models.JSONField(default=list, help_text='List of visible widget IDs')),
                ('auto_refresh', models.BooleanField(default=True)),
                ('refresh_interval', models.IntegerField(default=60, help_text='Auto-refresh interval in seconds')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dashboard Preference',
                'verbose_name_plural': 'Dashboard Preferences',
            },
        ),
    ]
