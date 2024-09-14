using manipulatorMobileApp.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class NotesPage : ContentPage
    {
        private string IP;
        private string port;
        private bool isEditMode = false;
        private const string OBJECT_OPEN = "<OBJ>";
        private const string OBJECT_CLOSE = "</OBJ>";
        private const string DISCONNECT = "<DISC_ME>";
        public NotesPage(string recievedIP, string recievedPort)
        {
            InitializeComponent();
            this.IP = recievedIP;
            this.port = recievedPort;
        }

        private void closeConversation(TcpClient client)
        {
            try
            {
                if (client != null && client.Connected)
                {
                    var stream = client.GetStream();
                    if (stream != null)
                    {
                        stream.Close();
                    }
                    client.Close();
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"An error occurred when trying to close the conversation: {ex.Message}");
            }
        }

        private async Task<bool> RequestConnectToServer(string ip, string string_port)
        {
            try
            {
                TcpClient client = new TcpClient();
                int port = Convert.ToInt32(string_port);
                await Task.Run(() => client.ConnectAsync(ip, port));
                if (client.Connected)
                {
                    Connection.Instance.client = client;
                    return true;
                }
                else
                {
                    DependencyService.Get<IToast>().Show("Connection unsuccessful\n" +
                                                         "Please, try again");
                    return false;
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show(ex.Message);
                return false;
            }
        }

        private async void AddStandardWords(string path)
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
                    using (StreamReader reader = new StreamReader(path))
                    {
                        while (!reader.EndOfStream)
                        {
                            string word = reader.ReadLine();
                            Record record = new Record();
                            record.Title = word;
                            record.Text = null;
                            record.Date = DateTime.Now;
                            await App.RecordsDB.SaveNoteAsync(record);
                        }
                        collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
                    }
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"An error occurred:\n{ex.Message}");
            }
        }

        private bool SendMsg(TcpClient client, string msge)
        {
            try
            {
                NetworkStream stream = client.GetStream();
                string msg = msge;
                byte[] message = Encoding.ASCII.GetBytes(msg);
                stream.Write(message, 0, message.Length);
                DependencyService.Get<IToast>().Show($"Request was successfully sent to:\n{IP}:{port}");
                return true;
            }
            catch (Exception ex)
            {
                closeConversation(client);
                DependencyService.Get<IToast>().Show($"Request sending error\nDetails: {ex.Message}");
                return false;
            }
        }

        protected override async void OnAppearing()
        {
            collectionView.ItemsSource = await App.RecordsDB.GetNotesAsync();
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

        private async Task HandleNonEditMode(Record record)
        {
            TcpClient client = null;
            try
            {
                bool _isConnected = await RequestConnectToServer(IP, port);
                if (!_isConnected)
                    return;
                client = Connection.Instance.client;
                string msge = OBJECT_OPEN + record.Title + OBJECT_CLOSE + DISCONNECT;
                bool sendObj = SendMsg(client, msge);
                if (sendObj)
                {
                    await client.GetStream().FlushAsync();
                    closeConversation(client);
                }
            }
            catch (SocketException ex)
            {
                closeConversation(client);
                DependencyService.Get<IToast>().Show("SocketException: " + ex.Message);
            }
            catch (IOException ex)
            {
                closeConversation(client);
                DependencyService.Get<IToast>().Show("IOException: " + ex.Message);
            }
            catch (Exception ex)
            {
                closeConversation(client);
                DependencyService.Get<IToast>().Show("Exception: " + ex.Message);
            }
        }

        private async void CollectionView_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.CurrentSelection == null)
                return;

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
            string fileName = "coco.names";
            string filePath = DependencyService.Get<IFileHelper>().GetFilePath(fileName);
            if (File.Exists(filePath))
            {
                AddStandardWords(filePath);
            }
            else
            {
                DependencyService.Get<IToast>().Show("File error");
            }
            refreshLists.IsRefreshing = false;
        }
    }
}