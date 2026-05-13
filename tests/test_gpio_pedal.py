"""
Tests for gpio-pedal.

RPi.GPIO and pynput are mocked so tests pass on any machine,
not just a Raspberry Pi.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# Stub out RPi.GPIO before any gpio_pedal imports
# ---------------------------------------------------------------------------

def _make_gpio_mock():
    gpio = MagicMock()
    gpio.BCM = 11
    gpio.IN = 1
    gpio.FALLING = 31
    gpio.PUD_UP = 22
    return gpio


gpio_mock = _make_gpio_mock()

# Inject fake RPi and RPi.GPIO modules so imports succeed everywhere
rpi_mod = types.ModuleType("RPi")
rpi_mod.GPIO = gpio_mock
sys.modules.setdefault("RPi", rpi_mod)
sys.modules.setdefault("RPi.GPIO", gpio_mock)

# Stub out pynput so we don't need a display
pynput_mock = types.ModuleType("pynput")
pynput_keyboard_mock = types.ModuleType("pynput.keyboard")

_FAKE_KEY_NAMES = ["space", "enter", "ctrl", "shift", "alt", "tab",
                   "backspace", "f1", "f2", "esc"]

class _FakeKey:
    # __members__ is the standard Enum API used by utils.py to list key names
    __members__ = {name: name for name in _FAKE_KEY_NAMES}
    space = "space"
    enter = "enter"
    ctrl = "ctrl"
    shift = "shift"
    alt = "alt"
    tab = "tab"
    backspace = "backspace"
    f1 = "f1"
    f2 = "f2"
    esc = "esc"

pynput_keyboard_mock.Key = _FakeKey
pynput_keyboard_mock.Controller = MagicMock
pynput_mock.keyboard = pynput_keyboard_mock

sys.modules.setdefault("pynput", pynput_mock)
sys.modules.setdefault("pynput.keyboard", pynput_keyboard_mock)


# ---------------------------------------------------------------------------
# Now safe to import gpio_pedal
# ---------------------------------------------------------------------------

from gpio_pedal.config import load_config, validate_config  # noqa: E402
from gpio_pedal.utils import (  # noqa: E402
    describe_config,
    is_valid_key,
    list_special_keys,
    validate_key,
)


# ---------------------------------------------------------------------------
# config.py tests
# ---------------------------------------------------------------------------

class TestValidateConfig:
    def test_valid_dict_int_keys(self):
        result = validate_config({17: "space", 22: "ctrl+c"})
        assert result == {17: "space", 22: "ctrl+c"}

    def test_valid_dict_string_keys(self):
        """JSON loads keys as strings; validate_config should coerce to int."""
        result = validate_config({"17": "space", "22": "m"})
        assert result == {17: "space", 22: "m"}

    def test_strips_whitespace_from_key(self):
        result = validate_config({17: "  space  "})
        assert result[17] == "space"

    def test_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            validate_config([17, "space"])

    def test_raises_on_invalid_pin(self):
        with pytest.raises(ValueError, match="Invalid GPIO pin"):
            validate_config({"abc": "space"})

    def test_raises_on_empty_key_string(self):
        with pytest.raises(ValueError, match="non-empty string"):
            validate_config({17: ""})

    def test_raises_on_empty_config(self):
        with pytest.raises(ValueError, match="at least one"):
            validate_config({})


class TestLoadConfig:
    def test_load_json(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text(json.dumps({"17": "space", "22": "ctrl+c"}))
        result = load_config(cfg)
        assert result == {17: "space", 22: "ctrl+c"}

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "missing.json")

    def test_unsupported_format(self, tmp_path):
        cfg = tmp_path / "config.csv"
        cfg.write_text("17,space")
        with pytest.raises(ValueError, match="Unsupported config"):
            load_config(cfg)

    def test_yaml_import_error(self, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text("17: space\n")
        # Temporarily remove yaml from sys.modules to simulate missing package
        original = sys.modules.pop("yaml", None)
        sys.modules["yaml"] = None  # type: ignore
        try:
            with pytest.raises((ImportError, TypeError)):
                load_config(cfg)
        finally:
            if original is not None:
                sys.modules["yaml"] = original
            else:
                sys.modules.pop("yaml", None)


# ---------------------------------------------------------------------------
# utils.py tests
# ---------------------------------------------------------------------------

class TestIsValidKey:
    def test_single_char(self):
        assert is_valid_key("a") is True
        assert is_valid_key("1") is True
        assert is_valid_key("!") is True

    def test_special_key(self):
        assert is_valid_key("space") is True
        assert is_valid_key("enter") is True

    def test_combination(self):
        assert is_valid_key("ctrl+c") is True

    def test_invalid_special(self):
        assert is_valid_key("superkey99") is False

    def test_empty_string(self):
        assert is_valid_key("") is False

    def test_non_string(self):
        assert is_valid_key(17) is False  # type: ignore


class TestValidateKey:
    def test_valid_passes(self):
        validate_key("space")  # should not raise

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid key"):
            validate_key("superkey99")


class TestDescribeConfig:
    def test_output_format(self):
        result = describe_config({17: "space", 22: "ctrl+c"})
        assert "17" in result
        assert "space" in result
        assert "22" in result

    def test_empty_config(self):
        result = describe_config({})
        assert "empty" in result.lower()


class TestListSpecialKeys:
    def test_returns_list_of_strings(self):
        keys = list_special_keys()
        assert isinstance(keys, list)
        assert all(isinstance(k, str) for k in keys)

    def test_contains_common_keys(self):
        keys = list_special_keys()
        assert "space" in keys
        assert "enter" in keys


# ---------------------------------------------------------------------------
# controller.py tests
# ---------------------------------------------------------------------------

class TestPedalController:
    """Tests for PedalController — GPIO and pynput are mocked."""

    def _make_controller(self, config=None, **kwargs):
        from gpio_pedal.controller import PedalController

        if config is None:
            config = {17: "space", 22: "ctrl+c"}
        mock_kbd = MagicMock()
        with patch("gpio_pedal.controller.Controller", return_value=mock_kbd):
            controller = PedalController(config, **kwargs)
        controller._mock_keyboard = mock_kbd
        return controller

    def test_gpio_setup_called_for_each_pin(self):
        gpio_mock.reset_mock()
        self._make_controller({17: "space", 22: "m"})
        pins_setup = [c.args[0] for c in gpio_mock.setup.call_args_list]
        assert 17 in pins_setup
        assert 22 in pins_setup

    def test_event_detect_registered(self):
        gpio_mock.reset_mock()
        self._make_controller({17: "space"})
        gpio_mock.add_event_detect.assert_called()

    def test_handle_press_triggers_keypress(self):
        controller = self._make_controller({17: "space"})
        with patch.object(controller, "_simulate_keypress") as mock_sim:
            controller._handle_press(17)
            mock_sim.assert_called_once_with("space")

    def test_handle_press_unknown_pin_does_nothing(self):
        controller = self._make_controller({17: "space"})
        with patch.object(controller, "_simulate_keypress") as mock_sim:
            controller._handle_press(99)
            mock_sim.assert_not_called()

    def test_simulate_single_key(self):
        controller = self._make_controller({17: "a"})
        kb = controller._mock_keyboard
        controller._simulate_keypress("a")
        kb.press.assert_called()
        kb.release.assert_called()

    def test_simulate_key_combination(self):
        controller = self._make_controller({17: "ctrl+c"})
        kb = controller._mock_keyboard
        controller._simulate_keypress("ctrl+c")
        kb.pressed.assert_called()

    def test_stop_exits_run_loop(self):
        """stop() should break out of run() promptly."""
        import threading
        controller = self._make_controller()

        def _stop_soon():
            import time
            time.sleep(0.15)
            controller.stop()

        t = threading.Thread(target=_stop_soon, daemon=True)
        t.start()
        controller.run()  # should return after stop()
        t.join(timeout=2)
        assert not t.is_alive()
