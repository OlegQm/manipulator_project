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
    ///
    /// A single static HttpClient is reused across all requests to avoid socket
    /// exhaustion that would result from creating a new instance per call.
    /// Auth credentials are attached per-request via HttpRequestMessage so that
    /// different servers with different credentials can be used within the same session.
    /// </summary>
    public static class ChatbotService
    {
        // One instance for the lifetime of the app — safe to share across threads.
        private static readonly HttpClient _client = new HttpClient
        {
            Timeout = TimeSpan.FromSeconds(30)
        };

        // ──────────────────────────────────────────────────────────
        // Helpers
        // ──────────────────────────────────────────────────────────

        /// <summary>
        /// Creates an <see cref="AuthenticationHeaderValue"/> for HTTP Basic auth,
        /// or returns null when no username is provided.
        /// </summary>
        private static AuthenticationHeaderValue BuildBasicAuth(string user, string pass)
        {
            if (string.IsNullOrWhiteSpace(user))
                return null;

            string credentials = $"{user}:{pass ?? string.Empty}";
            string encoded = Convert.ToBase64String(Encoding.UTF8.GetBytes(credentials));
            return new AuthenticationHeaderValue("Basic", encoded);
        }

        /// <summary>
        /// Creates an <see cref="HttpRequestMessage"/> pre-configured with the correct
        /// per-request Authorization header and content.
        /// </summary>
        private static HttpRequestMessage BuildRequest(
            HttpMethod method,
            string url,
            string authUser,
            string authPass,
            HttpContent content = null)
        {
            var request = new HttpRequestMessage(method, url);
            request.Headers.Authorization = BuildBasicAuth(authUser, authPass);
            if (content != null)
                request.Content = content;
            return request;
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
            string url = $"{baseUrl.TrimEnd('/')}/api/v1/sessions";
            using (var request = BuildRequest(HttpMethod.Post, url, authUser, authPass,
                       new StringContent(string.Empty)))
            {
                var response = await _client.SendAsync(request);
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
            string url = $"{baseUrl.TrimEnd('/')}/api/v1/chat";

            var payload = new
            {
                session_id = sessionId,
                message = message,
                image = imageBase64   // null → field omitted by serialiser
            };

            string body = JsonConvert.SerializeObject(payload,
                new JsonSerializerSettings { NullValueHandling = NullValueHandling.Ignore });

            var jsonContent = new StringContent(body, Encoding.UTF8, "application/json");
            using (var request = BuildRequest(HttpMethod.Post, url, authUser, authPass, jsonContent))
            {
                var response = await _client.SendAsync(request);
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
                string url = $"{baseUrl.TrimEnd('/')}/api/v1/sessions/{sessionId}";
                using (var request = BuildRequest(HttpMethod.Delete, url, authUser, authPass))
                {
                    await _client.SendAsync(request);
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
