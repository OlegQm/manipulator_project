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
        private string chatbotUrl;
        private string chatbotAuthUser;
        private string chatbotAuthPassword;

        public ModeSelectionPage(
            string token,
            string chatID,
            string chatbotUrl = null,
            string chatbotAuthUser = null,
            string chatbotAuthPassword = null)
        {
            InitializeComponent();
            this.token = token;
            this.chatID = chatID;
            this.chatbotUrl = chatbotUrl;
            this.chatbotAuthUser = chatbotAuthUser;
            this.chatbotAuthPassword = chatbotAuthPassword;
        }

        private async void ObjectListBtn_Clicked(object sender, EventArgs e)
        {
            objectListBtn.IsEnabled = false;
            NotesPage objectsList = new NotesPage(token, chatID, chatbotUrl, chatbotAuthUser, chatbotAuthPassword);
            await Navigation.PushAsync(objectsList);
            objectListBtn.IsEnabled = true;
        }

        private async void PossibleObjectsBtn_Clicked(object sender, EventArgs e)
        {
            possibleObjectsBtn.IsEnabled = false;
            ScreenshotPage scrPage = new ScreenshotPage(token, chatID, chatbotUrl, chatbotAuthUser, chatbotAuthPassword);
            await Navigation.PushAsync(scrPage);
            possibleObjectsBtn.IsEnabled = true;
        }
    }
}
