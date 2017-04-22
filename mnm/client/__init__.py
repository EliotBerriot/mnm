import mastodon


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
