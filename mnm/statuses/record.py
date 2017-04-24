import mastodon
from mnm.statuses import tasks


class StatusListener(mastodon.StreamListener):
        def on_update(self, status):
            tasks.send_to_influxdb.delay(status)


def record_public_status(client):
    client.public_stream(StatusListener())
