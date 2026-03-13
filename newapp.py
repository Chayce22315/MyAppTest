import os
import uuid

# ------------------------
# CONFIG
# ------------------------
project_name = "MyApp"  # change for each new app
repo_root = os.getcwd()
app_folder = os.path.join(repo_root, project_name)
xcodeproj_folder = os.path.join(app_folder, f"{project_name}.xcodeproj")

# ------------------------
# UTILITY
# ------------------------
def gen_uuid():
    return uuid.uuid4().hex[:24].upper()

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip())

# ------------------------
# 1️⃣ Create minimal Xcode project
# ------------------------
project_uuid = gen_uuid()
main_target_uuid = gen_uuid()
debug_conf_uuid = gen_uuid()
release_conf_uuid = gen_uuid()
build_config_list_uuid = gen_uuid()
scheme_uuid = gen_uuid()  # new UUID for shared scheme

pbxproj_content = f"""
// !$*UTF8*$!
{{
  archiveVersion = 1;
  classes = {{}};
  objectVersion = 56;
  objects = {{

    {project_uuid} = {{
      isa = PBXProject;
      attributes = {{
        LastUpgradeCheck = 1300;
      }};
      buildConfigurationList = {build_config_list_uuid};
      compatibilityVersion = "Xcode 16.0";
      developmentRegion = en;
      hasScannedForEncodings = 0;
      knownRegions = (en);
      mainGroup = {project_uuid}G;
      targets = ({main_target_uuid});
    }};

    {build_config_list_uuid} = {{
      isa = XCConfigurationList;
      buildConfigurations = ({debug_conf_uuid}, {release_conf_uuid});
      defaultConfigurationIsVisible = 0;
      defaultConfigurationName = Release;
    }};

    {debug_conf_uuid} = {{
      isa = XCBuildConfiguration;
      name = Debug;
      buildSettings = {{
        PRODUCT_NAME = "{project_name}";
      }};
    }};

    {release_conf_uuid} = {{
      isa = XCBuildConfiguration;
      name = Release;
      buildSettings = {{
        PRODUCT_NAME = "{project_name}";
      }};
    }};

    {main_target_uuid} = {{
      isa = PBXNativeTarget;
      name = "{project_name}";
      buildConfigurationList = {build_config_list_uuid};
      buildPhases = ();
      buildRules = ();
      dependencies = ();
      productName = "{project_name}";
      productType = "com.apple.product-type.application";
    }};

    {project_uuid}G = {{
      isa = PBXGroup;
      children = ();
      sourceTree = "<group>";
    }};
  }};
  rootObject = {project_uuid};
}}
"""
write_file(os.path.join(xcodeproj_folder, "project.pbxproj"), pbxproj_content)

# ------------------------
# 2️⃣ Add main.swift
# ------------------------
sources_path = os.path.join(app_folder, "Sources")
main_swift = """
import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        let vc = UIViewController()
        vc.view.backgroundColor = .systemOrange
        window?.rootViewController = vc
        window?.makeKeyAndVisible()
        return true
    }
}
"""
write_file(os.path.join(sources_path, "main.swift"), main_swift)

# ------------------------
# 3️⃣ Add Info.plist
# ------------------------
info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{project_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.example.{project_name.lower()}</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
</dict>
</plist>
"""
write_file(os.path.join(app_folder, "Info.plist"), info_plist)

# ------------------------
# 4️⃣ Add exportOptions.plist
# ------------------------
export_options = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>development</string>
    <key>signingStyle</key>
    <string>automatic</string>
</dict>
</plist>
"""
write_file(os.path.join(app_folder, "exportOptions.plist"), export_options)

# ------------------------
# 5️⃣ Add GitHub Actions workflow (with upload-artifact v4 + auto scheme)
# ------------------------
workflow_folder = os.path.join(app_folder, ".github", "workflows")
workflow_content = f"""
name: iOS Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: macos-latest

    steps:
      - uses: actions/checkout@v4

      - name: List Xcode project
        run: |
          xcodebuild -project {project_name}/{project_name}.xcodeproj -list

      - name: Create shared scheme
        run: |
          mkdir -p {project_name}/{project_name}.xcodeproj/xcshareddata/xcschemes
          cat > {project_name}/{project_name}.xcodeproj/xcshareddata/xcschemes/{project_name}.xcscheme <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion="1500"
   version="1.7"
   identifier="{scheme_uuid}">
   <BuildAction
      parallelizeBuildables="YES"
      buildImplicitDependencies="YES">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting="YES"
            buildForRunning="YES"
            buildForProfiling="YES"
            buildForArchiving="YES"
            buildForAnalyzing="YES">
            <BuildableReference
               BuildableIdentifier="primary"
               BlueprintIdentifier="PROJECT_TARGET_ID"
               BuildableName="{project_name}.app"
               BlueprintName="{project_name}"
               ReferencedContainer="container:{project_name}.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
</Scheme>
EOF

      - name: Archive app
        run: |
          xcodebuild -project {project_name}/{project_name}.xcodeproj \\
                     -scheme {project_name} \\
                     -configuration Release \\
                     -archivePath $PWD/build/{project_name}.xcarchive archive

      - name: Export .ipa
        run: |
          mkdir -p build/ipa
          xcodebuild -exportArchive \\
                     -archivePath $PWD/build/{project_name}.xcarchive \\
                     -exportPath $PWD/build/ipa \\
                     -exportOptionsPlist {project_name}/exportOptions.plist

      - name: Upload .ipa
        uses: actions/upload-artifact@v4
        with:
          name: {project_name}-ipa
          path: build/ipa
"""
write_file(os.path.join(workflow_folder, "ios-build.yml"), workflow_content)

print("✅ newapp.py: full buildable iOS project generated with workflow, auto scheme, .xcodeproj, main.swift, Info.plist, exportOptions.plist!")