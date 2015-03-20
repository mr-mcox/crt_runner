from unittest.mock import patch, MagicMock
from ..messenger import Messenger
import pytest
from ..config import Config

@pytest.fixture
def config():

    with patch('crt_runner.config.Config') as mock:
        instance = mock.return_value
        instance.mandrill_api_key = 'API_KEY'
    return instance


@pytest.fixture
def mocked_client(config):
    mandrill_client_mock = MagicMock()
    m_send_mock = MagicMock()
    with patch('mandrill.Mandrill', return_value=mandrill_client_mock):
        m = Messenger(config=config)
        mandrill_client_mock.messages.send = m_send_mock
    return {'client': m, 'send_mock': m_send_mock}

def test_non_variable_parameters_of_message(mocked_client):
    client = mocked_client['client']
    client.send_email()
    send_mock = mocked_client['send_mock']
    assert send_mock.called
    mocked_message = send_mock.call_args[1]['message']
    assert mocked_message['important'] == False
    assert mocked_message['tags'] == ['password-resets']

def test_variable_parameters_of_message(mocked_client):
    client = mocked_client['client']
    client.send_email()
    send_mock = mocked_client['send_mock']

    message_parameters = [
        {'from_name': 'Matthew Cox',
         'from_email': 'matthew.cox@teachforamerica.org',
         'to_name': 'Nick Smrdel',
         'to_email': 'nicholas.smrdel@teachforamerica.org',
         'subject': 'Program Tracker Imploded',
         'body': 'Perhaps we should reconsider taking a picnic'},
        {'from_name': 'Olivia',
         'from_email': 'olivia@gmail.com',
         'to_name': 'Katniss',
         'to_email': 'katniss@gmail.com',
         'subject': "Let's raid the food bin!",
         'body': "I'm bored and haven't caught a mouse for hours"}
    ]

    for ps in message_parameters:
        client.send_email(from_name=ps['from_name'],
                          from_email=ps['from_email'],
                          to_name=ps['to_name'],
                          to_email=ps['to_email'],
                          subject=ps['subject'],
                          body=ps['body'],
                          )
        assert send_mock.called
        mocked_message = send_mock.call_args[1]['message']
        assert mocked_message['from_name'] == ps['from_name']
        assert mocked_message['from_email'] == ps['from_email']
        assert mocked_message['to_name'] == ps['to_name']
        assert mocked_message['to_email'] == ps['to_email']
        assert mocked_message['subject'] == ps['subject']
        assert mocked_message['text'] == ps['body']
        assert mocked_message['headers'] == {'Reply-To': ps['from_email']}
        assert mocked_message['to'] == [{'email': ps['to_email'],
                                         'name': ps['to_name'],
                                         'type':'to'
                                         }]

def test_client_uses_config_api_key(config):
    with patch('mandrill.Mandrill') as mandrill_mock:
        Messenger(config=config)
    mandrill_mock.assert_called_with(config.mandrill_api_key)
