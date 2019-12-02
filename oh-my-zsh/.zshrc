# shellcheck disable=SC2148
# shellcheck disable=SC2034
# shellcheck disable=SC1090

# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH="${HOME}/.oh-my-zsh"

# Set name of the theme to load. Optionally, if you set this to "random"
# it'll load a random theme each time that oh-my-zsh is loaded.
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="bira"
#af-magic
#aussiegeek
#baboom
#bira
#bureau
#robbyrussell

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in ~/.oh-my-zsh/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion. Case
# sensitive completion must be off. _ and - will be interchangeable.
HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# The optional three formats: "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
HIST_STAMPS="yyyy-mm-dd"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
    colored-man-pages
    common-aliases
    debian
    docker
    git
    git-extras
    history
    sudo
    web-search
    zsh-completions # https://github.com/zsh-users/zsh-completions
    zsh-autosuggestions # https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md
)

# http://zsh.sourceforge.net/Doc/Release/Options.html#Options
HISTFILE=~/.zsh_history       # Where to save history to disk
HISTSIZE=10000                # How many lines of history to keep in memory
SAVEHIST=10000                # Number of history entries to save to disk
setopt appendhistory          # Append history to the history file (no overwriting)
setopt auto_pushd             # cd foo; cd bar; popd --> in foo again
setopt extended_history       # Save each command’s beginning timestamp (in seconds since the epoch) and the duration (in seconds) to the history file.
setopt hist_expire_dups_first # Deletes duplicates first before unique commands in history
setopt hist_ignore_space      # Space before command won't add command to history
setopt hist_reduce_blanks     # `a  b` normalizes to `a b` in history
setopt incappendhistory       # Immediately append to the history file, not just when a term is killed
setopt no_beep                # No beep on error
setopt no_rm_star_silent      # confirm on `rm *` (default, but let's be safe)
setopt pipe_fail              # fail when the first command in a pipeline fails
setopt rm_star_wait           # wait after confirmation on `rm *` to allow ^C
setopt sharehistory           # Share history across terminals

source "${ZSH}/oh-my-zsh.sh"

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#    export EDITOR='vim'
# else
#    export EDITOR='vim'
# fi

# https://github.com/wyntau/fzf-zsh
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# https://github.com/zsh-users/zsh-completions
autoload -U compinit && compinit

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# ssh
# export SSH_KEY_PATH="~/.ssh/rsa_id"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"
