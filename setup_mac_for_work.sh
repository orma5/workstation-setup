#!/bin/bash

# Function to prompt the user and check for 'y' or 'n' VERIFIED
prompt_for_confirmation() {
    while true; do
        read -p "Do you want to run this step? (Y/n) [default: y]: " yn
        case $yn in
            [Yy]* | "" )
                return 0  # Exit the function and allow the code block to run
                ;;
            [Nn]* )
                return 1  # Exit the function and skip the code block
                ;;
            * )
                echo "Please answer y or n."
                ;;
        esac
    done
}

echo "********** SETTING UP MAC FOR WORK **********"
echo ""
sudo -v

#keep sudo alive VERIFIED
while true; do sudo -n true; sleep 60; done 2>/dev/null &

# install homebrew with xcode clt VERIFIED
echo "********** DOWNLOAD AND INSTALL HOMEBREW WITH XCODE COMMAND LINE TOOLS **********"
if prompt_for_confirmation; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  #put brew on path
  echo >> /Users/po/.zprofile
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/po/.zprofile
  eval "$(/opt/homebrew/bin/brew shellenv)"
  echo ""
else
  echo "skipped"
fi

# install applications VERIFIED
echo "********** DOWNLOAD AND INSTALL APPLICATIONS USING HOMEBREW **********"
if prompt_for_confirmation; then
  brew install --cask iterm2 > /dev/null 2>&1
  echo "iterm2 installed"

  brew install --cask slack > /dev/null 2>&1
  echo "slack installed"

  brew install --cask openvpn-connect > /dev/null 2>&1
  echo "openvpn installed"

  brew install --cask intellij-idea > /dev/null 2>&1
  echo "intellij idea installed"

  brew install --cask 1password > /dev/null 2>&1
  echo "1password installed"

  brew install --cask 1password-cli > /dev/null 2>&1
  echo "1password-cli installed"

  brew install --cask windows-app > /dev/null 2>&1
  echo "windows app installed"

  brew install --cask postman > /dev/null 2>&1
  echo "postman installed"

  brew install --cask google-chrome > /dev/null 2>&1
  echo "google chrome installed"

  brew install --cask visual-studio-code > /dev/null 2>&1
  echo "visual studio code installed"

  brew install --cask teamviewer > /dev/null 2>&1
  echo "teamviewer installed"

  brew install --cask claude-code > /dev/null 2>&1
  echo "claude code installed"

  brew install kubernetes-cli > /dev/null 2>&1
  echo "kubernetes cli installed"

  brew install node > /dev/null 2>&1
  echo "node installed"

  brew install openjdk@21 > /dev/null 2>&1
  echo "openjdk 21 installed"

  brew install pipenv > /dev/null 2>&1
  echo "pipenv installed"

  brew install pyenv > /dev/null 2>&1
  echo "pyenv installed"

  brew install wget > /dev/null 2>&1
  echo "wget installed"

  brew install dockutil > /dev/null 2>&1
  echo "dockutil installed"

  brew install awscli > /dev/null 2>&1
  echo "aws cli installed"
  echo ""

  brew install --cask gcloud-cli > /dev/null 2>&1
  echo "gcp cli installed"
  echo ""

else
  echo "skipped"
fi

# create folders VERIFIED
echo "********** CREATE FOLDERS **********"
if prompt_for_confirmation; then
  mkdir ~/Development
  echo "Created Development folder"
  mkdir ~/Development/Projects
  echo "Created Development/Project folder"
  mkdir ~/Development/Scripts
  echo "Created Development/Scripts folder"
  mkdir ~/Development/tmp
  echo "Created Development/tmp folder"
  echo ""
else
  echo "skipped"
fi

# download and apply dotfiles and application files VERIFIED
echo "********** DOWNLOAD DOTFILES AND APPLICATION CONFIG FILES **********"
if prompt_for_confirmation; then
  git clone https://github.com/orma5/workstation-setup.git ~/Development/Scripts/workstation-setup > /dev/null 2>&1
  cp ~/Development/Scripts/workstation-setup/work/macos/dotfiles/.gitconfig ~/.gitconfig
  cp ~/Development/Scripts/workstation-setup/work/macos/dotfiles/.global-gitignore ~/.global-gitignore
  echo ""
else
  echo "skipped"
fi

echo "********** APPLICATION SETUP **********"
if prompt_for_confirmation; then

  # 1Password
  echo "loging in to 1password"
  op account add --address "https://my.1password.com"

  # google chrome
  echo "press any key to open chrome. Log in and return here and press enter"
  read
  open -a "Google Chrome"
  echo "press enter when done"
  read

  # open vpn
  echo "Fetching credentials for OpenVPN"
  echo "Enter the name of the 1Password item for OpenVPN:"
  read VPN_ITEM_NAME
  echo "Enter the OpenVPN server name:"
  read VPN_SERVER_NAME

  # Fetch credentials from 1Password
  VPN_USERNAME=$(op item get "$VPN_ITEM_NAME" --field username)
  VPN_PASSWORD=$(op item get "$VPN_ITEM_NAME" --reveal --field password)

  # Check if credentials were retrieved
  if [ -z "$VPN_USERNAME" ] || [ -z "$VPN_PASSWORD" ]; then
    echo "Failed to fetch credentials from 1Password. Please check the item name and try again."
  else
    # Download configuration file
    wget --user="$VPN_USERNAME" --password="$VPN_PASSWORD" --no-check-certificate "https://$VPN_SERVER_NAME:943/rest/GetUserlogin" -O ~/Download/client.ovpn

    if [ $? -eq 0 ]; then
      echo "Configuration downloaded as 'client.ovpn'."
    else
      echo "Failed to download the OpenVPN config file. Please download it manually."
    fi
  fi

  # SLACK
  echo "press any key to open Slack to login"
  read
  open -a "Slack"
  echo "press enter when done"
  read

  # IntelliJ
  echo "press any key to open IntelliJ to login and install material colors theme"
  read
  open -a "IntelliJ IDEA"
  echo "press enter when done"
  read

  #VS Code
  echo "press any key to open vSCODE to login and install profiles"
  read
  open -a "visual studio code"
  echo "press enter when done"
  read

  # windows app
  echo "press any key to open remote desktop and add connections"
  read
  open -a "Windows App"
  echo "press enter when done"
  read
else
  echo "skipped"
fi

echo "********** MACOS SETUP **********"
if prompt_for_confirmation; then

  # Save to disk (not to iCloud) by default
  defaults write NSGlobalDomain NSDocumentSaveNewDocumentsToCloud -bool false

  # Automatically quit printer app once the print jobs complete
  defaults write com.apple.print.PrintingPrefs "Quit When Finished" -bool true

  # Disable the “Are you sure you want to open this application?” dialog
  defaults write com.apple.LaunchServices LSQuarantine -bool false

  # Trackpad: enable tap to click for this user and for the login screen
  defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true
  defaults -currentHost write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
  defaults write NSGlobalDomain com.apple.mouse.tapBehavior -int 1

  # Increase sound quality for Bluetooth headphones/headsets
  defaults write com.apple.BluetoothAudioAgent "Apple Bitpool Min (editable)" -int 40

  # Enable full keyboard access for all controls
  # (e.g. enable Tab in modal dialogs)
  defaults write NSGlobalDomain AppleKeyboardUIMode -int 3

  # Disable press-and-hold for keys in favor of key repeat
  defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false

  # Set a blazingly fast keyboard repeat rate
  defaults write NSGlobalDomain KeyRepeat -int 1
  defaults write NSGlobalDomain InitialKeyRepeat -int 10

  # Stop iTunes from responding to the keyboard media keys
  launchctl unload -w /System/Library/LaunchAgents/com.apple.rcd.plist 2> /dev/null

  # Enable lid wakeup
  sudo pmset -a lidwake 1

  # Sleep the display after 15 minutes
  sudo pmset -a displaysleep 15

  # Disable machine sleep while charging
  sudo pmset -c sleep 0

  # Set machine sleep to 5 minutes on battery
  sudo pmset -b sleep 5

  # Set standby delay to 24 hours (default is 1 hour)
  sudo pmset -a standbydelay 86400

  # Never go into computer sleep mode
  sudo systemsetup -setcomputersleep Off > /dev/null

  # Hibernation mode
  # 0: Disable hibernation (speeds up entering sleep mode)
  # 3: Copy RAM to disk so the system state can still be restored in case of a
  #    power failure.
  sudo pmset -a hibernatemode 0

  # Remove the sleep image file to save disk space
  sudo rm /private/var/vm/sleepimage
  # Create a zero-byte file instead…
  sudo touch /private/var/vm/sleepimage
  # …and make sure it can’t be rewritten
  sudo chflags uchg /private/var/vm/sleepimage

  # Require password immediately after sleep or screen saver begins
  defaults write com.apple.screensaver askForPassword -int 1
  defaults write com.apple.screensaver askForPasswordDelay -int 0

  # Save screenshots to the desktop
  defaults write com.apple.screencapture location -string "${HOME}/Desktop"

  # Save screenshots in PNG format (other options: BMP, GIF, JPG, PDF, TIFF)
  defaults write com.apple.screencapture type -string "png"

  # Disable shadow in screenshots
  defaults write com.apple.screencapture disable-shadow -bool true

  # Enable subpixel font rendering on non-Apple LCDs
  # Reference: https://github.com/kevinSuttle/macOS-Defaults/issues/17#issuecomment-266633501
  defaults write NSGlobalDomain AppleFontSmoothing -int 1

  # Enable HiDPI display modes (requires restart)
  sudo defaults write /Library/Preferences/com.apple.windowserver DisplayResolutionEnabled -bool true

  # Finder: allow quitting via ⌘ + Q; doing so will also hide desktop icons
  defaults write com.apple.finder QuitMenuItem -bool true

  # Finder: disable window animations and Get Info animations
  defaults write com.apple.finder DisableAllAnimations -bool true

  # Set Desktop as the default location for new Finder windows
  # For other paths, use `PfLo` and `file:///full/path/here/`
  defaults write com.apple.finder NewWindowTarget -string "PfDe"
  defaults write com.apple.finder NewWindowTargetPath -string "file://${HOME}/Desktop/"

  # Show icons for hard drives, servers, and removable media on the desktop
  defaults write com.apple.finder ShowExternalHardDrivesOnDesktop -bool true
  defaults write com.apple.finder ShowHardDrivesOnDesktop -bool true
  defaults write com.apple.finder ShowMountedServersOnDesktop -bool true
  defaults write com.apple.finder ShowRemovableMediaOnDesktop -bool true

  # Finder: show hidden files by default
  defaults write com.apple.finder AppleShowAllFiles -bool true

  # Finder: show all filename extensions
  defaults write NSGlobalDomain AppleShowAllExtensions -bool true

  # Finder: show status bar
  defaults write com.apple.finder ShowStatusBar -bool true

  # Finder: show path bar
  defaults write com.apple.finder ShowPathbar -bool true

  # Display full POSIX path as Finder window title
  defaults write com.apple.finder _FXShowPosixPathInTitle -bool true

  # Keep folders on top when sorting by name
  defaults write com.apple.finder _FXSortFoldersFirst -bool true

  # When performing a search, search the current folder by default
  defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"

  # Disable the warning when changing a file extension
  defaults write com.apple.finder FXEnableExtensionChangeWarning -bool false

  # Enable spring loading for directories
  defaults write NSGlobalDomain com.apple.springing.enabled -bool true

  # Remove the spring loading delay for directories
  defaults write NSGlobalDomain com.apple.springing.delay -float 0

  # Avoid creating .DS_Store files on network or USB volumes
  defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true
  defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true

  # Disable disk image verification
  defaults write com.apple.frameworks.diskimages skip-verify -bool true
  defaults write com.apple.frameworks.diskimages skip-verify-locked -bool true
  defaults write com.apple.frameworks.diskimages skip-verify-remote -bool true

  # Automatically open a new Finder window when a volume is mounted
  defaults write com.apple.frameworks.diskimages auto-open-ro-root -bool true
  defaults write com.apple.frameworks.diskimages auto-open-rw-root -bool true
  defaults write com.apple.finder OpenWindowForNewRemovableDisk -bool true

  # Use list view in all Finder windows by default
  # Four-letter codes for the other view modes: `icnv`, `clmv`, `glyv`
  defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"

  # Disable the warning before emptying the Trash
  defaults write com.apple.finder WarnOnEmptyTrash -bool false

  # Show the ~/Library folder
  chflags nohidden ~/Library && xattr -d com.apple.FinderInfo ~/Library

  # Show the /Volumes folder
  sudo chflags nohidden /Volumes

  # Expand the following File Info panes:
  # “General”, “Open with”, and “Sharing & Permissions”
  defaults write com.apple.finder FXInfoPanesExpanded -dict \
    General -bool true \
    OpenWith -bool true \
    Privileges -bool true

  # Set the icon size of Dock items to 36 pixels
  defaults write com.apple.dock tilesize -int 36

  # Minimize windows into their application’s icon
  defaults write com.apple.dock minimize-to-application -bool true

  # Show indicator lights for open applications in the Dock
  defaults write com.apple.dock show-process-indicators -bool true

  # Disable Dashboard
  defaults write com.apple.dashboard mcx-disabled -bool true

  # Don’t show Dashboard as a Space
  defaults write com.apple.dock dashboard-in-overlay -bool true

  # Don’t automatically rearrange Spaces based on most recent use
  defaults write com.apple.dock mru-spaces -bool false

  # Don’t show recent applications in Dock
  defaults write com.apple.dock show-recents -bool false

  # Don’t display the annoying prompt when quitting iTerm
  defaults write com.googlecode.iterm2 PromptOnQuit -bool false

  # Don’t display the annoying prompt when quitting iTerm
  defaults write com.googlecode.iterm2 PromptOnQuit -bool false

  # Show the main window when launching Activity Monitor
  defaults write com.apple.ActivityMonitor OpenMainWindow -bool true

  # Visualize CPU usage in the Activity Monitor Dock icon
  defaults write com.apple.ActivityMonitor IconType -int 5

  # Show all processes in Activity Monitor
  defaults write com.apple.ActivityMonitor ShowCategory -int 0

  # Sort Activity Monitor results by CPU usage
  defaults write com.apple.ActivityMonitor SortColumn -string "CPUUsage"
  defaults write com.apple.ActivityMonitor SortDirection -int 0

  # Enable the debug menu in Disk Utility
  defaults write com.apple.DiskUtility DUDebugMenuEnabled -bool true
  defaults write com.apple.DiskUtility advanced-image-options -bool true

  # Disable the all too sensitive backswipe on trackpads
  defaults write com.google.Chrome AppleEnableSwipeNavigateWithScrolls -bool false
  defaults write com.google.Chrome.canary AppleEnableSwipeNavigateWithScrolls -bool false

  # Disable the all too sensitive backswipe on Magic Mouse
  defaults write com.google.Chrome AppleEnableMouseSwipeNavigateWithScrolls -bool false
  defaults write com.google.Chrome.canary AppleEnableMouseSwipeNavigateWithScrolls -bool false

  # Use the system-native print preview dialog
  defaults write com.google.Chrome DisablePrintPreview -bool true
  defaults write com.google.Chrome.canary DisablePrintPreview -bool true

  # Expand the print dialog by default
  defaults write com.google.Chrome PMPrintingExpandedStateForPrint2 -bool true
  defaults write com.google.Chrome.canary PMPrintingExpandedStateForPrint2 -bool true

  echo "setup top bar to include sound, displays, bluetooth and  press enter when done"
  read
  echo "update desktop background and press enter when done"
  read
else
  echo "skipped"
fi


echo "********** SETUP SSH (KEYS, ROOT CERTIFICATES, LOGINS, CONFIG) **********"
if prompt_for_confirmation; then
  # Prompt for work email and generate work SSH key
  read -p "Enter your work email (for GitLab): " WORK_EMAIL
  ssh-keygen -t rsa -C "$WORK_EMAIL" -b 4096

  # Prompt for GitHub email and generate personal SSH key
  read -p "Enter your personal email (for GitHub): " PERSONAL_EMAIL
  ssh-keygen -C "$PERSONAL_EMAIL"

  echo "Add generated work public key to GitLab and press enter when done"
  read
  echo "Add generated personal public key to GitHub and press enter when done"
  read
  echo "Download root certificate and press enter when done"
  read
  echo "Download hosts config and press enter when done"
  read
  echo "Create kubeconfig using AWS CLI"
  read
  aws configure

  # Prompt for EKS cluster config (region is omitted)
  read -p "Enter the EKS cluster name: " CLUSTER_NAME
  if [ -z "$CLUSTER_NAME" ]; then
    echo "❌ Cluster name cannot be empty."
    exit 1
  fi

  echo "⏳ Updating kubeconfig for cluster: $CLUSTER_NAME using default AWS region..."
  aws eks update-kubeconfig --name "$CLUSTER_NAME"

  if [ $? -eq 0 ]; then
    echo "✅ kubeconfig updated successfully."
  else
    echo "❌ Failed to update kubeconfig."
  fi

else
  echo "skipped"
fi

echo "********** CLONE DEVELOPMENT PROJECTS **********"
if prompt_for_confirmation; then
  echo "clone projects from gitlab/github and press enter when done"
  read
else
  echo "skipped"
fi

echo "********** SETUP DEVELOPMENT ENVIRONMENTS **********"
if prompt_for_confirmation; then
  echo "Downloading python versions"
  pyenv install 3.7.17
  pyenv install $(pyenv install --list | grep -E "^\s*[0-9]+\.[0-9]+\.[0-9]+$" | grep -v - | tail -1)
  echo ""
  echo "create virtual environment for projects and scripts and press enter when done"
  read
  echo "pip install for each development project and press enter when done"
  read
  echo "setup config and env files for python and java projects and press enter when done"
  read
  echo "setup database credentials in IDE and press enter when done"
  read
  echo "import profile(s) to vscode and press enter when done"
  read
else
  echo "skipped"
fi

# setup dock
echo "********** STEP 3. SETUP DOCK AND WALLPAPER **********"
if prompt_for_confirmation; then
  dockutil --remove all --no-restart > /dev/null 2>&1
  dockutil --add "/Applications/Google Chrome.app" --no-restart > /dev/null 2>&1
  dockutil --add "/Applications/Visual Studio Code.app" --no-restart > /dev/null 2>&1
  dockutil --add "/Applications/iterm.app" --no-restart > /dev/null 2>&1
  dockutil --add "/Applications/Intellij IDEA.app" --no-restart > /dev/null 2>&1
  dockutil --add "/Applications/System Settings.app" --no-restart > /dev/null 2>&1
  dockutil --add "~/Downloads" --section others --view auto --display folder --no-restart > /dev/null 2>&1
  /usr/libexec/PlistBuddy -c "Set :AllSpacesAndDisplays:Linked:Content:Choices:0:Provider com.apple.wallpaper.choice.sonoma" ~/Library/Application\ Support/com.apple.wallpaper/Store/Index.plist
  /usr/libexec/PlistBuddy -c "Set :SystemDefault:Linked:Content:Choices:0:Provider com.apple.wallpaper.choice.sonoma" ~/Library/Application\ Support/com.apple.wallpaper/Store/Index.plist
  killall Dock > /dev/null 2>&1
  echo ""
else
  echo "skipped"
fi

# setup terminal
echo "********** SETUP TERMINAL **********"
if prompt_for_confirmation; then
  sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
  NEW_THEME="powerlevel10k/powerlevel10k"
  ZSHRC_PATH="$HOME/.zshrc"
  if grep -q '^ZSH_THEME=' "$ZSHRC_PATH"; then
    sed -i.bak "s|^ZSH_THEME=.*|ZSH_THEME=\"$NEW_THEME\"|" "$ZSHRC_PATH"
  else
    echo "ZSH_THEME=\"$NEW_THEME\"" >> "$ZSHRC_PATH"
  fi
  zsh -c "source $ZSHRC_PATH"
  wget -O ~/Downloads/MaterialDesignColors.itermcolors https://raw.githubusercontent.com/mbadolato/iTerm2-Color-Schemes/master/schemes/MaterialDesignColors.itermcolors
  echo "open iterm and setup colors, fonts and terminal size and press enter when done"
  read
  echo ""
else
  echo "skipped"
fi

echo "********** SETUP COMPLETE **********"
echo "Press any key to reboot computer"
read
sudo reboot
