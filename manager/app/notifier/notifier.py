import datetime
print("Notifier Running")

with open('/app/notifier/test.txt', 'w') as f:
    f.write(datetime.datetime.now().strftime("%Y-%m-%d"))