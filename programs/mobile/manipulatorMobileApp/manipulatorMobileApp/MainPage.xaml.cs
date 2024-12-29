using manipulatorMobileApp.Views;
using System;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();
        }

        private async void ObjectListBtn_Clicked(object sender, EventArgs e)
        {
            objectListBtn.IsEnabled = false;
            NotesPage objectsList = new NotesPage();
            await Navigation.PushAsync(objectsList);
            objectListBtn.IsEnabled = true;
        }

        private async void PossibleObjectsBtn_Clicked(object sender, EventArgs e)
        {
            possibleObjectsBtn.IsEnabled = false;
            ScreenshotPage scrPage = new ScreenshotPage();
            await Navigation.PushAsync(scrPage);
            possibleObjectsBtn.IsEnabled = true;
        }
    }
}
