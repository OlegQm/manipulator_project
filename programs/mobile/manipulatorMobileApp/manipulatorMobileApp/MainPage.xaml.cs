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
            hostName.Text = server.name;
            hostIP.Text = server.IPParam;
            hostPort.Text = server.portParam;
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

        private bool IpChecking(string ip)
        {
            if (string.IsNullOrWhiteSpace(ip))
                return false;

            if (ip.Any(c => !char.IsDigit(c) && c != '.'))
                return false;

            if (ip.Count(c => c == '.') != 3)
                return false;

            return true;
        }

        private bool PortChecking(string port)
        {
            if (!string.IsNullOrWhiteSpace(port) &&
                port.Any(c => char.IsDigit(c)))
                return port.Length < 7;
            return false;
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
            }
            else
            {
                return;
            }
        }

        private async void SaveServer_Clicked(object sender, EventArgs e)
        {
            if (!IpChecking(hostIP.Text) || !PortChecking(hostPort.Text))
            {
                DependencyService.Get<IToast>().Show("Impossible Host or IP");
                return;
            }
            Server server = new Server();
            Server existingRecord = await App.ServersDB.FindRecordByName(hostName.Text);
            bool isServerNameFree = existingRecord == null;
            if (isServerNameFree)
            {
                server.name = !string.IsNullOrWhiteSpace(hostName.Text) ? hostName.Text : Convert.ToString(DateTime.Now);
                server.IPParam = hostIP.Text;
                server.portParam = hostPort.Text;
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
                    existingRecord.IPParam = hostIP.Text;
                    existingRecord.Date = DateTime.Now;
                    await App.ServersDB.SaveServerAsync(existingRecord);
                    RefreshCollection();
                }
            }
        }

        private async void StartWorking_Clicked(object sender, EventArgs e)
        {
            if (IpChecking(hostIP.Text) && PortChecking(hostPort.Text))
            {
                startToolbar.IsEnabled = false;
                startWorking.IsEnabled = false;
                ModeSelectionPage msPage = new ModeSelectionPage(hostIP.Text, hostPort.Text);
                await Navigation.PushAsync(msPage);
                startWorking.IsEnabled = true;
                startToolbar.IsEnabled = true;
            }
            else DependencyService.Get<IToast>().Show("Impossible Host or IP");
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
