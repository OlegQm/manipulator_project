using System;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class ModeSelectionPage : ContentPage
    {
        private string IP;
        private string port;
        public ModeSelectionPage(string IP, string port)
        {
            InitializeComponent();
            this.IP = IP;
            this.port = port;
        }

        private async void ObjectListBtn_Clicked(object sender, EventArgs e)
        {
            objectListBtn.IsEnabled = false;
            NotesPage objectsList = new NotesPage(IP, port);
            await Navigation.PushAsync(objectsList);
            objectListBtn.IsEnabled = true;
        }

        private async void PossibleObjectsBtn_Clicked(object sender, EventArgs e)
        {
            possibleObjectsBtn.IsEnabled = false;
            ScreenshotPage scrPage = new ScreenshotPage(IP, port);
            await Navigation.PushAsync(scrPage);
            possibleObjectsBtn.IsEnabled = true;
        }
    }
}