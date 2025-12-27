from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import requests

class TelegramServer:
    def __init__(self, token, pipe):
        self.token = token
        self.pipe = pipe
        self.saved_update_id = None
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, self.handle_channel_post))

    def initialize_last_update_id(self):
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        response = requests.get(url).json()
        result = response.get("result", [])
        if result:
            self.saved_update_id = result[-1]["update_id"]
            print(f"Saved last update_id: {self.saved_update_id}")

    async def handle_get_image_command(self, chat_id, context: ContextTypes.DEFAULT_TYPE):
        self.pipe.send("get_image")
        print("Waiting for main process to send image and objects...")

        image_data, objects = self.pipe.recv()
        print("Received image and objects from main process.")

        try:
            await context.bot.send_photo(chat_id=chat_id, photo=image_data, caption=objects)
        except Exception as e:
            print(f"Error occurred while sending photo: {e}")

    async def handle_selection_command(self, object_name):
        print(f"Selection command received: {object_name}")
        self.pipe.send(("selection", object_name))

    async def handle_switch_searching_command(self, state):
        if state == "0":
            print("Switching off searching mode")
        else:
            print("Switching on searching mode")
        self.pipe.send(("searching", state))
        
    async def handle_switch_flashlight_mode(self, mode):
        mode = mode.strip()
        if mode not in ["ON", "OFF"]:
            print("Unknown flashlight mode")
        print(f"Switching {mode.lower()} flashlight")
        self.pipe.send(("flashlight", mode))

    async def process_text_command(self, text, handler):
        command_parts = text.split(maxsplit=1)
        argument = command_parts[1] if len(command_parts) > 1 else None
        if argument:
            await handler(argument)

    async def handle_channel_post(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        if self.saved_update_id and update.update_id <= self.saved_update_id:
            return

        self.saved_update_id = update.update_id

        channel_post = update.channel_post
        text = channel_post.text if channel_post.text else ""
        chat_id = channel_post.chat_id

        if text.startswith("/get_image"):
            await self.handle_get_image_command(chat_id, context)
        elif text.startswith("/selection"):
            await self.process_text_command(
                text,
                self.handle_selection_command
            )
        elif text.startswith("/searching"):
            await self.process_text_command(
                text,
                self.handle_switch_searching_command
            )
        elif text.startswith("/flashlight"):
            await self.process_text_command(
                text,
                self.handle_switch_flashlight_mode
            )
    def run(self):
        self.initialize_last_update_id()
        print("Starting server...")
        self.app.run_polling()

