using System;
using System.Reflection;
using manipulatorMobileApp.Models;
using Xamarin.Essentials;
using Xamarin.Forms;

namespace manipulatorMobileApp.Views
{
    [QueryProperty(nameof(ItemId), nameof(ItemId))]
    public partial class NoteAddingPage : ContentPage
    {
        private bool ItemsRemovable = true;
        private bool IsFirstChange = true;
        private bool NoteTextFirstAdding = true;

        public string ItemId
        {
            set
            {
                LoadNote(value);
            }
        }

        public NoteAddingPage()
        {
            InitializeComponent();

            BindingContext = new Record();
        }

        private void Clear_Clicked(object sender, EventArgs e)
        {
            if (NoteEditor.Text != null)
            {
                NoteEditor.Text = null;
            }

            NoteEditor.IsVisible = true;
        }

        private async void LoadNote(string value)
        {
            try
            {
                int id = Convert.ToInt32(value);
                Record note = await App.RecordsDB.GetNoteAsync(id);
                BindingContext = note;
            }
            catch
            {
                await DisplayAlert("Something was wrong",
                                   "Please, try again",
                                   "OK");
            }
        }

        private async void OnSaveButton_Clicked(object sender, EventArgs e)
        {
            Record note = BindingContext as Record;
            note.Date = DateTime.Now;
            note.Title = TitleEditor.Text;
            if (!string.IsNullOrWhiteSpace(note.Text) || !string.IsNullOrWhiteSpace(note.Title))
            {
                await App.RecordsDB.SaveNoteAsync(note);
            }
            else
            {
                await App.RecordsDB.DeleteNoteAsync(note);
                DependencyService.Get<IToast>().Show("No text in the note");
            }
            await Navigation.PopAsync();
        }

        private async void OnDeleteButton_Clicked(object sender, EventArgs e)
        {
            bool result = await DisplayAlert("Remove Note",
                                             "Do you want to delete note?",
                                             "Delete",
                                             "Cancel");
            if (result)
            {
                Record note = BindingContext as Record;
                App.RecordsDB.DeleteNoteAsync(note).Wait();
                await Navigation.PopAsync();
            }
            else return;
        }

        private async void CopyButton_Clicked(object sender, EventArgs e)
        {
            await Clipboard.SetTextAsync(NoteEditor.Text);
            DependencyService.Get<IToast>().Show("Copied to clipboard");
        }
        
        private async void RefreshRecord(Record record)
        {
            if (string.IsNullOrWhiteSpace(TitleEditor.Text) && !string.IsNullOrWhiteSpace(NoteEditor.Text))
                if (NoteEditor.Text.Length > 45)
                {
                    record.Title = NoteEditor.Text.Substring(0, 42) + "...";
                }
                else
                {
                    record.Title = NoteEditor.Text;
                }
            if (!string.IsNullOrWhiteSpace(NoteEditor.Text) || !string.IsNullOrWhiteSpace(TitleEditor.Text))
            {
                await App.RecordsDB.SaveNoteAsync(record);
            }
        }

        private void NoteEditor_TextChanged(object sender, TextChangedEventArgs e)
        {
            Record note = BindingContext as Record;
            note.Date = DateTime.Now;
            RefreshRecord(note);

            if (ItemsRemovable && !IsFirstChange)
            {
                NoteTextFirstAdding = true;
            }
            IsFirstChange = false;
        }

        private void TitleEditor_TextChanged(object sender, TextChangedEventArgs e)
        {
            Record note = BindingContext as Record;
            note.Date = DateTime.Now;
            RefreshRecord(note);
        }

        private async void ScrollToEnd_Clicked(object sender, EventArgs e)
        {
            await Scroll.ScrollToAsync(DeleteButton, ScrollToPosition.End, true);
        }

        private async void ScrollToBegin_Clicked(object sender, EventArgs e)
        {
            await Scroll.ScrollToAsync(NoteEditor, ScrollToPosition.Start, true);
        }

        private void ReplaceDoubleSpaces_Clicked(object sender, EventArgs e)
        {
            while (NoteEditor.Text.IndexOf("  ") != -1)
            {
                NoteEditor.Text = NoteEditor.Text.Replace("  ", " ");
            }
        }

        private async void TextOptions_Clicked(object sender, EventArgs e)
        {
            var actionSheet = await DisplayActionSheet("Choose note text color",
                "Cancel", null, "Red", "Green", "Blue", "Aqua", "Fuchsia", "Yellow",
                "Gray", "Black", "White (default)");

            if (actionSheet == "Cancel" || actionSheet == null)
                return;
            else
            {
                if (actionSheet == "White (default)")
                {
                    actionSheet = "White";
                }
                NoteEditor.TextColor = (Color)typeof(Color).GetRuntimeField(actionSheet).GetValue(null);
            }
        }

        private async void BackgroundOptions_Clicked(object sender, EventArgs e)
        {
            var actionSheet = await DisplayActionSheet("Choose note background color",
                "Cancel", null, "Red", "Green", "Blue", "Aqua", "Fuchsia", "Yellow",
                "Gray", "Black (default)", "White");
            if (actionSheet == "Cancel" || actionSheet == null)
                return;
            else
            {
                if (actionSheet == "Black (default)")
                {
                    actionSheet = "Black";
                }
                BackgroundColor = (Color)typeof(Color).GetRuntimeField(actionSheet).GetValue(null);
            }
        }
    }
}