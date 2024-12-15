; ModuleID = 'obj\Debug\121\android\marshal_methods.armeabi-v7a.ll'
source_filename = "obj\Debug\121\android\marshal_methods.armeabi-v7a.ll"
target datalayout = "e-m:e-p:32:32-Fi8-i64:64-v128:64:128-a:0:32-n32-S64"
target triple = "armv7-unknown-linux-android"


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
@assembly_image_cache = local_unnamed_addr global [0 x %struct.MonoImage*] zeroinitializer, align 4
; Each entry maps hash of an assembly name to an index into the `assembly_image_cache` array
@assembly_image_cache_hashes = local_unnamed_addr constant [192 x i32] [
	i32 32687329, ; 0: Xamarin.AndroidX.Lifecycle.Runtime => 0x1f2c4e1 => 60
	i32 34715100, ; 1: Xamarin.Google.Guava.ListenableFuture.dll => 0x211b5dc => 84
	i32 39109920, ; 2: Newtonsoft.Json.dll => 0x254c520 => 10
	i32 57263871, ; 3: Xamarin.Forms.Core.dll => 0x369c6ff => 79
	i32 101534019, ; 4: Xamarin.AndroidX.SlidingPaneLayout => 0x60d4943 => 70
	i32 120558881, ; 5: Xamarin.AndroidX.SlidingPaneLayout.dll => 0x72f9521 => 70
	i32 165246403, ; 6: Xamarin.AndroidX.Collection.dll => 0x9d975c3 => 45
	i32 182336117, ; 7: Xamarin.AndroidX.SwipeRefreshLayout.dll => 0xade3a75 => 71
	i32 209399409, ; 8: Xamarin.AndroidX.Browser.dll => 0xc7b2e71 => 43
	i32 230216969, ; 9: Xamarin.AndroidX.Legacy.Support.Core.Utils.dll => 0xdb8d509 => 55
	i32 232815796, ; 10: System.Web.Services => 0xde07cb4 => 92
	i32 275081953, ; 11: OpenAI => 0x10656ae1 => 11
	i32 278686392, ; 12: Xamarin.AndroidX.Lifecycle.LiveData.dll => 0x109c6ab8 => 59
	i32 280482487, ; 13: Xamarin.AndroidX.Interpolator => 0x10b7d2b7 => 53
	i32 318968648, ; 14: Xamarin.AndroidX.Activity.dll => 0x13031348 => 35
	i32 321597661, ; 15: System.Numerics => 0x132b30dd => 27
	i32 342366114, ; 16: Xamarin.AndroidX.Lifecycle.Common => 0x146817a2 => 57
	i32 347068432, ; 17: SQLitePCLRaw.lib.e_sqlite3.android.dll => 0x14afd810 => 17
	i32 385762202, ; 18: System.Memory.dll => 0x16fe439a => 26
	i32 442521989, ; 19: Xamarin.Essentials => 0x1a605985 => 78
	i32 450948140, ; 20: Xamarin.AndroidX.Fragment.dll => 0x1ae0ec2c => 52
	i32 465846621, ; 21: mscorlib => 0x1bc4415d => 9
	i32 469710990, ; 22: System.dll => 0x1bff388e => 23
	i32 476646585, ; 23: Xamarin.AndroidX.Interpolator.dll => 0x1c690cb9 => 53
	i32 486930444, ; 24: Xamarin.AndroidX.LocalBroadcastManager.dll => 0x1d05f80c => 64
	i32 525008092, ; 25: SkiaSharp.dll => 0x1f4afcdc => 13
	i32 526420162, ; 26: System.Transactions.dll => 0x1f6088c2 => 86
	i32 548916678, ; 27: Microsoft.Bcl.AsyncInterfaces => 0x20b7cdc6 => 7
	i32 605376203, ; 28: System.IO.Compression.FileSystem => 0x24154ecb => 90
	i32 627609679, ; 29: Xamarin.AndroidX.CustomView => 0x2568904f => 49
	i32 662205335, ; 30: System.Text.Encodings.Web.dll => 0x27787397 => 31
	i32 663517072, ; 31: Xamarin.AndroidX.VersionedParcelable => 0x278c7790 => 75
	i32 666292255, ; 32: Xamarin.AndroidX.Arch.Core.Common.dll => 0x27b6d01f => 40
	i32 690569205, ; 33: System.Xml.Linq.dll => 0x29293ff5 => 34
	i32 723796036, ; 34: System.ClientModel.dll => 0x2b244044 => 20
	i32 748832960, ; 35: SQLitePCLRaw.batteries_v2 => 0x2ca248c0 => 15
	i32 775507847, ; 36: System.IO.Compression => 0x2e394f87 => 89
	i32 809851609, ; 37: System.Drawing.Common.dll => 0x30455ad9 => 88
	i32 842722721, ; 38: OpenAI.dll => 0x323aeda1 => 11
	i32 843511501, ; 39: Xamarin.AndroidX.Print => 0x3246f6cd => 67
	i32 928116545, ; 40: Xamarin.Google.Guava.ListenableFuture => 0x3751ef41 => 84
	i32 955402788, ; 41: Newtonsoft.Json => 0x38f24a24 => 10
	i32 967690846, ; 42: Xamarin.AndroidX.Lifecycle.Common.dll => 0x39adca5e => 57
	i32 974778368, ; 43: FormsViewGroup.dll => 0x3a19f000 => 4
	i32 1012816738, ; 44: Xamarin.AndroidX.SavedState.dll => 0x3c5e5b62 => 69
	i32 1035644815, ; 45: Xamarin.AndroidX.AppCompat => 0x3dbaaf8f => 39
	i32 1042160112, ; 46: Xamarin.Forms.Platform.dll => 0x3e1e19f0 => 81
	i32 1052210849, ; 47: Xamarin.AndroidX.Lifecycle.ViewModel.dll => 0x3eb776a1 => 61
	i32 1098259244, ; 48: System => 0x41761b2c => 23
	i32 1104002344, ; 49: Plugin.Media => 0x41cdbd28 => 12
	i32 1175144683, ; 50: Xamarin.AndroidX.VectorDrawable.Animated => 0x460b48eb => 73
	i32 1204270330, ; 51: Xamarin.AndroidX.Arch.Core.Common => 0x47c7b4fa => 40
	i32 1267360935, ; 52: Xamarin.AndroidX.VectorDrawable => 0x4b8a64a7 => 74
	i32 1292207520, ; 53: SQLitePCLRaw.core.dll => 0x4d0585a0 => 16
	i32 1293217323, ; 54: Xamarin.AndroidX.DrawerLayout.dll => 0x4d14ee2b => 51
	i32 1365406463, ; 55: System.ServiceModel.Internals.dll => 0x516272ff => 93
	i32 1376866003, ; 56: Xamarin.AndroidX.SavedState => 0x52114ed3 => 69
	i32 1395857551, ; 57: Xamarin.AndroidX.Media.dll => 0x5333188f => 65
	i32 1406073936, ; 58: Xamarin.AndroidX.CoordinatorLayout => 0x53cefc50 => 46
	i32 1411638395, ; 59: System.Runtime.CompilerServices.Unsafe => 0x5423e47b => 29
	i32 1460219004, ; 60: Xamarin.Forms.Xaml => 0x57092c7c => 82
	i32 1462112819, ; 61: System.IO.Compression.dll => 0x57261233 => 89
	i32 1469204771, ; 62: Xamarin.AndroidX.AppCompat.AppCompatResources => 0x57924923 => 38
	i32 1582372066, ; 63: Xamarin.AndroidX.DocumentFile.dll => 0x5e5114e2 => 50
	i32 1592978981, ; 64: System.Runtime.Serialization.dll => 0x5ef2ee25 => 3
	i32 1622152042, ; 65: Xamarin.AndroidX.Loader.dll => 0x60b0136a => 63
	i32 1624863272, ; 66: Xamarin.AndroidX.ViewPager2 => 0x60d97228 => 77
	i32 1636350590, ; 67: Xamarin.AndroidX.CursorAdapter => 0x6188ba7e => 48
	i32 1639515021, ; 68: System.Net.Http.dll => 0x61b9038d => 2
	i32 1657153582, ; 69: System.Runtime => 0x62c6282e => 30
	i32 1658251792, ; 70: Xamarin.Google.Android.Material.dll => 0x62d6ea10 => 83
	i32 1711441057, ; 71: SQLitePCLRaw.lib.e_sqlite3.android => 0x660284a1 => 17
	i32 1729485958, ; 72: Xamarin.AndroidX.CardView.dll => 0x6715dc86 => 44
	i32 1746115085, ; 73: System.IO.Pipelines.dll => 0x68139a0d => 24
	i32 1766324549, ; 74: Xamarin.AndroidX.SwipeRefreshLayout => 0x6947f945 => 71
	i32 1776026572, ; 75: System.Core.dll => 0x69dc03cc => 21
	i32 1788241197, ; 76: Xamarin.AndroidX.Fragment => 0x6a96652d => 52
	i32 1796167890, ; 77: Microsoft.Bcl.AsyncInterfaces.dll => 0x6b0f58d2 => 7
	i32 1808609942, ; 78: Xamarin.AndroidX.Loader => 0x6bcd3296 => 63
	i32 1813201214, ; 79: Xamarin.Google.Android.Material => 0x6c13413e => 83
	i32 1867746548, ; 80: Xamarin.Essentials.dll => 0x6f538cf4 => 78
	i32 1878053835, ; 81: Xamarin.Forms.Xaml.dll => 0x6ff0d3cb => 82
	i32 1885316902, ; 82: Xamarin.AndroidX.Arch.Core.Runtime.dll => 0x705fa726 => 41
	i32 1919157823, ; 83: Xamarin.AndroidX.MultiDex.dll => 0x7264063f => 66
	i32 2011961780, ; 84: System.Buffers.dll => 0x77ec19b4 => 19
	i32 2019465201, ; 85: Xamarin.AndroidX.Lifecycle.ViewModel => 0x785e97f1 => 61
	i32 2048185678, ; 86: Plugin.Media.dll => 0x7a14d54e => 12
	i32 2055257422, ; 87: Xamarin.AndroidX.Lifecycle.LiveData.Core.dll => 0x7a80bd4e => 58
	i32 2073269330, ; 88: manipulatorMobileApp.Android => 0x7b939452 => 0
	i32 2079903147, ; 89: System.Runtime.dll => 0x7bf8cdab => 30
	i32 2090596640, ; 90: System.Numerics.Vectors => 0x7c9bf920 => 28
	i32 2097448633, ; 91: Xamarin.AndroidX.Legacy.Support.Core.UI => 0x7d0486b9 => 54
	i32 2103459038, ; 92: SQLitePCLRaw.provider.e_sqlite3.dll => 0x7d603cde => 18
	i32 2126786730, ; 93: Xamarin.Forms.Platform.Android => 0x7ec430aa => 80
	i32 2201231467, ; 94: System.Net.Http => 0x8334206b => 2
	i32 2217644978, ; 95: Xamarin.AndroidX.VectorDrawable.Animated.dll => 0x842e93b2 => 73
	i32 2244775296, ; 96: Xamarin.AndroidX.LocalBroadcastManager => 0x85cc8d80 => 64
	i32 2256548716, ; 97: Xamarin.AndroidX.MultiDex => 0x8680336c => 66
	i32 2261435625, ; 98: Xamarin.AndroidX.Legacy.Support.V4.dll => 0x86cac4e9 => 56
	i32 2279755925, ; 99: Xamarin.AndroidX.RecyclerView.dll => 0x87e25095 => 68
	i32 2315684594, ; 100: Xamarin.AndroidX.Annotation.dll => 0x8a068af2 => 36
	i32 2465273461, ; 101: SQLitePCLRaw.batteries_v2.dll => 0x92f11675 => 15
	i32 2471841756, ; 102: netstandard.dll => 0x93554fdc => 1
	i32 2475788418, ; 103: Java.Interop.dll => 0x93918882 => 5
	i32 2501346920, ; 104: System.Data.DataSetExtensions => 0x95178668 => 87
	i32 2505896520, ; 105: Xamarin.AndroidX.Lifecycle.Runtime.dll => 0x955cf248 => 60
	i32 2570120770, ; 106: System.Text.Encodings.Web => 0x9930ee42 => 31
	i32 2581819634, ; 107: Xamarin.AndroidX.VectorDrawable.dll => 0x99e370f2 => 74
	i32 2620871830, ; 108: Xamarin.AndroidX.CursorAdapter.dll => 0x9c375496 => 48
	i32 2621301489, ; 109: manipulatorMobileApp => 0x9c3de2f1 => 6
	i32 2628210652, ; 110: System.Memory.Data => 0x9ca74fdc => 25
	i32 2633051222, ; 111: Xamarin.AndroidX.Lifecycle.LiveData => 0x9cf12c56 => 59
	i32 2732626843, ; 112: Xamarin.AndroidX.Activity => 0xa2e0939b => 35
	i32 2737747696, ; 113: Xamarin.AndroidX.AppCompat.AppCompatResources.dll => 0xa32eb6f0 => 38
	i32 2766581644, ; 114: Xamarin.Forms.Core => 0xa4e6af8c => 79
	i32 2778768386, ; 115: Xamarin.AndroidX.ViewPager.dll => 0xa5a0a402 => 76
	i32 2810250172, ; 116: Xamarin.AndroidX.CoordinatorLayout.dll => 0xa78103bc => 46
	i32 2819470561, ; 117: System.Xml.dll => 0xa80db4e1 => 33
	i32 2853208004, ; 118: Xamarin.AndroidX.ViewPager => 0xaa107fc4 => 76
	i32 2855708567, ; 119: Xamarin.AndroidX.Transition => 0xaa36a797 => 72
	i32 2903344695, ; 120: System.ComponentModel.Composition => 0xad0d8637 => 91
	i32 2905242038, ; 121: mscorlib.dll => 0xad2a79b6 => 9
	i32 2916838712, ; 122: Xamarin.AndroidX.ViewPager2.dll => 0xaddb6d38 => 77
	i32 2919462931, ; 123: System.Numerics.Vectors.dll => 0xae037813 => 28
	i32 2921128767, ; 124: Xamarin.AndroidX.Annotation.Experimental.dll => 0xae1ce33f => 37
	i32 2978675010, ; 125: Xamarin.AndroidX.DrawerLayout => 0xb18af942 => 51
	i32 3024354802, ; 126: Xamarin.AndroidX.Legacy.Support.Core.Utils => 0xb443fdf2 => 55
	i32 3033605958, ; 127: System.Memory.Data.dll => 0xb4d12746 => 25
	i32 3044182254, ; 128: FormsViewGroup => 0xb57288ee => 4
	i32 3111772706, ; 129: System.Runtime.Serialization => 0xb979e222 => 3
	i32 3124832203, ; 130: System.Threading.Tasks.Extensions => 0xba4127cb => 94
	i32 3201053252, ; 131: manipulatorMobileApp.dll => 0xbecc3244 => 6
	i32 3204380047, ; 132: System.Data.dll => 0xbefef58f => 85
	i32 3211777861, ; 133: Xamarin.AndroidX.DocumentFile => 0xbf6fd745 => 50
	i32 3247949154, ; 134: Mono.Security => 0xc197c562 => 95
	i32 3258312781, ; 135: Xamarin.AndroidX.CardView => 0xc235e84d => 44
	i32 3265893370, ; 136: System.Threading.Tasks.Extensions.dll => 0xc2a993fa => 94
	i32 3267021929, ; 137: Xamarin.AndroidX.AsyncLayoutInflater => 0xc2bacc69 => 42
	i32 3286872994, ; 138: SQLite-net.dll => 0xc3e9b3a2 => 14
	i32 3317135071, ; 139: Xamarin.AndroidX.CustomView.dll => 0xc5b776df => 49
	i32 3317144872, ; 140: System.Data => 0xc5b79d28 => 85
	i32 3340387945, ; 141: SkiaSharp => 0xc71a4669 => 13
	i32 3340431453, ; 142: Xamarin.AndroidX.Arch.Core.Runtime => 0xc71af05d => 41
	i32 3353484488, ; 143: Xamarin.AndroidX.Legacy.Support.Core.UI.dll => 0xc7e21cc8 => 54
	i32 3358260929, ; 144: System.Text.Json => 0xc82afec1 => 32
	i32 3360279109, ; 145: SQLitePCLRaw.core => 0xc849ca45 => 16
	i32 3362522851, ; 146: Xamarin.AndroidX.Core => 0xc86c06e3 => 47
	i32 3366347497, ; 147: Java.Interop => 0xc8a662e9 => 5
	i32 3374999561, ; 148: Xamarin.AndroidX.RecyclerView => 0xc92a6809 => 68
	i32 3395150330, ; 149: System.Runtime.CompilerServices.Unsafe.dll => 0xca5de1fa => 29
	i32 3404865022, ; 150: System.ServiceModel.Internals => 0xcaf21dfe => 93
	i32 3429136800, ; 151: System.Xml => 0xcc6479a0 => 33
	i32 3430777524, ; 152: netstandard => 0xcc7d82b4 => 1
	i32 3476120550, ; 153: Mono.Android => 0xcf3163e6 => 8
	i32 3485117614, ; 154: System.Text.Json.dll => 0xcfbaacae => 32
	i32 3486566296, ; 155: System.Transactions => 0xcfd0c798 => 86
	i32 3501239056, ; 156: Xamarin.AndroidX.AsyncLayoutInflater.dll => 0xd0b0ab10 => 42
	i32 3509114376, ; 157: System.Xml.Linq => 0xd128d608 => 34
	i32 3536029504, ; 158: Xamarin.Forms.Platform.Android.dll => 0xd2c38740 => 80
	i32 3558648585, ; 159: System.ClientModel => 0xd41cab09 => 20
	i32 3567349600, ; 160: System.ComponentModel.Composition.dll => 0xd4a16f60 => 91
	i32 3627220390, ; 161: Xamarin.AndroidX.Print.dll => 0xd832fda6 => 67
	i32 3632359727, ; 162: Xamarin.Forms.Platform => 0xd881692f => 81
	i32 3633644679, ; 163: Xamarin.AndroidX.Annotation.Experimental => 0xd8950487 => 37
	i32 3641597786, ; 164: Xamarin.AndroidX.Lifecycle.LiveData.Core => 0xd90e5f5a => 58
	i32 3672681054, ; 165: Mono.Android.dll => 0xdae8aa5e => 8
	i32 3676310014, ; 166: System.Web.Services.dll => 0xdb2009fe => 92
	i32 3682565725, ; 167: Xamarin.AndroidX.Browser => 0xdb7f7e5d => 43
	i32 3689375977, ; 168: System.Drawing.Common => 0xdbe768e9 => 88
	i32 3701090823, ; 169: manipulatorMobileApp.Android.dll => 0xdc9a2a07 => 0
	i32 3718780102, ; 170: Xamarin.AndroidX.Annotation => 0xdda814c6 => 36
	i32 3748608112, ; 171: System.Diagnostics.DiagnosticSource => 0xdf6f3870 => 22
	i32 3754567612, ; 172: SQLitePCLRaw.provider.e_sqlite3 => 0xdfca27bc => 18
	i32 3758932259, ; 173: Xamarin.AndroidX.Legacy.Support.V4 => 0xe00cc123 => 56
	i32 3786282454, ; 174: Xamarin.AndroidX.Collection => 0xe1ae15d6 => 45
	i32 3822602673, ; 175: Xamarin.AndroidX.Media => 0xe3d849b1 => 65
	i32 3829621856, ; 176: System.Numerics.dll => 0xe4436460 => 27
	i32 3876362041, ; 177: SQLite-net => 0xe70c9739 => 14
	i32 3885922214, ; 178: Xamarin.AndroidX.Transition.dll => 0xe79e77a6 => 72
	i32 3896760992, ; 179: Xamarin.AndroidX.Core.dll => 0xe843daa0 => 47
	i32 3920810846, ; 180: System.IO.Compression.FileSystem.dll => 0xe9b2d35e => 90
	i32 3921031405, ; 181: Xamarin.AndroidX.VersionedParcelable.dll => 0xe9b630ed => 75
	i32 3945713374, ; 182: System.Data.DataSetExtensions.dll => 0xeb2ecede => 87
	i32 3955647286, ; 183: Xamarin.AndroidX.AppCompat.dll => 0xebc66336 => 39
	i32 4023392905, ; 184: System.IO.Pipelines => 0xefd01a89 => 24
	i32 4025784931, ; 185: System.Memory => 0xeff49a63 => 26
	i32 4105002889, ; 186: Mono.Security.dll => 0xf4ad5f89 => 95
	i32 4151237749, ; 187: System.Core => 0xf76edc75 => 21
	i32 4182413190, ; 188: Xamarin.AndroidX.Lifecycle.ViewModelSavedState.dll => 0xf94a8f86 => 62
	i32 4213026141, ; 189: System.Diagnostics.DiagnosticSource.dll => 0xfb1dad5d => 22
	i32 4260525087, ; 190: System.Buffers => 0xfdf2741f => 19
	i32 4292120959 ; 191: Xamarin.AndroidX.Lifecycle.ViewModelSavedState => 0xffd4917f => 62
], align 4
@assembly_image_cache_indices = local_unnamed_addr constant [192 x i32] [
	i32 60, i32 84, i32 10, i32 79, i32 70, i32 70, i32 45, i32 71, ; 0..7
	i32 43, i32 55, i32 92, i32 11, i32 59, i32 53, i32 35, i32 27, ; 8..15
	i32 57, i32 17, i32 26, i32 78, i32 52, i32 9, i32 23, i32 53, ; 16..23
	i32 64, i32 13, i32 86, i32 7, i32 90, i32 49, i32 31, i32 75, ; 24..31
	i32 40, i32 34, i32 20, i32 15, i32 89, i32 88, i32 11, i32 67, ; 32..39
	i32 84, i32 10, i32 57, i32 4, i32 69, i32 39, i32 81, i32 61, ; 40..47
	i32 23, i32 12, i32 73, i32 40, i32 74, i32 16, i32 51, i32 93, ; 48..55
	i32 69, i32 65, i32 46, i32 29, i32 82, i32 89, i32 38, i32 50, ; 56..63
	i32 3, i32 63, i32 77, i32 48, i32 2, i32 30, i32 83, i32 17, ; 64..71
	i32 44, i32 24, i32 71, i32 21, i32 52, i32 7, i32 63, i32 83, ; 72..79
	i32 78, i32 82, i32 41, i32 66, i32 19, i32 61, i32 12, i32 58, ; 80..87
	i32 0, i32 30, i32 28, i32 54, i32 18, i32 80, i32 2, i32 73, ; 88..95
	i32 64, i32 66, i32 56, i32 68, i32 36, i32 15, i32 1, i32 5, ; 96..103
	i32 87, i32 60, i32 31, i32 74, i32 48, i32 6, i32 25, i32 59, ; 104..111
	i32 35, i32 38, i32 79, i32 76, i32 46, i32 33, i32 76, i32 72, ; 112..119
	i32 91, i32 9, i32 77, i32 28, i32 37, i32 51, i32 55, i32 25, ; 120..127
	i32 4, i32 3, i32 94, i32 6, i32 85, i32 50, i32 95, i32 44, ; 128..135
	i32 94, i32 42, i32 14, i32 49, i32 85, i32 13, i32 41, i32 54, ; 136..143
	i32 32, i32 16, i32 47, i32 5, i32 68, i32 29, i32 93, i32 33, ; 144..151
	i32 1, i32 8, i32 32, i32 86, i32 42, i32 34, i32 80, i32 20, ; 152..159
	i32 91, i32 67, i32 81, i32 37, i32 58, i32 8, i32 92, i32 43, ; 160..167
	i32 88, i32 0, i32 36, i32 22, i32 18, i32 56, i32 45, i32 65, ; 168..175
	i32 27, i32 14, i32 72, i32 47, i32 90, i32 75, i32 87, i32 39, ; 176..183
	i32 24, i32 26, i32 95, i32 21, i32 62, i32 22, i32 19, i32 62 ; 192..191
], align 4

@marshal_methods_number_of_classes = local_unnamed_addr constant i32 0, align 4

; marshal_methods_class_cache
@marshal_methods_class_cache = global [0 x %struct.MarshalMethodsManagedClass] [
], align 4; end of 'marshal_methods_class_cache' array


@get_function_pointer = internal unnamed_addr global void (i32, i32, i32, i8**)* null, align 4

; Function attributes: "frame-pointer"="all" "min-legal-vector-width"="0" mustprogress nofree norecurse nosync "no-trapping-math"="true" nounwind sspstrong "stack-protector-buffer-size"="8" "target-cpu"="generic" "target-features"="+armv7-a,+d32,+dsp,+fp64,+neon,+thumb-mode,+vfp2,+vfp2sp,+vfp3,+vfp3d16,+vfp3d16sp,+vfp3sp,-aes,-fp-armv8,-fp-armv8d16,-fp-armv8d16sp,-fp-armv8sp,-fp16,-fp16fml,-fullfp16,-sha2,-vfp4,-vfp4d16,-vfp4d16sp,-vfp4sp" uwtable willreturn writeonly
define void @xamarin_app_init (void (i32, i32, i32, i8**)* %fn) local_unnamed_addr #0
{
	store void (i32, i32, i32, i8**)* %fn, void (i32, i32, i32, i8**)** @get_function_pointer, align 4
	ret void
}

; Names of classes in which marshal methods reside
@mm_class_names = local_unnamed_addr constant [0 x i8*] zeroinitializer, align 4
@__MarshalMethodName_name.0 = internal constant [1 x i8] c"\00", align 1

; mm_method_names
@mm_method_names = local_unnamed_addr constant [1 x %struct.MarshalMethodName] [
	; 0
	%struct.MarshalMethodName {
		i64 0, ; id 0x0; name: 
		i8* getelementptr inbounds ([1 x i8], [1 x i8]* @__MarshalMethodName_name.0, i32 0, i32 0); name
	}
], align 8; end of 'mm_method_names' array


attributes #0 = { "min-legal-vector-width"="0" mustprogress nofree norecurse nosync "no-trapping-math"="true" nounwind sspstrong "stack-protector-buffer-size"="8" uwtable willreturn writeonly "frame-pointer"="all" "target-cpu"="generic" "target-features"="+armv7-a,+d32,+dsp,+fp64,+neon,+thumb-mode,+vfp2,+vfp2sp,+vfp3,+vfp3d16,+vfp3d16sp,+vfp3sp,-aes,-fp-armv8,-fp-armv8d16,-fp-armv8d16sp,-fp-armv8sp,-fp16,-fp16fml,-fullfp16,-sha2,-vfp4,-vfp4d16,-vfp4d16sp,-vfp4sp" }
attributes #1 = { "min-legal-vector-width"="0" mustprogress "no-trapping-math"="true" nounwind sspstrong "stack-protector-buffer-size"="8" uwtable "frame-pointer"="all" "target-cpu"="generic" "target-features"="+armv7-a,+d32,+dsp,+fp64,+neon,+thumb-mode,+vfp2,+vfp2sp,+vfp3,+vfp3d16,+vfp3d16sp,+vfp3sp,-aes,-fp-armv8,-fp-armv8d16,-fp-armv8d16sp,-fp-armv8sp,-fp16,-fp16fml,-fullfp16,-sha2,-vfp4,-vfp4d16,-vfp4d16sp,-vfp4sp" }
attributes #2 = { nounwind }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}
!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{i32 1, !"min_enum_size", i32 4}
!3 = !{!"Xamarin.Android remotes/origin/d17-5 @ 45b0e144f73b2c8747d8b5ec8cbd3b55beca67f0"}
!llvm.linker.options = !{}
