from unittest.mock import patch
from ..box_sync import BoxSync
import pytest
import os


@pytest.fixture
def mock_config():
    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.box_access_token_file = 'at.txt'
        instance.box_refresh_token_file = 'rt.txt'
    return instance


def test_store_tokens(mock_config):
    with patch.object(BoxSync,'authenticate_client'):
        bs = BoxSync(mock_config)
    bs.store_tokens('access', 'refresh')
    assert open(mock_config.box_access_token_file).readline() == 'access'
    assert open(mock_config.box_refresh_token_file).readline() == 'refresh'
    os.remove(mock_config.box_access_token_file)
    os.remove(mock_config.box_refresh_token_file)
