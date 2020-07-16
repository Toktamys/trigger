from django.db import models


class Customer(models.Model):
    phone = models.TextField(null=False, blank=False)
    email = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.phone
