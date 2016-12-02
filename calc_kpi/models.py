from django.db import models

# Create your models here.
class ProposedContractingData(models.Model):
    proposed_price = models.DecimalField(decimal_places=4,max_digits=100)
    timestamp = models.DateTimeField() #In UTC time

    def __str__(self):
        return "uploadded at " + str(self.timestamp) + " with price " + self.proposed_price
