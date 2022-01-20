from peewee import *
database = MySQLDatabase('db_cash_gift', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '42.192.51.96', 'user': 'root', 'password': 'root'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class CCashGift(BaseModel):
    cg_id = AutoField()
    cg_money = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    cg_name = CharField(null=True)
    cg_remark = CharField(null=True)
    cg_type = IntegerField(null=True)

    class Meta:
        table_name = 'c_cash_gift'

class CSystemAdmin(BaseModel):
    sa_id = AutoField()
    sa_login_ip = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    sa_login_time = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    sa_password = CharField(constraints=[SQL("DEFAULT ''")], null=True)
    sa_password_salt = CharField(constraints=[SQL("DEFAULT ''")], null=True)
    sa_status = IntegerField(constraints=[SQL("DEFAULT 1")], index=True, null=True)
    sa_username = CharField(constraints=[SQL("DEFAULT ''")], null=True, unique=True)

    class Meta:
        table_name = 'c_system_admin'

