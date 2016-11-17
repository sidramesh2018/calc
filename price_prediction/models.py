from django.db import models

class LaborCategoryLookUp(models.Model):
    labor_key = models.CharField(max_length=400)
    labor_value = models.CharField(max_length=400)
    start_date = models.DateField()
    
    def __str__(self):
        return self.labor_key + ":" + self.labor_value

