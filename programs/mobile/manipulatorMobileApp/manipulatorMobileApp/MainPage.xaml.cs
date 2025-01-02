using manipulatorMobileApp.Models;
using manipulatorMobileApp.Views;
using System;
using System.Linq;
using Xamarin.Forms;

namespace manipulatorMobileApp
{
    public partial class MainPage : ContentPage
    {
        private void SetEditorsParameters(Server server)
        {
            botName.Text = server.name;
            token.Text = server.botToken;
            chatID.Text = server.chatID;
        }

        private async void RefreshCollection()
        {
            var items = await App.ServersDB.GetServersAsync();
            collectionView.ItemsSource = items;
            int itemsNumber = items.Count();
            collectionView.ScrollTo(items[itemsNumber - 1], position: ScrollToPosition.End, animate: true);
        }
        public MainPage()
        {
            InitializeComponent();
        }

        protected override async void OnAppearing()
        {
            if (await App.ServersDB.IsDatabaseNotEmpty())
            {
                Server server = await App.ServersDB.GetLastRecord();
                if (server != null)
                {
                    SetEditorsParameters(server);
                }
                RefreshCollection();
            }

            base.OnAppearing();
        }

        private async void RefreshLists_Refreshing(object sender, EventArgs e)
        {
            collectionView.ItemsSource = await App.ServersDB.GetServersAsync();
            refreshLists.IsRefreshing = false;
        }

        private void CollectionView_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.CurrentSelection != null)
            {
                Server server = e.CurrentSelection.FirstOrDefault() as Server;
                SetEditorsParameters(server);
            }
        }

        private async void OnDelete(object sender, EventArgs e)
        {
            bool result = await DisplayAlert("Delete Server",
                                             "Do you want to delete this server?",
                                             "Delete",
                                             "Cancel");
            if (result)
            {
                SwipeItem swipeview = sender as SwipeItem;
                Server server = swipeview.CommandParameter as Server;
                await App.ServersDB.DeleteServerAsync(server);
                collectionView.ItemsSource = await App.ServersDB.GetServersAsync();
                if (botName.Text.Trim() == server.name)
                {
                    botName.Text = null;
                    token.Text = null;
                    chatID.Text = null;
                }
            }
            else
            {
                return;
            }
        }

        private async void SaveServer_Clicked(object sender, EventArgs e)
        {
            Server server = new Server();
            Server existingRecord = await App.ServersDB.FindRecordByName(botName.Text);
            bool isServerNameFree = existingRecord == null;
            if (isServerNameFree)
            {
                server.name = !string.IsNullOrWhiteSpace(botName.Text) ? botName.Text : Convert.ToString(DateTime.Now);
                server.botToken = token.Text.Trim();
                server.chatID = chatID.Text.Trim();
                server.Date = DateTime.Now;
                await App.ServersDB.SaveServerAsync(server);
                collectionView.ItemsSource = await App.ServersDB.GetServersAsync();
            }
            else
            {
                bool result = await DisplayAlert("Choose option",
                                                 "Replace existing record?",
                                                 "Replace",
                                                 "Cancel");
                if (result)
                {
                    existingRecord.botToken = token.Text.Trim();
                    existingRecord.chatID = chatID.Text.Trim();
                    existingRecord.Date = DateTime.Now;
                    await App.ServersDB.SaveServerAsync(existingRecord);
                    RefreshCollection();
                }
            }
        }

        bool CheckComponent(string componentValue, string message)
        {
            if (
                string.IsNullOrWhiteSpace(componentValue) ||
                string.IsNullOrEmpty(componentValue)
                )
            {
                DependencyService.Get<IToast>().Show(message);
                return false;
            }
            return true;
        }

        bool CheckStartPossible()
        {
            if (!CheckComponent(botName.Text, "Bot name is empty")) { return false; }
            if (!CheckComponent(token.Text, "Bot token is empty")) { return false; }
            if (!CheckComponent(chatID.Text, "Chat ID is empty")) { return false; }
            return true;
        }

        private async void StartWorking_Clicked(object sender, EventArgs e)
        {
            if (!CheckStartPossible()) { return; }
            startToolbar.IsEnabled = false;
            startWorking.IsEnabled = false;
            ModeSelectionPage msPage = new ModeSelectionPage(
                token.Text.Trim(),
                chatID.Text.Trim()
            );
            await Navigation.PushAsync(msPage);
            startWorking.IsEnabled = true;
            startToolbar.IsEnabled = true;
        }

        private async void deleteAll_Clicked(object sender, EventArgs e)
        {
            bool result = await DisplayAlert("Choose option",
                                             "Are you sure you want to delete all hosts?",
                                             "Yes",
                                             "Cancel");
            if (result)
            {
                await App.ServersDB.DeleteAllRecords();
                collectionView.ItemsSource = null;
            }
        }
    }
}
