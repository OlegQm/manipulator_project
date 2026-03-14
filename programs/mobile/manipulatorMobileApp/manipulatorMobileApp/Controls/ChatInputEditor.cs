using Xamarin.Forms;

namespace manipulatorMobileApp.Controls
{
    public class ChatInputEditor : Editor
    {
        public static readonly BindableProperty IsInternalScrollEnabledProperty =
            BindableProperty.Create(
                nameof(IsInternalScrollEnabled),
                typeof(bool),
                typeof(ChatInputEditor),
                false
            );

        public bool IsInternalScrollEnabled
        {
            get => (bool)GetValue(IsInternalScrollEnabledProperty);
            set => SetValue(IsInternalScrollEnabledProperty, value);
        }
    }
}
