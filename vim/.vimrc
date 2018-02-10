
"""""""""""""""""""""""""""""""""""""
" Setup
"""""""""""""""""""""""""""""""""""""

""" Plugin manager
" git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

""" Plugin management
" vim +PluginInstall +qall
" vim +PluginClean +qall
" vim +PluginList


"""""""""""""""""""""""""""""""""""""
" Vimrc configuration
"""""""""""""""""""""""""""""""""""""
set encoding=utf8

"""" START Vundle Configuration

" Disable file type for vundle
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" let Vundle manage Vundle, required
Plugin 'gmarik/Vundle.vim'

" Utility
Plugin 'scrooloose/nerdtree'
Plugin 'majutsushi/tagbar'
"Plugin 'ervandew/supertab'
"Plugin 'BufOnly.vim'
"Plugin 'wesQ3/vim-windowswap'
"Plugin 'SirVer/ultisnips'
"Plugin 'junegunn/fzf.vim'
"Plugin 'junegunn/fzf'
"Plugin 'godlygeek/tabular'
"Plugin 'ctrlpvim/ctrlp.vim'
"Plugin 'benmills/vimux'
"Plugin 'jeetsukumaran/vim-buffergator'
"Plugin 'gilsondev/searchtasks.vim'
"Plugin 'Shougo/neocomplete.vim'
"Plugin 'tpope/vim-dispatch'
"Plugin 'jceb/vim-orgmode'
"Plugin 'tpope/vim-speeddating'

" Generic Programming Support
Plugin 'jakedouglas/exuberant-ctags'
"Plugin 'honza/vim-snippets'
"Plugin 'Townk/vim-autoclose'
"Plugin 'tomtom/tcomment_vim'
"Plugin 'tobyS/vmustache'
"Plugin 'janko-m/vim-test'
"Plugin 'maksimr/vim-jsbeautify'
"Plugin 'vim-syntastic/syntastic'
"Plugin 'neomake/neomake'

" Markdown / Writting
"Plugin 'reedes/vim-pencil'
"Plugin 'tpope/vim-markdown'
"Plugin 'jtratner/vim-flavored-markdown'
"Plugin 'LanguageTool'

" Git Support
"Plugin 'kablamo/vim-git-log'
"Plugin 'gregsexton/gitv'
"Plugin 'tpope/vim-fugitive'
"Plugin 'jaxbot/github-issues.vim'

" Theme / Interface
"Plugin 'AnsiEsc.vim'
"Plugin 'ryanoasis/vim-devicons'
"Plugin 'vim-airline/vim-airline'
"Plugin 'vim-airline/vim-airline-themes'
"Plugin 'sjl/badwolf'
"Plugin 'tomasr/molokai'
"Plugin 'morhetz/gruvbox'
"Plugin 'zenorocha/dracula-theme', {'rtp': 'vim/'}
"Plugin 'junegunn/limelight.vim'
"Plugin 'mkarmona/colorsbox'
"Plugin 'romainl/Apprentice'
"Plugin 'Lokaltog/vim-distinguished'
"Plugin 'chriskempson/base16-vim'
"Plugin 'w0ng/vim-hybrid'
"Plugin 'AlessandroYorba/Sierra'
"Plugin 'daylerees/colour-schemes'
"Plugin 'effkay/argonaut.vim'
"Plugin 'ajh17/Spacegray.vim'
"Plugin 'atelierbram/Base2Tone-vim'
"Plugin 'colepeters/spacemacs-theme.vim'
"Plugin 'dylanaraps/wal.vim'
Plugin 'altercation/vim-colors-solarized'


call vundle#end()            " required
filetype plugin indent on    " required
"""" END Vundle Configuration

"""""""""""""""""""""""""""""""""""""
" Configuration Section
"""""""""""""""""""""""""""""""""""""
set nowrap

" Show linenumbers
set number

" Set Proper Tabs
set tabstop=4
set shiftwidth=4
set smarttab
set expandtab

" Always display the status line
set laststatus=2

" Enable Elite mode, No ARRRROWWS!!!!
let g:elite_mode=1

" Enable highlighting of the current line
set cursorline

" Theme and Styling
syntax enable
"set t_Co=256
let g:solarized_termcolors=256
set background=dark
colorscheme solarized

"""""""""""""""""""""""""""""""""""""
" Mappings configurationn
"""""""""""""""""""""""""""""""""""""
map <C-n> :NERDTreeToggle<CR>
map <C-m> :TagbarToggle<CR>

" <TAB>: completion.
inoremap <expr><TAB>  pumvisible() ? "\<C-n>" : "\<TAB>"

" Disable arrow movement, resize splits instead.
if get(g:, 'elite_mode')
	nnoremap <Up>    :resize +2<CR>
	nnoremap <Down>  :resize -2<CR>
	nnoremap <Left>  :vertical resize +2<CR>
	nnoremap <Right> :vertical resize -2<CR>
endif

" Tab navigation like Firefox.
nnoremap <C-S-tab> :tabprevious<CR>
nnoremap <C-tab>   :tabnext<CR>
nnoremap <C-t>     :tabnew<CR>
inoremap <C-S-tab> <Esc>:tabprevious<CR>i
inoremap <C-tab>   <Esc>:tabnext<CR>i
inoremap <C-t>     <Esc>:tabnew<CR>:

" Split windows and tabs
map <Tab> <C-W>w
map <Bar> <C-W>v<C-W><Right>
map -     <C-W>s<C-W><Down>

" Fix ctags problem on mac
" $ brew install ctags
" $ alias ctags if you used homebrew
" $ alias ctags="`brew --prefix`/bin/ctags"
