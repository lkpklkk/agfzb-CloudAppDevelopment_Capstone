from django.contrib import admin
from .models import CarModel, CarMake


# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 1  # Number of extra forms to display


# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "make",
        "dealerId",
        "carType",
    ]


# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = [
        "name",
        "description",
    ]


# Register models here
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(CarMake, CarMakeAdmin)
