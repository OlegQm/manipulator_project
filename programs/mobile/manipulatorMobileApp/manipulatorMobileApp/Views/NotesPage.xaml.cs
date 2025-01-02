using manipulatorMobileApp.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;
using OpenAI.Chat;
using Xamarin.Essentials;
using System.Net.Http;
using System.Net.Http.Headers;
using Newtonsoft.Json;
using SkiaSharp;
using Newtonsoft.Json.Linq;

namespace manipulatorMobileApp.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class NotesPage : ContentPage
    {
        private bool isEditMode = false;
        private const string apiEndpoint = "https://api.openai.com/v1/chat/completions";
        private string key = "default";
        private ChatClient _clientText;

        private string botToken;
        private string chatID;
        public NotesPage(string botToken, string chatID)
        {
            InitializeComponent();
            this.botToken = botToken;
            this.chatID = chatID;
        }

        private async Task getAPIKey()
        {
            string fileName = "api_key.txt";
            string filePath = DependencyService.Get<IFileHelper>().GetFilePath(fileName);
            key = "default";
            if (File.Exists(filePath))
            {
                using (StreamReader reader = new StreamReader(filePath))
                {
                    key = await reader.ReadLineAsync();
                    key = key.Trim();
                }
            }
            else
            {
                DependencyService.Get<IToast>().Show("Cannot read api key");
            }
        }

        private async void AddStandardWords()
        {
            try
            {
                bool result = await DisplayAlert("Load standard base",
                                                 "Are you sure you want to load the standard " +
                                                 "object database (previous entries will be deleted)?",
                                                 "Load",
                                                 "Cancel");
                if (result)
                {
                    await App.RecordsDB.DeleteAllRecords();
                    foreach (string word in App.GlobalWordsArray)
                    {
                        Record record = new Record
                        {
                            Title = word,
                            Text = null,
                            Date = DateTime.Now
                        };
                        await App.RecordsDB.SaveNoteAsync(record);
                    }
                    collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"An error occurred:\n{ex.Message}");
            }
        }

        protected override async void OnAppearing()
        {
            collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
            await getAPIKey();
            _clientText = new ChatClient(model: "gpt-4o", apiKey: key);
            base.OnAppearing();
        }

        private async void RefreshLists_Refreshing(object sender, EventArgs e)
        {
            collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
            refreshLists.IsRefreshing = false;
        }

        private async void AddButton_Clicked(object sender, EventArgs e)
        {
            AddButton.IsEnabled = false;
            await Navigation.PushAsync(new NoteAddingPage());
            notesSearchBar.Text = null;
            AddButton.IsEnabled = true;
        }

        private async void Handle_SearchButtonPressed(object sender, EventArgs e)
        {
            List<Record> allNotes = await App.RecordsDB.GetNotesAsync();
            List<Record> findNotes = new List<Record>();
            int notesNumber = allNotes.Count;
            for (int i = 0; i < notesNumber; i++)
            {
                if (allNotes[i].Title.ToLower().Contains(notesSearchBar.Text.ToLower().Trim()))
                {
                    findNotes.Add(allNotes[i]);
                }
            }
            if (findNotes.Count != 0)
            {
                collectionView.ItemsSource = findNotes;
            }
            else
            {
                DependencyService.Get<IToast>().Show("Nothing was found");
            }
        }

        private async void NotesSearchBar_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(e.NewTextValue))
            {
                collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
            }
        }

        private async void DeleteAllNotes_Clicked(object sender, EventArgs e)
        {
            bool result = await DisplayAlert("Delete all Entries",
                                             "Do you want to delete all entries?",
                                             "Delete",
                                             "Cancel");
            if (result)
            {
                await App.RecordsDB.DeleteAllRecords();
                collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
                DependencyService.Get<IToast>().Show("Ready!");
            }
            else return;
        }

        private async Task HandleEditMode(Record record)
        {
            NoteAddingPage noteAddingPage = new NoteAddingPage();
            string recordID = record.ID.ToString();
            noteAddingPage.ItemId = recordID;
            await Application.Current.MainPage.Navigation.PushAsync(noteAddingPage);
            notesSearchBar.Text = null;
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

        private async Task HandleNonEditMode(Record record)
        {
            try
            {
                var networkAccess = Connectivity.NetworkAccess;
                if (networkAccess != NetworkAccess.Internet)
                {
                    DependencyService.Get<IToast>().Show("No internet connection");
                    return;
                }
                await SendMessageToTelegram("/selection " + record.Title);
            }
            catch (IOException ex)
            {
                DependencyService.Get<IToast>().Show(
                    "IOException: " + ex.Message
                );
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show(
                    "Exception: " + ex.Message
                );
            }
        }

        private async void CollectionView_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.CurrentSelection == null) {
                return;
            }

            Record record = e.CurrentSelection.FirstOrDefault() as Record;
            if (isEditMode)
            {
                await HandleEditMode(record);
            }
            else
            {
                await HandleNonEditMode(record);
            }
        }

        private async void OnDelete(object sender, EventArgs e)
        {
            bool result = await DisplayAlert("Delete Record",
                                             "Do you want to delete this record?",
                                             "Delete",
                                             "Cancel");
            if (result)
            {
                refreshLists.IsRefreshing = true;
                SwipeItem swipeview = sender as SwipeItem;
                Record note = swipeview.CommandParameter as Record;
                await App.RecordsDB.DeleteNoteAsync(note);
                collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
                refreshLists.IsRefreshing = false;
            }
            else return;
        }

        private async void EditMode_Clicked(object sender, EventArgs e)
        {
            refreshLists.IsRefreshing = true;
            if (editMode.Text == "Edit mode")
            {
                isEditMode = true;
                editMode.Text = "Disable edit";
            }
            else
            {
                isEditMode = false;
                editMode.Text = "Edit mode";
            }
            collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
            refreshLists.IsRefreshing = false;
        }

        private void DefaultBtn_Clicked(object sender, EventArgs e)
        {
            refreshLists.IsRefreshing = true;
            AddStandardWords();
            refreshLists.IsRefreshing = false;
        }

        private async Task<string> sendPrompt(string objectsAsString, string description)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(objectsAsString))
                {
                    throw new ArgumentException("The list of objects cannot be null or empty.", nameof(objectsAsString));
                }
                if (string.IsNullOrWhiteSpace(description))
                {
                    throw new ArgumentException("The description cannot be null or empty.", nameof(description));
                }

                string prompt = $"I have a list of objects: {objectsAsString}. " +
                                $"Based on the description \"{description}\", " +
                                $"please return the matching words from the list separated by a space. " +
                                $"Return only the matching words, nothing else." +
                                $"If the word is not in the list or any other error occurs, return the word \"Unknown\"";

                ChatCompletion completion = await _clientText.CompleteChatAsync(prompt);

                if (completion == null || completion.Content == null || completion.Content.Count == 0)
                {
                    throw new InvalidOperationException("The response from the API was empty or invalid.");
                }

                return completion.Content[0].Text.Trim();
            }
            catch (ArgumentException ex)
            {
                Console.WriteLine($"Invalid argument: {ex.Message}");
                return "Error: Invalid input.";
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"API error: {ex.Message}");
                return "Error: API returned an invalid response.";
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An unexpected error occurred: {ex.Message}");
                return "Error: An unexpected error occurred.";
            }
        }

        private async Task<List<Record>> updateItems(string[] wordsArray, string gptResult)
        {
            List<Record> filteredItems = null;
            if (gptResult != null && wordsArray != null && gptResult.IndexOf("Error:") == -1)
            {
                filteredItems = await App.RecordsDB.FilterRecordsByKeywordsAsync(wordsArray);
            }
            return filteredItems;
        }

        private async void PromptButton_Clicked(object sender, EventArgs e)
        {
            string result = await DisplayPromptAsync(
                "Enter an object description",
                "You can describe an object in natural language",
                "Ready!",
                "Cancel",
                "Object description",
                maxLength: 100,
                keyboard: Keyboard.Text,
                initialValue: ""
            );
            if (!String.IsNullOrEmpty(result) && !String.IsNullOrEmpty(result))
            {
                refreshLists.IsRefreshing = true;
                var networkAccess = Connectivity.NetworkAccess;
                if (networkAccess != NetworkAccess.Internet)
                {
                    DependencyService.Get<IToast>().Show("No internet connection");
                    refreshLists.IsRefreshing = false;
                    return;
                }
                string promptResult = await sendPrompt(string.Join(", ", App.GlobalWordsArray), result);
                string[] wordsArray = promptResult.Split(' ');
                collectionView.ItemsSource = await updateItems(wordsArray, promptResult);
                refreshLists.IsRefreshing = false;
            }
        }

        private Stream ResizeImage(Stream inputImageStream, int width, int height)
        {
            using (var original = SKBitmap.Decode(inputImageStream))
            {
                var resized = original.Resize(new SKImageInfo(width, height), SKFilterQuality.High);

                if (resized == null)
                    throw new Exception("Unable to resize image");

                using (var image = SKImage.FromBitmap(resized))
                {
                    var outputStream = new MemoryStream();
                    image.Encode(SKEncodedImageFormat.Jpeg, 90).SaveTo(outputStream);
                    outputStream.Position = 0;
                    return outputStream;
                }
            }
        }

        private string ExtractContent(string jsonResponse)
        {
            var parsedJson = JObject.Parse(jsonResponse);
            string content = parsedJson["choices"]?[0]?["message"]?["content"]?.ToString();
            return content ?? "Unknown";
        }

        private async Task<string> GetObjectsFromImageAsync(Stream imageStream)
        {
            string objectsAsString = string.Join(", ", App.GlobalWordsArray);

            Stream resizedImageStream = ResizeImage(imageStream, 640, 480);
            byte[] resizedImageBytes;

            using (var memoryStream = new MemoryStream())
            {
                resizedImageStream.CopyTo(memoryStream);
                resizedImageBytes = memoryStream.ToArray();
            }
            string base64Image = Convert.ToBase64String(resizedImageBytes);

            string prompt = $"I have a list of objects: {objectsAsString}. " +
                            $"Based on the objects in the photo, " +
                            $"return the matching words from the list separated by a space. " +
                            $"Return only the matching words, nothing else. " +
                            $"If the word is not in the list or any other error occurs, return the word \"Unknown\".";

            var requestBody = new
            {
                model = "gpt-4o-mini",
                messages = new object[]
                {
                    new
                    {
                        role = "user",
                        content = new object[]
                        {
                            new { type = "text", text = prompt },
                            new
                            {
                                type = "image_url",
                                image_url = new
                                {
                                    url = $"data:image/jpeg;base64,{base64Image}"
                                }
                            }
                        }
                    }
                }
            };

            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", key);

                try
                {
                    var response = await client.PostAsync(apiEndpoint,
                        new StringContent(JsonConvert.SerializeObject(requestBody), Encoding.UTF8, "application/json"));

                    if (response.IsSuccessStatusCode)
                    {
                        var responseBody = await response.Content.ReadAsStringAsync();
                        return ExtractContent(responseBody);
                    }
                    else
                    {
                        DependencyService.Get<IToast>().Show("Error response");
                        return null;
                    }
                }
                catch (Exception ex)
                {
                    DependencyService.Get<IToast>().Show($"{ex.Message}");
                    return null;
                }
            }
        }

        private async void PhotoPromptButton_Clicked(object sender, EventArgs e)
        {
            var cameraStatus = await Permissions.CheckStatusAsync<Permissions.Camera>();
            if (cameraStatus != PermissionStatus.Granted)
            {
                cameraStatus = await Permissions.RequestAsync<Permissions.Camera>();
            }

            if (cameraStatus != PermissionStatus.Granted)
            {
                DependencyService.Get<IToast>().Show("Camera access is required to take photos.");
                return;
            }

            try
            {
                var photo = await MediaPicker.CapturePhotoAsync();

                if (photo == null)
                    return;

                using (var stream = await photo.OpenReadAsync())
                {
                    refreshLists.IsRefreshing = true;
                    var networkAccess = Connectivity.NetworkAccess;
                    if (networkAccess != NetworkAccess.Internet)
                    {
                        DependencyService.Get<IToast>().Show("No internet connection");
                        refreshLists.IsRefreshing = false;
                        return;
                    }
                    string promptResult = null;
                    string[] wordsArray = null;
                    promptResult = await GetObjectsFromImageAsync(stream);
                    if (promptResult != null)
                    {
                        promptResult = promptResult.Trim();
                        wordsArray = promptResult.Split(' ');
                    }
                    collectionView.ItemsSource = await updateItems(wordsArray, promptResult);
                    refreshLists.IsRefreshing = false;
                }
            }
            catch (FeatureNotSupportedException)
            {
                refreshLists.IsRefreshing = false;
                DependencyService.Get<IToast>().Show("Camera is not supported on this device.");
            }
            catch (PermissionException)
            {
                refreshLists.IsRefreshing = false;
                DependencyService.Get<IToast>().Show("Camera permissions are not granted.");
            }
            catch (Exception ex)
            {
                refreshLists.IsRefreshing = false;
                DependencyService.Get<IToast>().Show($"Something went wrong: {ex.Message}");
            }
        }
    }
}
