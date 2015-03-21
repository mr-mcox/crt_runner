from unittest.mock import patch, PropertyMock
from ..box_sync import BoxSync, SyncedFile
import pytest
import os
from datetime import datetime


@pytest.fixture
def mock_config():
    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.box_access_token_file = 'at.txt'
        instance.box_refresh_token_file = 'rt.txt'
    return instance


def test_store_tokens(mock_config):
    with patch.object(BoxSync, 'authenticate_client'):
        bs = BoxSync(mock_config)
    bs.store_tokens('access', 'refresh')
    assert open(mock_config.box_access_token_file).readline() == 'access'
    assert open(mock_config.box_refresh_token_file).readline() == 'refresh'
    os.remove(mock_config.box_access_token_file)
    os.remove(mock_config.box_refresh_token_file)


def test_file_modify_dates():
    modify_dates = {'file': {'box_modify_date': 1420092000.0,
                             'local_modify_date': 1420094000.0}}
    sf = SyncedFile('file', 'box_folder', 'parent_folder', modify_dates)
    assert sf.modify_dates == modify_dates['file']


def test_download_box_file_when_local_does_not_exist():
    sf = SyncedFile('file', 'box_folder', 'parent_folder')
    with patch.object(SyncedFile, '_local_file_exists',
                      new_callable=PropertyMock) as lfe, patch.object(SyncedFile, '_box_file_exists',
                                                                      new_callable=PropertyMock) as bfe, patch.object(SyncedFile,
                                                                                                                      '_download_box_file_to_local') as mock_download:
        lfe.return_value = False
        bfe.return_value = True
        sf.sync_files()
        assert mock_download.called


def test_upload_local_file_when_box_copy_does_not_exist():
    sf = SyncedFile('file', 'box_folder', 'parent_folder')
    # sf._local_file_exists = True
    # sf._box_file_exists = False
    with patch.object(SyncedFile, '_local_file_exists',
                      new_callable=PropertyMock) as lfe:
        with patch.object(SyncedFile, '_box_file_exists',
                          new_callable=PropertyMock) as bfe:
            lfe.return_value = True
            bfe.return_value = False
            with patch.object(SyncedFile,
                              '_upload_local_file_to_box_folder') as mock_upload:
                sf.sync_files()
        assert mock_upload.called


def test_download_box_file_when_box_more_recent():
    sf = SyncedFile('file', 'box_folder', 'parent_folder')
    # sf._local_file_exists = True
    # sf._box_file_exists = True
    # sf._box_file_more_recent = True
    with patch.object(SyncedFile, '_local_file_exists',
                      new_callable=PropertyMock) as lfe, patch.object(SyncedFile, '_box_file_exists',
                                                                      new_callable=PropertyMock) as bfe, patch.object(SyncedFile, '_box_file_more_recent',
                                                                                                                      new_callable=PropertyMock) as bfmr, patch.object(SyncedFile,
                                                                                                                                                                       '_download_box_file_to_local') as mock_download:
        lfe.return_value = True
        bfe.return_value = True
        bfmr.return_value = True
        sf.sync_files()
        assert mock_download.called


def test_update_box_file_when_local_more_recent():
    sf = SyncedFile('file', 'box_folder', 'parent_folder')
    # sf._local_file_exists = True
    # sf._box_file_exists = True
    # sf._local_file_more_recent = True
    with patch.object(SyncedFile, '_local_file_exists',
                      new_callable=PropertyMock) as lfe, patch.object(SyncedFile, '_box_file_exists',
                                                                      new_callable=PropertyMock) as bfe, patch.object(SyncedFile, '_local_file_more_recent',
                                                                                                                      new_callable=PropertyMock) as lfmr, patch.object(SyncedFile,
                                                                                                                                                                       '_replace_box_file_with_local') as mock_replace:
        lfe.return_value = True
        bfe.return_value = True
        lfmr.return_value = True
        sf.sync_files()
        assert mock_replace.called
