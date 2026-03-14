using System.ComponentModel;
using System.Runtime.CompilerServices;
using Xamarin.Forms;

namespace manipulatorMobileApp.Models
{
    /// <summary>
    /// Represents a single message in the chatbot conversation.
    /// </summary>
    public class ChatMessage : INotifyPropertyChanged
    {
        // ──────────────────────────────────────────────────────────
        // Static screen-width cache used to compute responsive margins.
        // Call SetScreenWidth from ChatPage.OnAppearing / OnSizeAllocated.
        // ──────────────────────────────────────────────────────────
        private static double _screenWidth = 360; // sensible default

        /// <summary>Updates the cached screen width used for bubble margins.</summary>
        public static void SetScreenWidth(double width)
        {
            if (width > 0)
                _screenWidth = width;
        }

        // ──────────────────────────────────────────────────────────
        // Core data
        // ──────────────────────────────────────────────────────────

        private string _role;
        private string _content;
        private bool _isPending;

        public event PropertyChangedEventHandler PropertyChanged;

        /// <summary>"user" or "assistant"</summary>
        public string Role
        {
            get => _role;
            set
            {
                if (_role == value)
                    return;

                _role = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(IsUser));
                OnPropertyChanged(nameof(BubbleColor));
                OnPropertyChanged(nameof(BubbleAlignment));
                OnPropertyChanged(nameof(BubbleMargin));
            }
        }

        /// <summary>Text content of the message.</summary>
        public string Content
        {
            get => _content;
            set
            {
                if (_content == value)
                    return;

                _content = value;
                OnPropertyChanged();
            }
        }

        /// <summary>True while this message is a temporary "thinking" placeholder.</summary>
        public bool IsPending
        {
            get => _isPending;
            set
            {
                if (_isPending == value)
                    return;

                _isPending = value;
                OnPropertyChanged();
                OnPropertyChanged(nameof(IsPendingVisible));
                OnPropertyChanged(nameof(IsMessageVisible));
                OnPropertyChanged(nameof(BubbleColor));
            }
        }

        // ──────────────────────────────────────────────────────────
        // Computed presentation properties (consumed by XAML bindings)
        // ──────────────────────────────────────────────────────────

        /// <summary>True when this message was authored by the local user.</summary>
        public bool IsUser => Role == "user";

        /// <summary>Show spinner row instead of plain message text.</summary>
        public bool IsPendingVisible => IsPending;

        /// <summary>Show the regular message text once the pending state is cleared.</summary>
        public bool IsMessageVisible => !IsPending;

        /// <summary>
        /// Bubble background: dark-blue for user, dark-gray for assistant.
        /// Both are readable on the black page background.
        /// </summary>
        public Color BubbleColor =>
            IsUser
                ? Color.FromHex("#2A78E4")
                : IsPending ? Color.FromHex("#2C3442") : Color.FromHex("#3A3A3C");

        /// <summary>
        /// Align user bubbles to the right edge, assistant bubbles to the left.
        /// </summary>
        public LayoutOptions BubbleAlignment =>
            IsUser ? LayoutOptions.End : LayoutOptions.Start;

        /// <summary>
        /// Push the bubble 25% away from the far edge so it never spans
        /// the full width. Works in both portrait and landscape because it
        /// recomputes from the current <see cref="_screenWidth"/>.
        /// User  → left push = 25 % screen width, right push = 4 dp
        /// Bot   → left push = 4 dp, right push = 25 % screen width
        /// </summary>
        public Thickness BubbleMargin
        {
            get
            {
                double push = _screenWidth * 0.25;
                return IsUser
                    ? new Thickness(push, 2, 4, 2)
                    : new Thickness(4, 2, push, 2);
            }
        }

        /// <summary>Refreshes width-dependent bindings after screen size changes.</summary>
        public void RefreshLayoutProperties()
        {
            OnPropertyChanged(nameof(BubbleMargin));
            OnPropertyChanged(nameof(BubbleAlignment));
        }

        private void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
