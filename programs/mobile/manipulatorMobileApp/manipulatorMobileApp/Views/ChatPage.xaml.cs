using manipulatorMobileApp.Models;
using manipulatorMobileApp.Services;
using manipulatorMobileApp.Controls;
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
        private ChatMessage _pendingBotMessage;
        private double _defaultMessageEntryHeight;
        private double _maxMessageEntryHeight;
        private bool _isAdjustingMessageEntryHeight;

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
            {
                ChatMessage.SetScreenWidth(width);
                foreach (var message in Messages)
                {
                    message.RefreshLayoutProperties();
                }
            }

            if (height > 0)
            {
                UpdateMessageEntryHeightLimit(height);
            }
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
            SetComposerEnabled(false);
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
                SetComposerEnabled(true);
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
            ResetMessageEntryHeight();
            SetSendEnabled(false);

            // ── Add user bubble ─────────────────────────────────
            Messages.Add(new ChatMessage { Role = "user", Content = text });
            await ScrollToBottomAsync();

            // ── Add pending bot bubble ──────────────────────────
            _pendingBotMessage = new ChatMessage
            {
                Role = "assistant",
                Content = "Bot is thinking...",
                IsPending = true
            };
            Messages.Add(_pendingBotMessage);
            await ScrollToBottomAsync();

            // ── Call chatbot ────────────────────────────────────
            string imageBase64 = null;
            if (!_imageSent && _imageBytes != null)
            {
                imageBase64 = Convert.ToBase64String(_imageBytes);
                _imageSent = true;

                // Remove the header completely so it doesn't leave empty space at the top.
                messagesList.Header = null;
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

            // ── Replace pending bot bubble with final response ──
            if (_pendingBotMessage != null)
            {
                _pendingBotMessage.Content = botResponse;
                _pendingBotMessage.IsPending = false;
                _pendingBotMessage = null;
            }

            await ScrollToBottomAsync();

            // ── Restore UI ──────────────────────────────────────
            SetSendEnabled(true);
            messageEntry.Focus();
        }

        // ──────────────────────────────────────────────────────────
        // UI helpers
        // ──────────────────────────────────────────────────────────

        /// <summary>Enables or disables the entire composer area.</summary>
        private void SetComposerEnabled(bool enabled)
        {
            messageEntry.IsEnabled = enabled;
            sendBtn.IsEnabled = enabled;
        }

        /// <summary>Keeps typing enabled while a request is in flight, but prevents duplicate sends.</summary>
        private void SetSendEnabled(bool enabled)
        {
            sendBtn.IsEnabled = enabled;
        }

        private void MessageEntry_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (_isAdjustingMessageEntryHeight)
                return;

            if (string.IsNullOrEmpty(e.NewTextValue))
            {
                ResetMessageEntryHeight();
                return;
            }

            bool textShrank = (e.OldTextValue?.Length ?? 0) > (e.NewTextValue?.Length ?? 0);

            // Only release the clamp when the text shrinks. Releasing it on every
            // keystroke causes repeated re-measure loops once the editor is already
            // capped, which is what makes long runs of blank lines feel frozen.
            if (messageEntry.HeightRequest > 0 && textShrank)
                messageEntry.HeightRequest = -1;
        }

        private void MessageEntry_SizeChanged(object sender, EventArgs e)
        {
            if (_isAdjustingMessageEntryHeight || messageEntry.Height <= 0)
                return;

            if (_defaultMessageEntryHeight <= 0 || string.IsNullOrEmpty(messageEntry.Text))
            {
                _defaultMessageEntryHeight = messageEntry.Height;
            }

            ApplyMessageEntryHeightLimit();
        }

        private void UpdateMessageEntryHeightLimit(double availablePageHeight)
        {
            double relativeMaxHeight = availablePageHeight * 0.28;
            double minimumAllowedHeight = _defaultMessageEntryHeight > 0 ? _defaultMessageEntryHeight : 72;
            _maxMessageEntryHeight = Math.Max(minimumAllowedHeight, Math.Min(relativeMaxHeight, 220));
            ApplyMessageEntryHeightLimit();
        }

        private void ApplyMessageEntryHeightLimit()
        {
            if (_isAdjustingMessageEntryHeight || _maxMessageEntryHeight <= 0)
                return;

            _isAdjustingMessageEntryHeight = true;
            try
            {
                if (messageEntry.Height > _maxMessageEntryHeight)
                {
                    messageEntry.HeightRequest = _maxMessageEntryHeight;
                    SetMessageEntryScrollEnabled(true);
                }
                else if (messageEntry.HeightRequest > 0)
                {
                    messageEntry.HeightRequest = -1;
                    SetMessageEntryScrollEnabled(false);
                }
                else
                {
                    SetMessageEntryScrollEnabled(false);
                }
            }
            finally
            {
                _isAdjustingMessageEntryHeight = false;
            }
        }

        private void ResetMessageEntryHeight()
        {
            if (messageEntry == null)
                return;

            messageEntry.HeightRequest = -1;
            SetMessageEntryScrollEnabled(false);
        }

        private void SetMessageEntryScrollEnabled(bool enabled)
        {
            if (messageEntry is ChatInputEditor chatInputEditor)
            {
                chatInputEditor.IsInternalScrollEnabled = enabled;
            }
        }

        /// <summary>
        /// Scrolls the messages list to the very last item.
        /// </summary>
        private async Task ScrollToBottomAsync()
        {
            try
            {
                if (Messages.Count > 0)
                {
                    await Task.Delay(60);
                    messagesList.ScrollTo(Messages[Messages.Count - 1],
                        position: ScrollToPosition.End, animate: false);
                }
            }
            catch
            {
            }
        }
    }
}
