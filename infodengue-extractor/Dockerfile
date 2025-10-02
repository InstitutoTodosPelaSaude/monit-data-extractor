FROM python:3.11-slim

ARG MANAGER_ENDPOINT

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


# CRON CONFIGS
RUN apt-get update && apt-get install -y cron

RUN mkdir -p /app/log
RUN touch /app/log/cron.log

# 0 9 * * *
RUN touch /etc/cron.d/infodengue-cron-job
RUN echo "0 9 * * * MANAGER_ENDPOINT=$MANAGER_ENDPOINT /usr/local/bin/python /app/main.py >> /app/log/cron.log 2>&1" >> /etc/cron.d/infodengue-cron-job
RUN chmod 0644 /etc/cron.d/infodengue-cron-job
RUN crontab /etc/cron.d/infodengue-cron-job


WORKDIR /app

CMD ["/usr/local/bin/entrypoint.sh"]