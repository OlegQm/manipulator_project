using Xamarin.Forms;

namespace manipulatorMobileApp.Models
{
    /// <summary>
    /// Represents a single message in the chatbot conversation.
    /// Instances are immutable once added to the Messages collection.
    /// </summary>
    public class ChatMessage
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

        /// <summary>"user" or "assistant"</summary>
        public string Role { get; set; }

        /// <summary>Text content of the message.</summary>
        public string Content { get; set; }

        // ──────────────────────────────────────────────────────────
        // Computed presentation properties (consumed by XAML bindings)
        // ──────────────────────────────────────────────────────────

        /// <summary>True when this message was authored by the local user.</summary>
        public bool IsUser => Role == "user";

        /// <summary>
        /// Bubble background: dark-blue for user, dark-gray for assistant.
        /// Both are readable on the black page background.
        /// </summary>
        public Color BubbleColor =>
            IsUser ? Color.FromHex("#1A73E8") : Color.FromHex("#3A3A3C");

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
    }
}
