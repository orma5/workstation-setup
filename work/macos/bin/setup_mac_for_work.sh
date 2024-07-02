#!/bin/bash

# Function to prompt the user and check for 'y' or 'n'
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

# install homebrew with xcode clt
echo "********** STEP 1. DOWNLOAD AND INSTALL HOMEBREW WITH XCODE COMMAND LINE TOOLS **********"
if prompt_for_confirmation; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  echo ""
else
  echo "skipping STEP 1."
fi

# install applications
echo "********** STEP 2. DOWNLOAD AND INSTALL APPLICATIONS USING HOMEBREW **********"
if prompt_for_confirmation; then
  brew install iterm2 > /dev/null 2>&1
  echo "iterm2 installed"

  brew install slack > /dev/null 2>&1
  echo "slack installed"

  brew install openvpn-connect > /dev/null 2>&1
  echo "openvpn installed"

  brew install intellij-idea > /dev/null 2>&1
  echo "intellij idea installed"

  brew install docker > /dev/null 2>&1
  echo "docker installed"

  brew install 1password > /dev/null 2>&1
  echo "1password installed"

  brew install microsoft-remote-desktop > /dev/null 2>&1
  echo "microsoft remote desktop installed"

  brew install postman > /dev/null 2>&1
  echo "postman installed"

  brew install teamviewer > /dev/null 2>&1
  echo "teamviewer installed"

  brew install google-chrome > /dev/null 2>&1
  echo "google chrome installed"

  brew install spotify > /dev/null 2>&1
  echo "spotify installed"

  brew install visual-studio-code > /dev/null 2>&1
  echo "visual studio code installed"

  brew install google-cloud-sdk > /dev/null 2>&1
  echo "google cloud sdk installed"

  brew install kubernetes-cli > /dev/null 2>&1
  echo "kubernetes cli installed"

  brew install node > /dev/null 2>&1
  echo "node installed"

  brew install openjdk@8 > /dev/null 2>&1
  echo "openjdk 8 installed"

  brew install openjdk > /dev/null 2>&1
  echo "openjdk installed"

  brew install pyenv > /dev/null 2>&1
  echo "pyenv installed"

  brew install wget > /dev/null 2>&1
  echo "wget installed"

  brew install sqlite > /dev/null 2>&1
  echo "sqlite installed"

  brew install dockutil > /dev/null 2>&1
  echo "dockutil installed"
  echo ""
else 
  echo "skipping STEP 2."
fi

# setup dock
echo "********** STEP 3. SETUP DOCK AND WALLPAPER **********"
if prompt_for_confirmation; then
  /usr/local/bin/dockutil --remove all --no-restart > /dev/null 2>&1
  /usr/local/bin/dockutil --add "/Applications/Google Chrome.app" --no-restart > /dev/null 2>&1
  /usr/local/bin/dockutil --add "/Applications/Visual Studio Code.app" --no-restart > /dev/null 2>&1
  /usr/local/bin/dockutil --add "/Applications/iterm.app" --no-restart > /dev/null 2>&1
  /usr/local/bin/dockutil --add "/Applications/Intellij IDEA.app" --no-restart > /dev/null 2>&1
  /usr/local/bin/dockutil --add "/Applications/System Settings.app" --no-restart > /dev/null 2>&1
  /usr/local/bin/dockutil --add "~/Downloads" --section others --view auto --display folder --no-restart > /dev/null 2>&1
  /usr/libexec/PlistBuddy -c "Set :AllSpacesAndDisplays:Linked:Content:Choices:0:Provider com.apple.wallpaper.choice.sonoma" ~/Library/Application\ Support/com.apple.wallpaper/Store/Index.plist
  /usr/libexec/PlistBuddy -c "Set :SystemDefault:Linked:Content:Choices:0:Provider com.apple.wallpaper.choice.sonoma" ~/Library/Application\ Support/com.apple.wallpaper/Store/Index.plist
  killall Dock > /dev/null 2>&1
  echo ""
else
  echo "skipping STEP 3."
fi

# setup terminal
# todo: instruct to open iterm2 and install colors and maybe do this step as last step
echo "********** STEP 4. SETUP TERMINAL **********"
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
else
  echo "skipping step 4."
fi

# create folders
echo "********** STEP 5. CREATE FOLDERS **********"
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
  echo "skipping STEP 5."
fi

# download and apply dotfiles and application files
# todo: dont kill all at the end
echo "********** STEP 6. DOWNLOAD AND APPLY DOTFILES AND APPLICATION CONFIG FILES **********"
if prompt_for_confirmation; then
  git clone https://github.com/orma5/workstation-setup.git ~/Downloads/tmp > /dev/null 2>&1
  cp ~/Downloads/tmp/work/macos/dotfiles/.macos ~/.macos
  cp ~/Downloads/tmp/work/macos/dotfiles/.gitconfig ~/.gitconfig
  cp ~/Downloads/tmp/work/macos/dotfiles/.global-gitignore ~/.global-gitignore
  yes | source ~/.macos > /dev/null 2>&1
  rm -rf ~/Downloads/tmp/
  echo ""
else
  echo "skipping STEP 6."
fi

echo "********** STEP 7. SETUP OPENVPN **********"
if prompt_for_confirmation; then
  echo "login to openvpn and fetch file and add to openvpn to login and press enter when done"
  read
else
  echo "skipping step 7."
fi

echo "********** STEP 7. CREATE SSH KEY AND ADD TO ONLINE APPLICATIONS AND GENERATE HOSTS CONFIG **********"
if prompt_for_confirmation; then
  ssh-keygen -f ~/.ssh/work-ed25519 -C "per-olof.markstrom@footway.com"
  ssh-keygen -f ~/.ssh/personal-ed25519 -C "po.markstrom@gmail.com"
  echo "Add generated work public key to gitlab and press enter when done"
  read
  echo "Add generated personal public key to github and press enter when done"
  read
  echo "Donwload root certificate and press enter when done"
  read
  echo "Donwload hosts config and press enter when done"
else
  echo "skipping step 7."
fi


echo "********** SETUP COMPLETE **********"
echo "Press any key to reboot computer"
read
sudo rebootß

