# blog/dynamic_preferences_registry.py

from dynamic_preferences.types import StringPreference, Section
from dynamic_preferences.registries import global_preferences_registry


instances_section = Section('instances')


@global_preferences_registry.register
class DetailDashboardUrl(StringPreference):
    section = instances_section
    name = 'detail_dashboard_url'
    default = 'https://dashboards.mnm.social/dashboard/db/instance-detail?var-instance={instance}'
