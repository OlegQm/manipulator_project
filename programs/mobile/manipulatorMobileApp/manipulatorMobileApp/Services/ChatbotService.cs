using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;

namespace manipulatorMobileApp.Services
{
    /// <summary>
    /// Communicates with the multimodal chatbot REST API.
    /// Uses Basic authentication and the same stateless static pattern as TelegramService.
    ///
    /// Endpoints used:
    ///   POST   /api/v1/sessions           — create a session, returns session_id
    ///   POST   /api/v1/chat               — send a message, returns agent response
    ///   DELETE /api/v1/sessions/{id}      — delete a session
    /// </summary>
    public static class ChatbotService
    {
        // ──────────────────────────────────────────────────────────
        // Helpers
        // ──────────────────────────────────────────────────────────

        /// <summary>
        /// Builds the Authorization header value for HTTP Basic authentication.
        /// </summary>
        private static string BuildBasicAuth(string user, string pass)
        {
            string credentials = $"{user}:{pass}";
            string encoded = Convert.ToBase64String(Encoding.UTF8.GetBytes(credentials));
            return $"Basic {encoded}";
        }

        /// <summary>
        /// Creates a pre-configured HttpClient for a single request.
        /// A new instance per call matches the rest of the app (TelegramService pattern).
        /// </summary>
        private static HttpClient CreateClient(string user, string pass)
        {
            var client = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
            if (!string.IsNullOrWhiteSpace(user))
                client.DefaultRequestHeaders.Authorization =
                    AuthenticationHeaderValue.Parse(BuildBasicAuth(user, pass ?? string.Empty));
            return client;
        }

        // ──────────────────────────────────────────────────────────
        // Public API
        // ──────────────────────────────────────────────────────────

        /// <summary>
        /// Creates a new chat session on the server.
        /// </summary>
        /// <param name="baseUrl">Chatbot server base URL, e.g. "http://35.156.245.59"</param>
        /// <param name="authUser">Basic-auth username (may be empty)</param>
        /// <param name="authPass">Basic-auth password (may be empty)</param>
        /// <returns>session_id string on success; null on failure.</returns>
        public static async Task<string> CreateSessionAsync(
            string baseUrl,
            string authUser,
            string authPass)
        {
            using (var client = CreateClient(authUser, authPass))
            {
                string url = $"{baseUrl.TrimEnd('/')}/api/v1/sessions";
                var response = await client.PostAsync(url, new StringContent(string.Empty));
                response.EnsureSuccessStatusCode();
                string json = await response.Content.ReadAsStringAsync();
                var obj = JObject.Parse(json);
                return obj["session_id"]?.ToString();
            }
        }

        /// <summary>
        /// Sends a message (and, optionally, a base-64 encoded image) to the chatbot.
        /// The image should be provided only for the first message in a session; the
        /// server stores it and the agent can reference it for all subsequent messages.
        /// </summary>
        /// <param name="baseUrl">Chatbot server base URL.</param>
        /// <param name="sessionId">Session UUID returned by <see cref="CreateSessionAsync"/>.</param>
        /// <param name="message">User's text message or question.</param>
        /// <param name="imageBase64">Base-64 encoded JPEG/PNG, or null if not sending an image.</param>
        /// <param name="authUser">Basic-auth username.</param>
        /// <param name="authPass">Basic-auth password.</param>
        /// <returns>Agent response text on success; null on failure.</returns>
        public static async Task<string> SendMessageAsync(
            string baseUrl,
            string sessionId,
            string message,
            string imageBase64,
            string authUser,
            string authPass)
        {
            using (var client = CreateClient(authUser, authPass))
            {
                string url = $"{baseUrl.TrimEnd('/')}/api/v1/chat";

                var payload = new
                {
                    session_id = sessionId,
                    message = message,
                    image = imageBase64   // null means the field is omitted by JSON serialiser
                };

                string body = JsonConvert.SerializeObject(payload,
                    new JsonSerializerSettings { NullValueHandling = NullValueHandling.Ignore });

                var content = new StringContent(body, Encoding.UTF8, "application/json");
                var response = await client.PostAsync(url, content);
                response.EnsureSuccessStatusCode();

                string json = await response.Content.ReadAsStringAsync();
                var obj = JObject.Parse(json);
                return obj["response"]?.ToString();
            }
        }

        /// <summary>
        /// Deletes a chat session from the server.
        /// This is called best-effort from ChatPage.OnDisappearing; errors are silently swallowed.
        /// </summary>
        /// <param name="baseUrl">Chatbot server base URL.</param>
        /// <param name="sessionId">Session UUID to delete.</param>
        /// <param name="authUser">Basic-auth username.</param>
        /// <param name="authPass">Basic-auth password.</param>
        public static async Task DeleteSessionAsync(
            string baseUrl,
            string sessionId,
            string authUser,
            string authPass)
        {
            try
            {
                using (var client = CreateClient(authUser, authPass))
                {
                    string url = $"{baseUrl.TrimEnd('/')}/api/v1/sessions/{sessionId}";
                    await client.DeleteAsync(url);
                    // Response status is intentionally ignored — best-effort cleanup.
                }
            }
            catch
            {
                // Silently ignore — session TTL on server will clean up eventually.
            }
        }
    }
}
