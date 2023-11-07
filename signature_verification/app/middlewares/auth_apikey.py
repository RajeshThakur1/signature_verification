import os
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader

from starlette.status import HTTP_403_FORBIDDEN

if "API_KEY" in os.environ:
    API_KEY = os.environ["API_KEY"]

API_KEY_NAME = "api_key"


api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):
    """Method for validating the api key
    author: Rajesh
    Args:
        api_key_query (str, optional): [description]. Defaults to Security(api_key_query).
        api_key_header (str, optional): [description]. Defaults to Security(api_key_header).
        api_key_cookie (str, optional): [description]. Defaults to Security(api_key_cookie).
    Raises:
        HTTPException: [description]
    Returns:
        [type]: [description]
    """
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate the credentials"
        )
