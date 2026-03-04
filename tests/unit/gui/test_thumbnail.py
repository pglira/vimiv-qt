# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Tests for vimiv.gui.thumbnail."""

import pytest

from vimiv.qt.core import QSize, Qt
from vimiv.qt.widgets import QStyle
from vimiv.qt.gui import QIcon

from vimiv.config import styles
from vimiv.gui.thumbnail import ThumbnailDelegate, ThumbnailItem, ThumbnailView


@pytest.fixture()
def item(mocker):
    """Fixture to retrieve a vanilla ThumbnailItem."""
    ThumbnailItem._default_icon = None
    mocker.patch.object(ThumbnailItem, "create_default_icon", return_value=QIcon())
    yield ThumbnailItem


@pytest.fixture()
def default_style():
    """Fixture to ensure a loaded style for delegate tests."""
    old_style = styles._style
    styles._style = styles.create_default(save_to_file=False)
    yield
    styles._style = old_style


def test_create_default_pixmap_once(item):
    """Ensure the default thumbnail icon is only created once."""
    size_hint = QSize(128, 128)
    for index in range(5):
        item(None, index, size_hint=size_hint)
    item.create_default_icon.assert_called_once()


def test_marked_thumbnail_uses_marked_background(default_style):
    delegate = ThumbnailDelegate(None)
    item = type("Item", (), {"marked": True, "highlighted": False})()

    color = delegate._get_background_color(item, QStyle.StateFlag.State_None)

    assert color == delegate.marked_bg


def test_marked_background_has_priority_over_search_highlight(default_style):
    delegate = ThumbnailDelegate(None)
    item = type("Item", (), {"marked": True, "highlighted": True})()

    color = delegate._get_background_color(item, QStyle.StateFlag.State_None)

    assert color == delegate.marked_bg


def test_draw_marked_overlay_uses_visible_alpha_for_opaque_color(default_style, mocker):
    delegate = ThumbnailDelegate(None)
    painter = mocker.Mock()
    option = mocker.Mock()
    option.rect = mocker.Mock()
    option.rect.adjusted.return_value = option.rect

    delegate.marked_bg.setAlpha(255)
    delegate._draw_marked_overlay(painter, option)

    overlay_color = painter.setBrush.call_args_list[0][0][0]
    assert overlay_color.alpha() == 104
    assert painter.drawRect.call_count == 4


def test_mark_from_mouse_ctrl_toggles_single_path(mocker):
    view = ThumbnailView.__new__(ThumbnailView)
    view._paths = ["a", "b", "c"]
    view._mark_anchor_index = None
    view._suppress_center_on_scroll = False
    view._select_index = mocker.Mock()
    view.count = mocker.Mock(return_value=3)
    mark = mocker.patch("vimiv.gui.thumbnail.api.mark.mark")

    handled = ThumbnailView._mark_from_mouse(
        view, 1, Qt.KeyboardModifier.ControlModifier
    )

    assert handled
    view._select_index.assert_called_once_with(1)
    mark.assert_called_once_with(["b"], action=mocker.ANY)
    assert mark.call_args.kwargs["action"].value == "toggle"
    assert view._mark_anchor_index == 1
    assert not view._suppress_center_on_scroll


def test_mark_from_mouse_shift_marks_range(mocker):
    view = ThumbnailView.__new__(ThumbnailView)
    view._paths = ["a", "b", "c", "d", "e"]
    view._mark_anchor_index = 1
    view._suppress_center_on_scroll = False
    view._select_index = mocker.Mock()
    view.count = mocker.Mock(return_value=5)
    mark = mocker.patch("vimiv.gui.thumbnail.api.mark.mark")

    handled = ThumbnailView._mark_from_mouse(view, 4, Qt.KeyboardModifier.ShiftModifier)

    assert handled
    view._select_index.assert_called_once_with(4)
    mark.assert_called_once_with(["b", "c", "d", "e"], action=mocker.ANY)
    assert mark.call_args.kwargs["action"].value == "mark"
    assert view._mark_anchor_index == 4
    assert not view._suppress_center_on_scroll
