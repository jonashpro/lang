" Vim syntax file
" Language: Lang

if exists("b:current_syntax")
	finish
endif

" Comments
syntax keyword langTodo contained TODO FIXME XXX
syntax match langComment "//.*$" contains=langTodo

" Keywords
syntax keyword langKeyword fn do while if else return let include continue break stdout stdin stderr

" String
syntax match langSpecialCharacters "\\[abfnrtv\n"\\]"
syntax region langString start=/\v"/ end=/\v"/ skip=/\v\\./ contains=langSpecialCharacters

" Numbers
syntax match langNumber "\<[0-9]\+\>"
syntax match langNumber "\<0b[0-1]\+\>"
syntax match langNumber "\<0o[0-7]\+\>"
syntax match langNumber "\<0x[0-9abcdefABCDEF]\+\>"

" Constants
syntax keyword langConstant nil false true

" Functions
syntax keyword langFunction write exit append pop length copy type set fopen fwrite fread fclose freadln

hi def link langKeyword Keyword
hi def link langComment Comment
hi def link langString String
hi def link langNumber Number
hi def link langConstant Constant
hi def link langFunction Identifier

let b:current_syntax = "lang"

