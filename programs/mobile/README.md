# manipulatorMobileApp

Welcome to **manipulatorMobileApp**, a cross-platform mobile application built with Xamarin.Forms for Android and iOS devices.

---

## 🚀 Features

- **Cross-Platform**: Single codebase for both Android and iOS
- **Rich UI**: Leverages Xamarin.Forms controls for a native look and feel
- **Easy Installation**: Get up and running in minutes
- **Local Data**: Simple record/server persistence via SQLite helpers
- **Platform Hooks**: Toasts and file helpers implemented per platform

---

## 📋 Prerequisites

- **Visual Studio Community 2022**
  - Ensure you have the **Xamarin.Forms** workload installed
- **Android SDK** (installed via Visual Studio installer)
- **Xcode** (for iOS builds on macOS)
- .NET tooling that ships with Visual Studio for Xamarin development

---

## 🗂️ Solution structure

`manipulatorMobileApp.sln`

- `manipulatorMobileApp/` — shared Xamarin.Forms project
  - `App.xaml`, `App.xaml.cs` — app bootstrap and navigation root
  - `MainPage.xaml(.cs)` — entry page
  - `Views/`
    - `ModeSelectionPage` — chooses operating mode
    - `NotesPage`, `NoteAddingPage` — notes list and creation flow
    - `ScreenshotPage` — screen capture view
  - `Data/`
    - `RecordsDB.cs` — SQLite helper for `Record` entities
    - `ServersDB.cs` — SQLite helper for `Server` entities
  - `Models/`
    - `Record.cs`, `Server.cs` — model definitions
  - `IToast.cs`, `IFileHelper.cs` — dependency-service contracts implemented per platform
- `manipulatorMobileApp.Android/`
  - `MainActivity.cs` — Android entry point
  - `FileHelperDroid.cs`, `ToastDroid.cs` — Android-specific DI implementations
  - `Resources/` — icons, styles, manifests, assets
- `manipulatorMobileApp.iOS/`
  - `AppDelegate.cs`, `Main.cs` — iOS entry points
  - `FileHelperiOS.cs`, `ToastIOS.cs` — iOS-specific DI implementations
  - `Assets.xcassets/`, `Resources/`, `Info.plist`, entitlements

---

## ⚙️ App flow & logic

- **Startup** (`App.xaml.cs`)
  - Initializes dark theme and navigation root (`NavigationPage -> MainPage`).
  - Lazy-creates SQLite databases for notes (`RecordsDB`) and servers (`ServersDB`) in `LocalApplicationData`.
  - Loads a list of standard object names from `names.names` via `IFileHelper`; exposes it as `GlobalWordsArray`.
  - On failure to load words, shows a toast via platform `IToast`.

- **Main screen (servers)** (`MainPage`)
  - Editors for bot name/token/chat ID; saves to `ServersDB`.
  - Lists saved servers with swipe-to-delete and “Delete All”.
  - On selection, populates editors from the chosen server.
  - “Start”/toolbar “Start” opens **ModeSelectionPage** with the current token and chat ID (both required; validation shows toast on missing values).

- **Mode selection** (`ModeSelectionPage`)
  - Two branches: **NotesPage** (“OBJECTS LIST”) and **ScreenshotPage** (“POSSIBLE OBJECTS”), both receive the bot token/chat ID.

- **Notes list & actions** (`NotesPage`)
  - Loads/saves `Record` entries from `RecordsDB`; search bar filters locally by title.
  - “Add” opens `NoteAddingPage` for create/edit; swipe-to-delete removes a record; “Delete All” drops and recreates the table.
  - **Edit mode** toggle: tap navigates to `NoteAddingPage` for the selected record; otherwise tap sends `/selection <Title>` to the Telegram bot (HTTP POST).
  - **Default Buttons**: reloads `GlobalWordsArray` into the DB after confirmation, replacing existing entries.
  - **Filter by prompt**: sends a text prompt with the known object list to OpenAI (`gpt-4o`), splits the response into keywords, filters records by those keywords.
  - **Filter by photo**: captures a photo (permissions via `Xamarin.Essentials`), resizes with SkiaSharp, calls OpenAI vision (`gpt-4o-mini`) with the image and known object list, then filters records by returned keywords.
  - **OFF/ON searching**: toggles `/searching 0/1` via Telegram; **Turn on/off flashlight** sends `/flashlight ON/OFF`.

- **Add/Edit note** (`NoteAddingPage`)
  - Binds a `Record`; loads by ID when navigated from edit mode.
  - Saves or updates on “Save”; deletes on “Delete”; auto-updates DB on text/title change to keep timestamps in sync.
  - Toolbar utilities: clear text, replace double spaces, scroll to top/bottom, change text/background colors.
  - Auto-generates a title from the first 45 chars of the description if the title is empty.

- **Screenshot & available objects** (`ScreenshotPage`)
  - “SCREENSHOT” sends `/get_image` to the Telegram bot, then polls `getUpdates` to fetch the latest photo and caption; displays the image and splits the caption into available object items.
  - Selecting an item sends `/selection <word>` to the bot.
  - Toolbar toggle `/searching 0/1` similar to NotesPage.

---

## 🗄️ Data & services

- **SQLite**: `RecordsDB` and `ServersDB` wrap SQLiteAsyncConnection; create tables on first use; provide CRUD plus helpers (last server, filter records by keywords, drop/reset).
- **DependencyService contracts**:
  - `IFileHelper` — resolve platform file paths (used to load `names.names`, `api_key.txt`).
  - `IToast` — platform toast notifications.
- **External APIs**:
  - Telegram Bot API (`sendMessage`, `getUpdates`, `getFile`) for bot control, screenshot retrieval, and selection commands.
  - OpenAI Chat (`gpt-4o`) for text-based filtering; OpenAI vision (`gpt-4o-mini`) for image-based object extraction.
  - Network access checked via `Xamarin.Essentials.Connectivity`; camera via `MediaPicker` with runtime permissions.

---

## 🔧 Build & run

2. **Open in Visual Studio 2022**
   - Launch Visual Studio Community 2022
   - Select **File → Open → Project/Solution**
   - Navigate to `manipulatorMobileApp/ManipulatorMobileApp.sln` and open it

3. **Restore NuGet packages**
   - In **Solution Explorer**, right-click the solution and choose **Restore NuGet Packages**

4. **Deploy to Device or Emulator**
   - Set the **Startup Project** to your desired platform (Android or iOS)
   - Choose an emulator or connected device
   - Press **F5** to build and run

---

## 💡 Usage

- Explore the intuitive UI
- Test on both Android and iOS simulators/emulators
- Customize styles and controls in `App.xaml`
- Update data access or models in `Data/` and `Models/` as your schema evolves
- Extend platform-specific behavior by adding dependency-service implementations in the platform projects
