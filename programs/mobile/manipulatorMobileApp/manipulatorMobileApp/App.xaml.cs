using manipulatorMobileApp.Data;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Xamarin.Forms;

namespace manipulatorMobileApp
{
    public partial class App : Application
    {
        static RecordsDB notesDB;
        static ServersDB serversDB;

        public static string[] GlobalWordsArray { get; private set; }

        public static RecordsDB RecordsDB
        {
            get
            {
                if (notesDB == null)
                {
                    notesDB = new RecordsDB(
                        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                        "notesDatabase.db3"));
                }
                return notesDB;
            }
        }

        public static ServersDB ServersDB
        {
            get
            {
                if (serversDB == null)
                {
                    serversDB = new ServersDB(
                        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                        "serversDatabase.db3"));
                }
                return serversDB;
            }
        }

        public static async Task LoadWordsAsync(string path)
        {
            List<string> words = new List<string>();

            using (StreamReader reader = new StreamReader(path))
            {
                while (!reader.EndOfStream)
                {
                    string word = await reader.ReadLineAsync();
                    words.Add(word);
                }
            }

            GlobalWordsArray = words.ToArray();
        }

        public App()
        {
            InitializeComponent();
            Application.Current.UserAppTheme = OSAppTheme.Dark;
            MainPage = new NavigationPage(new MainPage());
        }

        protected override async void OnStart()
        {
            string fileName = "names.names";
            string filePath = DependencyService.Get<IFileHelper>().GetFilePath(fileName);
            if (File.Exists(filePath))
            {
                await LoadWordsAsync(filePath);
            }
            else
            {
                DependencyService.Get<IToast>().Show("Cannot read objects names");
            }
        }

        protected override void OnSleep()
        {
        }

        protected override void OnResume()
        {
        }
    }
}
