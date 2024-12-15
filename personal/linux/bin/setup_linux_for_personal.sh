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

echo "********** SETTING UP LINUX FOR PERSONAL USE **********"
echo ""
sudo -v

#keep sudo alive VERIFIED
while true; do sudo -n true; sleep 60; done 2>/dev/null &

# install homebrew with xcode clt VERIFIED
echo "********** DOWNLOAD AND INSTALL HOMEBREW WITH XCODE COMMAND LINE TOOLS **********"
if prompt_for_confirmation; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  #put brew on path
  echo >> /home/ploppe/.zshrc
  echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/ploppe/.zshrc
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

  echo ""
  sudo apt-get install build-essential

else
  echo "skipped"
fi

# install applications VERIFIED
echo "********** DOWNLOAD AND INSTALL APPLICATIONS USING HOMEBREW **********"
if prompt_for_confirmation; then
  brew install gcc > /dev/null 2>&1
  echo "gcc installed"

  brew install --cask iterm2 > /dev/null 2>&1
  echo "iterm2 installed"

  brew install --cask 1password > /dev/null 2>&1
  echo "1password installed"

  brew install --cask 1password-cli > /dev/null 2>&1
  echo "1password-cli installed"

  brew install --cask postman > /dev/null 2>&1
  echo "postman installed"

  brew install --cask google-chrome > /dev/null 2>&1
  echo "google chrome installed"

  brew install --cask visual-studio-code > /dev/null 2>&1
  echo "visual studio code installed"

  brew install --cask teamviewer > /dev/null 2>&1
  echo "teamviewer installed"

  brew install node > /dev/null 2>&1
  echo "node installed"

  brew install pipenv > /dev/null 2>&1
  echo "pipenv installed"

  brew install pyenv > /dev/null 2>&1
  echo "pyenv installed"

  brew install wget > /dev/null 2>&1
  echo "wget installed"

  brew install sqlite > /dev/null 2>&1
  echo "sqlite installed"

  brew install awscli > /dev/null 2>&1
  echo "aws cli installed"

  brew install docker > /dev/null 2>&1
  echo "docker installed"
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

  # Postman
  echo "press any key to open Postman to login"
  read
  open -a "Postman"
  echo "press enter when done"
  read

  
else
  echo "skipped"
fi


echo "********** SETUP SSH (KEYS, ROOT CERTIFICATES, LOGINS, CONFIG) **********"
if prompt_for_confirmation; then
  ssh-keygen -C "po.markstrom@gmail.com"
  echo "Add generated personal public key to github and press enter when done"
  read
else
  echo "skipped"
fi

echo "********** CLONE DEVELOPMENT PROJECTS **********"
if prompt_for_confirmation; then
  echo "clone projects from github and press enter when done"
  read
else
  echo "skipped"
fi

echo "********** SETUP DEVELOPMENT ENVIRONMENTS **********"
if prompt_for_confirmation; then
  echo "download python versions for fwms and press enter when done"
  read
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

