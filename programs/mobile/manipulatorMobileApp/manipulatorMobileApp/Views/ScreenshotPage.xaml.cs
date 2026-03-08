using Newtonsoft.Json.Linq;
using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using manipulatorMobileApp.Helpers;
using manipulatorMobileApp.Services;
using Xamarin.Essentials;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class ScreenshotPage : ContentPage
    {
        private string botToken;
        private string chatID;
        private int lastUpdateId = 0;

        // Chatbot connection settings (forwarded from server config)
        private string chatbotUrl;
        private string chatbotAuthUser;
        private string chatbotAuthPassword;

        // Raw image bytes of the last successful screenshot — sent to the chatbot on first message
        private byte[] _imageBytes;

        public ScreenshotPage(string botToken, string chatID,
            string chatbotUrl = null, string chatbotAuthUser = null, string chatbotAuthPassword = null)
        {
            InitializeComponent();
            this.botToken = botToken;
            this.chatID = chatID;
            this.chatbotUrl = chatbotUrl;
            this.chatbotAuthUser = chatbotAuthUser;
            this.chatbotAuthPassword = chatbotAuthPassword;
        }

        public class ItemModel
        {
            public string Word { get; set; }
        }

        private void AddWordsToCollection(string text)
        {
            availableObjects.ItemsSource = null;
            if (string.IsNullOrEmpty(text))
            {
                return;
            }

            var availableObjectsData = new ObservableCollection<ItemModel>();
            string[] words = text.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (string word in words)
            {
                availableObjectsData.Add(new ItemModel { Word = word });
            }
            availableObjects.ItemsSource = availableObjectsData;
        }

        private async Task FetchImageFromTelegram(JToken result)
        {
            try
            {
                var photoResult = await TelegramService.FetchLatestPhotoAsync(botToken, result);
                if (photoResult == null)
                {
                    return;
                }

                // Store raw bytes so we can forward the image to the chatbot
                _imageBytes = photoResult.ImageBytes;
                ChatButton.IsEnabled = true;

                imageView.Source = ImageSource.FromStream(
                    () => new MemoryStream(photoResult.ImageBytes)
                );
                AddWordsToCollection(photoResult.Caption);
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Error! {ex.Message}");
            }
        }

        private async void Screenshot_Clicked(object sender, EventArgs e)
        {
            screenshot.IsEnabled = false;
            screenshot.Text = "RESHOOT";
            var networkAccess = Connectivity.NetworkAccess;
            if (networkAccess != NetworkAccess.Internet)
            {
                DependencyService.Get<IToast>().Show("No internet connection");
                return;
            }
            try
            {
                await TelegramService.SendMessageAsync(botToken, chatID, "/get_image");
                lastUpdateId = await TelegramService.GetLastUpdateIdAsync(botToken);
                using (var cts = new CancellationTokenSource(10000))
                {
                    var updateResult = await TelegramService.WaitForNewMessageAsync(
                        botToken,
                        lastUpdateId,
                        cts.Token
                    );

                    if (updateResult != null)
                    {
                        lastUpdateId = updateResult.LastUpdateId;
                        await FetchImageFromTelegram(updateResult.Updates);
                    }
                    else
                    {
                        DependencyService.Get<IToast>().Show(
                            "Error: No new message received within the timeout period."
                        );
                    }
                }
            }
            catch (OperationCanceledException)
            {
                DependencyService.Get<IToast>().Show(
                    "Error: No new message received within the timeout period."
                );
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Error: {ex.Message}");
            }
            finally
            {
                screenshot.IsEnabled = true;
            }
        }

        private async void AvailableObjects_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.CurrentSelection == null)
            {
                return;
            }

            try
            {
                var networkAccess = Connectivity.NetworkAccess;
                if (networkAccess != NetworkAccess.Internet)
                {
                    DependencyService.Get<IToast>().Show("No internet connection");
                    return;
                }
                ItemModel selectedItem = e.CurrentSelection[0] as ItemModel;
                string selectedWord = selectedItem.Word.Trim();
                await TelegramService.SendMessageAsync(botToken, chatID, $"/selection {selectedWord}");
            }
            catch (IOException ex)
            {
                DependencyService.Get<IToast>().Show("IOException: " + ex.Message);
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show("Exception: " + ex.Message);
            }
        }

        private async void SearchingButton_Clicked(object sender, EventArgs e)
        {
            await SearchingToggleHelper.ToggleAsync(SearchingButton, botToken, chatID);
        }

        private async void FlashlightButton_Clicked(object sender, EventArgs e)
        {
            await FlashlightToggleHelper.ToggleAsync(FlashlightButton, botToken, chatID);
        }

        /// <summary>
        /// Opens the chatbot chat page. The button is only active after an image has been
        /// received from Telegram (<see cref="_imageBytes"/> is not null).
        /// Validates that chatbot connection settings are configured before navigating.
        /// </summary>
        private async void ChatButton_Clicked(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(chatbotUrl))
            {
                DependencyService.Get<IToast>().Show(
                    "Chatbot URL is not configured. Please add it in the server settings.");
                return;
            }

            ChatButton.IsEnabled = false;
            try
            {
                var chatPage = new ChatPage(_imageBytes, chatbotUrl, chatbotAuthUser, chatbotAuthPassword);
                await Navigation.PushAsync(chatPage);
            }
            finally
            {
                ChatButton.IsEnabled = true;
            }
        }
    }
}
