from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from telegram_business_bot.faq import answer_faq, order_status
from telegram_business_bot.leads import LeadStore, parse_lead_command
from telegram_business_bot.settings import Settings

logging.basicConfig(level=logging.INFO)
settings = Settings()
lead_store = LeadStore(settings.leads_csv_path)
dispatcher = Dispatcher()


@dispatcher.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        f"Welcome to {settings.business_name}. Use /lead, /faq, or /status to continue."
    )


@dispatcher.message(Command("lead"))
async def capture_lead(message: Message) -> None:
    try:
        lead = parse_lead_command(message.text or "")
    except ValueError as exc:
        await message.answer(str(exc))
        return
    lead_store.append(lead)
    await message.answer("Thanks. Your request was captured.")


@dispatcher.message(Command("faq"))
async def faq(message: Message) -> None:
    topic = (message.text or "").removeprefix("/faq").strip()
    await message.answer(answer_faq(topic))


@dispatcher.message(Command("status"))
async def status(message: Message) -> None:
    order_id = (message.text or "").removeprefix("/status").strip()
    await message.answer(order_status(order_id))


@dispatcher.message(Command("export_leads"), F.from_user.id.in_(settings.admin_ids))
async def export_leads(message: Message) -> None:
    summary = lead_store.summary()
    await message.answer(
        f"Lead rows available: {summary.rows}. "
        f"Latest lead: {summary.latest_created_at or 'none'}. "
        f"CSV path: {summary.path}"
    )


async def run() -> None:
    bot = Bot(token=settings.telegram_bot_token)
    await dispatcher.start_polling(bot)


def main() -> None:
    asyncio.run(run())
