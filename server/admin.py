from django.contrib import admin
import models as server_models

admin.site.register(server_models.Driver)
admin.site.register(server_models.FleetPartner)
