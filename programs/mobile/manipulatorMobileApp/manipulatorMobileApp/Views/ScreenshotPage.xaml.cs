using manipulatorMobileApp.Models;
using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class ScreenshotPage : ContentPage
    {
        private string IP;
        private string port;
        private const string OBJECT_OPEN = "<OBJ>";
        private const string OBJECT_CLOSE = "</OBJ>";
        private const string DISCONNECT = "<DISC_ME>";
        private const string GET_IMG = "<TSC>";

        public ScreenshotPage(string IP, string port)
        {
            InitializeComponent();
            this.IP = IP;
            this.port = port;
        }

        private byte[] getData(TcpClient client)
        {
            NetworkStream stream = client.GetStream();
            byte[] fileSizeBytes = new byte[4];
            int bytes = stream.Read(fileSizeBytes, 0, fileSizeBytes.Length);
            int dataLength = BitConverter.ToInt32(fileSizeBytes, 0);

            int bytesLeft = dataLength;
            byte[] data = new byte[dataLength];

            int buffersize = 1024;
            int bytesRead = 0;

            while (bytesLeft > 0)
            {
                int curDataSize = Math.Min(buffersize, bytesLeft);
                if (client.Available < curDataSize)
                {
                    curDataSize = client.Available;
                }
                bytes = stream.Read(data, bytesRead, curDataSize);
                bytesRead += curDataSize;
                bytesLeft -= curDataSize;
            }
            return data;
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
                    screenshot.IsEnabled = true;
                    return false;
                }
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show(ex.Message);
                screenshot.IsEnabled = true;
                return false;
            }
        }

        private bool SendMsg(TcpClient client, string msg)
        {
            try
            {
                NetworkStream stream = client.GetStream();
                string msge = msg;
                byte[] message = Encoding.ASCII.GetBytes(msge);
                stream.Write(message, 0, message.Length);
                DependencyService.Get<IToast>().Show($"Request was successfully sent to:\n{IP}:{port}");
                return true;
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Request sending error\nDetails: {ex.Message}");
                screenshot.IsEnabled = true;
                return false;
            }
        }

        public class ItemModel
        {
            public string Word { get; set; }
        }

        private void AddWordsToCollection(string text)
        {
            availableObjects.ItemsSource = null;
            if (string.IsNullOrEmpty(text))
                return;

            var availableObjectsData = new ObservableCollection<ItemModel>();
            string[] words = text.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
            foreach (string word in words)
            {
                availableObjectsData.Add(new ItemModel { Word = word });
            }
            availableObjects.ItemsSource = availableObjectsData;
        }

        private async void ReceiveText(TcpClient client)
        {
            using (NetworkStream stream = client.GetStream())
            {
                using (StreamReader reader = new StreamReader(stream))
                {
                    string receivedText = await reader.ReadToEndAsync();
                    AddWordsToCollection(receivedText);
                }
            }
        }

        private async void Screenshot_Clicked(object sender, EventArgs e)
        {
            screenshot.IsEnabled = false;
            screenshot.Text = "RESHOOT";
            bool _isConnected = await RequestConnectToServer(IP, port);
            if (!_isConnected)
                return;
            
            var client = Connection.Instance.client;
            NetworkStream stream = client.GetStream();
            string s = GET_IMG;
            bool _isSended = SendMsg(client, s);
            if (!_isSended)
                return;

            var data = getData(client);
            imageView.Source = ImageSource.FromStream(() => new MemoryStream(data));
            ReceiveText(client);
            screenshot.IsEnabled = true;
        }

        private async void AvailableObjects_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.CurrentSelection == null)
                return;

            bool _isConnected = await RequestConnectToServer(IP, port);
            if (!_isConnected)
                return;

            TcpClient client = Connection.Instance.client;
            ItemModel selectedItem = e.CurrentSelection[0] as ItemModel;
            string selectedWord = selectedItem.Word.Trim();
            string msge = OBJECT_OPEN + selectedWord + OBJECT_CLOSE + DISCONNECT;
            bool sendObj = SendMsg(client, msge);
            if (sendObj)
            {
                client.GetStream().Close();
                client.Close();
            }
        }
    }
}