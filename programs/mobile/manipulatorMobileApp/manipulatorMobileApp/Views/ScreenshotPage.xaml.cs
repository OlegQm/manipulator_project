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
        private static readonly byte[] PlaceholderImageBytes = Convert.FromBase64String(
            "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"
        );

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
            SafeAreaHelper.Apply(this);
            ChatButton.IsEnabled = false;
            this.botToken = botToken;
            this.chatID = chatID;
            this.chatbotUrl = chatbotUrl;
            this.chatbotAuthUser = chatbotAuthUser;
            this.chatbotAuthPassword = chatbotAuthPassword;

            LoadPlaceholderImage();
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

        private void LoadPlaceholderImage()
        {
            _imageBytes = PlaceholderImageBytes;
            ChatButton.IsEnabled = true;
            imageView.Source = ImageSource.FromStream(() => new MemoryStream(PlaceholderImageBytes));
            AddWordsToCollection("Temporary test image");
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
