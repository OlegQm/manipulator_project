using System.ComponentModel;
using manipulatorMobileApp.Controls;
using manipulatorMobileApp.iOS.Renderers;
using Xamarin.Forms;
using Xamarin.Forms.Platform.iOS;

[assembly: ExportRenderer(typeof(ChatInputEditor), typeof(ChatInputEditorRenderer))]

namespace manipulatorMobileApp.iOS.Renderers
{
    public class ChatInputEditorRenderer : EditorRenderer
    {
        protected override void OnElementChanged(ElementChangedEventArgs<Editor> e)
        {
            base.OnElementChanged(e);
            UpdateScrollState();
        }

        protected override void OnElementPropertyChanged(object sender, PropertyChangedEventArgs e)
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

            Control.ScrollEnabled = editor.IsInternalScrollEnabled;
            Control.ShowsVerticalScrollIndicator = editor.IsInternalScrollEnabled;
            Control.Bounces = editor.IsInternalScrollEnabled;
        }
    }
}
