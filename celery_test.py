from celery_app import add




if __name__ == '__main__':
    result = add.delay(4, 6)
    #print("Waiting for result...")
    #print("Result:", result.get(timeout=10))
