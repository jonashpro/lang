" Vim syntax file
" Language: Lang

if exists("b:current_syntax")
	finish
endif

syntax keyword langKeywords fn do while if else return let include
syntax region langComment start="//" end="$"
syntax region langString start=/\v"/ end=/\v"/ skip=/\v\\./
syntax match langNumber "\<[0-9]\+\>"

hi def link langKeywords Keyword
hi def link langComment Comment
hi def link langString String
hi def link langNumber Number

let b:current_syntax = "lang"

