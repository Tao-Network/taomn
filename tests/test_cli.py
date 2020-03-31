import pytest

import docker

import taomn as package

client = docker.from_env()


@pytest.fixture
def runner():
    from click.testing import CliRunner
    runner = CliRunner()
    return runner


@pytest.fixture
def taomn():
    from taomn import taomn
    from taomn.environments import environments
    from taomn import configuration
    environments['devnet'] = {
        'tao': {
            'BOOTNODES': (
                'test'
            ),
            'NETSTATS_HOST': 'test.com',
            'NETSTATS_PORT': '443',
            'NETWORK_ID': '90',
            'WS_SECRET': (
                'test'
            )
        },
        'metrics': {
            'METRICS_ENDPOINT': 'https://test.com'
        }
    }
    environments['testnet'] = environments['devnet']
    configuration.resources.init('tao', 'tao_tests')
    return taomn


def _clean(taomn):
    from taomn import configuration
    try:
        client.containers.get('test1_tao').remove(force=True)
    except Exception:
        pass
    try:
        client.containers.get('test1_metrics').remove(force=True)
    except Exception:
        pass
    try:
        client.volumes.get('test1_chaindata').remove(force=True)
    except Exception:
        pass
    try:
        client.networks.get('test1_taomn').remove()
    except Exception:
        pass
    configuration.resources.init('tao', 'tao_tests')
    configuration.resources.user.delete('id')
    configuration.resources.user.delete('name')
    configuration.resources.user.delete('net')


def test_version(runner, taomn):
    version = '0.5.1'
    result = runner.invoke(taomn.main, ['--version'])
    assert result.output[-6:-1] == version
    assert package.__version__ == version


def test_error_docker(runner, taomn):
    result = runner.invoke(taomn.main, ['--docker', 'unix://test', 'docs'])
    assert '! error: could not access the docker daemon\nNone\n'
    assert result.exit_code == 0


def test_command(runner, taomn):
    result = runner.invoke(taomn.main)
    assert result.exit_code == 0


def test_command_docs(runner, taomn):
    result = runner.invoke(taomn.main, ['docs'])
    msg = 'Documentation on running a masternode:'
    link = 'https://docs.tao.network/masternode/taomn/\n'
    assert result.output == "{} {}".format(msg, link)
    assert result.exit_code == 0


def test_command_start_init_devnet(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(taomn)


def test_command_start_init_testnet(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'testnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(taomn)


def test_command_start_init_mainnet(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'mainnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(taomn)


def test_command_start_init_invalid_name(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'tes', '--net', 'devnet', '--pkey', '1234'])
    lines = result.output.splitlines()
    assert 'error' in lines[1]
    assert '! error: --name is not valid' in lines
    _clean(taomn)


def test_command_start_init_no_pkey(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net', 'devnet'])
    lines = result.output.splitlines()
    assert ('! error: --pkey is required when starting a new '
            'masternode') in lines
    _clean(taomn)


def test_command_start_init_invalid_pkey_len(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net', 'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890'])
    lines = result.output.splitlines()
    assert '! error: --pkey is not valid' in lines
    _clean(taomn)


def test_command_start_init_no_net(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'])
    lines = result.output.splitlines()
    assert '! error: --net is required when starting a new masternode' in lines
    _clean(taomn)


def test_command_start_init_no_name(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'])
    lines = result.output.splitlines()
    assert ('! error: --name is required when starting a new '
            'masternode') in lines
    _clean(taomn)


def test_command_start(runner, taomn):
    runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(taomn.main, ['start'])
    lines = result.output.splitlines()
    assert 'Starting masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(taomn)


def test_command_start_ignore(runner, taomn):
    result = runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(taomn.main, ['start', '--name', 'test'])
    lines = result.output.splitlines()
    assert '! warning: masternode test1 is already configured' in lines
    _clean(taomn)


def test_command_stop(runner, taomn):
    runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(taomn.main, ['stop'])
    lines = result.output.splitlines()
    assert 'Stopping masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(taomn)


def test_command_status(runner, taomn):
    runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(taomn.main, ['status'])
    lines = result.output.splitlines()
    assert 'Masternode test1 status:' in lines
    _clean(taomn)


def test_command_inspect(runner, taomn):
    runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(taomn.main, ['inspect'])
    lines = result.output.splitlines()
    assert 'Masternode test1 details:' in lines
    _clean(taomn)


def test_command_update(runner, taomn):
    runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(taomn.main, ['update'])
    lines = result.output.splitlines()
    assert 'Updating masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(taomn)


def test_command_remove(runner, taomn):
    runner.invoke(taomn.main, [
        'start', '--name', 'test1', '--net',
        'devnet', '--pkey',
        '0123456789012345678901234567890123456789012345678901234567890123'
    ])
    result = runner.invoke(taomn.main, ['remove', '--confirm'])
    lines = result.output.splitlines()
    assert 'Removing masternode test1:' in lines
    for line in lines:
        assert '✗' not in line
    _clean(taomn)
