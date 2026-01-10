using System.Threading.Tasks;
using manipulatorMobileApp.Services;
using Xamarin.Forms;

namespace manipulatorMobileApp.Helpers
{
    public static class FlashlightToggleHelper
    {
        public static async Task ToggleAsync(ToolbarItem button, string botToken, string chatId)
        {
            button.IsEnabled = false;
            if (button.Text == "Turn on flashlight")
            {
                await TelegramService.SendMessageAsync(botToken, chatId, "/flashlight ON");
                button.Text = "Turn off flashlight";
            }
            else
            {
                await TelegramService.SendMessageAsync(botToken, chatId, "/flashlight OFF");
                button.Text = "Turn on flashlight";
            }
            button.IsEnabled = true;
        }
    }
}
