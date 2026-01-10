using System.Threading.Tasks;
using manipulatorMobileApp.Services;
using Xamarin.Forms;

namespace manipulatorMobileApp.Helpers
{
    public static class SearchingToggleHelper
    {
        public static async Task ToggleAsync(ToolbarItem button, string botToken, string chatId)
        {
            button.IsEnabled = false;
            if (button.Text == "OFF searching")
            {
                await TelegramService.SendMessageAsync(botToken, chatId, "/searching 0");
                button.Text = "ON searching";
            }
            else
            {
                await TelegramService.SendMessageAsync(botToken, chatId, "/searching 1");
                button.Text = "OFF searching";
            }
            button.IsEnabled = true;
        }
    }
}
