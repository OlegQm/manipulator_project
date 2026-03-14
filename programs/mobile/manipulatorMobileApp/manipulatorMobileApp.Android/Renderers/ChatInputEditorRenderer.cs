using Android.Content;
using Android.Views;
using manipulatorMobileApp.Controls;
using manipulatorMobileApp.Droid.Renderers;
using Xamarin.Forms;
using Xamarin.Forms.Platform.Android;

[assembly: ExportRenderer(typeof(ChatInputEditor), typeof(ChatInputEditorRenderer))]

namespace manipulatorMobileApp.Droid.Renderers
{
    public class ChatInputEditorRenderer : EditorRenderer
    {
        public ChatInputEditorRenderer(Context context) : base(context)
        {
        }

        protected override void OnElementChanged(ElementChangedEventArgs<Editor> e)
        {
            base.OnElementChanged(e);
            UpdateScrollState();
        }

        protected override void OnElementPropertyChanged(object sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            base.OnElementPropertyChanged(sender, e);

            if (e.PropertyName == ChatInputEditor.IsInternalScrollEnabledProperty.PropertyName)
            {
                UpdateScrollState();
            }
        }

        private void UpdateScrollState()
        {
            if (Control == null || !(Element is ChatInputEditor editor))
                return;

            bool isScrollEnabled = editor.IsInternalScrollEnabled;
            Control.VerticalScrollBarEnabled = isScrollEnabled;
            Control.ScrollbarFadingEnabled = !isScrollEnabled;
            Control.OverScrollMode = isScrollEnabled
                ? OverScrollMode.IfContentScrolls
                : OverScrollMode.Never;
        }
    }
}
