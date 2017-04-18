# import mastodon
#
#
# class StatusListener(mastodon.StreamListener):
#         def on_update(self, status):
#             print(status)
#
#
# # mastodon.Mastodon.create_app(
# #      'mnm',
# #      to_file='mnm.txt',
# #      api_base_url='https://mastodon.xyz',
# # )
#
# m = mastodon.Mastodon(client_id='mnm.txt', api_base_url='https://mastodon.xyz',)
# m.log_in(
#      'contact@eliotberriot.com',
#      'KatAlamNEt32?0h1z9D',
#      scopes=['read'],
#      to_file='mnm_user.txt',
#
# )
#
# m = mastodon.Mastodon(
#     client_id='mnm.txt',
#     access_token='mnm_user.txt',
#     api_base_url='https://mastodon.xyz',
# )
#
# m.public_stream(StatusListener())
