from streamlit.testing.v1 import AppTest
from storage import ROOT


def button(app, label):
    return next(b for b in app.button if b.label == label)


def test_editor_switch_and_logs(tmp_path, monkeypatch):
    import storage
    events = []
    monkeypatch.setattr(storage, 'append_log', lambda e: events.append(e))
    monkeypatch.setenv('TRACETUTOR_MODE', 'demo')
    app = AppTest.from_file(ROOT / 'app.py', default_timeout=30).run()
    assert not app.exception
    assert button(app, 'Get Hint').disabled
    button(app, 'Run Tests').click().run()
    button(app, 'Get Hint').click().run()
    assert len(events) == 1
    app.run()
    assert len(events) == 1
    app.text_area[0].set_value('def sum_numbers(numbers):\n    return 123').run()
    assert button(app, 'Get Hint').disabled
    assert len(app.warning) > 0
    app.selectbox[1].select(1).run()
    assert 'count_even' in app.text_area[0].value
    assert not app.session_state['result']
    button(app, 'Run Tests').click().run()
    button(app, 'Reset Exercise').click().run()
    assert not app.session_state['result'] and not app.exception
    from storage import load_exercises
    app.text_area[0].set_value(load_exercises()[1]['reference']).run()
    button(app, 'Run Tests').click().run()
    assert len(app.success) == 1 and button(app, 'Get Hint').disabled
