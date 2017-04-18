import mastodon

from mnm.statuses import tasks


class StatusListener(mastodon.StreamListener):
        def on_update(self, status):
            tasks.send_to_influxdb.delay(status)

# get your access token / secrets
# mastodon.Mastodon.create_app(
#      'mnm',
#      to_file='mnm.txt',
#      api_base_url='instanceurl',
# )

# m = mastodon.Mastodon(client_id='mnm.txt', api_base_url='instanceurl',)
# m.log_in(
#      'email@domain',
#      'password',
#      scopes=['read'],
#      to_file='mnm_user.txt',
#
# )
#
# m = mastodon.Mastodon(
#     client_id='mnm.txt',
#     access_token='mnm_user.txt',
#     api_base_url='instanceurl',
# )
#
# m.public_stream(StatusListener())


def create_app(url):
    mastodon.Mastodon.create_app(
         'mnm',
         to_file='mnm.txt',
         api_base_url=url,
    )


def get_client(
            client_id,
            client_secret,
            access_token,
            api_base_url,
        ):
    return mastodon.Mastodon(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        api_base_url=api_base_url,
    )


def record_public_status(client):
    client.public_stream(StatusListener())
