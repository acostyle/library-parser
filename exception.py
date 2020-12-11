def raise_redirect_case(response):
    if response.status_code == 302 or response.status_code == 301:
        raise requests.HTTPError
