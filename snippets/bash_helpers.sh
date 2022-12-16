#!/bin/bash
alias history2='history | grep '
alias find2='find | grep '
alias ps2='ps -Af | grep '

function matchboth_help () { echo "matchboth arg1 arg2: looks for files with lines containing both arg1 and arg2 (in the same line)"; }
function matchboth() {
  grep $1 * -R | grep $2
}

function matchbothquick_help () { echo "matchbothquick arg1 arg2: looks for files with contents matching both arg1 and arg2 (not necessarily in same line), quicker than matchboth (but only returns file names)"; }
function matchbothquick() {
  grep $1 $(ag $2 -l) -l
}

function matchbothlist_help () { echo "matchbothlist arg1 arg2: looks for files containing arg1 in the contents, and arg2 in the name"; }
function matchbothlist() {
  ag $2 $(ag $1 -l) -l
}
function agless() {
  ag $@ --color | less -R
}

function runless_help () { echo "runless cmd: runs cmd, and sends stdout and stderr to less"; }
function runless() {
  $1 2>&1 | less
}

function runhead_help () { echo "runhead cmd n: runs cmd, and displays the first n lines of stdout and stderr"; }
function runhead() {
  $1 2>&1 | head -n $2
}

function rungedit() {
  $@ 2>&1 | gedit -
}

function vimgrep() {
  vim $(grep -l $@ *)
}
function geditgrep() {
  gedit $(grep -l $@ *)
}

function goo_help () { echo "goo query: opens a browser window, looking for query in google search"; }
function goo() {
  query=$(echo $@ | sed -e "s/ /+/g");
  chrome "http://www.google.com/search?q=$query";
}

function gitadds_help () { echo "gitadds: prints all \"git add ...\" commands that could be used at this time"; }
function gitadds() {
  for line in $(git status | grep "Changes not staged for commit\|Untracked files\|Unmerged paths" -A 10000 | grep $'^\t' | sed $'s/^\t//g' |  sed "s/both modified:\|both added:\|deleted:\|deleted by them:\|modified://g" | sed "s/ //g" ); do
    echo git add $line;
  done
}

function alertsound_help () { echo "alertsound: plays an alert sound"; }
alias alertsound="mpg123 /usr/REPLACE/alert.mp3"

function alertmessage_help () { echo "alertmessage message: displays a notification box, with 'message' on it"; }
function alertmessage () {
  (sleep 1 && wmctrl -a Information -b add,above )&  (zenity --info --text="$@")&
}

function simplealert_help () { echo "simplealert: displays a standard notification box, and makes a sound"; }
alias simplealert="alertsound; sleep 2; alertmessage 'Something finished processing'"

function simplealert2_help () { echo "simplealert2 message: displays a standard notification box saying message, and makes a sound"; }
function simplealert2 () {
  alertsound; sleep 2; alertmessage "$@"
}

function simplealert-remote_help () { echo "simplealert-remote: make a beep that works in ssh too"; }
alias simplealert-remote="echo -e '\a'"

function colordate_help () { echo "colordate: prints date in a color bg"; }
function colordate () {
  echo -e "\e[48;5;236m$(date)\e[0m"
}

function xdg-all_help () { echo "xdg-all files: runs xdg-open on each file listed"; }
function xdg-all () {
  for i in $@; do xdg-open $i; done
}

function xdg-find2_help () { echo "xdg-all substring: runs xdg-open on each file with a name that contains substring"; }
function xdg-find2 () {
  xdg-all $(find2 $@)
}

function my() {
  echo "Commands:"
  echo "history2 find2 ps2"
  echo "matchboth matchbothquick matchbothlist"
  echo "agless runless runhead rungedit vimgrep geditgrep"
  echo "goo gitadds colordate xdg-all xdg-find2"
  echo "alertsound alertmessage simplealert simplealert2 simplealert-remote"
}
