using manipulatorMobileApp.Models;
using manipulatorMobileApp.Services;
using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using Xamarin.Essentials;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace manipulatorMobileApp.Views
{
    /// <summary>
    /// Full-page chat UI for the multimodal chatbot.
    ///
    /// Lifecycle:
    ///   Open  → creates a server-side session (async in OnAppearing)
    ///   Close → deletes the session (fire-and-forget in OnDisappearing)
    ///
    /// Image handling:
    ///   The screenshot received from Telegram is attached (as base-64) to the
    ///   FIRST message the user sends.  All subsequent messages are text-only;
    ///   the server keeps the image in the session context and the agent can
    ///   reference it via the `analyze_image` tool.
    /// </summary>
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class ChatPage : ContentPage
    {
        // ──────────────────────────────────────────────────────────
        // Fields
        // ──────────────────────────────────────────────────────────

        private readonly byte[] _imageBytes;
        private readonly string _chatbotUrl;
        private readonly string _authUser;
        private readonly string _authPass;

        private string _sessionId;

        /// <summary>True once the image has been included in a chat request.</summary>
        private bool _imageSent;

        /// <summary>Bound to the CollectionView ItemsSource.</summary>
        public ObservableCollection<ChatMessage> Messages { get; } =
            new ObservableCollection<ChatMessage>();

        // ──────────────────────────────────────────────────────────
        // Constructor
        // ──────────────────────────────────────────────────────────

        /// <summary>
        /// Creates a new ChatPage.
        /// </summary>
        /// <param name="imageBytes">Raw JPEG/PNG bytes of the Telegram screenshot.</param>
        /// <param name="chatbotUrl">Base URL of the chatbot server.</param>
        /// <param name="authUser">Basic-auth username.</param>
        /// <param name="authPass">Basic-auth password.</param>
        public ChatPage(byte[] imageBytes, string chatbotUrl, string authUser, string authPass)
        {
            InitializeComponent();
            _imageBytes = imageBytes;
            _chatbotUrl = chatbotUrl;
            _authUser = authUser ?? string.Empty;
            _authPass = authPass ?? string.Empty;

            messagesList.ItemsSource = Messages;
            BindingContext = this;
        }

        // ──────────────────────────────────────────────────────────
        // Page lifecycle
        // ──────────────────────────────────────────────────────────

        /// <inheritdoc/>
        protected override async void OnAppearing()
        {
            base.OnAppearing();

            // Seed the responsive margin with the current page width.
            // OnSizeAllocated will refresh this again once layout is measured.
            ChatMessage.SetScreenWidth(Width > 0 ? Width : DeviceDisplay.MainDisplayInfo.Width);

            await CreateSessionAsync();
        }

        /// <inheritdoc/>
        protected override void OnSizeAllocated(double width, double height)
        {
            base.OnSizeAllocated(width, height);

            // Re-seed on every orientation change so BubbleMargin stays correct.
            if (width > 0)
                ChatMessage.SetScreenWidth(width);
        }

        /// <summary>
        /// Deletes the server-side session when the page is removed from the navigation stack
        /// (back button, swipe-back gesture) or when the app is suspended.
        /// Fire-and-forget — errors are handled inside <see cref="ChatbotService.DeleteSessionAsync"/>.
        /// </summary>
        protected override void OnDisappearing()
        {
            base.OnDisappearing();

            if (!string.IsNullOrEmpty(_sessionId))
            {
                // Fire-and-forget; the task runs independently of navigation.
                _ = ChatbotService.DeleteSessionAsync(_chatbotUrl, _sessionId, _authUser, _authPass);
                _sessionId = null;
            }
        }

        // ──────────────────────────────────────────────────────────
        // Session management
        // ──────────────────────────────────────────────────────────

        /// <summary>
        /// Creates a new chatbot session and stores the returned session_id.
        /// On failure, shows a toast and pops back to ScreenshotPage.
        /// </summary>
        private async Task CreateSessionAsync()
        {
            SetInputEnabled(false);
            try
            {
                _sessionId = await ChatbotService.CreateSessionAsync(_chatbotUrl, _authUser, _authPass);
                if (string.IsNullOrEmpty(_sessionId))
                    throw new Exception("Server returned an empty session ID.");
            }
            catch (Exception ex)
            {
                DependencyService.Get<IToast>().Show($"Failed to start chat session: {ex.Message}");
                await Navigation.PopAsync();
                return;
            }
            finally
            {
                SetInputEnabled(true);
            }
        }

        // ──────────────────────────────────────────────────────────
        // Send logic
        // ──────────────────────────────────────────────────────────

        /// <summary>
        /// Handles the Send button tap.
        /// Appends the user bubble, calls the chatbot, then appends the bot bubble.
        /// The screenshot is attached only to the very first message.
        /// </summary>
        private async void SendBtn_Clicked(object sender, EventArgs e)
        {
            string text = messageEntry.Text?.Trim();
            if (string.IsNullOrEmpty(text))
                return;

            // Guard: session must exist (created in OnAppearing)
            if (string.IsNullOrEmpty(_sessionId))
            {
                DependencyService.Get<IToast>().Show("No active session. Please reopen the chat.");
                return;
            }

            // ── Prepare UI ──────────────────────────────────────
            messageEntry.Text = string.Empty;
            SetInputEnabled(false);
            ShowLoading(true);

            // ── Add user bubble ─────────────────────────────────
            Messages.Add(new ChatMessage { Role = "user", Content = text });
            await ScrollToBottomAsync();

            // ── Call chatbot ────────────────────────────────────
            string imageBase64 = null;
            if (!_imageSent && _imageBytes != null)
            {
                imageBase64 = Convert.ToBase64String(_imageBytes);
                _imageSent = true;

                // Hide the "image will be attached" hint after first send
                imageHintFrame.IsVisible = false;
            }

            string botResponse;
            try
            {
                botResponse = await ChatbotService.SendMessageAsync(
                    _chatbotUrl,
                    _sessionId,
                    text,
                    imageBase64,
                    _authUser,
                    _authPass);

                if (string.IsNullOrEmpty(botResponse))
                    botResponse = "(empty response)";
            }
            catch (Exception ex)
            {
                botResponse = $"Error: {ex.Message}";
                // If image was supposed to be sent but failed, reset so the next
                // attempt can try again.
                if (imageBase64 != null)
                    _imageSent = false;
            }

            // ── Add bot bubble ──────────────────────────────────
            Messages.Add(new ChatMessage { Role = "assistant", Content = botResponse });
            await ScrollToBottomAsync();

            // ── Restore UI ──────────────────────────────────────
            ShowLoading(false);
            SetInputEnabled(true);
            messageEntry.Focus();
        }

        // ──────────────────────────────────────────────────────────
        // UI helpers
        // ──────────────────────────────────────────────────────────

        /// <summary>Enables or disables the message input and send button.</summary>
        private void SetInputEnabled(bool enabled)
        {
            messageEntry.IsEnabled = enabled;
            sendBtn.IsEnabled = enabled;
        }

        /// <summary>Shows or hides the "bot is thinking" indicator row.</summary>
        private void ShowLoading(bool visible)
        {
            loadingRow.IsVisible = visible;
            loadingIndicator.IsRunning = visible;
        }

        /// <summary>
        /// Scrolls the messages list to the very last item.
        /// Wrapped in a try/catch because CollectionView.ScrollTo can silently
        /// fail on some Android API levels when the list is empty.
        /// </summary>
        private async Task ScrollToBottomAsync()
        {
            try
            {
                if (Messages.Count > 0)
                {
                    // Small delay lets the layout engine measure the new cell first.
                    await Task.Delay(80);
                    messagesList.ScrollTo(Messages[Messages.Count - 1],
                        position: ScrollToPosition.End, animate: true);

                    // Also scroll the outer ScrollView to the bottom.
                    await messagesScrollView.ScrollToAsync(0, messagesScrollView.ContentSize.Height, false);
                }
            }
            catch
            {
                // Non-critical — user can scroll manually.
            }
        }
    }
}
