import pytest
from pytest_mock import mocker
from unittest.mock import Mock
import telebot
from telebot import types

import main


def test_get_text_message_start(mocker):
    telebot.TeleBot.send_message = Mock()
    message = Mock()
    message.text = '/start'
    message.from_user.id = 1
    main.get_text_messages(message)
    main.bot.send_message.assert_called_with(message.from_user.id, "Сыграем.")


def test_get_text_message_help(mocker):
    telebot.TeleBot.send_message = Mock()
    message = Mock()
    message.text = '/help'
    main.get_text_messages(message)
    main.bot.send_message.assert_called_with(message.from_user.id, "Type /start to start")
