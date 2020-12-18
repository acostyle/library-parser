import requests


def raise_if_redirect(response):
    if response.status_code == 302 or response.status_code == 301:
        raise requests.HTTPError
        print('Error')
