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
                    SetEditorsParameters(server);
            }
            collectionView.ItemsSource = await App.ServersDB.GetServersAsync();
            base.OnAppearing();
        }

        private bool IpChecking(string ip)
        {
            if (!string.IsNullOrWhiteSpace(ip) && ip.IndexOf(".") != -1 &&
                !ip.Any(c => char.IsLetter(c)))
            {
                int pointsCounter = 0;
                for (int i = 0; i < ip.Length; i++)
                    if (ip[i] == '.') pointsCounter++;
                return pointsCounter == 3;
            }
            return false;
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
            else return;
        }

        private async void SaveServer_Clicked(object sender, EventArgs e)
        {
            if (IpChecking(hostIP.Text) && PortChecking(hostPort.Text))
            {
                Server server = new Server();
                bool isServerNameFree = await App.ServersDB.GetServerNameAvailibiltyAsync(hostName.Text);
                if (!string.IsNullOrWhiteSpace(hostName.Text) && isServerNameFree)
                    server.name = hostName.Text;
                if (!isServerNameFree)
                    DependencyService.Get<IToast>().Show("This server name already exists");
                else if (string.IsNullOrWhiteSpace(hostName.Text))
                    server.name = Convert.ToString(DateTime.Now);
                if (isServerNameFree)
                {
                    server.IPParam = hostIP.Text;
                    server.portParam = hostPort.Text;
                    server.Date = DateTime.Now;
                    await App.ServersDB.SaveServerAsync(server);
                    collectionView.ItemsSource = await App.ServersDB.GetServersAsync();
                }
            }
            else DependencyService.Get<IToast>().Show("Impossible Host or IP");
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
    }
}
