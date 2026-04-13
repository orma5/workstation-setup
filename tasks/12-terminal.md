# Task: Terminal Configuration

## Goal
Install Oh My Zsh, Powerlevel10k theme, and download the iTerm2 Material Design color scheme.

## Prerequisites
- `git` and `curl` must be installed
- iTerm2 must be installed (from task 01-homebrew)

## Idempotency Check
- Check if `~/.oh-my-zsh` exists → Oh My Zsh already installed
- Check if `~/.oh-my-zsh/custom/themes/powerlevel10k` exists → Powerlevel10k already installed
- Check if `~/.zshrc` already contains `ZSH_THEME="powerlevel10k/powerlevel10k"` → theme already set
- Check if `~/Downloads/MaterialDesignColors.itermcolors` exists → color scheme already downloaded
Skip steps that are already done.

## Steps

### 1. Install Oh My Zsh
If `~/.oh-my-zsh` does not exist:
```bash
RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
If `~/.oh-my-zsh` already exists, log "Oh My Zsh already installed."

### 2. Install Powerlevel10k
If `~/.oh-my-zsh/custom/themes/powerlevel10k` does not exist:
```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k
```

### 3. Configure .zshrc Theme
If `~/.zshrc` exists:
- If it contains a `ZSH_THEME=` line, replace it with `ZSH_THEME="powerlevel10k/powerlevel10k"` using Edit tool.
- If it doesn't contain a `ZSH_THEME=` line, append `ZSH_THEME="powerlevel10k/powerlevel10k"` to the file.
If `~/.zshrc` does not exist, warn and skip.

### 4. Download iTerm2 Color Scheme
If `~/Downloads/MaterialDesignColors.itermcolors` does not exist:
```bash
curl -fsSL -o ~/Downloads/MaterialDesignColors.itermcolors \
  https://raw.githubusercontent.com/MartinSeeler/iterm2-material-design/master/material-design-colors.itermcolors
```

### 5. Manual Instructions
Tell the user:
> "Terminal setup is done. One manual step remains:
>
> 1. Open **iTerm2**
> 2. Go to **Preferences > Profiles > Colors > Color Presets > Import**
> 3. Import: `~/Downloads/MaterialDesignColors.itermcolors`
> 4. Select the imported preset
> 5. Configure your font: recommended **MesloLGS NF** for Powerlevel10k
> 6. Restart iTerm2
>
> Press Enter when done."

Wait for user confirmation.

## Completion Criteria
- `~/.oh-my-zsh` exists
- `~/.oh-my-zsh/custom/themes/powerlevel10k` exists
- `~/.zshrc` contains `ZSH_THEME="powerlevel10k/powerlevel10k"`
- `~/Downloads/MaterialDesignColors.itermcolors` exists
- User has confirmed manual iTerm2 steps
