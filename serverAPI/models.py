from django.db import models
from serverAPI.constants import Constant
# Create your models here.


class CheckPoint(models.Model):
    chain_id = models.CharField(max_length=255, default="")
    owner = models.CharField(max_length=255)
    round = models.PositiveIntegerField()
    result = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'checkpoint'
        unique_together = ("chain_id","owner", "round")

class NodeInfo(models.Model):
    reg_time = models.DateTimeField()
    address = models.CharField(max_length=255, primary_key=True)
    private_key = models.CharField(max_length=255)
    loc_x = models.IntegerField()
    loc_y = models.IntegerField()
    chain_id = models.CharField(max_length=255)
    host = models.CharField(max_length=255, default="127.0.0.1:8000")
    last_update = models.IntegerField(default=0)
    credit = models.FloatField(default=Constant.Credit0)
    class Meta:
        db_table = 'node_info'


class CarInfo(models.Model):
    address = models.CharField(max_length=255, primary_key=True)

    class Meta:
        db_table = 'car_info'


class SelfInfo(models.Model):
    address = models.CharField(max_length=255, primary_key=True)
    private_key = models.CharField(max_length=255)

    current_round = models.PositiveIntegerField()
    bc_port = models.CharField(max_length=5)

    class Meta:
        db_table = 'self_info'

class AreaInfo(models.Model):
    chainID = models.CharField(max_length=255, primary_key=True)
    bc_endpoint = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'area_info'