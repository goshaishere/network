from django.contrib import admin

from .models import (
    WorkBoard,
    WorkColumn,
    WorkContact,
    WorkCounterparty,
    WorkGroup,
    WorkGroupMembership,
    WorkTask,
)

admin.site.register(WorkGroup)
admin.site.register(WorkGroupMembership)
admin.site.register(WorkBoard)
admin.site.register(WorkColumn)
admin.site.register(WorkTask)
admin.site.register(WorkCounterparty)
admin.site.register(WorkContact)
