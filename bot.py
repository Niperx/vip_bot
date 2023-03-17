import logging
import config
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import modules.chat_rights as rights
from modules.commands_list import CMD_LIST
from handlers.common import register_handlers_common

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = []
    for cmd in CMD_LIST:
        commands.append(types.BotCommand(command=cmd[0], description=cmd[1]))
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    dp.filters_factory.bind(rights.IsAdmin)
    dp.filters_factory.bind(rights.IsPrivate)

    register_handlers_common(dp)

    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
