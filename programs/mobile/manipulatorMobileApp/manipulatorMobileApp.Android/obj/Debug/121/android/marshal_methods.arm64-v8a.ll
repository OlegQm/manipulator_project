; ModuleID = 'obj\Debug\121\android\marshal_methods.arm64-v8a.ll'
source_filename = "obj\Debug\121\android\marshal_methods.arm64-v8a.ll"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128"
target triple = "aarch64-unknown-linux-android"


%struct.MonoImage = type opaque

%struct.MonoClass = type opaque

%struct.MarshalMethodsManagedClass = type {
	i32,; uint32_t token
	%struct.MonoClass*; MonoClass* klass
}

%struct.MarshalMethodName = type {
	i64,; uint64_t id
	i8*; char* name
}

%class._JNIEnv = type opaque

%class._jobject = type {
	i8; uint8_t b
}

%class._jclass = type {
	i8; uint8_t b
}

%class._jstring = type {
	i8; uint8_t b
}

%class._jthrowable = type {
	i8; uint8_t b
}

%class._jarray = type {
	i8; uint8_t b
}

%class._jobjectArray = type {
	i8; uint8_t b
}

%class._jbooleanArray = type {
	i8; uint8_t b
}

%class._jbyteArray = type {
	i8; uint8_t b
}

%class._jcharArray = type {
	i8; uint8_t b
}

%class._jshortArray = type {
	i8; uint8_t b
}

%class._jintArray = type {
	i8; uint8_t b
}

%class._jlongArray = type {
	i8; uint8_t b
}

%class._jfloatArray = type {
	i8; uint8_t b
}

%class._jdoubleArray = type {
	i8; uint8_t b
}

; assembly_image_cache
@assembly_image_cache = local_unnamed_addr global [0 x %struct.MonoImage*] zeroinitializer, align 8
; Each entry maps hash of an assembly name to an index into the `assembly_image_cache` array
@assembly_image_cache_hashes = local_unnamed_addr constant [192 x i64] [
	i64 120698629574877762, ; 0: Mono.Android => 0x1accec39cafe242 => 8
	i64 210515253464952879, ; 1: Xamarin.AndroidX.Collection.dll => 0x2ebe681f694702f => 45
	i64 232391251801502327, ; 2: Xamarin.AndroidX.SavedState.dll => 0x3399e9cbc897277 => 69
	i64 295915112840604065, ; 3: Xamarin.AndroidX.SlidingPaneLayout => 0x41b4d3a3088a9a1 => 70
	i64 634308326490598313, ; 4: Xamarin.AndroidX.Lifecycle.Runtime.dll => 0x8cd840fee8b6ba9 => 60
	i64 702024105029695270, ; 5: System.Drawing.Common => 0x9be17343c0e7726 => 88
	i64 720058930071658100, ; 6: Xamarin.AndroidX.Legacy.Support.Core.UI => 0x9fe29c82844de74 => 54
	i64 870603111519317375, ; 7: SQLitePCLRaw.lib.e_sqlite3.android => 0xc1500ead2756d7f => 17
	i64 872800313462103108, ; 8: Xamarin.AndroidX.DrawerLayout => 0xc1ccf42c3c21c44 => 51
	i64 940822596282819491, ; 9: System.Transactions => 0xd0e792aa81923a3 => 86
	i64 996343623809489702, ; 10: Xamarin.Forms.Platform => 0xdd3b93f3b63db26 => 81
	i64 1000557547492888992, ; 11: Mono.Security.dll => 0xde2b1c9cba651a0 => 95
	i64 1120440138749646132, ; 12: Xamarin.Google.Android.Material.dll => 0xf8c9a5eae431534 => 83
	i64 1301485588176585670, ; 13: SQLitePCLRaw.core => 0x120fce3f338e43c6 => 16
	i64 1315114680217950157, ; 14: Xamarin.AndroidX.Arch.Core.Common.dll => 0x124039d5794ad7cd => 40
	i64 1425944114962822056, ; 15: System.Runtime.Serialization.dll => 0x13c9f89e19eaf3a8 => 3
	i64 1518315023656898250, ; 16: SQLitePCLRaw.provider.e_sqlite3 => 0x151223783a354eca => 18
	i64 1624659445732251991, ; 17: Xamarin.AndroidX.AppCompat.AppCompatResources.dll => 0x168bf32877da9957 => 38
	i64 1628611045998245443, ; 18: Xamarin.AndroidX.Lifecycle.ViewModelSavedState.dll => 0x1699fd1e1a00b643 => 62
	i64 1636321030536304333, ; 19: Xamarin.AndroidX.Legacy.Support.Core.Utils.dll => 0x16b5614ec39e16cd => 55
	i64 1731380447121279447, ; 20: Newtonsoft.Json => 0x18071957e9b889d7 => 10
	i64 1743969030606105336, ; 21: System.Memory.dll => 0x1833d297e88f2af8 => 26
	i64 1795316252682057001, ; 22: Xamarin.AndroidX.AppCompat.dll => 0x18ea3e9eac997529 => 39
	i64 1836611346387731153, ; 23: Xamarin.AndroidX.SavedState => 0x197cf449ebe482d1 => 69
	i64 1865037103900624886, ; 24: Microsoft.Bcl.AsyncInterfaces => 0x19e1f15d56eb87f6 => 7
	i64 1875917498431009007, ; 25: Xamarin.AndroidX.Annotation.dll => 0x1a08990699eb70ef => 36
	i64 1981742497975770890, ; 26: Xamarin.AndroidX.Lifecycle.ViewModel.dll => 0x1b80904d5c241f0a => 61
	i64 2040001226662520565, ; 27: System.Threading.Tasks.Extensions.dll => 0x1c4f8a4ea894a6f5 => 94
	i64 2133195048986300728, ; 28: Newtonsoft.Json.dll => 0x1d9aa1984b735138 => 10
	i64 2136356949452311481, ; 29: Xamarin.AndroidX.MultiDex.dll => 0x1da5dd539d8acbb9 => 66
	i64 2165725771938924357, ; 30: Xamarin.AndroidX.Browser => 0x1e0e341d75540745 => 43
	i64 2262844636196693701, ; 31: Xamarin.AndroidX.DrawerLayout.dll => 0x1f673d352266e6c5 => 51
	i64 2284400282711631002, ; 32: System.Web.Services => 0x1fb3d1f42fd4249a => 92
	i64 2329709569556905518, ; 33: Xamarin.AndroidX.Lifecycle.LiveData.Core.dll => 0x2054ca829b447e2e => 58
	i64 2335503487726329082, ; 34: System.Text.Encodings.Web => 0x2069600c4d9d1cfa => 31
	i64 2337758774805907496, ; 35: System.Runtime.CompilerServices.Unsafe => 0x207163383edbc828 => 29
	i64 2470498323731680442, ; 36: Xamarin.AndroidX.CoordinatorLayout => 0x2248f922dc398cba => 46
	i64 2479423007379663237, ; 37: Xamarin.AndroidX.VectorDrawable.Animated.dll => 0x2268ae16b2cba985 => 73
	i64 2497223385847772520, ; 38: System.Runtime => 0x22a7eb7046413568 => 30
	i64 2547086958574651984, ; 39: Xamarin.AndroidX.Activity.dll => 0x2359121801df4a50 => 35
	i64 2592350477072141967, ; 40: System.Xml.dll => 0x23f9e10627330e8f => 33
	i64 2624866290265602282, ; 41: mscorlib.dll => 0x246d65fbde2db8ea => 9
	i64 2783046991838674048, ; 42: System.Runtime.CompilerServices.Unsafe.dll => 0x269f5e7e6dc37c80 => 29
	i64 2960931600190307745, ; 43: Xamarin.Forms.Core => 0x2917579a49927da1 => 79
	i64 3017704767998173186, ; 44: Xamarin.Google.Android.Material => 0x29e10a7f7d88a002 => 83
	i64 3063847325783385934, ; 45: System.ClientModel.dll => 0x2a84f8e8eb59674e => 20
	i64 3289520064315143713, ; 46: Xamarin.AndroidX.Lifecycle.Common => 0x2da6b911e3063621 => 57
	i64 3303437397778967116, ; 47: Xamarin.AndroidX.Annotation.Experimental => 0x2dd82acf985b2a4c => 37
	i64 3311221304742556517, ; 48: System.Numerics.Vectors.dll => 0x2df3d23ba9e2b365 => 28
	i64 3522470458906976663, ; 49: Xamarin.AndroidX.SwipeRefreshLayout => 0x30e2543832f52197 => 71
	i64 3531994851595924923, ; 50: System.Numerics => 0x31042a9aade235bb => 27
	i64 3571415421602489686, ; 51: System.Runtime.dll => 0x319037675df7e556 => 30
	i64 3716579019761409177, ; 52: netstandard.dll => 0x3393f0ed5c8c5c99 => 1
	i64 3727469159507183293, ; 53: Xamarin.AndroidX.RecyclerView => 0x33baa1739ba646bd => 68
	i64 3966267475168208030, ; 54: System.Memory => 0x370b03412596249e => 26
	i64 4337444564132831293, ; 55: SQLitePCLRaw.batteries_v2.dll => 0x3c31b2d9ae16203d => 15
	i64 4525561845656915374, ; 56: System.ServiceModel.Internals => 0x3ece06856b710dae => 93
	i64 4636684751163556186, ; 57: Xamarin.AndroidX.VersionedParcelable.dll => 0x4058d0370893015a => 75
	i64 4782108999019072045, ; 58: Xamarin.AndroidX.AsyncLayoutInflater.dll => 0x425d76cc43bb0a2d => 42
	i64 4794310189461587505, ; 59: Xamarin.AndroidX.Activity => 0x4288cfb749e4c631 => 35
	i64 4795410492532947900, ; 60: Xamarin.AndroidX.SwipeRefreshLayout.dll => 0x428cb86f8f9b7bbc => 71
	i64 5142919913060024034, ; 61: Xamarin.Forms.Platform.Android.dll => 0x475f52699e39bee2 => 80
	i64 5202753749449073649, ; 62: Plugin.Media => 0x4833e4f841be63f1 => 12
	i64 5203618020066742981, ; 63: Xamarin.Essentials => 0x4836f704f0e652c5 => 78
	i64 5205316157927637098, ; 64: Xamarin.AndroidX.LocalBroadcastManager => 0x483cff7778e0c06a => 64
	i64 5348796042099802469, ; 65: Xamarin.AndroidX.Media => 0x4a3abda9415fc165 => 65
	i64 5376510917114486089, ; 66: Xamarin.AndroidX.VectorDrawable.Animated => 0x4a9d3431719e5d49 => 73
	i64 5408338804355907810, ; 67: Xamarin.AndroidX.Transition => 0x4b0e477cea9840e2 => 72
	i64 5507995362134886206, ; 68: System.Core.dll => 0x4c705499688c873e => 21
	i64 5692067934154308417, ; 69: Xamarin.AndroidX.ViewPager2.dll => 0x4efe49a0d4a8bb41 => 77
	i64 5896680224035167651, ; 70: Xamarin.AndroidX.Lifecycle.LiveData.dll => 0x51d5376bfbafdda3 => 59
	i64 6085203216496545422, ; 71: Xamarin.Forms.Platform.dll => 0x5472fc15a9574e8e => 81
	i64 6086316965293125504, ; 72: FormsViewGroup.dll => 0x5476f10882baef80 => 4
	i64 6183170893902868313, ; 73: SQLitePCLRaw.batteries_v2 => 0x55cf092b0c9d6f59 => 15
	i64 6222399776351216807, ; 74: System.Text.Json.dll => 0x565a67a0ffe264a7 => 32
	i64 6319713645133255417, ; 75: Xamarin.AndroidX.Lifecycle.Runtime => 0x57b42213b45b52f9 => 60
	i64 6401687960814735282, ; 76: Xamarin.AndroidX.Lifecycle.LiveData.Core => 0x58d75d486341cfb2 => 58
	i64 6504860066809920875, ; 77: Xamarin.AndroidX.Browser.dll => 0x5a45e7c43bd43d6b => 43
	i64 6548213210057960872, ; 78: Xamarin.AndroidX.CustomView.dll => 0x5adfed387b066da8 => 49
	i64 6591024623626361694, ; 79: System.Web.Services.dll => 0x5b7805f9751a1b5e => 92
	i64 6659513131007730089, ; 80: Xamarin.AndroidX.Legacy.Support.Core.UI.dll => 0x5c6b57e8b6c3e1a9 => 54
	i64 6671798237668743565, ; 81: SkiaSharp => 0x5c96fd260152998d => 13
	i64 6876862101832370452, ; 82: System.Xml.Linq => 0x5f6f85a57d108914 => 34
	i64 6894844156784520562, ; 83: System.Numerics.Vectors => 0x5faf683aead1ad72 => 28
	i64 7036436454368433159, ; 84: Xamarin.AndroidX.Legacy.Support.V4.dll => 0x61a671acb33d5407 => 56
	i64 7103753931438454322, ; 85: Xamarin.AndroidX.Interpolator.dll => 0x62959a90372c7632 => 53
	i64 7348123982286201829, ; 86: System.Memory.Data.dll => 0x65f9c7d471b2a3e5 => 25
	i64 7488575175965059935, ; 87: System.Xml.Linq.dll => 0x67ecc3724534ab5f => 34
	i64 7635363394907363464, ; 88: Xamarin.Forms.Core.dll => 0x69f6428dc4795888 => 79
	i64 7637365915383206639, ; 89: Xamarin.Essentials.dll => 0x69fd5fd5e61792ef => 78
	i64 7654504624184590948, ; 90: System.Net.Http => 0x6a3a4366801b8264 => 2
	i64 7820441508502274321, ; 91: System.Data => 0x6c87ca1e14ff8111 => 85
	i64 7836164640616011524, ; 92: Xamarin.AndroidX.AppCompat.AppCompatResources => 0x6cbfa6390d64d704 => 38
	i64 8044118961405839122, ; 93: System.ComponentModel.Composition => 0x6fa2739369944712 => 91
	i64 8083354569033831015, ; 94: Xamarin.AndroidX.Lifecycle.Common.dll => 0x702dd82730cad267 => 57
	i64 8087206902342787202, ; 95: System.Diagnostics.DiagnosticSource => 0x703b87d46f3aa082 => 22
	i64 8103644804370223335, ; 96: System.Data.DataSetExtensions.dll => 0x7075ee03be6d50e7 => 87
	i64 8167236081217502503, ; 97: Java.Interop.dll => 0x7157d9f1a9b8fd27 => 5
	i64 8601935802264776013, ; 98: Xamarin.AndroidX.Transition.dll => 0x7760370982b4ed4d => 72
	i64 8626175481042262068, ; 99: Java.Interop => 0x77b654e585b55834 => 5
	i64 8684531736582871431, ; 100: System.IO.Compression.FileSystem => 0x7885a79a0fa0d987 => 90
	i64 8725526185868997716, ; 101: System.Diagnostics.DiagnosticSource.dll => 0x79174bd613173454 => 22
	i64 9312692141327339315, ; 102: Xamarin.AndroidX.ViewPager2 => 0x813d54296a634f33 => 77
	i64 9324707631942237306, ; 103: Xamarin.AndroidX.AppCompat => 0x8168042fd44a7c7a => 39
	i64 9359846129620719819, ; 104: manipulatorMobileApp => 0x81e4da76dc5b98cb => 6
	i64 9662334977499516867, ; 105: System.Numerics.dll => 0x8617827802b0cfc3 => 27
	i64 9678050649315576968, ; 106: Xamarin.AndroidX.CoordinatorLayout.dll => 0x864f57c9feb18c88 => 46
	i64 9711637524876806384, ; 107: Xamarin.AndroidX.Media.dll => 0x86c6aadfd9a2c8f0 => 65
	i64 9808709177481450983, ; 108: Mono.Android.dll => 0x881f890734e555e7 => 8
	i64 9834056768316610435, ; 109: System.Transactions.dll => 0x8879968718899783 => 86
	i64 9998632235833408227, ; 110: Mono.Security => 0x8ac2470b209ebae3 => 95
	i64 10038780035334861115, ; 111: System.Net.Http.dll => 0x8b50e941206af13b => 2
	i64 10229024438826829339, ; 112: Xamarin.AndroidX.CustomView => 0x8df4cb880b10061b => 49
	i64 10430153318873392755, ; 113: Xamarin.AndroidX.Core => 0x90bf592ea44f6673 => 47
	i64 10447083246144586668, ; 114: Microsoft.Bcl.AsyncInterfaces.dll => 0x90fb7edc816203ac => 7
	i64 10847732767863316357, ; 115: Xamarin.AndroidX.Arch.Core.Common => 0x968ae37a86db9f85 => 40
	i64 11023048688141570732, ; 116: System.Core => 0x98f9bc61168392ac => 21
	i64 11037814507248023548, ; 117: System.Xml => 0x992e31d0412bf7fc => 33
	i64 11162124722117608902, ; 118: Xamarin.AndroidX.ViewPager => 0x9ae7d54b986d05c6 => 76
	i64 11340910727871153756, ; 119: Xamarin.AndroidX.CursorAdapter => 0x9d630238642d465c => 48
	i64 11392833485892708388, ; 120: Xamarin.AndroidX.Print.dll => 0x9e1b79b18fcf6824 => 67
	i64 11513602507638267977, ; 121: System.IO.Pipelines.dll => 0x9fc8887aa0d36049 => 24
	i64 11529969570048099689, ; 122: Xamarin.AndroidX.ViewPager.dll => 0xa002ae3c4dc7c569 => 76
	i64 11578238080964724296, ; 123: Xamarin.AndroidX.Legacy.Support.V4 => 0xa0ae2a30c4cd8648 => 56
	i64 11580057168383206117, ; 124: Xamarin.AndroidX.Annotation => 0xa0b4a0a4103262e5 => 36
	i64 11597940890313164233, ; 125: netstandard => 0xa0f429ca8d1805c9 => 1
	i64 11672361001936329215, ; 126: Xamarin.AndroidX.Interpolator => 0xa1fc8e7d0a8999ff => 53
	i64 11739066727115742305, ; 127: SQLite-net.dll => 0xa2e98afdf8575c61 => 14
	i64 11806260347154423189, ; 128: SQLite-net => 0xa3d8433bc5eb5d95 => 14
	i64 12102847907131387746, ; 129: System.Buffers => 0xa7f5f40c43256f62 => 19
	i64 12137774235383566651, ; 130: Xamarin.AndroidX.VectorDrawable => 0xa872095bbfed113b => 74
	i64 12145679461940342714, ; 131: System.Text.Json => 0xa88e1f1ebcb62fba => 32
	i64 12279246230491828964, ; 132: SQLitePCLRaw.provider.e_sqlite3.dll => 0xaa68a5636e0512e4 => 18
	i64 12313367145828839434, ; 133: System.IO.Pipelines => 0xaae1de2e1c17f00a => 24
	i64 12401053665971001862, ; 134: OpenAI.dll => 0xac19649b08c1da06 => 11
	i64 12451044538927396471, ; 135: Xamarin.AndroidX.Fragment.dll => 0xaccaff0a2955b677 => 52
	i64 12466513435562512481, ; 136: Xamarin.AndroidX.Loader.dll => 0xad01f3eb52569061 => 63
	i64 12487638416075308985, ; 137: Xamarin.AndroidX.DocumentFile.dll => 0xad4d00fa21b0bfb9 => 50
	i64 12538491095302438457, ; 138: Xamarin.AndroidX.CardView.dll => 0xae01ab382ae67e39 => 44
	i64 12550732019250633519, ; 139: System.IO.Compression => 0xae2d28465e8e1b2f => 89
	i64 12700543734426720211, ; 140: Xamarin.AndroidX.Collection => 0xb041653c70d157d3 => 45
	i64 12963446364377008305, ; 141: System.Drawing.Common.dll => 0xb3e769c8fd8548b1 => 88
	i64 13370592475155966277, ; 142: System.Runtime.Serialization => 0xb98de304062ea945 => 3
	i64 13401370062847626945, ; 143: Xamarin.AndroidX.VectorDrawable.dll => 0xb9fb3b1193964ec1 => 74
	i64 13454009404024712428, ; 144: Xamarin.Google.Guava.ListenableFuture => 0xbab63e4543a86cec => 84
	i64 13491513212026656886, ; 145: Xamarin.AndroidX.Arch.Core.Runtime.dll => 0xbb3b7bc905569876 => 41
	i64 13572454107664307259, ; 146: Xamarin.AndroidX.RecyclerView.dll => 0xbc5b0b19d99f543b => 68
	i64 13643785327914841093, ; 147: Plugin.Media.dll => 0xbd587677c60cf405 => 12
	i64 13647894001087880694, ; 148: System.Data.dll => 0xbd670f48cb071df6 => 85
	i64 13959074834287824816, ; 149: Xamarin.AndroidX.Fragment => 0xc1b8989a7ad20fb0 => 52
	i64 13967638549803255703, ; 150: Xamarin.Forms.Platform.Android => 0xc1d70541e0134797 => 80
	i64 14124974489674258913, ; 151: Xamarin.AndroidX.CardView => 0xc405fd76067d19e1 => 44
	i64 14172845254133543601, ; 152: Xamarin.AndroidX.MultiDex => 0xc4b00faaed35f2b1 => 66
	i64 14261073672896646636, ; 153: Xamarin.AndroidX.Print => 0xc5e982f274ae0dec => 67
	i64 14486659737292545672, ; 154: Xamarin.AndroidX.Lifecycle.LiveData => 0xc90af44707469e88 => 59
	i64 14551742072151931844, ; 155: System.Text.Encodings.Web.dll => 0xc9f22c50f1b8fbc4 => 31
	i64 14644440854989303794, ; 156: Xamarin.AndroidX.LocalBroadcastManager.dll => 0xcb3b815e37daeff2 => 64
	i64 14731917719247821583, ; 157: manipulatorMobileApp.Android => 0xcc72491cd40c9b0f => 0
	i64 14792063746108907174, ; 158: Xamarin.Google.Guava.ListenableFuture.dll => 0xcd47f79af9c15ea6 => 84
	i64 14852515768018889994, ; 159: Xamarin.AndroidX.CursorAdapter.dll => 0xce1ebc6625a76d0a => 48
	i64 14987728460634540364, ; 160: System.IO.Compression.dll => 0xcfff1ba06622494c => 89
	i64 14988210264188246988, ; 161: Xamarin.AndroidX.DocumentFile => 0xd000d1d307cddbcc => 50
	i64 15370334346939861994, ; 162: Xamarin.AndroidX.Core.dll => 0xd54e65a72c560bea => 47
	i64 15383240894167415497, ; 163: System.Memory.Data => 0xd57c4016df1c7ac9 => 25
	i64 15484597214878758184, ; 164: OpenAI => 0xd6e4572042d9f528 => 11
	i64 15582737692548360875, ; 165: Xamarin.AndroidX.Lifecycle.ViewModelSavedState => 0xd841015ed86f6aab => 62
	i64 15609085926864131306, ; 166: System.dll => 0xd89e9cf3334914ea => 23
	i64 15777549416145007739, ; 167: Xamarin.AndroidX.SlidingPaneLayout.dll => 0xdaf51d99d77eb47b => 70
	i64 15810740023422282496, ; 168: Xamarin.Forms.Xaml => 0xdb6b08484c22eb00 => 82
	i64 15963349826457351533, ; 169: System.Threading.Tasks.Extensions => 0xdd893616f748b56d => 94
	i64 16154507427712707110, ; 170: System => 0xe03056ea4e39aa26 => 23
	i64 16324796876805858114, ; 171: SkiaSharp.dll => 0xe28d5444586b6342 => 13
	i64 16565028646146589191, ; 172: System.ComponentModel.Composition.dll => 0xe5e2cdc9d3bcc207 => 91
	i64 16750964477065896785, ; 173: manipulatorMobileApp.Android.dll => 0xe877617104b32351 => 0
	i64 16755018182064898362, ; 174: SQLitePCLRaw.core.dll => 0xe885c843c330813a => 16
	i64 16822611501064131242, ; 175: System.Data.DataSetExtensions => 0xe975ec07bb5412aa => 87
	i64 16833383113903931215, ; 176: mscorlib => 0xe99c30c1484d7f4f => 9
	i64 17006954551347072385, ; 177: System.ClientModel => 0xec04d70ec8414d81 => 20
	i64 17024911836938395553, ; 178: Xamarin.AndroidX.Annotation.Experimental.dll => 0xec44a31d250e5fa1 => 37
	i64 17037200463775726619, ; 179: Xamarin.AndroidX.Legacy.Support.Core.Utils => 0xec704b8e0a78fc1b => 55
	i64 17544493274320527064, ; 180: Xamarin.AndroidX.AsyncLayoutInflater => 0xf37a8fada41aded8 => 42
	i64 17704177640604968747, ; 181: Xamarin.AndroidX.Loader => 0xf5b1dfc36cac272b => 63
	i64 17710060891934109755, ; 182: Xamarin.AndroidX.Lifecycle.ViewModel => 0xf5c6c68c9e45303b => 61
	i64 17838668724098252521, ; 183: System.Buffers.dll => 0xf78faeb0f5bf3ee9 => 19
	i64 17882897186074144999, ; 184: FormsViewGroup => 0xf82cd03e3ac830e7 => 4
	i64 17892495832318972303, ; 185: Xamarin.Forms.Xaml.dll => 0xf84eea293687918f => 82
	i64 17928294245072900555, ; 186: System.IO.Compression.FileSystem.dll => 0xf8ce18a0b24011cb => 90
	i64 18116111925905154859, ; 187: Xamarin.AndroidX.Arch.Core.Runtime => 0xfb695bd036cb632b => 41
	i64 18129453464017766560, ; 188: System.ServiceModel.Internals.dll => 0xfb98c1df1ec108a0 => 93
	i64 18370042311372477656, ; 189: SQLitePCLRaw.lib.e_sqlite3.android.dll => 0xfeef80274e4094d8 => 17
	i64 18380184030268848184, ; 190: Xamarin.AndroidX.VersionedParcelable => 0xff1387fe3e7b7838 => 75
	i64 18393538163818138746 ; 191: manipulatorMobileApp.dll => 0xff42f981c0f88c7a => 6
], align 8
@assembly_image_cache_indices = local_unnamed_addr constant [192 x i32] [
	i32 8, i32 45, i32 69, i32 70, i32 60, i32 88, i32 54, i32 17, ; 0..7
	i32 51, i32 86, i32 81, i32 95, i32 83, i32 16, i32 40, i32 3, ; 8..15
	i32 18, i32 38, i32 62, i32 55, i32 10, i32 26, i32 39, i32 69, ; 16..23
	i32 7, i32 36, i32 61, i32 94, i32 10, i32 66, i32 43, i32 51, ; 24..31
	i32 92, i32 58, i32 31, i32 29, i32 46, i32 73, i32 30, i32 35, ; 32..39
	i32 33, i32 9, i32 29, i32 79, i32 83, i32 20, i32 57, i32 37, ; 40..47
	i32 28, i32 71, i32 27, i32 30, i32 1, i32 68, i32 26, i32 15, ; 48..55
	i32 93, i32 75, i32 42, i32 35, i32 71, i32 80, i32 12, i32 78, ; 56..63
	i32 64, i32 65, i32 73, i32 72, i32 21, i32 77, i32 59, i32 81, ; 64..71
	i32 4, i32 15, i32 32, i32 60, i32 58, i32 43, i32 49, i32 92, ; 72..79
	i32 54, i32 13, i32 34, i32 28, i32 56, i32 53, i32 25, i32 34, ; 80..87
	i32 79, i32 78, i32 2, i32 85, i32 38, i32 91, i32 57, i32 22, ; 88..95
	i32 87, i32 5, i32 72, i32 5, i32 90, i32 22, i32 77, i32 39, ; 96..103
	i32 6, i32 27, i32 46, i32 65, i32 8, i32 86, i32 95, i32 2, ; 104..111
	i32 49, i32 47, i32 7, i32 40, i32 21, i32 33, i32 76, i32 48, ; 112..119
	i32 67, i32 24, i32 76, i32 56, i32 36, i32 1, i32 53, i32 14, ; 120..127
	i32 14, i32 19, i32 74, i32 32, i32 18, i32 24, i32 11, i32 52, ; 128..135
	i32 63, i32 50, i32 44, i32 89, i32 45, i32 88, i32 3, i32 74, ; 136..143
	i32 84, i32 41, i32 68, i32 12, i32 85, i32 52, i32 80, i32 44, ; 144..151
	i32 66, i32 67, i32 59, i32 31, i32 64, i32 0, i32 84, i32 48, ; 152..159
	i32 89, i32 50, i32 47, i32 25, i32 11, i32 62, i32 23, i32 70, ; 160..167
	i32 82, i32 94, i32 23, i32 13, i32 91, i32 0, i32 16, i32 87, ; 168..175
	i32 9, i32 20, i32 37, i32 55, i32 42, i32 63, i32 61, i32 19, ; 176..183
	i32 4, i32 82, i32 90, i32 41, i32 93, i32 17, i32 75, i32 6 ; 192..191
], align 4

@marshal_methods_number_of_classes = local_unnamed_addr constant i32 0, align 4

; marshal_methods_class_cache
@marshal_methods_class_cache = global [0 x %struct.MarshalMethodsManagedClass] [
], align 8; end of 'marshal_methods_class_cache' array


@get_function_pointer = internal unnamed_addr global void (i32, i32, i32, i8**)* null, align 8

; Function attributes: "frame-pointer"="non-leaf" "min-legal-vector-width"="0" mustprogress nofree norecurse nosync "no-trapping-math"="true" nounwind sspstrong "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+neon,+outline-atomics" uwtable willreturn writeonly
define void @xamarin_app_init (void (i32, i32, i32, i8**)* %fn) local_unnamed_addr #0
{
	store void (i32, i32, i32, i8**)* %fn, void (i32, i32, i32, i8**)** @get_function_pointer, align 8
	ret void
}

; Names of classes in which marshal methods reside
@mm_class_names = local_unnamed_addr constant [0 x i8*] zeroinitializer, align 8
@__MarshalMethodName_name.0 = internal constant [1 x i8] c"\00", align 1

; mm_method_names
@mm_method_names = local_unnamed_addr constant [1 x %struct.MarshalMethodName] [
	; 0
	%struct.MarshalMethodName {
		i64 0, ; id 0x0; name: 
		i8* getelementptr inbounds ([1 x i8], [1 x i8]* @__MarshalMethodName_name.0, i32 0, i32 0); name
	}
], align 8; end of 'mm_method_names' array


attributes #0 = { "min-legal-vector-width"="0" mustprogress nofree norecurse nosync "no-trapping-math"="true" nounwind sspstrong "stack-protector-buffer-size"="8" uwtable willreturn writeonly "frame-pointer"="non-leaf" "target-cpu"="generic" "target-features"="+neon,+outline-atomics" }
attributes #1 = { "min-legal-vector-width"="0" mustprogress "no-trapping-math"="true" nounwind sspstrong "stack-protector-buffer-size"="8" uwtable "frame-pointer"="non-leaf" "target-cpu"="generic" "target-features"="+neon,+outline-atomics" }
attributes #2 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5}
!llvm.ident = !{!6}
!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{i32 1, !"branch-target-enforcement", i32 0}
!3 = !{i32 1, !"sign-return-address", i32 0}
!4 = !{i32 1, !"sign-return-address-all", i32 0}
!5 = !{i32 1, !"sign-return-address-with-bkey", i32 0}
!6 = !{!"Xamarin.Android remotes/origin/d17-5 @ 45b0e144f73b2c8747d8b5ec8cbd3b55beca67f0"}
!llvm.linker.options = !{}
