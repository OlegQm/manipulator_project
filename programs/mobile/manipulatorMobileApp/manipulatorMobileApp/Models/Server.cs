using SQLite;
using System;

namespace manipulatorMobileApp.Models
{
    public class Server
    {
        [PrimaryKey, AutoIncrement]
        public int ID { get; set; }
        public string name { get; set; }
        public string botToken { get; set; }
        public string chatID { get; set; }
        public DateTime Date { get; set; }

        // Multimodal chatbot connection settings (optional per server)
        public string chatbotUrl { get; set; }
        public string chatbotAuthUser { get; set; }
        public string chatbotAuthPassword { get; set; }
    }
}
