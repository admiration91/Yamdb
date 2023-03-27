from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from reviews.models import User


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'role', 'bio', 'first_name', 'last_name'
        )


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
    list_display = (
        'email', 'username', 'role', 'bio', 'first_name', 'last_name'
    )
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
