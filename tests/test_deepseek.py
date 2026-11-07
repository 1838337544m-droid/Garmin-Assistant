import asyncio
import json

import httpx
import pytest

from garmin_assistant.config import load_settings, save_settings
from garmin_assistant.deepseek import ask, tool_definitions, tool_output
from garmin_assistant.menu import MenuStore


@pytest.mark.parametrize('model', ['deepseek-flash', 'deepseek-v4-pro'])
def test_deepseek_round_trip_uses_real_mcp_menu_and_blocks_unknown_tools(monkeypatch, model):
    save_settings(load_settings(), language='en')
    requests = []

    def reply(request):
        assert request.url == 'https://api.deepseek.com/chat/completions'
        assert request.headers['Authorization'] == 'Bearer test-deepseek-key'
        body = json.loads(request.content)
        assert 'test-deepseek-key' not in request.content.decode()
        requests.append(body)
        if len(requests) == 1:
            calls = [
                {'id': 'menu', 'type': 'function', 'function': {'name': 'garmin_function_menu', 'arguments': '{}'}},
                {'id': 'blocked', 'type': 'function', 'function': {'name': 'garmin_remove_custom_function', 'arguments': '{"custom_id":100}'}},
            ]
            message = {'content': None, 'tool_calls': calls}
        else:
            menu, blocked = body['messages'][-2:]
            assert menu['tool_call_id'] == 'menu'
            assert [item['id'] for item in json.loads(menu['content'])['function_menu']] == list(range(1, 5))
            assert 'unavailable' in blocked['content']
            message = {'content': 'Here is the Garmin menu.'}
        return httpx.Response(200, json={'choices': [{'message': message}]})

    async def run():
        from garmin_assistant import server

        store = MenuStore(load_settings().data_dir / 'menu-preferences.json')
        store.add('Private workflow', 'Private instructions kept off the wire until selected')
        monkeypatch.setattr(server, 'menu_store', store)
        mcp = server.mcp
        tools = await tool_definitions(mcp)
        assert 'garmin_remove_custom_function' not in {tool['function']['name'] for tool in tools}
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply), headers={'Authorization': 'Bearer test-deepseek-key'}) as client:
            return await ask(client, mcp, model, tools, [{'role': 'user', 'content': 'Show the menu'}])

    assert asyncio.run(run()) == 'Here is the Garmin menu.'
    assert all(body['model'] == model for body in requests)
    assert all(body['thinking'] == {'type': 'disabled'} for body in requests)


def test_declining_data_transfer_skips_key_prompt_and_connection(monkeypatch):
    from garmin_assistant import deepseek

    settings = save_settings(load_settings(), language='zh')
    monkeypatch.setattr(deepseek.sys.stdin, 'isatty', lambda: True)
    monkeypatch.setattr('builtins.input', lambda _: 'no')
    monkeypatch.delenv('DEEPSEEK_API_KEY', raising=False)

    def unexpected(*args, **kwargs):
        pytest.fail('Declining should skip authentication and chat')

    monkeypatch.setattr(deepseek.getpass, 'getpass', unexpected)
    monkeypatch.setattr(deepseek, 'chat', unexpected)
    assert deepseek.run(settings, model='deepseek-flash') == 0


def test_monitoring_sync_metadata_does_not_send_unselected_custom_workflows():
    class MonitoringServer:
        async def call_tool(self, name, arguments):
            return {'sync': {'fresh': True, 'function_menu': [{'id': 1, 'command': 'Sync'},
                     {'id': 100, 'command': 'Private', 'description': 'Private workflow details'}]}}

    result = asyncio.run(tool_output(MonitoringServer(), {'name': 'garmin_training_status', 'arguments': '{}'}))
    assert json.loads(result)['sync']['function_menu'] == [{'id': 1, 'command': 'Sync'}]
    assert 'Private' not in result
