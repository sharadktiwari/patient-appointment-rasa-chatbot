import datetime
import numpy

def dmytoymd(user_date):
    try:
        db_date = (datetime.datetime.strptime(user_date, '%d/%m/%Y')).strftime('%Y/%m/%d')
        return db_date
    except Exception as e:
        print(e)
        return False

def ymdtodmy(db_date):
    try:
        user_date = (datetime.datetime.strptime(db_date, '%Y/%m/%d')).strftime('%d/%m/%Y')
        return user_date
    except Exception as e:
        print(e)
        return False
    
def generate_id():
    try:
        return datetime.datetime.now().strftime("%y%m%d%H%M%S")+f"{str(numpy.random.randint(1,999)).zfill(3)}"
    except Exception as e:
        print(e)
        return str(numpy.random.randint(1,999999999999999)).zfill(15)

