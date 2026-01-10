using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using manipulatorMobileApp;
using Newtonsoft.Json.Linq;
using Xamarin.Forms;

namespace manipulatorMobileApp.Services
{
    public static class TelegramService
    {
        public class TelegramUpdatesResult
        {
            public JToken Updates { get; set; }
            public int LastUpdateId { get; set; }
        }

        public class TelegramPhotoResult
        {
            public byte[] ImageBytes { get; set; }
            public string Caption { get; set; }
        }

        public static async Task SendMessageAsync(string botToken, string chatId, string message)
        {
            try
            {
                using (HttpClient client = new HttpClient())
                {
                    var url = $"https://api.telegram.org/bot{botToken}/sendMessage";
                    var content = new FormUrlEncodedContent(new[]
                    {
                        new KeyValuePair<string, string>("chat_id", chatId),
                        new KeyValuePair<string, string>("text", message)
                    });

                    var response = await client.PostAsync(url, content);
                    if (response.IsSuccessStatusCode)
                    {
                        DependencyService.Get<IToast>().Show(
                            "Success! Request has been sent to Telegram!"
                        );
                    }
                    else
                    {
                        DependencyService.Get<IToast>().Show(
                            "Error! Request has not been sent to Telegram!"
                        );
                    }
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Error! {ex.Message}");
            }
        }

        public static async Task<int> GetLastUpdateIdAsync(string botToken)
        {
            using (HttpClient client = new HttpClient())
            {
                var url = $"https://api.telegram.org/bot{botToken}/getUpdates";
                var response = await client.GetStringAsync(url);
                var updates = JObject.Parse(response);
                var result = updates["result"];
                if (result != null && result.HasValues)
                {
                    return result.Last["update_id"].Value<int>();
                }
            }

            return 0;
        }

        public static async Task<TelegramUpdatesResult> WaitForNewMessageAsync(
            string botToken,
            int lastUpdateId,
            System.Threading.CancellationToken cancellationToken
        )
        {
            const int intervalMilliseconds = 250;
            while (!cancellationToken.IsCancellationRequested)
            {
                using (HttpClient client = new HttpClient())
                {
                    var url = $"https://api.telegram.org/bot{botToken}/getUpdates?offset={lastUpdateId + 1}";
                    var response = await client.GetStringAsync(url);
                    var updates = JObject.Parse(response);
                    var result = updates["result"];

                    if (result != null && result.HasValues)
                    {
                        return new TelegramUpdatesResult
                        {
                            Updates = result,
                            LastUpdateId = result.Last["update_id"].Value<int>()
                        };
                    }
                }

                await Task.Delay(intervalMilliseconds, cancellationToken);
            }

            return null;
        }

        public static async Task<TelegramPhotoResult> FetchLatestPhotoAsync(
            string botToken,
            JToken updates
        )
        {
            if (updates == null || !updates.HasValues)
            {
                return null;
            }

            var update = updates.Last;
            var channelPost = update["channel_post"];
            if (channelPost?["photo"] == null)
            {
                return null;
            }

            var photoArray = channelPost["photo"];
            var caption = channelPost["caption"]?.ToString() ?? "";
            var fileIdToken = photoArray.Last?["file_id"];
            if (fileIdToken == null)
            {
                return null;
            }

            var fileId = fileIdToken.ToString();
            using (HttpClient client = new HttpClient())
            {
                var fileUrlResponse = await client.GetStringAsync(
                    $"https://api.telegram.org/bot{botToken}/getFile?file_id={fileId}");
                var filePath = JObject.Parse(fileUrlResponse)["result"]["file_path"].ToString();
                var fileUrl = $"https://api.telegram.org/file/bot{botToken}/{filePath}";

                var imageBytes = await client.GetByteArrayAsync(fileUrl);
                return new TelegramPhotoResult
                {
                    ImageBytes = imageBytes,
                    Caption = caption
                };
            }
        }
    }
}
