using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
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

        public ScreenshotPage(string botToken, string chatID)
        {
            InitializeComponent();
            this.botToken = botToken;
            this.chatID = chatID;
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
                var update = result.Last;
                var channelPost = update["channel_post"];
                if (channelPost?["photo"] != null)
                {
                    var photoArray = channelPost["photo"];
                    var caption = channelPost["caption"]?.ToString() ?? "";

                    var fileId = photoArray.Last["file_id"].ToString();
                    using (HttpClient client = new HttpClient())
                    {
                        var fileUrlResponse = await client.GetStringAsync(
                            $"https://api.telegram.org/bot{botToken}/getFile?file_id={fileId}");
                        var filePath = Newtonsoft.Json.Linq.JObject.Parse(fileUrlResponse)["result"]["file_path"].ToString();
                        var fileUrl = $"https://api.telegram.org/file/bot{botToken}/{filePath}";

                        var imageBytes = await client.GetByteArrayAsync(fileUrl);
                        imageView.Source = ImageSource.FromStream(() => new MemoryStream(imageBytes));
                        AddWordsToCollection(caption);
                    }
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Error! {ex.Message}");
            }
        }

        private async Task SendMessageToTelegram(string message)
        {
            try
            {
                using (HttpClient client = new HttpClient())
                {
                    var url = $"https://api.telegram.org/bot{botToken}/sendMessage";
                    var content = new FormUrlEncodedContent(new[]
                    {
                        new KeyValuePair<string, string>("chat_id", chatID),
                        new KeyValuePair<string, string>("text", message)
                    });

                    var response = await client.PostAsync(url, content);
                    if (response.IsSuccessStatusCode)
                    {
                        DependencyService.Get<IToast>().Show("Success! Request has been sent to Telegram!");
                    }
                    else
                    {
                        DependencyService.Get<IToast>().Show("Error! Request has not been sent to Telegram!");
                    }
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Error! {ex.Message}");
            }
        }

        private async Task<JToken> WaitForNewMessageAsync(CancellationToken cancellationToken)
        {
            const int intervalMilliseconds = 250;
            while (!cancellationToken.IsCancellationRequested)
            {
                using (HttpClient client = new HttpClient())
                {
                    var url = $"https://api.telegram.org/bot{botToken}/getUpdates?offset={lastUpdateId + 1}";
                    var response = await client.GetStringAsync(url);
                    var updates = Newtonsoft.Json.Linq.JObject.Parse(response);
                    var result = updates["result"];

                    if (result != null && result.HasValues)
                    {
                        lastUpdateId = result.Last["update_id"].Value<int>();
                        return result;
                    }
                }

                await Task.Delay(intervalMilliseconds, cancellationToken);
            }

            return null;
        }

        private async Task UpdateLastID()
        {
            using (HttpClient client = new HttpClient())
            {
                var url = $"https://api.telegram.org/bot{botToken}/getUpdates";
                var response = await client.GetStringAsync(url);
                var updates = Newtonsoft.Json.Linq.JObject.Parse(response);
                var result = updates["result"];
                if (result != null && result.HasValues)
                {
                    lastUpdateId = result.Last["update_id"].Value<int>();
                }
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
                await SendMessageToTelegram("/get_image");
                await UpdateLastID();
                using (var cts = new CancellationTokenSource(10000))
                {
                    var result = await WaitForNewMessageAsync(cts.Token);

                    if (result != null)
                    {
                        await FetchImageFromTelegram(result);
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
                await SendMessageToTelegram($"/selection {selectedWord}");
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
    }
}
