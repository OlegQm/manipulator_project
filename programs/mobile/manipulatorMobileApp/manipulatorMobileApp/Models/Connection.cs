using System.Net.Sockets;

namespace manipulatorMobileApp.Models
{
    public class Connection
    {
        private static Connection _instance;
        public static Connection Instance
        {
            get
            {
                if (_instance == null) _instance = new Connection();
                return _instance;
            }
        }
        public TcpClient client { get; set; }
    }
}
