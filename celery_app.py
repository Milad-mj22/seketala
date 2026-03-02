# from celery import Celery

# app = Celery(
#     'tasks',
#     broker='redis://localhost:6379/0',  # آدرس Redis
#     backend='redis://localhost:6379/0'  # برای ذخیره نتیجه تسک
# )

# @app.task
# def add(x, y):
#     return x + y


from celery import Celery

app = Celery('myapp', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def add(x, y):
    return x + y
