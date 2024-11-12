FROM python:3.11-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN apt-get update && apt-get install -y cron

RUN mkdir -p /app/notifier/log
RUN touch /app/notifier/log/cron.log

# 0 6-20 * * *
RUN echo "* * * * *  /usr/local/bin/python /app/notifier/notifier.py >> /app/notifier/log/cron.log 2>&1" > /etc/cron.d/notifier-cron-job
RUN chmod 0644 /etc/cron.d/notifier-cron-job
RUN crontab /etc/cron.d/notifier-cron-job

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]