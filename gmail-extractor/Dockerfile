FROM python:3.11-slim

ARG MANAGER_ENDPOINT
ARG EMAIL_ADDRESS
ARG EMAIL_APP_PASSWORD

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


# CRON CONFIGS
RUN apt-get update && apt-get install -y cron

RUN mkdir -p /app/log
RUN touch /app/log/cron.log

# 0 */6 * * *
RUN touch /etc/cron.d/gmail-cron-job
RUN echo "0 3-23 * * * MANAGER_ENDPOINT=$MANAGER_ENDPOINT EMAIL_ADDRESS=$EMAIL_ADDRESS EMAIL_APP_PASSWORD=\"$EMAIL_APP_PASSWORD\" /usr/local/bin/python /app/main.py >> /app/log/cron.log 2>&1" >> /etc/cron.d/gmail-cron-job
RUN chmod 0644 /etc/cron.d/gmail-cron-job
RUN crontab /etc/cron.d/gmail-cron-job


WORKDIR /app

CMD ["/usr/local/bin/entrypoint.sh"]
