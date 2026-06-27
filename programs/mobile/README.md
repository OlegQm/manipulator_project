# manipulatorMobileApp

`manipulatorMobileApp` is a Xamarin.Forms mobile application used to control the
robotic arm prototype, request camera screenshots through Telegram, select tracked
objects, and optionally discuss the latest image with a multimodal chatbot backend.

---

## Features

- Stores Telegram server/bot settings locally with SQLite.
- Sends control commands to the robotic arm through Telegram Bot API.
- Requests the current camera image and displays the returned object list.
- Sends `/selection`, `/searching`, and `/flashlight` commands.
- Maintains a local object database and supports manual, text-prompt, and photo-based filtering.
- Opens a chat page that sends the displayed image to the chatbot backend and keeps a server-side session for follow-up questions.

---

## Prerequisites

- **Visual Studio Community 2022**
  - Ensure you have the **Xamarin.Forms** workload installed
- **Android SDK** (installed via Visual Studio installer)
- **Xcode** (for iOS builds on macOS)
- .NET tooling that ships with Visual Studio for Xamarin development
- Telegram bot token and chat/channel ID for communication with the robotic arm
- Optional chatbot server URL and Basic Auth credentials
- `api_key.txt` in the application data path when OpenAI-based object-list filtering is used

---

## Solution structure

`manipulatorMobileApp.sln`

- `manipulatorMobileApp/` — shared Xamarin.Forms project
  - `App.xaml`, `App.xaml.cs` — app bootstrap and navigation root
  - `MainPage.xaml(.cs)` — entry page
  - `Views/`
    - `ModeSelectionPage` — chooses operating mode
    - `NotesPage`, `NoteAddingPage` — notes list and creation flow
    - `ScreenshotPage` — camera screenshot, available objects, and chatbot entry
    - `ChatPage` — image-based chatbot conversation
  - `Services/`
    - `TelegramService.cs` — Telegram Bot API communication
    - `ChatbotService.cs` — REST client for the multimodal chatbot backend
  - `Helpers/`
    - `SearchingToggleHelper.cs`, `FlashlightToggleHelper.cs` — shared Telegram command toggles
    - `SafeAreaHelper.cs` — platform-safe layout helper
  - `Controls/`
    - `ChatInputEditor.cs` — custom chat input editor
  - `Data/`
    - `RecordsDB.cs` — SQLite helper for `Record` entities
    - `ServersDB.cs` — SQLite helper for `Server` entities
  - `Models/`
    - `Record.cs`, `Server.cs`, `ChatMessage.cs` — model definitions
  - `IToast.cs`, `IFileHelper.cs` — dependency-service contracts implemented per platform
- `manipulatorMobileApp.Android/`
  - `MainActivity.cs` — Android entry point
  - `FileHelperDroid.cs`, `ToastDroid.cs` — Android-specific DI implementations
  - `Renderers/ChatInputEditorRenderer.cs` — Android renderer for the chat input
  - `Resources/` — icons, styles, manifests, assets
- `manipulatorMobileApp.iOS/`
  - `AppDelegate.cs`, `Main.cs` — iOS entry points
  - `FileHelperiOS.cs`, `ToastIOS.cs` — iOS-specific DI implementations
  - `Assets.xcassets/`, `Resources/`, `Info.plist`, entitlements

---

## App flow and logic

- **Startup** (`App.xaml.cs`)
  - Initializes dark theme and navigation root (`NavigationPage -> MainPage`).
  - Lazy-creates SQLite databases for notes (`RecordsDB`) and servers (`ServersDB`) in `LocalApplicationData`.
  - Loads a list of standard object names from `names.names` via `IFileHelper`; exposes it as `GlobalWordsArray`.
  - On failure to load words, shows a toast via platform `IToast`.

- **Main screen (servers)** (`MainPage`)
  - Editors for server name, bot token, chat ID, optional chatbot URL, and optional Basic Auth credentials; saves to `ServersDB`.
  - Lists saved servers with swipe-to-delete and “Delete All”.
  - On selection, populates editors from the chosen server.
  - “Start”/toolbar “Start” opens **ModeSelectionPage** with the current Telegram settings and optional chatbot settings. Server name, bot token, and chat ID are required.

- **Mode selection** (`ModeSelectionPage`)
  - Two branches: **NotesPage** (“OBJECTS LIST”) and **ScreenshotPage** (“POSSIBLE OBJECTS”).
  - `NotesPage` receives the Telegram token/chat ID.
  - `ScreenshotPage` also receives the chatbot URL and authentication values.

- **Notes list & actions** (`NotesPage`)
  - Loads/saves `Record` entries from `RecordsDB`; search bar filters locally by title.
  - “Add” opens `NoteAddingPage` for create/edit; swipe-to-delete removes a record; “Delete All” drops and recreates the table.
  - **Edit mode** toggle: tap navigates to `NoteAddingPage` for the selected record; otherwise tap sends `/selection <Title>` to the Telegram bot (HTTP POST).
  - **Default Buttons**: reloads `GlobalWordsArray` into the DB after confirmation, replacing existing entries.
  - **Filter by prompt**: sends a text prompt with the known object list to OpenAI (`gpt-4o-mini`), splits the response into keywords, filters records by those keywords.
  - **Filter by photo**: captures a photo (permissions via `Xamarin.Essentials`), resizes with SkiaSharp, calls OpenAI vision (`gpt-4o-mini`) with the image and known object list, then filters records by returned keywords.
  - **OFF/ON searching**: toggles `/searching 0/1` via Telegram; **Turn on/off flashlight** sends `/flashlight ON/OFF`.

- **Add/Edit note** (`NoteAddingPage`)
  - Binds a `Record`; loads by ID when navigated from edit mode.
  - Saves or updates on “Save”; deletes on “Delete”; auto-updates DB on text/title change to keep timestamps in sync.
  - Toolbar utilities: clear text, replace double spaces, scroll to top/bottom, change text/background colors.
  - Auto-generates a title from the first 45 chars of the description if the title is empty.

- **Screenshot & available objects** (`ScreenshotPage`)
  - Initially displays a built-in placeholder image and enables the Chat toolbar item, so the chatbot can be tested even before a real screenshot is received.
  - “SCREENSHOT” sends `/get_image` to the Telegram bot, then polls `getUpdates` to fetch the latest photo and caption; displays the image and splits the caption into available object items.
  - Selecting an item sends `/selection <word>` to the bot.
  - Toolbar toggles send `/searching 0/1` and `/flashlight ON/OFF`.
  - The Chat toolbar item opens `ChatPage` with the currently displayed image. If no Telegram screenshot has been fetched yet, the placeholder image is used.

- **Chatbot conversation** (`ChatPage`)
  - Creates a server-side chatbot session with `POST /api/v1/sessions` when the page opens.
  - Sends the currently displayed image as Base64 only with the first chat message.
  - Sends later messages as text-only; the backend keeps the image in the same session and can reuse it for follow-up questions.
  - Deletes the session with `DELETE /api/v1/sessions/{session_id}` when the chat page disappears. Errors during deletion are intentionally ignored because server cleanup also handles expired sessions.

---

## Data and services

- **SQLite**: `RecordsDB` and `ServersDB` wrap SQLiteAsyncConnection; create tables on first use; provide CRUD plus helpers (last server, filter records by keywords, drop/reset).
  `Server` records also store optional chatbot URL, username, and password.
- **DependencyService contracts**:
  - `IFileHelper` — resolve platform file paths (used to load `names.names`, `api_key.txt`).
  - `IToast` — platform toast notifications.
- **External APIs**:
  - Telegram Bot API (`sendMessage`, `getUpdates`, `getFile`) for bot control, screenshot retrieval, and selection commands.
  - OpenAI Chat/Vision (`gpt-4o-mini`) for object-list filtering in `NotesPage`.
  - Multimodal chatbot REST API (`/api/v1/sessions`, `/api/v1/chat`, `/api/v1/sessions/{id}`) for image-based conversation in `ChatPage`.
  - Network access checked via `Xamarin.Essentials.Connectivity`; camera via `MediaPicker` with runtime permissions.

---

## Build and run

1. **Open in Visual Studio 2022**
   - Launch Visual Studio Community 2022
   - Select **File → Open → Project/Solution**
   - Navigate to `manipulatorMobileApp/manipulatorMobileApp.sln` and open it

2. **Restore NuGet packages**
   - In **Solution Explorer**, right-click the solution and choose **Restore NuGet Packages**

3. **Configure runtime values**
   - Add a Telegram bot token and chat ID on the main screen.
   - Add chatbot URL and Basic Auth values only if `ChatPage` should call the multimodal chatbot backend.
   - Add `api_key.txt` only if prompt/photo filtering in `NotesPage` should use OpenAI.

4. **Deploy to device or emulator**
   - Set the **Startup Project** to your desired platform (Android or iOS)
   - Choose an emulator or connected device
   - Press **F5** to build and run

---

## Usage notes

- Use **OBJECTS LIST** when selecting from the local object database.
- Use **POSSIBLE OBJECTS** when requesting a live camera screenshot and selecting one of the detected objects.
- Open **Chat** from the screenshot screen to ask questions about the currently displayed image.
- The first chatbot message includes the image; follow-up messages rely on the same server-side session.
