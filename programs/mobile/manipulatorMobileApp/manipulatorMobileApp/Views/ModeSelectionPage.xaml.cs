using System;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class ModeSelectionPage : ContentPage
    {
        private string token;
        private string chatID;
        public ModeSelectionPage(string token, string chatID)
        {
            InitializeComponent();
            this.token = token;
            this.chatID = chatID;
        }

        private async void ObjectListBtn_Clicked(object sender, EventArgs e)
        {
            objectListBtn.IsEnabled = false;
            NotesPage objectsList = new NotesPage(token, chatID);
            await Navigation.PushAsync(objectsList);
            objectListBtn.IsEnabled = true;
        }

        private async void PossibleObjectsBtn_Clicked(object sender, EventArgs e)
        {
            possibleObjectsBtn.IsEnabled = false;
            ScreenshotPage scrPage = new ScreenshotPage(token, chatID);
            await Navigation.PushAsync(scrPage);
            possibleObjectsBtn.IsEnabled = true;
        }
    }
}
